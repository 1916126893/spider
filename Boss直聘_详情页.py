

from lxml import etree
import logging
import re
import os
import time
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
    name = 'Boss直聘_详情页'
    base_url = 'https://www.zhipin.com/'

    def init(self):
        self.browser = ''
        self.page = ''
        self.state = False

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

    async def get_detail_page(self, url):
        try:
            await self.page.goto(url, options={'timeout': 1000 * 50})
        except Exception as e:
            print(e)
            raise Exception('retry')
        await asyncio.sleep(15)
        html = await self.page.content()
        page = etree.HTML(html)
        if '您访问的页面不存在' in html:
            print('您访问的页面不存在,当前页面url：{}'.format(self.page.url))
            return True
        try:
            job_name = ''.join(page.xpath('//*[@id="main"]/div[1]/div/div/div[*]/div[*]//@title')) or 'null'
        except:
            job_name = 'null'
        if job_name == '' or job_name == 'null':
            print('无法访问，当前页面url：{}'.format(self.page.url))
            raise Exception('retry')
        try:
            job_pay = ''.join(page.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div[2]/span/text()')) or 'null'
        except:
            job_pay = 'null'
        try:
            job_year = page.xpath('//*[@id="main"]/div[1]/div/div/div[*]/p/text()')[0] or 'null'
        except:
            job_year = 'null'
        try:
            job_education = page.xpath('//*[@id="main"]/div[1]/div/div/div[*]/p/text()')[-1] or 'null'
        except:
            job_education = 'null'
        try:
            job_welfare = ''.join(page.xpath('//*[@id="main"]/div[1]/div/div/div[3]/div[2]//text()')) or 'null'
        except:
            job_welfare = 'null'
        try:
            job_company = ''.join(page.xpath('//*[@id="main"]/div[3]/div/div[2]/div[2]/div[5]/div[1]/text()')) or ''.join(page.xpath('//*[@id="main"]/div[3]/div/div[2]/div[2]/div[6]/div[1]/text()')) or 'null'
        except:
            job_company = 'null'
        try:
            job_address = ''.join(page.xpath('//*[@id="main"]/div[3]/div/div[2]/div[2]/div[*]/div/div[1]/text()')) or 'null'
            if '综合竞争力评估' in job_address:
                job_address = job_address.replace('综合竞争力评估', '')
            else:
                job_address = 'null'
        except:
            job_address = 'null'
        try:
            if '薪资详情' in ''.join(page.xpath('//*[@id="main"]/div[3]/div/div[2]/div[2]/div[1]//text()')):
                job_need = '\n'.join(page.xpath('//*[@id="main"]/div[3]/div/div[2]/div[2]/div[2]/div/text()')) or 'null'
            else:
                job_need = '\n'.join(page.xpath('//*[@id="main"]/div[3]/div/div[2]/div[2]/div[1]/div/text()')) or 'null'
        except:
            job_need = 'null'
        try:
            job_nop = re.findall('职位招聘(.*?)人', ''.join(page.xpath('//*[@id="main"]/div[3]/div/div[2]/div[2]/div[*]/div/text()')))[0] or 'null'
        except:
            job_nop = 'null'
        try:
            job_industry = ''.join(page.xpath('//*[@id="main"]/div[3]/div/div[1]/div[2]/p[3]/a/text()')) or 'null'
        except:
            job_industry = 'null'
        try:
            job_logo = ''.join(page.xpath('//*[@id="main"]/div[3]/div/div[1]/div[2]/div/a[1]/img/@src')) or 'null'
        except:
            job_logo = ''
        try:
            job_nature = ''.join(page.xpath('//*[@id="main"]/div[3]/div/div[2]/div[2]/div[*]/div[2]/li[4]/text()')) or 'null'
        except:
            job_nature = 'null'
        try:
            job_industry = ''.join(page.xpath('//*[@id="main"]/div[3]/div/div[*]/div[*]/p[*]/a/text()')) or 'null'
        except:
            job_industry = 'null'
        try:
            for i in page.xpath('//*[@id="main"]/div[3]/div/div[*]/div[*]/p[*]/text()'):
                if '人' in i:
                    job_people = i
                    break
        except:
            job_people = 'null'
        try:
            job_base = page.xpath('//*[@id="main"]/div[1]/div/div/div[*]/p/a/text()')[0] or 'null'
        except:
            job_base = 'null'
        job_url = url
        try:
            if '公司介绍' in ''.join(page.xpath('//*[@id="main"]/div[*]/div/div[*]/div[*]/div[2]//text()')):
                job_type = ''.join(page.xpath('//*[@id="main"]/div[*]/div/div[*]/div[*]/div[2]/div/text()')) or 'null'
            else:
                job_type = ''.join(page.xpath('//*[@id="main"]/div[*]/div/div[*]/div[*]/div[3]/div/text()')) or 'null'
        except:
            job_type = 'null'
        data = {
            '职位名称': job_name,
            '基本工资': job_pay,
            '工作经验': job_year,
            '学历要求': job_education,
            '招聘人数': job_nop,
            '职位福利': job_welfare,
            '公司名称': job_company,
            '工作地址': job_address,
            '职位描述': job_need,
            '行业职位': job_name,
            '公司logo': job_logo,
            '公司性质': job_nature,
            '公司行业': job_industry,
            '公司规模': job_people,
            '地区': job_base,
            '页面网址': job_url,
            '当前时间': self.gettime(),
            '公司介绍': job_type,
        }
        print(data)
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
            proxy['url'] = 'http://' + resp['data'][0]['host'] + ':' + str(resp['data'][0]['port'])
            proxy['proxyip'] = resp['data'][0]['host'] + ':' + str(resp['data'][0]['port'])
            return proxy
        except Exception as e:
            print(e)

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def gettime(self):
        ti = time.localtime()
        ti = '%d-%d-%d %d:%d:%d' % (ti[0], ti[1], ti[2], ti[3], ti[4], ti[5])
        return ti

    @tenacity.retry(stop=tenacity.stop_after_attempt(50))
    def get_detail_taowa(self, url):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.get_detail_page(url))
        except Exception as e:
            if self.page.url != 'https://www.zhipin.com/':
                asyncio.get_event_loop().run_until_complete(self.browser.close())
                asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
                raise Exception(e)
            else:
                print('当前页面url：{}'.format(self.page.url))


    def process_item(self, keyword):
        asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
        try:
            self.get_detail_taowa(keyword)
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
            'https://www.zhipin.com/job_detail/dea8307f7e09986e0HR-2dS9Els~.html',
            'https://www.zhipin.com/job_detail/e3674e3603179cbe1nxz09q8FVdX.html?ka=job_recommend_1',
            'https://www.zhipin.com/job_detail/88df084c84d90dbe3nV509y9EVs~.html',
            'https://www.zhipin.com/job_detail/a1fa84ec2ca499d81nF83t-0FlNU.html?ka=job_recommend_4',
            'https://www.zhipin.com/job_detail/15ce37f2bf38047233Z439m0FVE~.html',
            'https://www.zhipin.com/job_detail/aba3f3ad0507d69e1nN539i9GVFT.html',
        ],
    }
    function = AtomExecutor()
    function.init()
    for params in params['MainKeys']:
        try:
            function.process_item(params)
        except Exception as e:
            print(e)


