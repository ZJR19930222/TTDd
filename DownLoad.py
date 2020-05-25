import threading
from time import sleep
from requests import get, exceptions
from re import sub
from re import compile as Compile
from json import loads
from os import mkdir, path
from bs4 import BeautifulSoup as bs
from hashlib import md5
default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
}
api_headers = {
    'Host': 'api.bilibili.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
}
page_headers = {
    'Host': 'www.bilibili.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}
old_url_headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Host':'interface.bilibili.com',
    'Connection':'keep-alive',
}
def old_url(CID,QUALITY=64):
    """通过cid编号获取视频下载地址,默认清晰度是720p"""
    keystr='rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'[::-1]
    tempstr=''
    for letter in keystr:
        addstr=chr(ord(letter)+2)
        tempstr+=addstr
    keystr1,keystr2=tempstr.split(":")
    keystr3=f"appkey={keystr1}&cid={CID}&otype=json&qn={QUALITY}&quality={QUALITY}&type="
    keystr4=md5(bytes(keystr3+keystr2,'utf-8')).hexdigest()
    geturl=f"https://interface.bilibili.com/v2/playurl?{keystr3}&sign={keystr4}"
    try:
        htmljson=Go(geturl,old_url_headers).json()
        # print(htmljson)
    except AttributeError:
        print(f'\x1b[4;31m访问旧视频地址{CID}失败\x1b[0m')
        # error_container_list.append(f'访问旧视频地址失败:{CID}')
    else:
        videourl=htmljson['durl']
        ddd=[]
        for dict1 in videourl:
            ddd.append(dict1['url'])
        return ddd
class MyException(Exception):
    """ 自定义错误基类 """
    pass
class ConnectError(MyException):
    """ 连接不上服务器 """
    def __init__(self):
        self.args = ('连接不上目标服务器',)
class PattenError(MyException):
    """ 连接不上服务器 """
    def __init__(self):
        self.args = ('网页源码匹配错误',)
response_time_max = 60
def MakeDir(PATH:"文件或目录")->int:
    """ 存在文件则返回1,否则创建并返回0 """
    if not path.exists(PATH):
        mkdir(PATH)
        return 0
    return 1
def RemoveInvalidChr(STRING):
    """去除文件名中那些不合法的字符(?*/)"""
    q=sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]',"",rf'{STRING}')
    q = q.replace('\\','')
    q = sub(r'[?*"<>/:|]',"",q)
    if len(q) > 60:
        return q[:60]
    else:
        return q
def ValueCopy(SEQUENCE)->list: # 也可以用copy.deepcopy()
    """对列表和字典进行完全的值拷贝,不受原先对象改变的影响"""
    INITIALLIST,INITIALDIRECTORY=[],{}
    if type(SEQUENCE)==list:
        for item in SEQUENCE:
            INITIALLIST.append(ValueCopy(item))
        return INITIALLIST
    elif type(SEQUENCE)==dict:
        for key,value in SEQUENCE.items():
            key=ValueCopy(key);value=ValueCopy(value)
            INITIALDIRECTORY[key]=value
        return INITIALDIRECTORY
    else:
        return SEQUENCE
def Go(url, headers, *, timeout=response_time_max, **kwargs)->"<response>":
    num = 0
    while num < 6:
        try:
            response = get(url, headers=headers, timeout=timeout, **kwargs)
        except exceptions.RequestException:
            num += 1
        else:
            return response
    raise ConnectError()
def playget(URL,HEADERS=page_headers)->"(video_url,audio_url)/False":
    """视频播放页面信息获取"""
    html_text=Go(URL,HEADERS).text
    html_lxml=bs(html_text, 'lxml')
    data=html_lxml.head.find_all('script')[2]
    data=data.string
    data_play=loads(data[20:])['data']
    if 'dash' in data_play:
        video_new_url=data_play['dash']['video'][0]['baseUrl']
        audio_new_url=data_play['dash']['audio'][0]['baseUrl']
        return video_new_url, audio_new_url
    else:
        return False
def PattenCut(patten, string, start=0, end=None)->list:
    """ 按照模式patten对目标字符串截取匹配部分coincidence,
    返回coincidence[start:end],若没有匹配则返回None """
    patten1 = Compile(patten)
    coincide = patten1.finditer(string)
    if coincide:
        cc = []
        for i in coincide:
            cc.append(i.group()[start:end])
        return cc
    else:
        raise PattenError()
