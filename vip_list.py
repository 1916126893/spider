import asyncio
import random
import time
import re
import os
import json
import requests
import tenacity
from pyppeteer import launch
import logging
pyppeteer_level = logging.WARNING
logging.getLogger('pyppeteer').setLevel(pyppeteer_level)
logging.getLogger('websockets.protocol').setLevel(pyppeteer_level)
pyppeteer_logger = logging.getLogger('pyppeteer')
pyppeteer_logger.setLevel(logging.WARNING)
try:
    import nest_asyncio
except:
    os.system('pip install nest_asyncio')
    import nest_asyncio
nest_asyncio.apply()


class AtomExecutor():
    name = 'vip_list'
    base_url = 'https://list.vip.com/'

    def init(self):
        self.browser = ''
        self.page = ''
        self.key = ''
        self.sku_url_list = []
        self.randonum = str(random.randint(1700000000, 1799999999))

    async def PyppeteerMain(self):
        self.browser = await launch({
            'headless': True,
            'userDataDir': 'pyppeteer_data_for_cjt' + '_{}'.format(time.time()),
            'args': ['--no-sandbox',
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

    async def intercept_network_request(self, request):
        if '&api_key' and 'pageOffset' in request.url:
            self.key = request.url
        else:
            return ''

    async def get_vip_key(self, url):
        try:
            self.page.on('request', lambda request: asyncio.create_task(self.intercept_network_request(request)))
            await self.page.goto(url, options={'timeout': 1000 * 20})
        except Exception as e:
            raise Exception(e)

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_list_page(self, url, num):
        try:
            headers = {
                'referer': 'https://list.vip.com/',
                'user-agent': self.get_ua(),
            }
            res = requests.get(url, headers=headers, timeout=20)
            data = res.text.replace('getProductIdsListRank(', '').replace(')', '').replace('getMerchandiseIds(', '')
            data_json = json.loads(data)
            sku_list = data_json.get('data').get('products')
            if sku_list != None:
                if len(sku_list) == 0:
                    if num < data_json.get('data')['total']:
                        return(True)
                    else:
                        return(False)
                for i in range(0,len(sku_list)):
                    sku_url = 'https://detail.vip.com/detail-{}-{}.html'.format(self.randonum, sku_list[i]['pid'], '.html')
                    if sku_url not in self.sku_url_list:
                        self.sku_url_list.append(sku_url)
                        d = {
                            'URL': sku_url + '|' + str(int(num/120)) + '|' + str(i+1)
                        }
                        print(d)

            else:
                return(False)
        except Exception as e:
            raise Exception(e)
        return(True)

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def vip_key(self, url):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.get_vip_key(url))
        except Exception as e:
            asyncio.get_event_loop().run_until_complete(self.browser.close())
            asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
            raise Exception(e)

    def process_item(self, keyword,pagesize):
        p = int(pagesize)
        self.init()
        asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
        try:
            self.vip_key(keyword)
        except Exception as e:
            print(e)
        if self.key != '':
            timestamp_list = re.findall('[0-9][0-9]{12,13}', self.key)
            if timestamp_list:
                timestamp_two = '&_={}'.format(str(timestamp_list[-1]))
            for i in range(0, p):
                try:
                    url = self.key.replace('pageOffset=0', 'pageOffset={}'.format(str(i*120))).replace(timestamp_two, '&_={}'.format(str(int(time.time()*1000))))
                    if self.get_list_page(url, i*120) == False:
                        break
                except Exception as e:
                    print(e)
        asyncio.get_event_loop().run_until_complete(self.browser.close())

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
            'https://list.vip.com/autolist.html?rule_id=52882091&title=%E4%BC%91%E9%97%B2%E8%85%95%E8%A1%A8&refer_url=https%3A%2F%2Fcategory.vip.com%2Fhome',
        ],
        "Pagesize": 200,
    }
    pagesize = params['Pagesize']
    function = AtomExecutor()
    for params in params['MainKeys']:
        try:
            function.process_item(params,pagesize)
        except Exception as e:
            print(e)

