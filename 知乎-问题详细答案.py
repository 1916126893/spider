import json
import time
import random
import os
import re
try:
    import hashlib
except:
    os.system('pip install hashlib')
    import hashlib
try:
    import execjs
except:
    os.system('pip install PyExecJS')
    import execjs
os.system('npm install jsdom')
from selenium import webdriver
import requests
from lxml import etree
import tenacity
###by:ZMH
####2022年2月11日15:37:52

class AtomExecutor():
    name = '知乎-问题详细答案-限云采集'
    base_url = 'https://www.zhihu.com/'

    def init(self):
        self.driver = ''
        self.cookie = ''
        self.header = ''
        self.answer_id = []
        self.total_num = 0
        self.questionInfo = {
            '问题ID': '',
            '问题标题': '',
            '问题链接': '',
            '提问时间': '',
            '问题最新编辑时间': '',
            '回答ID': '',
            '链接': '',
            '作者': '',
            '回答内容': '',
            '评论数量': '',
            '赞同数量': '',
            '回答时间': '',
            '编辑时间': '',
            '问题内容': '',
            '问题标签': '',
            '问题回答数': '',
            '问题浏览数': '',
            '问题评论数': '',
            '问题关注数': ''
        }
        self.js_str = """
            const jsdom = require("jsdom");
            const {JSDOM} = jsdom;
            const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`);
            window = dom.window;
            document = window.document;
            XMLHttpRequest = window.XMLHttpRequest;

            function t(e) {
                return (t = "function" == typeof Symbol && "symbol" == typeof Symbol.A ? function (e) {
                            return typeof e
                        }
                        : function (e) {
                            return e && "function" == typeof Symbol && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e
                        }
                )(e)
            }

            Object.defineProperty(exports, "__esModule", {
                value: !0
            });
            var A = "2.0"
                , __g = {};

            function s() {
            }

            function i(e) {
                this.t = (2048 & e) >> 11,
                    this.s = (1536 & e) >> 9,
                    this.i = 511 & e,
                    this.h = 511 & e
            }

            function h(e) {
                this.s = (3072 & e) >> 10,
                    this.h = 1023 & e
            }

            function a(e) {
                this.a = (3072 & e) >> 10,
                    this.c = (768 & e) >> 8,
                    this.n = (192 & e) >> 6,
                    this.t = 63 & e
            }

            function c(e) {
                this.s = e >> 10 & 3,
                    this.i = 1023 & e
            }

            function n() {
            }

            function e(e) {
                this.a = (3072 & e) >> 10,
                    this.c = (768 & e) >> 8,
                    this.n = (192 & e) >> 6,
                    this.t = 63 & e
            }

            function o(e) {
                this.h = (4095 & e) >> 2,
                    this.t = 3 & e
            }

            function r(e) {
                this.s = e >> 10 & 3,
                    this.i = e >> 2 & 255,
                    this.t = 3 & e
            }

            s.prototype.e = function (e) {
                e.o = !1
            }
                ,
                i.prototype.e = function (e) {
                    switch (this.t) {
                        case 0:
                            e.r[this.s] = this.i;
                            break;
                        case 1:
                            e.r[this.s] = e.k[this.h]
                    }
                }
                ,
                h.prototype.e = function (e) {
                    e.k[this.h] = e.r[this.s]
                }
                ,
                a.prototype.e = function (e) {
                    switch (this.t) {
                        case 0:
                            e.r[this.a] = e.r[this.c] + e.r[this.n];
                            break;
                        case 1:
                            e.r[this.a] = e.r[this.c] - e.r[this.n];
                            break;
                        case 2:
                            e.r[this.a] = e.r[this.c] * e.r[this.n];
                            break;
                        case 3:
                            e.r[this.a] = e.r[this.c] / e.r[this.n];
                            break;
                        case 4:
                            e.r[this.a] = e.r[this.c] % e.r[this.n];
                            break;
                        case 5:
                            e.r[this.a] = e.r[this.c] == e.r[this.n];
                            break;
                        case 6:
                            e.r[this.a] = e.r[this.c] >= e.r[this.n];
                            break;
                        case 7:
                            e.r[this.a] = e.r[this.c] || e.r[this.n];
                            break;
                        case 8:
                            e.r[this.a] = e.r[this.c] && e.r[this.n];
                            break;
                        case 9:
                            e.r[this.a] = e.r[this.c] !== e.r[this.n];
                            break;
                        case 10:
                            e.r[this.a] = t(e.r[this.c]);
                            break;
                        case 11:
                            e.r[this.a] = e.r[this.c] in e.r[this.n];
                            break;
                        case 12:
                            e.r[this.a] = e.r[this.c] > e.r[this.n];
                            break;
                        case 13:
                            e.r[this.a] = -e.r[this.c];
                            break;
                        case 14:
                            e.r[this.a] = e.r[this.c] < e.r[this.n];
                            break;
                        case 15:
                            e.r[this.a] = e.r[this.c] & e.r[this.n];
                            break;
                        case 16:
                            e.r[this.a] = e.r[this.c] ^ e.r[this.n];
                            break;
                        case 17:
                            e.r[this.a] = e.r[this.c] << e.r[this.n];
                            break;
                        case 18:
                            e.r[this.a] = e.r[this.c] >>> e.r[this.n];
                            break;
                        case 19:
                            e.r[this.a] = e.r[this.c] | e.r[this.n];
                            break;
                        case 20:
                            e.r[this.a] = !e.r[this.c]
                    }
                }
                ,
                c.prototype.e = function (e) {
                    e.Q.push(e.C),
                        e.B.push(e.k),
                        e.C = e.r[this.s],
                        e.k = [];
                    for (var t = 0; t < this.i; t++)
                        e.k.unshift(e.f.pop());
                    e.g.push(e.f),
                        e.f = []
                }
                ,
                n.prototype.e = function (e) {
                    e.C = e.Q.pop(),
                        e.k = e.B.pop(),
                        e.f = e.g.pop()
                }
                ,
                e.prototype.e = function (e) {
                    switch (this.t) {
                        case 0:
                            e.u = e.r[this.a] >= e.r[this.c];
                            break;
                        case 1:
                            e.u = e.r[this.a] <= e.r[this.c];
                            break;
                        case 2:
                            e.u = e.r[this.a] > e.r[this.c];
                            break;
                        case 3:
                            e.u = e.r[this.a] < e.r[this.c];
                            break;
                        case 4:
                            e.u = e.r[this.a] == e.r[this.c];
                            break;
                        case 5:
                            e.u = e.r[this.a] != e.r[this.c];
                            break;
                        case 6:
                            e.u = e.r[this.a];
                            break;
                        case 7:
                            e.u = !e.r[this.a]
                    }
                }
                ,
                o.prototype.e = function (e) {
                    switch (this.t) {
                        case 0:
                            e.C = this.h;
                            break;
                        case 1:
                            e.u && (e.C = this.h);
                            break;
                        case 2:
                            e.u || (e.C = this.h);
                            break;
                        case 3:
                            e.C = this.h,
                                e.w = null
                    }
                    e.u = !1
                }
                ,
                r.prototype.e = function (e) {
                    switch (this.t) {
                        case 0:
                            for (var t = [], n = 0; n < this.i; n++)
                                t.unshift(e.f.pop());
                            e.r[3] = e.r[this.s](t[0], t[1]);
                            break;
                        case 1:
                            for (var r = e.f.pop(), i = [], o = 0; o < this.i; o++)
                                i.unshift(e.f.pop());
                            e.r[3] = e.r[this.s][r](i[0], i[1]);
                            break;
                        case 2:
                            for (var a = [], c = 0; c < this.i; c++)
                                a.unshift(e.f.pop());
                            e.r[3] = new e.r[this.s](a[0], a[1])
                    }
                }
            ;
            var k = function (e) {
                for (var t = 66, n = [], r = 0; r < e.length; r++) {
                    var i = 24 ^ e.charCodeAt(r) ^ t;
                    n.push(String.fromCharCode(i)),
                        t = i
                }
                return n.join("")
            };

            function Q(e) {
                this.t = (4095 & e) >> 10,
                    this.s = (1023 & e) >> 8,
                    this.i = 1023 & e,
                    this.h = 63 & e
            }

            function C(e) {
                this.t = (4095 & e) >> 10,
                    this.a = (1023 & e) >> 8,
                    this.c = (255 & e) >> 6
            }

            function B(e) {
                this.s = (3072 & e) >> 10,
                    this.h = 1023 & e
            }

            function f(e) {
                this.h = 4095 & e
            }

            function g(e) {
                this.s = (3072 & e) >> 10
            }

            function u(e) {
                this.h = 4095 & e
            }

            function w(e) {
                this.t = (3840 & e) >> 8,
                    this.s = (192 & e) >> 6,
                    this.i = 63 & e
            }

            function G() {
                this.r = [0, 0, 0, 0],
                    this.C = 0,
                    this.Q = [],
                    this.k = [],
                    this.B = [],
                    this.f = [],
                    this.g = [],
                    this.u = !1,
                    this.G = [],
                    this.b = [],
                    this.o = !1,
                    this.w = null,
                    this.U = null,
                    this.F = [],
                    this.R = 0,
                    this.J = {
                        0: s,
                        1: i,
                        2: h,
                        3: a,
                        4: c,
                        5: n,
                        6: e,
                        7: o,
                        8: r,
                        9: Q,
                        10: C,
                        11: B,
                        12: f,
                        13: g,
                        14: u,
                        15: w
                    }
            }

            Q.prototype.e = function (e) {
                switch (this.t) {
                    case 0:
                        e.f.push(e.r[this.s]);
                        break;
                    case 1:
                        e.f.push(this.i);
                        break;
                    case 2:
                        e.f.push(e.k[this.h]);
                        break;
                    case 3:
                        e.f.push(k(e.b[this.h]))
                }
            }
                ,
                C.prototype.e = function (A) {
                    switch (this.t) {
                        case 0:
                            var t = A.f.pop();
                            A.r[this.a] = A.r[this.c][t];
                            break;
                        case 1:
                            var s = A.f.pop()
                                , i = A.f.pop();
                            A.r[this.c][s] = i;
                            break;
                        case 2:
                            var h = A.f.pop();
                            A.r[this.a] = eval(h)
                    }
                }
                ,
                B.prototype.e = function (e) {
                    e.r[this.s] = k(e.b[this.h])
                }
                ,
                f.prototype.e = function (e) {
                    e.w = this.h
                }
                ,
                g.prototype.e = function (e) {
                    throw e.r[this.s]
                }
                ,
                u.prototype.e = function (e) {
                    var t = this
                        , n = [0];
                    e.k.forEach((function (e) {
                            n.push(e)
                        }
                    ));
                    var r = function (r) {
                        var i = new G;
                        return i.k = n,
                            i.k[0] = r,
                            i.v(e.G, t.h, e.b, e.F),
                            i.r[3]
                    };
                    r.toString = function () {
                        return "() { [native code] }"
                    }
                        ,
                        e.r[3] = r
                }
                ,
                w.prototype.e = function (e) {
                    switch (this.t) {
                        case 0:
                            for (var t = {}, n = 0; n < this.i; n++) {
                                var r = e.f.pop();
                                t[e.f.pop()] = r
                            }
                            e.r[this.s] = t;
                            break;
                        case 1:
                            for (var i = [], o = 0; o < this.i; o++)
                                i.unshift(e.f.pop());
                            e.r[this.s] = i
                    }
                }
                ,
                G.prototype.D = function (e) {
                    for (var t = window.atob(e), n = t.charCodeAt(0) << 8 | t.charCodeAt(1), r = [], i = 2; i < n + 2; i += 2)
                        r.push(t.charCodeAt(i) << 8 | t.charCodeAt(i + 1));
                    this.G = r;
                    for (var o = [], a = n + 2; a < t.length;) {
                        var c = t.charCodeAt(a) << 8 | t.charCodeAt(a + 1)
                            , u = t.slice(a + 2, a + 2 + c);
                        o.push(u),
                            a += c + 2
                    }
                    this.b = o
                }
                ,
                G.prototype.v = function (e, t, n) {
                    for (t = t || 0,
                            n = n || [],
                            this.C = t,
                            "string" == typeof e ? this.D(e) : (this.G = e,
                                this.b = n),
                            this.o = !0,
                            this.R = Date.now(); this.o;) {
                        var r = this.G[this.C++];
                        if ("number" != typeof r)
                            break;
                        var i = Date.now();
                        if (500 < i - this.R)
                            return;
                        this.R = i;
                        try {
                            this.e(r)
                        } catch (e) {
                            this.U = e,
                            this.w && (this.C = this.w)
                        }
                    }
                }
                ,
                G.prototype.e = function (e) {
                    var t = (61440 & e) >> 12;
                    new this.J[t](e).e(this)
                }
                ,
            "undefined" != typeof window && (new G).v("AxjgB5MAnACoAJwBpAAAABAAIAKcAqgAMAq0AzRJZAZwUpwCqACQACACGAKcBKAAIAOcBagAIAQYAjAUGgKcBqFAuAc5hTSHZAZwqrAIGgA0QJEAJAAYAzAUGgOcCaFANRQ0R2QGcOKwChoANECRACQAsAuQABgDnAmgAJwMgAGcDYwFEAAzBmAGcSqwDhoANECRACQAGAKcD6AAGgKcEKFANEcYApwRoAAxB2AGcXKwEhoANECRACQAGAKcE6AAGgKcFKFANEdkBnGqsBUaADRAkQAkABgCnBagAGAGcdKwFxoANECRACQAGAKcGKAAYAZx+rAZGgA0QJEAJAAYA5waoABgBnIisBsaADRAkQAkABgCnBygABoCnB2hQDRHZAZyWrAeGgA0QJEAJAAYBJwfoAAwFGAGcoawIBoANECRACQAGAOQALAJkAAYBJwfgAlsBnK+sCEaADRAkQAkABgDkACwGpAAGAScH4AJbAZy9rAiGgA0QJEAJACwI5AAGAScH6AAkACcJKgAnCWgAJwmoACcJ4AFnA2MBRAAMw5gBnNasCgaADRAkQAkABgBEio0R5EAJAGwKSAFGACcKqAAEgM0RCQGGAYSATRFZAZzshgAtCs0QCQAGAYSAjRFZAZz1hgAtCw0QCQAEAAgB7AtIAgYAJwqoAASATRBJAkYCRIANEZkBnYqEAgaBxQBOYAoBxQEOYQ0giQKGAmQABgAnC6ABRgBGgo0UhD/MQ8zECALEAgaBxQBOYAoBxQEOYQ0gpEAJAoYARoKNFIQ/zEPkAAgChgLGgkUATmBkgAaAJwuhAUaCjdQFAg5kTSTJAsQCBoHFAE5gCgHFAQ5hDSCkQAkChgBGgo0UhD/MQ+QACAKGAsaCRQCOYGSABoAnC6EBRoKN1AUEDmRNJMkCxgFGgsUPzmPkgAaCJwvhAU0wCQFGAUaCxQGOZISPzZPkQAaCJwvhAU0wCQFGAUaCxQMOZISPzZPkQAaCJwvhAU0wCQFGAUaCxQSOZISPzZPkQAaCJwvhAU0wCQFGAkSAzRBJAlz/B4FUAAAAwUYIAAIBSITFQkTERwABi0GHxITAAAJLwMSGRsXHxMZAAk0Fw8HFh4NAwUABhU1EBceDwAENBcUEAAGNBkTGRcBAAFKAAkvHg4PKz4aEwIAAUsACDIVHB0QEQ4YAAsuAzs7AAoPKToKDgAHMx8SGQUvMQABSAALORoVGCQgERcCAxoACAU3ABEXAgMaAAsFGDcAERcCAxoUCgABSQAGOA8LGBsPAAYYLwsYGw8AAU4ABD8QHAUAAU8ABSkbCQ4BAAFMAAktCh8eDgMHCw8AAU0ADT4TGjQsGQMaFA0FHhkAFz4TGjQsGQMaFA0FHhk1NBkCHgUbGBEPAAFCABg9GgkjIAEmOgUHDQ8eFSU5DggJAwEcAwUAAUMAAUAAAUEADQEtFw0FBwtdWxQTGSAACBwrAxUPBR4ZAAkqGgUDAwMVEQ0ACC4DJD8eAx8RAAQ5GhUYAAFGAAAABjYRExELBAACWhgAAVoAQAg/PTw0NxcQPCQ5C3JZEBs9fkcnDRcUAXZia0Q4EhQgXHojMBY3MWVCNT0uDhMXcGQ7AUFPHigkQUwQFkhaAkEACjkTEQspNBMZPC0ABjkTEQsrLQ==");
            var b = function (e) {
                return __g._encrypt(encodeURIComponent(e))
            };
            exports.ENCRYPT_VERSION = A,
                exports.default = b
            """

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

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_zhihu_headers(self, url):
        self.header = {
            'User-Agent': self.get_ua(),
            "cookie": self.cookie
        }
        cookie_key = re.findall('d_c0=(.*?);', self.cookie)[0]
        api_url = url.replace("https://www.zhihu.com", "")
        include = "101_3_2.0+{}+{}".format(api_url, cookie_key)
        md5 = hashlib.new('md5', include.encode()).hexdigest()
        js_run = execjs.compile(self.js_str)
        xzse96 = "2.0_%s" % js_run.call('b', md5)
        self.header["x-zse-93"] = "101_3_2.0"
        self.header["x-zse-96"] = xzse96
        return self.header

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_zhihu_list_answer(self, zhihu_id, num):
        # proxy = self.getProxy()
        url = "https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B*%5D.topics%3Bdata%5B*%5D.settings.table_of_content.enabled&offset={}&limit={}&sort_by=default&platform=desktop".format(zhihu_id, str(num*5), "5")
        header = self.get_zhihu_headers(url)
        response = requests.get(url, headers=header, timeout=20)
        json_result = json.loads(response.text)
        json_data = json_result['data']
        for question in json_data:
            if question['id'] not in self.answer_id:
                self.answer_id.append(question['id'])
                try:
                    zhihu_video_id = 'https://www.zhihu.com/zvideo/{}'.format(question['attachment']['video']['zvideo_id'])
                except:
                    zhihu_video_id = ''
                self.questionInfo['问题ID'] = question['question']['id']
                self.questionInfo['问题标题'] = question['question']['title']
                self.questionInfo['问题链接'] = 'https://www.zhihu.com/question/{}'.format(zhihu_id)
                self.questionInfo['提问时间'] = self.get_transform_time(question['question']['created'])
                self.questionInfo['问题最新编辑时间'] = self.get_transform_time(question['question']['updated_time'])
                self.questionInfo['回答ID'] = question['id']
                self.questionInfo['链接'] = 'https://www.zhihu.com/question/{}/answer/{}'.format(question['question']['id'], question['id'])
                self.questionInfo['作者'] = question['author']['name']
                self.questionInfo['回答内容'] = re.sub('<(.*?)>', '', question['content']) + zhihu_video_id
                self.questionInfo['评论数量'] = question['comment_count']
                self.questionInfo['赞同数量'] = question['voteup_count']
                self.questionInfo['回答时间'] = self.get_transform_time(question['updated_time'])
                self.questionInfo['编辑时间'] = self.get_transform_time(question['updated_time'])
                print(self.questionInfo)
            else:
                print('重复数据：{}'.format('https://www.zhihu.com/question/{}/answer/{}'.format(question['question']['id'], question['id'])))
        if len(self.answer_id) == int(self.questionInfo['问题回答数']):
            return False
        return (True)

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_zhihu_cookies(self, zhihu_id):
        url = "https://www.zhihu.com/question/{}".format(zhihu_id)
        self.driver.get(url)
        time.sleep(10)
        html = self.driver.page_source
        page = etree.HTML(html)
        cookie_items = self.driver.get_cookies()
        cookie_str = ""
        # 组装cookie字符串
        for item_cookie in cookie_items:
            item_str = item_cookie["name"]+"="+item_cookie["value"]+"; "
            cookie_str += item_str
        json_data = json.loads(page.xpath('//*[@id="js-initialData"]/text()')[0])
        question = json_data.get('initialState').get('entities').get('questions')[zhihu_id]
        tags = ''
        for i in question['topics']:
            tags += i['name'] + ' '
        self.questionInfo['问题内容'] = re.sub('<(.*?)>', '', question['detail'])
        self.questionInfo['问题标签'] = tags
        self.questionInfo['问题回答数'] = question['answerCount']
        self.questionInfo['问题浏览数'] = question['visitCount']
        self.questionInfo['问题评论数'] = question['commentCount']
        self.questionInfo['问题关注数'] = question['followerCount']
        return(cookie_str)


    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_transform_time(self, t):
        ti = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        return ti

    def process_item(self, keyword,pagesize):
        self.init()
        p = pagesize
        self.driver = self.get_driver()
        #############
        try:
            self.cookie = self.get_zhihu_cookies(keyword)
        except Exception as e:
            self.driver.quit()
            self.driver = self.get_driver()
            print(e)
        #############
        try:
            pagesize = int(self.questionInfo['问题回答数'])
            if pagesize > p:
                for i in range(0, p):
                    if self.get_zhihu_list_answer(keyword, i) == False:
                        break
            else:
                for i in range(0, pagesize):
                    if self.get_zhihu_list_answer(keyword, i) == False:
                        break
        except Exception as e:
            print(e)
        #############
        self.answer_id = []
        self.driver.quit()

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def getProxy(self):
        proxies = {
            "http": '',
            "https": '',
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
            '55807309',
            '28981353',
            '44436685',
            '489252629',
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
