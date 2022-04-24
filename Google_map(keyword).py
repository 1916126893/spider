import logging
import os
import random
import re
import json
import time
from pyppeteer import launch
import random
import requests
import tenacity
import asyncio
from lxml import etree
import json
try:
    import nest_asyncio
except:
    os.system('pip install nest_asyncio')
    import nest_asyncio
nest_asyncio.apply()
pyppeteer_level = logging.WARNING
logging.getLogger('pyppeteer').setLevel(pyppeteer_level)
logging.getLogger('websockets.protocol').setLevel(pyppeteer_level)
pyppeteer_logger = logging.getLogger('pyppeteer')
pyppeteer_logger.setLevel(logging.WARNING)


class AtomExecutor():
    name = 'Google_map(keyword)'
    base_url = 'https://www.google.es/maps/?hl=en'

    def init(self):
        self.browser = ''
        self.page = ''
        self.api_url = ''
        self.google_list_url = []
        self.keyword = ''
        self.Pagesize = 0
        self.proxy = {
            'http': 'http://127.0.0.1:10809',
            'https': 'http://127.0.0.1:10809',
        }

    async def PyppeteerMain(self):
        self.browser = await launch({
            'headless': False,
            'userDataDir': 'pyppeteer_data_for_cjt' + '_{}'.format(time.time()),
            'args': [
                '--no-sandbox',
                '--start-maximized',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled',
                '--user-agent={}'.format(self.get_ua()),
            ],
            'dumpio': True
        })
        self.page = await self.browser.newPage()
        await self.page.setUserAgent(self.get_ua())
        await self.page.setViewport({
            "width": 1920,
            "height": 1080
        })

    async def goto_google_map(self):
        await asyncio.sleep(5)
        await self.page.type('#searchboxinput', self.keyword)
        await self.page.keyboard.press('Enter')
        await asyncio.sleep(10)
        return True

    async def intercept_network_request(self, request):
        if 'search?' in request.url:
            self.api_url = request.url
        else:
            await request.continue_()

    @tenacity.retry(stop=tenacity.stop_after_attempt(5))
    def google_map(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.page.setRequestInterception(True))
            self.page.on('request', lambda request: asyncio.create_task(self.intercept_network_request(request)))
            loop.run_until_complete(self.page.goto("https://www.google.com/maps?hl=en", options={'timeout': 1000 * 50}))
            loop.run_until_complete(self.goto_google_map())
        except Exception as e:
            asyncio.get_event_loop().run_until_complete(self.browser.close())
            asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
            print('google_map：{}'.format(e))
            raise Exception(e)
        if '&ech=1' and '7i20!' in self.api_url:
            return True
        else:
            asyncio.get_event_loop().run_until_complete(self.browser.close())
            asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
            error = '{}：没有捕获到api,retry'.format(self.keyword)
            print(error)
            raise Exception(error)

    @tenacity.retry(stop=tenacity.stop_after_attempt(2))
    def get_google_list(self, url):
        try:
            response = self.get_google_html(url)
            if response.status_code == 200:
                return self.get_detail(response, url)
        except Exception as e:
            raise Exception(e)

    def process_item(self, keyword,PageSize):
        self.init()
        self.keyword = keyword
        self.Pagesize = PageSize
        asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
        try:
            self.google_map()
        except Exception as e:
            print('process_item：{}'.format(e))
        asyncio.get_event_loop().run_until_complete(self.browser.close())
        if self.api_url:
            for i in range(1, self.Pagesize*3):
                url = self.api_url.replace('7i20!', '7i20!8i{}!'.format(i*10)).replace('&ech=1', '&ech={}'.format(i))
                try:
                    if self.get_google_list(url) == False:
                        break
                except Exception as e:
                    print('get_google_list：{}'.format(e))
        else:
            print('{}：没有捕获到api,over'.format(self.keyword))

    def get_detail(self, response, key_url):
        html = response.text
        data_dict = json.loads(html.replace('/*""*/', ''))
        d_str = data_dict['d'].replace(")]}'", '')
        d_list = json.loads(d_str)
        data_list = d_list[0][1]
        if data_list:
            for data in data_list:
                try:
                    if len(data) > 14:
                        try:
                            key_list_9_2 = round(data[14][9][2], 7)
                            key_list_9_3 = round(data[14][9][3], 7)
                            key_list_10 = data[14][10]
                            key_list_11 = data[14][11]
                            url = 'https://www.google.es/maps/place/{}/data=!4m5!3m4!1s{}!8m2!3d{}!4d{}?authuser=0&hl=en&rclk=1'.format(key_list_11.replace(' ', '+'), key_list_10, key_list_9_2, key_list_9_3)
                        except:
                            url = ''
                        if url:
                            if url not in self.google_list_url:
                                try:
                                    data_json = self.get_google_detail(url)
                                    try:
                                        if data_json[6][160][0] == 1:
                                            current_Status = 'Temporarily closed'
                                        else:
                                            current_Status = ''
                                    except:
                                        current_Status = ''
                                except Exception as e:
                                    print(e)
                                self.google_list_url.append(url)
                                if len(self.google_list_url) >= self.Pagesize*20:
                                    return False
                        else:
                            print('{}：获取失败，URL：{}'.format(self.keyword, key_url))
                except Exception as e:
                    print(e)
        # 是否还有下一页
        try:
            code = d_list[0][3]
            if code == 1:
                return True
            else:
                return False
        except:
            return False

    def get_google_detail(self, url):
        try:
            response = self.get_google_html(url)
            page = etree.HTML(response.text)
            a = page.xpath('/html/head/script/text()')
            for b in a:
                if '(function(){window.APP_OPTIONS=' in b:
                    c = b
                    break
            if c:
                e = json.loads(re.findall('window.APP_INITIALIZATION_STATE=(.*?);window.APP_FLAGS', c)[0])
                d = json.loads(e[3][6].replace(")]}'", ''))
                return d
            else:
                return False
        except Exception as e:
            return False

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_google_html(self,url):
        try:
            response = requests.request("GET", url, proxies=self.proxy, timeout=20)
            if response.status_code == 200:
                return response
            else:
                error = '{}：api：{},返回：{}'.format(self.keyword, url, response.status_code)
                raise Exception(error)
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def get_ua():
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
        ]
        return random.choice(user_agent_list)


if __name__ == "__main__":
    params = {
        "MainKeys": [
            'Kumar Pathological Lab',
            'Hotels',
        ],
        "PageSize": 20,
    }
    Pagesize = params['PageSize']
    function = AtomExecutor()
    MainKeys =  params['MainKeys']
    for params in MainKeys:
        try:
            function.process_item(params,Pagesize)
        except Exception as e:
            print(e)