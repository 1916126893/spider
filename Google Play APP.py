import time
import re
import os
import json
import random
import requests
from lxml import etree
import tenacity
from selenium import webdriver

class AtomExecutor():
    name = 'Google Play APP'
    base_url = 'https://play.google.com/'

    def init(self):
        self.driver = ''
        self.url_lists = []

    def get_driver(self):
        # proxy = self.getProxy()
        # proxy =proxy['http'].replace('http://','')
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_experimental_option("excludeSwitches", ['enable-automation'])
        chromeOptions.add_experimental_option('useAutomationExtension', False)
        chromeOptions.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        chromeOptions.add_argument("--disable-blink-features=AutomationControlled")
        # chromeOptions.add_argument("--proxy-server={}".format(proxy))
        chromeOptions.add_argument(
            f'--user-agent=f{self.get_ua()}')
        prefs = {}
        preferences = {
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False
        }
        chromeOptions.add_experimental_option('prefs', preferences)
        chromeOptions.add_argument('--disable-infobars')
        chromeOptions.add_argument("--start-maximized")
        # No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        # chromeOptions.add_experimental_option("prefs", No_Image_loading)
        # 修改1
        chromeOptions.add_argument("--headless")  # 开关浏览器 注释了就是开 不注释就是关
        chromeOptions.add_argument("--no-sandbox")
        # 后面是你的浏览器驱动位置，记得前面加r'','r'是防止字符转义的
        try:
            driver = webdriver.Chrome("C:\\Users\\Administrator\\Desktop\\chromedriver.exe")
        except:
            driver = webdriver.Chrome(options=chromeOptions)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """Object.defineProperty(navigator, 'webdriver', {get: () : false})""",
        })
        driver.set_page_load_timeout(120)
        return driver

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_list_page(self, url):
        try:
            self.driver.get(url)
        except Exception as e:
            print(e)
        for i in range(0, 30):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.driver.implicitly_wait(5)
            time.sleep(5)
            html = self.driver.page_source
            page = etree.HTML(html)
            data_list = page.xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/c-wiz/c-wiz/c-wiz/div/div[2]/c-wiz[*]/div')
            if ''.join(data_list[-1].xpath('./div/div[*]/div/div/a/@href')) in self.url_lists:
                break
            for d in data_list:
                url = ''.join(d.xpath('./div/div[*]/div/div/a/@href'))
                title = ''.join(d.xpath('./div/div[*]/div/div/div[*]/div/div/div[*]/a/div/@title'))
                stars = ''.join(d.xpath('./div/div[*]/div/div/div[*]/div/div/div/div/@aria-label'))
                if url not in self.url_lists:
                    self.url_lists.append(url)
                    data = {
                        'Name_of_App':title,
                        'Rating':stars,
                        'App_Detail_Web_Page_URL':'https://play.google.com{}'.format(url)

                    }
                    print(data)
                else:
                    print('重复数据：{}'.format(url))

    def gettime(self):
        ti = time.localtime()
        ti = '%d/%d/%d %d:%d:%d' % (ti[2], ti[1], ti[0], ti[3], ti[4], ti[5])
        return ti


    def process_item(self, keyword):
        self.driver = self.get_driver()
        try:
            url = 'https://play.google.com/store/search?q={}&c=apps'.format(keyword)
            self.get_list_page(url)
        except Exception as e:
            self.driver.quit()
            self.driver = self.get_driver()
            print(e)
        self.driver.quit()
        print('run over')

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
            'app',
            'game',
        ],
    }

    function = AtomExecutor()
    function.init()
    for params in params['MainKeys']:
        try:
            function.process_item(params)
        except Exception as e:
            print(e)
