import asyncio
import random
import time
import re
import os
import json
from urllib import parse
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
    name = 'Twitter'
    base_url = 'https://twitter.com/'

    def init(self):
        self.browser = ''
        self.api_prex = ''
        self.twitter_key = ''
        self.headers = ''
        self.starttime = ''
        self.endtime = ''

    async def PyppeteerMain(self):
        self.browser = await launch({
            'headless': False,
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
        await self.page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36')
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
        if 'api.twitter.com/2/search/adaptive' in request.url:
            self.api_prex = "https://api.twitter.com/2/search/adaptive.json?"
            self.headers = request.headers
        if 'twitter.com/i/api/2/search/adaptive' in request.url:
            self.api_prex = "https://twitter.com/i/api/2/search/adaptive.json?"
            self.headers = request.headers
        else:
            return ''

    async def get_twitter_headers(self, url):
        try:
            self.page.on('request', lambda request: asyncio.create_task(self.intercept_network_request(request)))
            await self.page.goto(url)
        except Exception as e:
            print(e)

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def twitter_headers(self, url):
        loop = asyncio.get_event_loop()
        asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
        try:
            loop.run_until_complete(self.get_twitter_headers(url))
        except Exception as e:
            asyncio.get_event_loop().run_until_complete(self.browser.close())
            raise Exception(e)

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def twitter_list(self, keyword):
        keyword = parse.quote(keyword,encoding='utf-8')
        if self.twitter_key == '':
            url = f'{self.api_prex}include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_composer_source=true&include_ext_alt_text=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&send_error_codes=true&simple_quoted_tweets=true&q={keyword}%20until%3A{self.endtime}%20since%3A{self.starttime}&tweet_search_mode=live&count=20&query_source=typed_query&pc=1&spelling_corrections=1&ext=mediaStats%2ChighlightedLabel%2CcameraMoment'
        else:
            self.twitter_key = self.twitter_key.replace('+', '%2B').replace('=', '%3D')
            url = f'{self.api_prex}include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_composer_source=true&include_ext_alt_text=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&send_error_codes=true&simple_quoted_tweets=true&q={keyword}%20until%3A{self.endtime}%20since%3A{self.starttime}&tweet_search_mode=live&count=20&query_source=typed_query&cursor={self.twitter_key}&pc=1&spelling_corrections=1&ext=mediaStats%2ChighlightedLabel%2CcameraMoment'
        res = requests.get(url, headers=self.headers,timeout=20)
        data_json = json.loads(res.text)
        try:
            self.twitter_key = data_json.get('timeline').get('instructions')[0].get('addEntries').get('entries')[-1].get('content').get('operation').get('cursor').get('value')
        except Exception as e:
            try:
                self.twitter_key =  data_json.get('timeline').get('instructions')[-1].get('replaceEntry').get('entry').get('content').get('operation').get('cursor').get('value')
            except Exception as e:
                print(e)
                return False
        if self.twitter_key == '' or self.twitter_key == None:
            return False
        twitter_json = data_json.get('globalObjects').get('tweets')
        for twitter in twitter_json:
            twitter_data = twitter_json.get(twitter)
            if twitter_data:
                try:
                    postid = twitter_data.get('id_str')
                except:
                    postid = ''
                try:
                    time = twitter_data.get('created_at')
                except:
                    time= ''
                try:
                    userid = twitter_data.get('user_id_str')
                except:
                    userid = ''
                try:
                    userhandle = twitter_data.get('entities').get('user_mentions')[0].get('screen_name')
                except:
                    userhandle = ''
                try:
                    tweeturl = 'https://twitter.com/{}/status/{}'.format(userhandle,postid)
                except:
                    tweeturl = ''
                try:
                    content = twitter_data.get('full_text')
                except:
                    content= ''
                try:
                    username = twitter_data.get('entities').get('user_mentions')[0].get('name')
                except:
                    username = ''
                try:
                    retweetnum = twitter_data.get('retweet_count')
                except:
                    retweetnum = ''
                try:
                    likenum = twitter_data.get('favorite_count')
                except:
                    likenum = ''
                try:
                    commentsnum = twitter_data.get('reply_count')
                except:
                    commentsnum = ''
                try:
                    userurl = 'https://twitter.com/{}'.format(userhandle)
                except:
                    userurl = ''
                try:
                    location =  twitter_data.get('entities').get('user_mentions')[0].get('location')
                except:
                    location = ''
                data = {
                    'Content': content,
                    'SearchCategory': keyword,
                    'Time': time,
                    'TweetUrl': tweeturl,
                    'UserHandle': userhandle,
                    'UserName': username,
                    'RetweetNum': retweetnum,
                    'LikeNum': likenum,
                    'CommentsNum': commentsnum,
                    'UserID': userid,
                    'UserUrl': userurl,
                    'Location': location,
                }
                print(data)


    def process_item(self, keyword,starttime,endtime):
        self.init()
        self.starttime = starttime
        self.endtime = endtime
        try:
            url = 'https://twitter.com/search?q={}%20until%3A{}%20since%3A{}&src=typed_query&f=live'.format(keyword, self.endtime, self.starttime)
            self.twitter_headers(url)
        except Exception as e:
            print(e)
        if self.api_prex:
            while True:
                try:
                    if self.twitter_list(keyword) == False:
                        break
                except Exception as e:
                    print(e)
        else:
            print('No headers')

    @staticmethod
    def getProxy():
        proxies = {
            'http': '127.0.0.1:10808',
            'https': '127.0.0.1:10808'
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
            'NIL athlete',
        ],
        "starttime": '2021-12-1',
        "endtime": '2021-12-31',

    }
    starttime = params['starttime']
    endtime = params['endtime']
    function = AtomExecutor()
    for params in params['MainKeys']:
        try:
            function.process_item(params,starttime,endtime)
        except Exception as e:
            print(e)

