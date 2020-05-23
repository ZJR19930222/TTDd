# TTDd
B站视频下载器
## 简介
### 我是谁？
1. 一个轻量桌面应用，目前支持 windows10 和 manjaro-linux
2. 主要由 python(3.8+),ffmpeg 和 Qt5 开发
3. 目前支持：B站视频下载，口袋48app视频下载，弹幕下载，美化和烧录，视频的简单剪辑包括导出gif
### 使用方法
### manjaro-linux
进入linux文件夹运行 main.py
> 不需要安装和配置什么，可以直接运行。推荐！
----------------------------------------
### windows10
安装最新版python,需要3.8以上版本。
https://www.python.org/downloads/

安装两个解析模块(parser module)
```sh
pip install lxml
pip install bs4
```
安装Qt对应于python的开发库
```sh
pip install PyQt5
```
安装网络请求库
```sh
pip install requests
```
安装ffmpeg
http://ffmpeg.org/download.html

安装完成之后，进入win10文件夹点击 run.bat 运行！
