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
    name = 'Google Play Reviews'
    base_url = 'https://play.google.com/'

    def init(self):
        self.driver = ''
        self.data_lists = []

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
    
    def get_last_data(self, data_list):
        d = data_list[-1]
        name = ''.join(d.xpath('./div/div/span/text()'))
        ti = ''.join(d.xpath('./div[1]/div[1]/div/span[2]/text()'))
        stars = ''.join(d.xpath('./div[*]/div[*]/div/span[*]/div/div/@aria-label'))
        comments = ''.join(d.xpath('./div[2]/span[1]/text()'))
        msg = name + '|' + ti + '|' + comments + '|' + ''.join(re.findall('Rated(.*?)stars',stars)).replace(' ','')
        if msg not in self.data_lists:
            return True
        else:
            return False


    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_deatil_page(self, url,pagesize):
        try:
            self.driver.get(url)
        except Exception as e:
            raise Exception(e)
        self.driver.implicitly_wait(10)
        time.sleep(5)
        html = self.driver.page_source
        page = etree.HTML(html)
        app_name = ''.join(page.xpath('//h1[@class="AHFaub"]/span/text()'))
        try:
            company_name = page.xpath('//a[contains(@class, "hrTbp R8zArc")]//text()')[0]
        except:
            company_name = ''
        try:
            categiry = page.xpath('//a[contains(@class, "hrTbp R8zArc")]//text()')[1]
            category_url = 'https://play.google.com{}'.format(page.xpath('//a[contains(@class, "hrTbp R8zArc")]/@href')[1])
        except:
            categiry = ''
            category_url = ''
        data = {}
        data['App_Name'] = app_name
        data['Company_Name'] = company_name
        data['Category_URL'] = category_url
        data['Category'] = categiry
        data['URL'] = self.driver.current_url
        for i in range(0,pagesize):
            self.driver.execute_script("window.scrollTo(0,0);")
            try:
                self.driver.find_element_by_xpath('//*[contains(text(), "Read All Reviews")]').click()
                print('点击成功：阅读所有评论')
            except Exception as e:
                print(e)
            try:
                self.driver.find_element_by_xpath('//*[contains(text(), "Show More")]').click()
                print('点击成功：显示更多内容')
            except Exception as e:
                print(e)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.driver.implicitly_wait(5)
            time.sleep(5)
            html = self.driver.page_source
            page = etree.HTML(html)
            data_list = page.xpath('//*[contains(@class, "d15Mdf bAhLNe")]')
            if data_list:
                try:
                    if  self.get_last_data(data_list) == False:
                        return False
                except Exception as e:
                    print(e)
                for d in data_list:
                    name = ''.join(d.xpath('./div/div/span/text()'))
                    stars = ''.join(d.xpath('./div[*]/div[*]/div/span[*]/div/div/@aria-label'))
                    comments = ''.join(d.xpath('./div[2]/span[1]/text()'))
                    ti = ''.join(d.xpath('./div[1]/div[1]/div/span[2]/text()'))
                    data['Name'] = name
                    data['Time'] = ti
                    data['Comments'] = comments
                    data['Star_rating'] = ''.join(re.findall('Rated(.*?)stars',stars)).replace(' ','')
                    msg = name + '|' + ti + '|' + comments + '|' + stars
                    if msg not in self.data_lists:
                        self.data_lists.append(msg)
                        print(data)
                    else:
                        print('重复数据')
            else:
                data['Name'] = ''
                data['Time'] = ''
                data['Comments'] = ''
                data['Star_rating'] = ''
                self.upload(data)
                return False
        return True

    def gettime(self):
        ti = time.localtime()
        ti = '%d/%d/%d %d:%d:%d' % (ti[2], ti[1], ti[0], ti[3], ti[4], ti[5])
        return ti

    def process_item(self, keyword,Pagesize):
        pagesize = int(Pagesize)
        self.driver = self.get_driver()
        if '&hl=en' not in keyword:
            keyword = keyword + '&hl=en'
        try:
            if self.get_deatil_page(keyword,pagesize) == False:
                print('NO data')
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
            #'https://play.google.com/store/apps/details?id=com.graphicstool.pubggfxtool.graphicssettings.gfx.for.pubg.settings.optimizer',
            #'https://play.google.com/store/apps/details?id=com.pubg.krmobile',
            'https://play.google.com/store/apps/details?id=gg.op.lol.android&showAllReviews=true'
            'https://play.google.com/store/apps/details?id=com.squidgame.hpwallpaper.download',
        ],
        "Pagesize": 200,
    }
    function = AtomExecutor()
    function.init()
    Pagesize = params['Pagesize']
    for params in params['MainKeys']:
        try:
            function.process_item(params,Pagesize)
        except Exception as e:
            print(e)


