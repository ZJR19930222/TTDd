from requests import get, exceptions, post
from os import path, mkdir, remove
from threading import Thread, Semaphore
from re import sub
from re import compile as Compile
from subprocess import call
from json import dumps
from glob import glob
from time import sleep
# 初始请求头部
Req_Headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
}
# 响应时间限制
Req_Time_Max=20


class MyException(Exception):
    """ 自定义错误基类 """
    pass


class ConnectError(MyException):
    def __init__(self):
        self.args = ('连接不上目标服务器',)


class NoneResourceError(MyException):
    def __init__(self):
        self.args = ('没有有效资源',)


def hostget(url:str)->str:
    """ 通过输入连接🔗获取服务器主机域名 """
    return '/'.join(url.split('/')[:3])


def removefile(files:"str/list"):
    """ 移除文件📄 """
    if type(files) == list:
        for i in files:
            remove(i)
    elif type(files) == str:
        remove(files)


def PattenCut(patten:str, string:str, start:int=0, end:int=None)->iter:
    """ 标准的字符截取器,返回一个迭代对象 """
    pattenX = Compile(patten)
    coincide = pattenX.finditer(string)
    if coincide:
        for i in coincide:
            yield i.group()[start:end]


def MakeDir(PATH):
    if not path.exists(PATH):
        mkdir(PATH)


def go(url, headers=Req_Headers, timeout=Req_Time_Max, **kwargs)->'<response>':
    """ 返回响应体 """
    num = 0
    while num < 6:
        try:
            data = get(url=url, headers=headers, timeout=timeout, **kwargs)
        except exceptions.RequestException: # 捕获异常
            num += 1
        else:
            return data
    raise ConnectError()


class DownLoad_M3U8:
    koudaicc = [] # 进度容器
    Counts = 0 # 计数变量
    ck = []
    def __init__(self, url:'initial url'):
        self.url = url
        self.uid = list(PattenCut('id=[0-9]+', self.url, start=3))[0] # 也用这个视频编号来命名
        self.filename = self.uid


    def rename_ts_file(self, _):
        self.Counts += 1
        return f"./temp/{self.Counts}.ts" # 生成的x.ts流文件保存在当前目录下文件temp中


    def get_m3u8(self):
        PlayLoadData = {"liveId": self.uid}
        head={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            "Referer": f"{self.url}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        url_live = "https://pocketapi.48.cn/live/api/v1/live/getLiveOne"
        url_open_live = 'https://pocketapi.48.cn/live/api/v1/live/getOpenLiveOne'
        try:
            data = post(url_live, data=dumps(PlayLoadData), headers=head).json()
            data = data['content']
        except Exception:
            data = post(url_open_live, data=dumps(PlayLoadData), headers=head).json()
            data = data['content']
        finally:
            if 'playStreamPath' in data:
                lrc_url = data['msgFilePath']
                m3u8_url = data['playStreamPath']
            elif 'playStreams' in data:
                m3u8_url = data['playStreams'][0]['streamPath']
                lrc_url = None
            else:
                raise NoneResourceError()
            self.m3u8_url = m3u8_url;self.lrc_url = lrc_url


    def ts_url_list(self, host48):
        self.host48 = host48
        def TS_Url(lst):
            url_list = []
            for i in lst:
                url_list.append(self.host48 + i)
            return url_list, len(url_list)
        data_text = go(self.m3u8_url).text
        self.save_m3u8(data_text)
        data_list = data_text.split('\n')
        data_list1=[]
        for item in data_list:
            if "/fragments" in item:
                data_list1.append(item.strip())
        self.TsUrlList, self.UrlLength = TS_Url(data_list1)
        self.ck.append(self.UrlLength)

    
    
    def save_m3u8(self, txt):
        txt = sub("/fragments.+?ts", self.rename_ts_file, txt)
        with open('me.m3u8', 'w', encoding='utf-8') as file:
            file.write(txt)
    
    
    def download(self, url, lock, index):
        lock.acquire()
        data = go(url).content
        with open(f"./temp/{index}.ts", 'wb') as file:
            file.write(data)
        self.koudaicc.append(1)
        lock.release()
    
    def begin(self):
        threads = []
        mylock = Semaphore(value=8)
        j = 0
        self.get_m3u8()
        self.ts_url_list(hostget(self.m3u8_url))
        if self.lrc_url:
            with open(f'{self.uid}.lrc', 'wb') as fileobject:
                fileobject.write(go(self.lrc_url).content)
        for urlx in self.TsUrlList:
            j += 1
            threads.append(Thread(target=self.download, args=(urlx, mylock, j)))
        for item in threads:
            item.start()
        for item in threads:
	        item.join()
        self.combineTS()
        removefile(glob('.\\temp\\*.ts'))
        removefile('me.m3u8')
        print('视频合并完成')

    def combineTS(self):
        call(['ffmpeg','-allowed_extensions','ALL','-i','me.m3u8','-c','copy', f"{self.uid}.mp4",'-loglevel', 'quiet'])



