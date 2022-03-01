import json
import random
import re
from sys import platform
import requests
from lxml import etree
import tenacity


class AtomExecutor():
    name = 'walmart_list'
    base_url = 'https://www.walmart.com/'

    def init(self):
        self.pagesize = 0
        self.cookie = ''
        self.dataup_list = []

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_list_page(self, url):
        proxy = self.getProxy()
        payload = {}
        headers = {
            'Host': 'www.walmart.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers',
            'Cookie': self.cookie
        }
        res = requests.request("GET", url, headers=headers, data=payload, timeout=20)
        html = res.text
        page = etree.HTML(html)
        data_list = page.xpath(
            '//*[@id="__next"]/div[1]/div/div/div/div/main/div/div/div/div/div[*]/section/div/div[*]')
        if len(data_list) == 0:
            raise Exception('retry')
        if self.pagesize == 0:
            try:
                self.pagesize = int(int(re.findall('[1-9]\d*|0$', page.xpath(
                    '//*[@id="__next"]/div[1]/div/div/div/div/main/div/div[2]/div/div/div[1]/div/div/span/text()')[-1])[-1])/32)
            except:
                self.pagesize = 8
        data = page.xpath('//*[@id="__NEXT_DATA__"]/text()')[0]
        data_json = json.loads(data)
        data_list = data_json.get('props').get('pageProps').get(
            'initialData').get('searchResult').get('itemStacks')[0].get('items')
        for d in data_list:
            try:
                shop_title = d.get('name')
                shop_url = d.get('canonicalUrl')
                if shop_url != None and shop_title != None:
                    shop_url = 'https://www.walmart.com' + shop_url
                    if shop_url not in self.dataup_list:
                        self.dataup_list.append(shop_url)
                        data = {
                            'Title': shop_title,
                            'Url': shop_url,
                        }
                        print(data)
                    else:
                        print(shop_url)
            except Exception as e:
                print(e)

    def process_item(self, keyword, Cookie):
        keyword = keyword.replace(' ', '-')
        self.cookie = Cookie
        for i in range(0, 2):
            if self.pagesize != 0:
                try:
                    for i in range(2, self.pagesize):
                        url = 'https://www.walmart.com/search?q={}&page={}&affinityOverride=default'.format(
                            keyword, str(i))
                        self.get_list_page(url)
                except Exception as e:
                    print(e)
            else:
                try:
                    url = 'https://www.walmart.com/search?q={}'.format(keyword)
                    self.get_list_page(url)
                except Exception as e:
                    print(e)

    @staticmethod
    def getProxy():
        proxies = {
            'http': '',
            'https': '',
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
            'car battery',
        ],
        'Cookie': 'ACID=7fb3420a-7001-4ede-bf6f-b33be46afb57; hasACID=true; vtc=TtLw6sZXLxEr96RFKbiq9M; com.walmart.accfitment=Y:2016#M:Aston Martin#BV:137016#MO:V12 Vantage#SM:1#EB:1207; dimensionData=937; hasLocData=1; locGuestData=eyJpbnRlbnQiOiJTSElQUElORyIsInN0b3JlSW50ZW50IjoiUElDS1VQIiwibWVyZ2VGbGFnIjp0cnVlLCJpc0RlZmF1bHRlZCI6ZmFsc2UsInBpY2t1cCI6eyJub2RlSWQiOiIzNzE3IiwidGltZXN0YW1wIjoxNjQxNzgzNDUyMzcwfSwicG9zdGFsQ29kZSI6eyJ0aW1lc3RhbXAiOjE2NDE3ODM0NTIzNzAsImJhc2UiOiIzNzIxMSJ9LCJ2YWxpZGF0ZUtleSI6InByb2Q6djI6N2ZiMzQyMGEtNzAwMS00ZWRlLWJmNmYtYjMzYmU0NmFmYjU3In0=; TBV=7; adblocked=false; _pxvid=111ec31b-92cd-11ec-9dbb-6770796f7945; tb_sw_supported=true; QuantumMetricUserID=6755d7d8f68bb516ce1244543ba44f7f; AID=wmlspartner%3D0%3Areflectorid%3D0000000000000000000000%3Alastupd%3D1645417046579; pxcts=d6b2964e-95f1-11ec-83ae-6b535058694a; ak_bmsc=6DD62F0EE05CE150283CFB2C27425391~000000000000000000000000000000~YAAQdmgDFxTgxSR/AQAAIS+MLw46/UkDiX1foDylrEnkhYgrIAYcWfKFIv7vr/RQLCm7kkjRD3dRRPbnn/ycDmNvm4CsR2GrP+fyBd4vTEysVtmrbvX6fZGTuCmCR93OiKBCS1Bov5zxt+oWkcYJCCqMKrW5+E9d9mApqtFhn0elBzQnvG5aSdobaMzGQGVqOF0NodKAZ4xtwLgbUHDSTyXISMuMc2oFZ7aNsItvZ1oj5w+Kmv+MLkhwMX800EDxy09vWQvqQ9s322E3CkIFqXfXZHpnnMAaL4J2DJUUxxbPpg4Md3S+BCN/AJxG2tSVgK9Xx52iwkpa/j1jh3eV1xvHfhL0tLZRk3FOTYQkVQXlQ0H+7qWbOVCL4xKvlhPCu46+VclYCBJLjih6; com.wm.reflector="reflectorid:0000000000000000000000@lastupd:1645771260805@firstcreate:1637718239841"; auth=MTAyOTYyMDE4jT+5pgonU4T5QUXfqA4075RlX1SiAQk15bn4HLCQAYVriZRzPFPznCqmtGrME49CeWcV8BLxM03YL+xkX1T9kJ3LxXKgRzQzmcdz8b6zVU5/7eAOyE+/hOLoZMsd8VB6767wuZloTfhm7Wk2KcjygpySosImygUk1x1iKsdnk4/NXAtDdh7R0WAOXjey8VbscSMx3USJXOMHVXxaqyKn4ZpeYmF0j68/+SIUIyVSCEUUMk70P8glgOEpLOprhDfMM/FHGZ2dCNmxWrdkwqEKrnLsALLL2ZOUDVip6W0mBcpLN6srctAIICCXicuU4M1harA8vdhncrEJMkqJnrxRvISopqVS3BcPuBeEgq0oUCihkTTRbxKOyEgXZyHIfK7/0beVBmrE5hcYJ3NwttA6xVjKcklje4R5ioW78kDnDBU=; assortmentStoreId=3717; TB_Latency_Tracker_100=1; TB_Navigation_Preload_01=1; TB_SFOU-100=1; bstc=bWFtVe1LA7V3kbm4z9954k; mobileweb=0; xpa=92i0d|DAwQd|Ph1zP|YgI0R|cahsq|iTIZ4|kdDWN|o6gca|vseyf; xpm=0+1645771260+TtLw6sZXLxEr96RFKbiq9M~+0; exp-ck=92i0d1DAwQd2YgI0R1cahsq1iTIZ41kdDWN1o6gca1vseyf1; xptwg=3897353389:1D9D0A2F0C45BA0:4D483B0:ABFB9B:DF3B6993:8C9EB94E:; TS01b0be75=01538efd7c9942c7db7cfd4aa7c6a3759c5b3884678ccf316d0d924ff5e545580cf2271db0c284bcfc5f03f08091a3f8eeae1c6db7; TS013ed49a=01538efd7c9942c7db7cfd4aa7c6a3759c5b3884678ccf316d0d924ff5e545580cf2271db0c284bcfc5f03f08091a3f8eeae1c6db7; akavpau_p2=1645771862~id=877e268f9b8c3798fbfda101aa1cdd43; bm_mi=0890AFDD0D8FD0B160C88AD74BF1F03E~HNhQcFjteZ1/7+4jPKB02WWBJBZfCq/fCk348UyCL/TSsXorlLxohGXm+3eSOqhJzXR1T496nRByCCwtaxTRf6GzW9DVsKmTapXkINTR3Sf7R1nyFRu6kFwRbOEcGYv3n+QHJlEETf5DnuBJZCPS9xyNFyxr8aEyGs3+8ahQOXDrAOMaJPfnMYtwuaVC6KfB8hKYgdZ/brwb6KRlFcN+kvz0VPVA45QeWe90kSoe5aM=; bm_sv=45E62E7E9410475AC1CE4160857DC0F3~ITCvYA0bPVSs/1vDbZgV+zy+3rWszVOPpZ3tgw9gumXia0fe60IBbcaQDfi/0pXnafeIohdSr2YLvycTrYA2Z1/ffGpPHK9wjD/0WXp3IV/ePGGq9JWaLuh2Rksq2b5S5e1FJtWn2S7MzuJ+yZtCRI6nr1A2p1iJojrf8EEvHBI='
        }
    Cookie = params['Cookie']
    function = AtomExecutor()
    function.init()
    for params in params['MainKeys']:
        try:
            function.process_item(params, Cookie)
        except Exception as e:
            print(e)
