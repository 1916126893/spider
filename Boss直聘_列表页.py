

from lxml import etree
from urllib import parse
import logging
import re
import os
import time
import shutil
import json
from pyppeteer import launch
import random
import requests
import tenacity
import asyncio
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
    name = 'Boss直聘_列表页'
    base_url = 'https://www.zhipin.com/'

    def init(self):
        self.browser = ''
        self.page = ''
        self.region_url = []
        self.state = False
        self.zhaopin_url = []

    async def PyppeteerMain(self):
        proxy = self.getProxy()
        self.browser = await launch({
            'headless': True,
            'userDataDir': 'pyppeteer_data_for_cjt' + '_{}'.format(time.time()),
            'args': [
                '--no-sandbox',
                '--start-maximized',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled',
                '--proxy-server={}'.format(proxy['proxyip']),
                '--user-agent={}'.format(self.get_ua()),
            ],
            'dumpio': True
        })
        self.page = await self.browser.newPage()
        await self.page.authenticate({'username': proxy['username'], 'password': proxy['password']})
        await self.page.setUserAgent(self.get_ua())
        await self.page.setViewport({
            "width": 1920,
            "height": 1080
        })
        self.page = await asyncio.ensure_future(self.fake_js(self.page))

    async def fake_js(self, page):
        # 执行一系列js代码进行伪装
        # 绕开webdriver检测
        # Pass the Webdriver Test
        await page.evaluateOnNewDocument('''() => {
                                    const newProto = navigator.__proto__;
                                    delete newProto.webdriver;
                                    navigator.__proto__ = newProto;
                                }''')

        await page.evaluateOnNewDocument('''() => {
                                        Object.defineProperty(navigator, 'WebDriver', {
                                                    get: () => false;
                                            });
                                        }''')

        await page.evaluateOnNewDocument('''() => {
                Object.defineProperty(navigator, 'plugins', {
                    //伪装真实的插件信息
                    get: () => [
                    {
                        0: {
                        type: 'application/x-google-chrome-pdf',
                        suffixes: 'pdf',
                        description: 'Portable Document Format',
                        enabledPlugin: Plugin,
                        },
                        description: 'Portable Document Format',
                        filename: 'internal-pdf-viewer',
                        length: 1,
                        name: 'Chrome PDF Plugin',
                    },
                    {
                        0: {
                        type: 'application/pdf',
                        suffixes: 'pdf',
                        description: '',
                        enabledPlugin: Plugin,
                        },
                        description: '',
                        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                        length: 1,
                        name: 'Chrome PDF Viewer',
                    },
                    {
                        0: {
                        type: 'application/x-nacl',
                        suffixes: '',
                        description: 'Native Client Executable',
                        enabledPlugin: Plugin,
                        },
                        1: {
                        type: 'application/x-pnacl',
                        suffixes: '',
                        description: 'Portable Native Client Executable',
                        enabledPlugin: Plugin,
                        },
                        description: '',
                        filename: 'internal-nacl-plugin',
                        length: 2,
                        name: 'Native Client',
                    }
                ],
                });
            }''')

        await page.evaluateOnNewDocument('''() => {
                window.chrome = {};
                window.chrome.app = {
                    InstallState: 'hehe',
                    RunningState: 'haha',
                    getDetails: 'xixi',
                    getIsInstalled: 'ohno',
                };
                window.chrome.csi = function () {};
                window.chrome.loadTimes = function () {};
                window.chrome.runtime = function () {};
            }''')
        await page.evaluateOnNewDocument('''() => {
                Object.defineProperty(navigator, 'userAgent', {
                    #userAgent在无头模式下有headless字样，所以需覆盖
                    get: () =>
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
                });
            }''')
        await page.evaluateOnNewDocument('''() => {
                Object.defineProperty(navigator, 'languages', {
                    //添加语言
                    get: () => "zh-CN"
                });
            }''')

        await page.evaluateOnNewDocument('''() => {
                        Object.defineProperty(navigator, 'deviceMemory', {
                                    get: () => 8
                                });
                    }''')

        await page.evaluateOnNewDocument('''() => {
                                Object.defineProperty(navigator, 'platform', {
                                        get: () => 'MacIntel'
                                    });
                            }''')

        await page.evaluateOnNewDocument('''() => {
                const originalQuery = window.navigator.permissions.query; //notification伪装
                window.navigator.permissions.query = (parameters) =>
                    parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : originalQuery(parameters);
            }''')
        await page.evaluateOnNewDocument('''() => {
                const getParameter = WebGLRenderingContext.getParameter;
                WebGLRenderingContext.prototype.getParameter = function (parameter) {
                    // UNMASKED_VENDOR_WEBGL
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    // UNMASKED_RENDERER_WEBGL
                    if (parameter === 37446) {
                        return 'Intel(R) Iris(TM) Graphics 6100';
                    }
                    return getParameter(parameter);
                };
            }''')
        print('伪装代码执行完毕！')
        return page

    async def get_list_city(self, url, keyword):
        if '100010000' in url:
            url_list = self.get_city_code(keyword)
            return url_list
        else:
            try:
                await self.page.goto(url, options={'timeout': 1000 * 30})
            except Exception as e:
                raise Exception(e)
            time.sleep(15)
            html = await self.page.content()
            page = etree.HTML(html)
            city = ''.join(page.xpath(
                '//*[@id="filter-box"]/div/div[*]/div[*]/form/div[*]/div[1]/span/b/text()'))
            if city:
                city_url_list = page.xpath(
                    '//*[@id="filter-box"]/div/div[2]/dl[2]/dd/a/@href')
                url_list = []
                for city_ur in city_url_list[1:len(city_url_list)]:
                    if city_ur != 'javascript:;':
                        url_list.append(
                            'https://www.zhipin.com/{}'.format(city_ur))
                    else:
                        break
                cookies = await self.page.cookies()
                return url_list
            else:
                raise Exception(html)

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_city_code(self, keyword):
        proxy = self.getProxy()['url']
        url = "https://www.zhipin.com/wapi/zpCommon/data/cityGroup.json"
        headers = {
            'authority': 'www.zhipin.com',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        response = requests.request("GET", url, headers=headers, timeout=20)
        data_json = json.loads(response.text).get('zpData')
        firstChar_list = data_json.get('cityGroup')
        city_list = []
        code_list = []
        for firstChar in firstChar_list:
            city_list = firstChar.get('cityList')
            for city in city_list:
                code_list.append('https://www.zhipin.com/job_detail/?query={}&city={}'.format(
                    parse.quote(keyword, encoding='utf-8'), str(city.get('code'))))
        return code_list

    async def get_list_page(self, url, keyword, pagesize):
        try:
            await self.page.goto(url, options={'timeout': 1000 * 30})
        except Exception as e:
            print(e)
            raise Exception('retry')
        time.sleep(15)
        html = await self.page.content()
        page = etree.HTML(html)
        city = ''.join(page.xpath(
            '//*[@id="filter-box"]/div/div[*]/div[*]/form/div[*]/div[1]/span/b/text()'))
        data_list = page.xpath('//*[@id="main"]/div/div[*]/ul/li[*]')
        if city:
            for d in data_list:
                job_url = 'https://www.zhipin.com{}'.format(
                    ''.join(d.xpath('./div/div[*]/div[*]/div/div[*]/span[*]/a/@href')))
                if job_url not in self.zhaopin_url:
                    self.zhaopin_url.append(job_url)
                    job_keyword = keyword
                    job_name = ''.join(
                        d.xpath('./div/div[*]/div[*]/div/div[*]/span[*]/a/@title'))
                    job_address = ''.join(
                        d.xpath('./div/div[*]/div[*]/div/div[*]/span[*]/span/text()'))
                    job_pay = ''.join(
                        d.xpath('./div/div[*]/div[*]/div/div[2]/span/text()'))
                    msg = ''.join(
                        d.xpath('./div/div[*]/div[*]/div/div[2]/p/text()'))
                    if '天' in msg:
                        for i in range(0, 4):
                            job_need = ''.join(
                                d.xpath('./div/div[*]/div[*]/div/div[2]/p/text()[{}]'.format(str(i))))
                            if job_need != '':
                                if '天' not in job_need and '周' not in job_need and '月' not in job_need:
                                    break
                        job_year = ''.join(
                            d.xpath('./div/div[*]/div[*]/div/div[2]/p/text()')).replace(job_need, '')
                    else:
                        job_year = ''.join(
                            d.xpath('./div/div[*]/div[*]/div/div[2]/p/text()[1]'))
                        job_need = ''.join(
                            d.xpath('./div/div[*]/div[*]/div/div[2]/p/text()[2]'))
                    job_company_name = ''.join(
                        d.xpath('./div/div[*]/div[*]/div/h3/a/text()'))
                    job_company_xingye = ''.join(
                        d.xpath('./div/div[*]/div[*]/div/p/a/text()'))
                    job_company_people = ''.join(
                        d.xpath('./div/div[*]/div[*]/div/p/text()[2]'))
                    print(job_company_people)
                    job_company_link = 'https://www.zhipin.com/{}'.format(
                        ''.join(d.xpath('./div/div[*]/div[*]/div/h3/a/@href')))
                    data = {
                        '页码': str(pagesize),
                        '搜索链接': url,
                        '招聘链接': job_url,
                        '城市': city,
                        '关键词': job_keyword,
                        '职位名称': job_name,
                        '区域': job_address,
                        '薪资': job_pay,
                        '经验要求': job_year,
                        '学历要求': job_need,
                        '公司名称': job_company_name,
                        '公司行业': job_company_xingye,
                        '公司规模': job_company_people,
                        '公司链接': job_company_link
                    }
                    print(data)
                else:
                    print('重复数据：{}'.format(job_url))
        else:
            raise Exception(url)
        try:
            next_url = page.xpath(
                '//*[@id="main"]/div/div[*]/div[*]/a/@href')[-1]
            if next_url == 'javascript:;':
                return False
        except:
            return False
        return True

    @staticmethod
    def getProxy():
        try:
            url = ""
            headers = {
                'Authorization': ''
            }
            resp = requests.get(url=url, headers=headers, timeout=5).json()
            proxy = {}
            proxy['username'] = resp['data'][0]['userName']
            proxy['password'] = resp['data'][0]['passWord']
            proxy['url'] = {
                'http': 'http://' + resp['data'][0]['host'] + ':' + str(resp['data'][0]['port']),
                'https': 'http://' + resp['data'][0]['host'] + ':' + str(resp['data'][0]['port']),
            }
            proxy['proxyip'] = resp['data'][0]['host'] + \
                ':' + str(resp['data'][0]['port'])
            return proxy
        except Exception as e:
            print(e)

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def gettime(self):
        ti = time.localtime()
        ti = '%d-%d-%d %d:%d:%d' % (ti[0], ti[1], ti[2], ti[3], ti[4], ti[5])
        return ti

    @tenacity.retry(stop=tenacity.stop_after_attempt(50))
    def get_list_taowa(self, url, keyword, i, code):
        loop = asyncio.get_event_loop()
        try:
            if code == 1:
                return loop.run_until_complete(self.get_list_city(url, keyword))
            elif code == 2:
                if loop.run_until_complete(self.get_list_page(url, keyword, i)) == False:
                    return False
        except Exception as e:
            print(e)
            asyncio.get_event_loop().run_until_complete(self.browser.close())
            self.del_old_user_data()
            asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
            raise Exception(e)

    # 删除之前残留的浏览器文件
    def del_old_user_data(self):
        try:
            for file_name in os.listdir():
                if 'pyppeteer_data_for_cjt' in file_name:
                    shutil.rmtree(file_name)
        except Exception as e:
            print(e)

    def process_item(self, keyword,Pagesize,Zipcode):
        self.del_old_user_data()
        p = int(Pagesize)
        zipcode = Zipcode
        asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
        for code in zipcode:
            if code != '100010000':
                try:
                    url = 'https://www.zhipin.com/job_detail/?query={}&city={}'.format(
                        parse.quote(keyword, encoding='utf-8'), code)
                    self.region_url = self.get_list_taowa(url, keyword, 1, 1)
                except Exception as e:
                    print(e)
                try:
                    for url in self.region_url:
                        for i in range(1, p):
                            if self.get_list_taowa('{}&page={}&ka=page-{}'.format(url, str(i), str(i)), keyword, i, 2) == False:
                                break
                except Exception as e:
                    print(e)
                asyncio.get_event_loop().run_until_complete(self.browser.close())

    @staticmethod
    def get_ua():
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
            "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        return random.choice(user_agent_list)


if __name__ == "__main__":
    params = {
        "MainKeys": [
            '爬虫',
            '网络',
        ],
        "Pagesize": 200,
        'Zipcode': [
            '101280600',
            '101010100',
        ]
    }
    Pagesize = params['Pagesize']
    Zipcode  = params['Zipcode']
    function = AtomExecutor()
    function.init()
    for params in params['MainKeys']:
        try:
            function.process_item(params,Pagesize,Zipcode)
        except Exception as e:
            print(e)