def file_part(url, head,threadnum)->tuple:
    data= Go(url, head)
    content = data.headers["Content-Range"]
    content = int(PattenCut("/[0-9]+", content, start=1)[0])
    block = content//threadnum
    range_list = []
    write_list = []
    auxiliary_list = []
    for i in range(threadnum):
        auxiliary_list.append(i*block - 1)
        write_list.append(i*block)
    for i in auxiliary_list:
        range_list.append([i + 1, i + block])
    range_list[-1][-1] = content - 1
    return range_list, write_list
API_URL="https://api.bilibili.com/x/web-interface/view?bvid="
PLAY_URL='https://www.bilibili.com/video/BV'
def apiget(URL, HEADERS=api_headers)->list:
    """ cid,title,aid,name,videos,view,danmaku,desc,picurl,dimension """
    data=Go(URL, HEADERS).json()['data']
    aid = data["aid"]
    videos = data["videos"]
    desc = data["desc"]
    picurl = data["pic"]
    name = data["owner"]["name"]
    view = data["stat"]["view"]
    danmaku = data["stat"]["danmaku"]
    part=[]
    cid = []
    dimension = []
    title = RemoveInvalidChr(data['title'])
    for item in data['pages']:
        cid.append(item["cid"])
        part.append(RemoveInvalidChr(item['part']))
        dimension.append([item["dimension"]["width"], item["dimension"]["height"]])
    if len(cid) == 1:
        part = [title]
    return cid, part, aid, name, videos, view, danmaku, desc, dimension, picurl
container = []
odc = {}
class download:
    def __init__(self, page_url, title, threadnum, save_dict, rec_dict, index, cid):
        self.page_url = page_url
        self.title = title
        self.save_dict = save_dict.replace('/', '\\\\')
        self.threadnum = threadnum
        self.head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Origin': 'https://www.bilibili.com',
            'Connection': 'keep-alive',
            'Range': 'bytes=0-2028',
            'Referer': f'{self.page_url}'
        }
        self.cid = cid
        self.index = index
        self.rec_dict = rec_dict.replace('/', '\\\\')
        MakeDir(self.rec_dict)
        MakeDir(self.save_dict)
    def newORold(self):
        try:
            self.page_video_url = playget(self.page_url)
            if not self.page_video_url:
                self.page_video_url = old_url(self.cid)
                self.oldbegin()
            else:
                self.begin()
        except Exception:
            raise PattenError()
    def oldbegin(self):
        odc[int(self.index)] = len(self.page_video_url)
        j = 1
        for urlx in self.page_video_url:
            filename = self.rec_dict+'\\'+self.title+f'_{j}.flv'
            with open(filename,"wb") as f:
                pass
            f.close()
            lock = threading.Lock()
            range_list, write_list = file_part(urlx, self.head, self.threadnum)
            j +=1
            threads = []
            for i in range(len(write_list)):
                threads.append(threading.Thread(target=downloadcore,
                	args=(urlx, filename, lock, self.head, range_list[i], write_list[i], self.index)))
            for i in threads:
                i.start()
    def begin(self):
        self.filebox=(
            self.rec_dict + "\\" + self.title + "_video.flv",
            self.rec_dict + "\\" + self.title + "_audio.flv",
        )
        j = 0
        for url in self.page_video_url:
            filename = self.filebox[j]
            with open(filename,"wb") as f:
                    pass
            f.close()
            lock = threading.Lock()
            range_list, write_list = file_part(url, self.head, self.threadnum)
            j += 1
            threads = []
            for i in range(len(write_list)):
                threads.append(threading.Thread(target=downloadcore,
                	args=(url, filename, lock, self.head, range_list[i], write_list[i], self.index)))
            for i in threads:
                i.start()
def downloadcore(url, filename, lock, headers, rangex, writex, index):
    head = ValueCopy(headers)
    head.update({'Range':f"bytes={rangex[0]}-{rangex[1]}"})
    data = Go(url, head).content
    lock.acquire()
    with open(filename, 'rb+') as file:
        file.seek(writex)
        file.write(data)
    container[index].append(1)
    lock.release()
