import time
import re
import os
import json
import random
import requests
from lxml import etree
import tenacity
from selenium import webdriver
try:
    import execjs
except:
    os.system('pip install PyExecJS')
    import execjs


class AtomExecutor():
    name = 'vip_deatil'
    base_url = 'https://list.vip.com/'

    def init(self):
        self.datas = 0
        self.driver = ''
        self.run_date = ''
        self.tx_js = r'''
                    function vq(sourceText) {
                        let data = encodeURI(sourceText).replace(/&/g, '%26');
                        return(data)
                    }
        '''
        self.tk_js = r'''
                    function vq(a, uq = `445904.3958516492`) {
                        if (null !== uq)
                            var b = uq;
                        else {
                            b = sq('T');
                            var c = sq('K');
                            b = [b(), c()];
                            b = (uq = window[b.join(c())] || "") || ""
                        }
                        var d = sq('t');
                        c = sq('k');
                        d = [d(), c()];
                        c = "&" + d.join("") + "=";
                        d = b.split(".");
                        b = Number(d[0]) || 0;
                        for (var e = [], f = 0, g = 0; g < a.length; g++) {
                            var l = a.charCodeAt(g);
                            128 > l ? e[f++] = l : (2048 > l ? e[f++] = l >> 6 | 192 : (55296 == (l & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (l = 65536 + ((l & 1023) << 10) + (a.charCodeAt(++g) & 1023),
                                e[f++] = l >> 18 | 240,
                                e[f++] = l >> 12 & 63 | 128) : e[f++] = l >> 12 | 224,
                                e[f++] = l >> 6 & 63 | 128),
                                e[f++] = l & 63 | 128)
                        }
                        a = b;
                        for (f = 0; f < e.length; f++)
                            a += e[f],
                                a = tq(a, "+-a^+6");
                        a = tq(a, "+-3^+b+-f");
                        a ^= Number(d[1]) || 0;
                        0 > a && (a = (a & 2147483647) + 2147483648);
                        a %= 1000000;
                        return c + (a.toString() + "." + (a ^ b))
                    }

                    function sq(a) {
                        return function () {
                            return a
                        }
                    }

                    function tq(a, b) {
                        for (var c = 0; c < b.length - 2; c += 3) {
                            var d = b.charAt(c + 2);
                            d = "a" <= d ? d.charCodeAt(0) - 87 : Number(d);
                            d = "+" == b.charAt(c + 1) ? a >>> d : a << d;
                            a = "+" == b.charAt(c) ? a + d & 4294967295 : a ^ d
                        }
                        return a
                    }
                    '''
        self.tk_js = execjs.compile(self.tk_js)
        self.tx_js = execjs.compile(self.tx_js)

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
        chromeOptions.add_argument("--disable-gpu")
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
        driver.set_page_load_timeout(70)
        return driver

    @tenacity.retry(stop=tenacity.stop_after_attempt(3))
    def get_detail(self, url,pagesize,index):
        try:
            self.driver.get(url)
        except Exception as e:
            raise Exception(e)
        time.sleep(10)
        self.driver.implicitly_wait(20)
        html = self.driver.page_source
        page = etree.HTML(html)
        data = {}
        try:
            title = page.xpath("//div[@class='pib-title']/p[contains(@class,'pib-title-detail')]/text()")[0] or 'null'
        except:
            title = 'null'
        try:
            price = page.xpath('//*[@id="J-specialPrice-wrap"]/div[*]/div[*]/div[*]/span[1]/text()')[0] or 'null'
        except:
            price = 'null'
        try:
            warranty_type = ''.join(re.findall('【(.+?)】', title)) or 'null'
        except:
            warranty_type = 'null'
        try:
            brand = ''.join(page.xpath("//div[@class='pib-title']/a/text()")) or ''.join(page.xpath('//*[@id="J_detail_info_mation"]/div[1]/a/text()')) or 'null'
        except:
            brand = 'null'
        try:
            model_number = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'商品编码')]/following-sibling::td[1]/text()")) or 'null'
        except:
            model_number = 'null'
        try:
            selling_price = ''.join(page.xpath('//*[@id="J-specialPrice-wrap"]/div[*]/div[*]/div[2]/span[*]//text()')) or 'null'
        except:
            selling_price = 'null'
        try:
            image_url = 'https:' + ''.join(page.xpath('//*[@id="J-img-content"]/div[1]/img/@src')) or 'null'
        except:
            image_url = 'null'
        try:
            original_price = ''.join(page.xpath("//div[@class='sp-info']//span[@class='sp-price']/text()")) or 'null'
        except:
            original_price = 'null'
        try:
            seller_selling_price = ''.join(page.xpath('//*[@id="J-specialPrice-wrap"]/div[*]/div[*]/div[*]/span[*]/span[*]/span[*]/span[*]//text()')) or 'null'
        except:
            seller_selling_price = 'null'
        try:
            shipping_fee = ''.join(page.xpath("//dl[@id='J_freight_frame']//span[@id='J_freight_tips']/text()")) or 'null'
        except:
            shipping_fee = 'null'
        try:
            count_review = ''.join(page.xpath("//div[@class='c-product-comment-satisfy-info']/span/text()")) or 'null'
        except:
            count_review = 'null'
        try:
            average_customer_review = ''.join(page.xpath("//ul[@class='dt-list']/a/span//text()")) or 'null'
        except:
            average_customer_review = 'null'
        try:
            gender = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'适用性别')]/following-sibling::td[1]/text()")) or 'null'
        except:
            gender = 'null'
        try:
            band_colour = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'表带颜色')]/following-sibling::td[1]/text()")) or 'null'
        except:
            band_colour = 'null'
        try:
            band_material = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'表带材质')]/following-sibling::td[1]/text()")) or 'null'
        except:
            band_material = 'null'
        try:
            case_diameter = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'表盘直径')]/following-sibling::td[1]/text()")) or 'null'
        except:
            case_diameter = 'null'
        try:
            case_material = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'表壳材质')]/following-sibling::td[1]/text()")) or 'null'
        except:
            case_material = 'null'
        try:
            clasp = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'表扣方式')]/following-sibling::td[1]/text()")) or 'null'
        except:
            clasp = 'null'
        try:
            item_shape = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'表盘形状')]/following-sibling::td[1]/text()")) or 'null'
        except:
            item_shape = 'null'
        try:
            water_resistance_depth = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'防水深度')]/following-sibling::td[1]/text()")) or 'null'
        except:
            water_resistance_depth = 'null'
        try:
            style = ''.join(page.xpath("//div[@class='dc-table-content']//tbody/tr/th[contains(text(),'风格')]/following-sibling::td[1]/text()")) or 'null'
        except:
            style = 'null'
        try:
            ranslate_data = self.re_null(brand + '\n' + model_number + '\n' + title + '\n' + shipping_fee + '\n' + gender + '\n' + band_colour + '\n' + band_material + '\n' + case_diameter + '\n' + case_material + '\n' + clasp + '\n' + item_shape + '\n' + warranty_type + '\n' + water_resistance_depth + '\n' + style)
            translate_data_list = self.translate(ranslate_data).split('\n')
        except Exception as e:
            translate_data_list = []
        data['RUN_DATE'] = self.run_date
        data['RECORD_DATE'] = self.gettime()
        data['MARKETPLACE'] = "VIP"
        data['CATERGORY'] = "Watches"
        data['PRICE'] = price
        data['KEYWORD'] = 'null'
        data['PRODUCT_URL'] = self.driver.current_url
        data['PAGE'] = pagesize
        data['POSITION'] = index
        if len(translate_data_list) == 14:
            data['BRAND'] = translate_data_list[0]
            data['MODEL_NUMBER'] = translate_data_list[1]
            data['TITLE'] = translate_data_list[2]
            data['ADVERTISED'] = 'null'
            data['IMAGE_URL'] = image_url
            data['SELLING_PRICE'] = selling_price
            data['ORIGINAL_PRICE'] = original_price
            data['COUNT_SELLER'] = 'null'
            data['SELLER_NAME'] = 'null'
            data['SELLER_SELLING_PRICE'] = seller_selling_price
            data['SHIPPING_FEE'] = translate_data_list[3]
            data['COUNT_RATING'] = 'null'
            data['COUNT_REVIEW'] = count_review
            data['AVERAGE_CUSTOMER_REVIEW'] = average_customer_review
            data['GENDER'] = translate_data_list[4]
            data['BAND_COLOUR'] = translate_data_list[5]
            data['BAND_MATERIAL'] = translate_data_list[6]
            data['CASE_DIAMETER'] = translate_data_list[7]
            data['CASE_MATERIAL'] = translate_data_list[8]
            data['CLASP'] = translate_data_list[9]
            data['ITEM_SHAPE'] = translate_data_list[10]
            data['WARRANTY_TYPE'] = translate_data_list[11]
            data['WATER_RESISTANCE_DEPTH'] = translate_data_list[12]
            data['Style'] = translate_data_list[13]
        else:
            data['BRAND'] = brand
            data['MODEL_NUMBER'] = model_number
            data['TITLE'] = title
            data['ADVERTISED'] = 'null'
            data['IMAGE_URL'] = image_url
            data['SELLING_PRICE'] = selling_price
            data['ORIGINAL_PRICE'] = original_price
            data['COUNT_SELLER'] = 'null'
            data['SELLER_NAME'] = 'null'
            data['SELLER_SELLING_PRICE'] = seller_selling_price
            data['SHIPPING_FEE'] = shipping_fee
            data['COUNT_RATING'] = 'null'
            data['COUNT_REVIEW'] = count_review
            data['AVERAGE_CUSTOMER_REVIEW'] = average_customer_review
            data['GENDER'] = gender
            data['BAND_COLOUR'] = band_colour
            data['BAND_MATERIAL'] = band_material
            data['CASE_DIAMETER'] = case_diameter
            data['CASE_MATERIAL'] = case_material
            data['CLASP'] = clasp
            data['ITEM_SHAPE'] = item_shape
            data['WARRANTY_TYPE'] = warranty_type
            data['WATER_RESISTANCE_DEPTH'] = water_resistance_depth
            data['Style'] = style
        self.datas += 1
        print(data)
        return()

    def translate(self, sourceText):
        tk = self.tk_js.call("vq", sourceText)
        encodeKeyword = self.tx_js.call("vq", sourceText)
        header = {
            "Content-Type": "application/json",
            "User-Agent": self.get_ua(),
        }
        url = 'https://translate.google.cn/translate_a/t?client=webapp&sl=zh-CN&tl=en&hl=zh-CN&v=1.0&source=is{}&q={}'.format(tk, encodeKeyword)
        res = requests.get(url, headers=header, timeout=20)
        try:
            data = json.loads(res.text)[0]
        except:
            raise Exception('retry')
        return(data)

    def re_null(self, sourceText):
        text = sourceText.split('\n')
        data = ''
        for d in text:
            if d == '':
                data += 'null' + '\n'
            else:
                data += d + '\n'
        return(data)
    def gettime(self):
        ti = time.localtime()
        ti = '%d/%d/%d %d:%d:%d' % (ti[2], ti[1], ti[0], ti[3], ti[4], ti[5])
        return ti
        

    def process_item(self, keyword):
        data = keyword.split('|')
        self.init()
        if len(data) == 3:
            self.driver = self.get_driver()
            try:
                self.run_date = self.gettime()
                self.get_detail(data[0],data[1],data[2])
            except Exception as e:
                self.driver.quit()
                self.driver = self.get_driver()
                print(e)
            self.driver.quit()

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def getProxy():
        username = ""
        password = ""
        proxy = ''
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
            'https://detail.vip.com/detail-1705116801-6919564823037352842.html|0|1'
        ],
    }
    function = AtomExecutor()
    for params in params['MainKeys']:
        try:
            function.process_item(params)
        except Exception as e:
            print(e)

