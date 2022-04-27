
from lxml import etree
import logging
import re
import cv2
import os
import time
from pyppeteer import launch
import random
import requests
import tenacity
import asyncio
import json
import io
from pathlib import Path
import aiohttp
aiohttp_session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
try:
    from PIL import Image
except:
    os.system('pip install Pillow==8.4.0')
    from PIL import Image
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
    name = 'leboncoin'
    base_url = 'https://www.leboncoin.fr/'

    def init(self):
        self.browser = ''
        self.page = ''
        self.ads_url_list = []
        self.picture_url_bg = ''
        self.picture_url_bg_gap = ''
        self.picture_url_slice = ''
        self.response_html = ''
        self.pagesize = 0
        self.pagenum = 1
        self.bloqué_html = ''
        self.keyword = ''
        self.request = ''
        self.stops = False
        self.max_pages = 0
        self.proxy = {
                    'http': 'http://127.0.0.1:10809',
                    'https': 'http://127.0.0.1:10809',
                }

    async def PyppeteerMain(self):
        self.browser = await launch({
            'headless': True,
            'userDataDir': 'pyppeteer_data_for_cjt' + '_{}'.format(time.time()),
            'args': [
                '--no-sandbox',
                '--start-maximized',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled',
                # '--proxy-server={}'.format(),
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

    # 监听图片url地址
    async def intercept_network_request(self, request):
        # 有缺口的背景图
        if 'static.geetest.com/pictures/gt/' and '.webp' and '/bg/' in request.url:
            if 'pagead2.googlesyndication' not in request.url:
                if self.picture_url_bg_gap == '':
                    self.picture_url_bg_gap = request.url
                    print(request.url)
            await request.continue_()
        # 滑块图
        elif 'static.geetest.com/pictures/gt/' and '.png' and '/slice/' in request.url:
            if self.picture_url_slice == '':
                self.picture_url_slice = request.url
                print(request.url)
            await request.continue_()
        # 无缺口背景图
        elif 'static.geetest.com/pictures/gt/' and '.webp' in request.url:
            if self.picture_url_bg == '':
                self.picture_url_bg = request.url
                print(request.url)
            await request.continue_()
        elif 'leboncoin.fr/recherche?text=' in request.url:
            try:
                req = {
                    "headers": request.headers,
                    "data": request.postData,
                    "proxy": self.proxy,
                    "timeout": 5,
                    "ssl": False,
                }
                try:
                    # 使用第三方库获取响应
                    async with aiohttp_session.request(
                        method=request.method, url=request.url, **req
                    ) as response:
                        body = await response.read()
                except Exception as e:
                    body = ''
                    print(e)
                    await request.abort()
                # 数据返回给浏览器
                resp = {"body": body, "headers": response.headers,
                        "status": response.status}
                if response.status == 200:
                    self.request = request
                    self.stops = True
                await request.respond(resp)
            except Exception as e:
                print('url：{},error：{}'.format(request.url, e))
        else:
            await request.continue_()

    # 拦截返回来的html内容，避免跳转后无法获取
    async def intercept_network_response(self, response):
        if 'leboncoin.fr/recherche?text=' in response.url:
            self.response_html = await response.text()
            try:
                await self.upload_data(self.response_html, self.keyword)
            except Exception as e:
                print(e)
        elif 'geo.captcha-delivery.com/captcha/?initialCid=' in response.url:
            self.bloqué_html = await response.text()

    async def get_leboncoin_lists(self, keyword, url):
        while True:
            if self.stops == True:
                print('成功获取，跳出循环')
                break
            try:
                await asyncio.sleep(10)
                check_captcha = await self.check_captcha()
                if check_captcha == True:
                    print('无需滑块验证')
                    await asyncio.sleep(5)
                    await self.click_accept()
                    await asyncio.sleep(5)
                    await self.goto_pgae(url)
                    await asyncio.sleep(10)
                    break
                elif check_captcha == False:
                    print('需要滑块验证')
                    code = await self.click_picture()
                    if code == True:
                        await self.move_slice()
                    else:
                        raise Exception('没有正确的ifame')
            except Exception as e:
                print(e)
                raise Exception(e)
    # 翻页
    async def goto_pgae(self, url):
        try:
            await self.page.goto(url, options={'timeout': 1000 * 50})
        except Exception as e:
            print(e)
        return True

    # 上传数据
    async def upload_data(self, html, keyword):
        page = etree.HTML(html)
        data = page.xpath('//*[@id="__NEXT_DATA__"]//text()')[0]
        data_json = json.loads(data)
        ads_list = data_json.get('props').get(
            'pageProps').get('searchData').get('ads')

    # 输入关键点击搜索
    async def click_recherche(self, keyword):
        await self.page.type('[autocomplete~=search-keyword-suggestions]', keyword)
        await self.page.keyboard.press('Enter')
        return True

    # 判断是否需要验证码
    async def check_captcha(self):
        html = await self.page.content()
        page = etree.HTML(html)
        data = page.xpath('/html/body/script/text()')[0]
        base_data = re.findall("'(.*?)',", data)[1]
        ddk = base_data[6:len(base_data)]
        if 'eboncoin.fr/tags.js' in ddk:
            return True
        else:
            if len(html) < 800 and 'Please enable JS and disable any ad blocker' in html:
                raise Exception('check_captcha:< 800,retry')
            elif 'Vous avez été bloqué(e)' in self.bloqué_html:
                self.bloqué_html = ''
                raise Exception('check_captcha:Vous avez été bloqué(e),retry')
            else:
                return False

    # 点击接受
    async def click_accept(self):
        try:
            await self.page.hover('#didomi-notice-agree-button')
            await self.page.mouse.down()
            await self.page.mouse.up()
            await asyncio.sleep(5)
        except Exception as e:
            print(e)

    # 点击获取验证码图片
    async def click_picture(self):
        frames = self.page.frames
        for iframe in frames:
            try:
                # 获取焦点,点击获取验证图片
                await iframe.hover('.geetest_wait')
                await self.page.mouse.down()
                await self.page.mouse.up()
                await asyncio.sleep(5)
                print('{}:正确的iframe'.format(iframe))
                return True
            except:
                print('{}:不是正确的iframe'.format(iframe))
        return False

    # 移动滑块
    async def move_slice(self):
        try:
            path_list = await self.download_img()
            x = self.get_slice_x(path_list[0], path_list[1])
            length_list = self.slide_list(x)
            frames = self.page.frames
            for iframe in frames:
                try:
                    await iframe.hover(".geetest_slider_button")
                    await self.page.mouse.down()
                    await self.page.waitFor(1000)
                    for length in length_list:
                        await self.page.mouse.move(self.page.mouse._x + length, self.page.mouse._y, {'delay': random.randint(1000, 2000), 'steps': 3})
                    await self.page.mouse.move(self.page.mouse._x - 1, self.page.mouse._y, {'delay': random.randint(1000, 2000), 'steps': 3})
                    await self.page.waitFor(1000)
                    await self.page.mouse.up()
                except Exception as e:
                    print(e)
            print('位置偏移：{}'.format(x))
            self.picture_url_bg = ''
            self.picture_url_bg_gap = ''
            self.picture_url_slice = ''
            return(True)
        except Exception as e:
            print(e)
            raise Exception(e)

    # 识别缺口位置
    def get_slice_x(self, bg_path, slice_path):
        # 读取背景图片和缺口图片
        bg_img = cv2.imread(bg_path, 0)  # 背景图片
        tp_img = cv2.imread(slice_path, 0)  # 缺口图片
        # 识别图片边缘
        bg_edge = cv2.Canny(bg_img, 100, 200)
        tp_edge = cv2.Canny(tp_img, 100, 200)
        # 转换图片格式
        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
        # 缺口匹配
        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
        X = max_loc[0]
        # 绘制方框
        th, tw = tp_pic.shape[:2]
        tl = max_loc  # 左上角点的坐标
        br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
        cv2.rectangle(bg_img, tl, br, (0, 0, 255), 2)  # 绘制矩形
        cv2.imwrite('out.jpg', bg_img)  # 保存在本地
        return X

    # 生成随机轨迹
    def slide_list(self, total_length):
        v = 0  # 初速度
        t = 1  # 单位时间为0.3s来统计轨迹，轨迹即0.3内的位移
        slide_result = []  # 位移/轨迹列表，列表内的一个元素代表一个T时间单位的位移,t越大，每次移动的距离越大
        current = 0  # 当前的位移
        mid = total_length * 3 / 5  # 到达mid值开始减速
        while current < total_length:
            if current < mid:
                a = 0.4  # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
            else:
                a = -0.5
            v0 = v  # 初速度
            s = v0 * t + 0.5 * a * (t ** 2)  # 0.2秒时间内的位移
            current += s  # 当前的位置
            slide_result.append(round(s))  # 添加到轨迹列表
            v = v0 + a * t  # 速度已经达到v,该速度作为下次的初速度
        return slide_result

    # 下载极验证乱序图片和缺口
    async def download_img(self):
        if self.picture_url_bg_gap:
            bg_gap_path, slice_path = '', ''
            try:
                # 下载并且还原有缺口背景图
                path = await self.get_decode_image('bg_gap.jpg', self.picture_url_bg_gap)
                bg_gap_path = await self.parse_bg_captcha(path, 'bg_gap.jpg')
                # 下载滑块图
                path = await self.get_decode_image('slice.jpg', self.picture_url_slice)
                slice_path = Path(path).resolve().__str__()
            except Exception as e:
                raise Exception(e)
            return [bg_gap_path, slice_path]
        else:
            raise Exception('retry')

    # 下载图片
    async def get_decode_image(self, filename, url):
        if url:
            try:
                img = requests.get(url, timeout=20).content
                with open(filename, "wb") as f:
                    f.write(img)
                    f.close()
                return filename
            except Exception as e:
                raise Exception(e)
        else:
            raise Exception('get_decode_image:{},retry'.format(url))

    # 还原极验乱序图片
    async def parse_bg_captcha(self, img, save_path=None):
        if isinstance(img, (str, Path)):
            _img = Image.open(img)
        elif isinstance(img, bytes):
            _img = Image.open(io.BytesIO(img))
        else:
            raise ValueError(
                f'输入图片类型错误, 必须是<type str>/<type Path>/<type bytes>: {type(img)}')
        # 图片还原顺序, 定值
        _Ge = [39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29, 27, 26, 36, 37, 31, 30, 44, 45, 43,
               42, 12, 13, 23, 22, 14, 15, 21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17]
        w_sep, h_sep = 10, 80
        # 还原后的背景图
        new_img = Image.new('RGB', (260, 160))
        for idx in range(len(_Ge)):
            x = _Ge[idx] % 26 * 12 + 1
            y = h_sep if _Ge[idx] > 25 else 0
            # 从背景图中裁剪出对应位置的小块
            img_cut = _img.crop((x, y, x + w_sep, y + h_sep))
            # 将小块拼接到新图中
            new_x = idx % 26 * 10
            new_y = h_sep if idx > 25 else 0
            new_img.paste(img_cut, (new_x, new_y))
        if save_path is not None:
            save_path = Path(save_path).resolve().__str__()
            new_img.save(save_path)
        return save_path

    @tenacity.retry(stop=tenacity.stop_after_attempt(10))
    def get_transform_time(self, t):
        ti = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        return ti

    @tenacity.retry(stop=tenacity.stop_after_attempt(20))
    def get_leboncoin_list(self, keyword):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.page.setRequestInterception(True))
            self.page.on('request', lambda request: asyncio.create_task(
                self.intercept_network_request(request)))
            self.page.on('response', lambda response: asyncio.create_task(
                self.intercept_network_response(response)))
            loop.run_until_complete(self.page.goto(
                'https://www.leboncoin.fr/', options={'timeout': 1000 * 100}))
            loop.run_until_complete(asyncio.sleep(10))
            for i in range(self.pagenum, self.pagesize):
                if self.stops == True:
                    print('成功获取，跳出循环')
                    break
                try:
                    url = 'https://www.leboncoin.fr/recherche?text={}&page={}'.format(
                        keyword, i)
                    loop.run_until_complete(
                        self.get_leboncoin_lists(keyword, url))
                except Exception as e:
                    self.pagenum = i
                    raise Exception(e)
        except Exception as e:
            asyncio.get_event_loop().run_until_complete(self.browser.close())
            asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
            raise Exception(e)

    def process_item(self, keyword,Pagesize):
        self.init()
        self.keyword = keyword
        self.pagesize = Pagesize
        asyncio.get_event_loop().run_until_complete(self.PyppeteerMain())
        try:
            self.get_leboncoin_list(keyword)
        except Exception as e:
            print(e)
        if self.request:
            for i in range(self.pagenum, self.pagesize):
                try:
                    self.get_data_taowa(i)
                except Exception as e:
                    print(e)
        else:
            print('无request')
        asyncio.get_event_loop().run_until_complete(self.browser.close())

    @tenacity.retry(stop=tenacity.stop_after_attempt(20))
    def get_data_taowa(self, i):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.get_data(self.request, i))
        except Exception as e:
            raise Exception(e)

    async def get_data(self, request, i):
        loop = asyncio.get_event_loop()
        myurl = 'https://www.leboncoin.fr/recherche?text={}&page={}'.format(
            self.keyword, i)
        try:
            req = {
                "headers": request.headers,
                "data": request.postData,
                "proxy": self.proxy,
                "timeout": 5,
                "ssl": False,
            }
            # 使用第三方库获取响应
            async with aiohttp_session.request(
                method=request.method, url=myurl, **req
            ) as response:
                body = await response.read()
            if response.status == 200:
                loop.run_until_complete(self.upload_data(body, self.keyword))
            else:
                raise Exception(myurl, response.status)
        except Exception as e:
            print(myurl, e)
            raise Exception(e)

    @staticmethod
    def get_ua():
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
        ]
        return random.choice(user_agent_list)

if __name__ == "__main__":
    params = {
        "MainKeys": [
            'Voitures'
        ],
        "PageSize": 20,
    }
    Pagesize = params['PageSize']
    function = AtomExecutor()
    MainKeys =  params['MainKeys']
    for params in MainKeys:
        try:
            function.process_item(params,Pagesize)
        except Exception as e:
            print(e)