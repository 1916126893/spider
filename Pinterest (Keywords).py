import re
import json
from urllib import parse
import time
import calendar
from selenium import webdriver
import random
from sys import platform
import requests
import tenacity
from lxml import etree

class AtomExecutor():
    name = 'Pinterest (Keywords)'
    base_url = 'https://www.pinterest.com/'
    def init(self):
        self.RUN_DATE = None
        self.data_list = []

    def get_driver(self):
        # proxy = self.getProxy()
        # proxy =proxy['http'].replace('http://','')
        chromeOptions = webdriver.ChromeOptions()
        # chromeOptions.add_argument("--proxy-server={}".format(proxy))
        chromeOptions.add_experimental_option("excludeSwitches", ['enable-automation'])
        chromeOptions.add_argument("--disable-blink-features=AutomationControlled")
        chromeOptions.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36')
        chromeOptions.add_experimental_option('useAutomationExtension', False)
        chromeOptions.add_argument('--disable-infobars')
        chromeOptions.add_argument("--start-maximized")
        ###########修改1
        chromeOptions.add_argument("--headless")##开关浏览器 注释了就是开 不注释就是关
        chromeOptions.add_argument("--no-sandbox")
        # 后面是你的浏览器驱动位置，记得前面加r'','r'是防止字符转义的
        try:
            driver = webdriver.Chrome("C:\\Users\\Administrator\\Desktop\\chromedriver.exe")
        except:

            driver = webdriver.Chrome(options=chromeOptions)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined}) """})
        driver.set_page_load_timeout(120)
        return driver

    ###2021年11月26日16:50:43
    ##重写采集列表页，api改浏览器
    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_list_page(self,words,p):
        ###############
        word_split = ''
        if ' ' in words:
            keyword_list = words.split(' ')
            for keyword in keyword_list:
                word_split = word_split +  '&term_meta[]={}|typed'.format(parse.quote(keyword,encoding='utf-8'))
        else:
            word_split =  '&term_meta[]={}|typed'.format(parse.quote(words,encoding='utf-8'))
        ######################
        url = 'https://www.pinterest.com/search/pins/?q={}&rs=typed{}'.format(parse.quote(words,encoding='utf-8'),word_split)
        driver = self.get_driver()
        driver.get(url)
        for i in range(1,100):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            html = driver.page_source
            page = etree.HTML(html)
            data_list = page.xpath('//div[@class="Yl- MIw Hb7"]')
            #############################
            if len(data_list) == 0:
                driver.quit()
                raise Exception('retry')
            #############################
            for d in data_list:
                id = ''.join(d.xpath('./div/div/@data-test-pin-id'))
                picture = ''.join(d.xpath('./div/div/div[1]/div[1]/a/img/@src'))
                data = {
                    '关键词':words,
                    '帖子ID':id,
                    '图片url':picture,
                }
                if data not in self.data_list:
                    try:
                        self.get_detail_info(data)
                    except Exception as e:
                        print(e)
                if len(self.data_list) >= p:
                    driver.quit()
                    return(True)
        return(False)
    

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_detail_info(self, data):
        id = data['帖子ID']
        url = 'https://www.pinterest.com/pin/'  + id
        headers = {
            'User-Agent': self.get_ua(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        requests.packages.urllib3.disable_warnings()
        res = requests.get(url, headers=headers,timeout=20)
        page_source = res.content.decode()
        page = etree.HTML(page_source)
        data_msg = page.xpath('//*[@id="__PWS_DATA__"]/text()')
        ############
        title = ''
        key = ''
        username = ''
        name= ''
        info = ''
        title = ''
        fans = ''
        ###############
        if data_msg:
            data_json = json.loads(data_msg[0])
            try:
                username = data_json.get('props').get('initialReduxState').get('pins').get(id).get(
                    'closeup_attribution').get('first_name')
                name = data_json.get('props').get('initialReduxState').get('pins').get(id).get(
                    'closeup_attribution').get('username')
                key = data_json.get('props').get('initialReduxState').get('pins').get(id).get('aggregated_pin_data').get('id')
                info = data_json.get('props').get('initialReduxState').get('pins').get(id).get('closeup_unified_description')
                title = data_json.get('props').get('initialReduxState').get('pins').get(id)['grid_title']
                fans = data_json.get('props').get('initialReduxState').get('pins').get(id).get('closeup_attribution').get(
                    'follower_count')
            except Exception as e:
                data_dict = data_json.get('props').get('initialReduxState').get('resources').get('PinResource')
                key_dict = 'field_set_key="unauth_react_main_pin",id="' + id + '''"'''
                username = data_dict[key_dict]['data']['pinner']['full_name']
                name = data_dict[key_dict]['data']['pinner']['username']
                key = data_dict[key_dict]['data']['aggregated_pin_data']['id']
                info = data_dict[key_dict]['data']['closeup_description']
                title = data_dict[key_dict]['data']['grid_title']
                if info == None:
                    info = data_dict[key_dict]['data']['closeup_unified_description']
                fans = data_dict[key_dict]['data']['pinner']['follower_count']
            ##花里胡哨，这种情况是视频主页，接口采集不到正文，换浏览器
            if info == ' ':
                try:
                    info = self.get_info(url)
                except:
                    info = 'null'
                
            #获取评论详情接口,一次请求200条评论
            pagesize = 200
            pl_data_list = []
            l = 200
            while pagesize == l:
                ##初始化变量
                l = 0
                ######
                pl_url =  "https://www.pinterest.com/resource/AggregatedCommentFeedResource/get/?source_url=/pin/" +  id +"/&data={%22options%22:{%22objectId%22:%22" + key + "%22,%22page_size%22:"+ str(pagesize) + ",%22redux_normalize_feed%22:true,%22featured_ids%22:null,%22no_fetch_context_on_resource%22:false},%22context%22:{}}&_=" + str(int(time.time() * 1000))
                res = requests.get(pl_url,timeout=20)
                data_json = json.loads(res.text)
                ########父评论
                pl_data_list = data_json.get('resource_response').get('data')
                ########子评论
                for pl_data in pl_data_list:
                    comment_count = pl_data.get('comment_count')
                    l += int(comment_count)
                ################
                l += len(pl_data_list)
                if pagesize == l:
                    pagesize = pagesize + 50
                else:
                    break
            ###2021年11月23日10:16:10，解决粉丝数为0的问题
            if fans == 0:
                fans = self.get_fans(username,name)
            ################
            data_upload = {
                '关键词':data['关键词'],
                '图片url':data['图片url'],
                '帖子URL':url,
                '标题':title,
                '内容':info,
                '账户名':username,
                '粉丝数':fans,
                '评论数':str(l),
            }
            print(data_upload)
            self.data_list.append(data)


    def gettime(self):
        ti = time.localtime()
        ti = '%d-%d-%d %d:%d:%d' % (ti[0], ti[1], ti[2], ti[3], ti[4], ti[5])
        return ti

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_info(self,url):
        driver = self.get_driver()
        driver.get(url)
        time.sleep(3)
        driver.implicitly_wait(20)
        driver.refresh()
        time.sleep(3)
        driver.implicitly_wait(20)
        html = driver.page_source
        page = etree.HTML(html)
        try:
            info = '\n'.join(page.xpath('//*[@id="mweb-unauth-container"]/div/div/div/div[*]/div/div/div[*]/div/div[*]/div[*]/div/div[*]/div/text()'))
            if info == ' ' or '':
                info = '\n'.join(page.xpath('//*[@id="mweb-unauth-container"]/div/div/div/div[*]/div/div/div/div/div[*]/div/div/div/div[*]/div/h2/span/text()'))
        except:
            info = 'null'
        driver.quit()
        return(info)

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_fans(self,username,twoname):
        name = username.lower().replace(' ' ,'')
        headers = {
            'User-Agent': self.get_ua(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        url = 'https://www.pinterest.com/resource/UserResource/get/?source_url=/' + name + '/_created/&data={"options":{"field_set_key":"profile","username":"' + name + '","is_mobile_fork":true},"context":{}}&_=' + str(int(time.time() * 1000))
        res = requests.get(url,headers=headers,timeout=5)
        data_json = json.loads(res.text)
        try:
            fans = str(data_json.get('resource_response').get('data')['follower_count'])
        except:
            fans = 'null'
        ###########花里胡哨
        if fans == 'null':
            name = username.replace(' ' ,'')
            url = 'https://www.pinterest.com/resource/UserResource/get/?source_url=/' + name + '/_created/&data={"options":{"field_set_key":"profile","username":"' + name + '","is_mobile_fork":true},"context":{}}&_=' + str(int(time.time() * 1000))
            res = requests.get(url,headers=headers,timeout=5)
            data_json = json.loads(res.text)
            try:
                fans = data_json.get('resource_response').get('data')['follower_count']
            except:
                fans = 'null'
        ###########花里胡哨
        if fans == 'null':
            url = '-+' + str(int(time.time() * 1000))
            res = requests.get(url,headers=headers,timeout=5)
            data_json = json.loads(res.text)
            try:
                fans = data_json.get('resource_response').get('data')['follower_count']
            except:
                fans = 'null'
        return fans


    def process_item(self, keyword,pagesize):
        #需要获取的数量
        p = int(pagesize)
        try:
            self.get_list_page(keyword,p)
        except Exception as e:
            print(e)
        #################
        self.data_list = []

    @staticmethod
    def getProxy():
            proxies = {
                "http": "", 
                "https": ""
            }
            return proxies

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
            'wedding budget categories',
        ],
        "pagesize": 200,
    }
    pagesize = params['pagesize']
    function = AtomExecutor()
    function.init()
    for params in params['MainKeys']:
        try:
            function.process_item(params,pagesize)
        except Exception as e:
            print(e)



