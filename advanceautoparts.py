import json
from urllib import parse
import random
import re
from sys import platform
import requests
import tenacity

class AtomExecutor():
    name = 'advanceautoparts'
    base_url = 'https://shop.advanceautoparts.com/'

    def init(self):
        self.data_list = []
        self.page_url = ''

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_list_page(self, url):
        proxy = self.getProxy()
        header = {
            'Host': 'apigw.advanceautoparts.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://shop.advanceautoparts.com/',
            'x-auth-method': 'cookie-token',
        }
        res = requests.get(url, headers=header,timeout=20)
        json_data = json.loads(res.text)
        data_list = json_data.get('products')
        if len(data_list) == 0:
            return (False)
        for d in data_list:
            try:
                if d not in self.data_list:
                    #########################
                    Specification = ''
                    try:
                        Specification_list = d['specifications']
                        if len(Specification_list) != 0:

                            for a in Specification_list:
                                name = a['name']
                                value = a['value']
                                Specification += name + ':' + value + ',\n'
                        else:
                            Specification = 'null'
                    except:
                        Specification = 'null'
                    #######################
                    self.data_list.append(d)
                    ###########################
                    try:
                        Product_URL = 'https://shop.advanceautoparts.com/p/diehard-platinum-agm-battery-group-size-h6-760-cca-h6-agm/{}'.format(
                            d['id'])
                    except:
                        Product_URL = 'null'
                    try:
                        Product_titled = d['manufacturerName'] + d['category']
                    except:
                        Product_titled = 'null'
                    try:
                        Star_rating = d['averageRating']
                    except:
                        Star_rating = 'null'
                    try:
                        Warranty = d['warrantyDetails']
                    except:
                        Warranty = 'null'
                    try:
                        Price = d['salePrice']
                    except:
                        Price = 'null'
                    try:
                        Core_charge = d['coreCharge']
                    except:
                        Core_charge = 'null'
                    try:
                        Total_price = round(Price + Core_charge, 2)
                    except:
                        Total_price = 'null'
                    try:
                        Parts_number = d['partNumber']
                    except:
                        Parts_number = 'null'
                    try:
                        sku = d['id']
                    except:
                        sku = 'null'
                    try:
                        Descriptions = d['description']
                    except:
                        Descriptions = 'null'
                    try:
                        img_url = d['images'][0]['largeImageUrl']
                    except:
                        img_url = 'null'
                    ################
                    data = {
                        'Product URL': Product_URL,
                        'Product title': ''.join(Product_titled.split(',')[0]),
                        'Star rating': Star_rating,
                        'Warranty': Warranty,
                        'Price': Price,
                        'Core charge': Core_charge,
                        'Total price': Total_price,
                        'Parts number': Parts_number,
                        'SKU': sku,
                        'Page_url': self.page_url,
                        'Descriptions': re.sub('<(.*?)>', '', Descriptions),
                        'Specification': Specification,
                        'Picture_url': img_url
                    }
                    print(data)
                    data = {}
                else:
                    return (False)
            except Exception as e:
                print(e)
        return (True)



    def process_item(self, keyword,pagesize):
        p = int(pagesize)
        self.page_url = 'https://shop.advanceautoparts.com/web/SearchResults?searchTerm={}'.format(keyword)
        for i in range(1, p):
            try:

                url = 'https://apigw.advanceautoparts.com/v13/search?autoCorrectResults%5BfitmentFilter%5D=true&autoCorrectResults%5BvehicleSwitching%5D=true&autoCorrectResults%5BspellingSuggestion%5D=true&autoCorrectResults%5BpreferSpellingSuggestionResults%5D=true&count=10&order=BEST_MATCH&term={}&offset={}&allowMultiSelect=true'.format(
                    parse.quote(keyword, encoding='utf-8'), str(i * 10))
                if self.get_list_page(url) == False:
                    break
            except Exception as e:
                print(e)


    @staticmethod
    def getProxy():
        username = ""
        password = ""
        proxy = ""
        proxies = {
            'http': proxy,
            'https': proxy
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
            'car batteries',
        ],
        "Pagesize": 200,
    }

    pagesize = params['Pagesize']
    function = AtomExecutor()
    function.init()
    for params in params['MainKeys']:
        try:
            function.process_item(params,pagesize)
        except Exception as e:
            print(e)