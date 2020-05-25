import sys
from os import path, remove, rename
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow,
QTableWidgetItem,QVBoxLayout,QLabel,QGroupBox,QHBoxLayout,QSizePolicy,QToolButton,QProgressBar,QMenu,QPushButton,
QGraphicsPixmapItem, QGraphicsScene,QStyleFactory)
from PyQt5 import QtCore, QtGui
import window
from DownLoad import *
from subprocess import run as cmd
import sip
from koudai import DownLoad_M3U8
from shutil import copyfile
#1Ct411u7Yr
#1VQ4y1T7S8
countn = -1
def filenamere(num, filenmae:str)->str:
    b1,b2=path.splitext(filenmae)
    return b1+str(num)+b2
class myui(QMainWindow):
    notesi = QtCore.pyqtSignal(int)
    noteodd = QtCore.pyqtSignal(int)
    downrecord = []
    videon = False
    picturen = False
    flp = True
    flp1 = False

    def __init__(self):
        super().__init__()
        self.ui = window.Ui_myWindow()
        self.ui.setupUi(self)
        self.timer = QtCore.QTimer()
        self.timer.stop()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.putprogressbar)
        self.notesi.connect(self.combinebe)
        self.noteodd.connect(self.odcombinebe)

    
    def diropen(self):
        # 打开保存文件
        if self.sender() == self.ui.actionsave:
            self.ui.filesave = QFileDialog.getExistingDirectory(self, '选择保存视频文件', './')
        if self.sender() == self.ui.actionrecycle:
            self.ui.filerec = QFileDialog.getExistingDirectory(self, '选择保存中间文件', './')
        
    
    def partVD(self): # D:/B站视频
        """ 切换工具栏分页 """
        if self.ui.stackedWidget.currentIndex():
            self.ui.stackedWidget.setCurrentIndex(0)
        else:
            self.ui.stackedWidget.setCurrentIndex(1)


    def vopen(self):
        """ 打开视频文件 """
        tempdir = self.ui.filesave
        filename, _ = QFileDialog.getOpenFileName(self, '选择打开文件', f'{tempdir}', "Video(*.mp4 *.flv *mkv *mpeg *gif)")
        filename = filename.strip()
        cmd(['ffplay','-x','960','-y','600',filename])


    def tpaste(self):
        """ 剪切板操作 """
        temp = self.ui.myclipboard.text()
        if len(temp) < 10:
            return None
        if len(temp) > 10:
            try:
            	temp = PattenCut('[a-zA-Z0-9]{12}', temp, start=0)[0][2:]
            except Exception as e:
                temp = ''
        self.ui.lineTextBV.setText(temp)


    def start_info(self):
        self.ui.partWidget.setCurrentIndex(0)
        if self.flp1:
            self.clearall()
        self.videon = True
        self.picturen = True
        bv = self.ui.lineTextBV.text()[0:10]
        self.page_1 = PLAY_URL + bv
        self.cid, self.title, *_rest, self.dim, self.pic = apiget(API_URL + bv)
        title = QTableWidgetItem(self.title[0])
        av = QTableWidgetItem(f"{_rest[0]}")
        self.ui.infoChart.setItem(0, 0, av)
        self.ui.infoChart.setItem(1, 0, title)
        name = QTableWidgetItem(_rest[1])
        videos = QTableWidgetItem(f'{_rest[2]}')
        self.ui.infoChart.setItem(2, 0, name)
        self.ui.infoChart.setItem(3, 0, videos)
        view = QTableWidgetItem(f'{_rest[3]}')
        self.ui.infoChart.setItem(4, 0, view)
        danmu = QTableWidgetItem(f'{_rest[4]}')
        self.ui.infoChart.setItem(5, 0, danmu)
        size = QTableWidgetItem(f'{self.dim[0][0]}x{self.dim[0][1]}')
        self.ui.infoChart.setItem(6, 0, size)
        self.ui.DesctextBrowser.setText(_rest[5])
        self.flp1 = True


    def clearall(self):
        global countn
        if not hasattr(self, 'grouplist'):
        	return None
        for i in self.grouplist:
            self.ui.scrollVLayout.removeWidget(i)
            sip.delete(i)
        for i in range(len(container)):
            container.pop()
        self.downrecord = []
        self.timer.stop()
        self.flp = True
        countn = -1
    def videobar_show(self, intt):
        if intt == 1 and self.videon:
            self.videon = False
            num = 0
            for i in self.title:
                odc[num] = None
                container.append([])
                downloadgroup = QGroupBox(self.ui.scrollAreaWidgetContents)
                downloadgroup.setTitle(f'{num+1}')
                downloadgroup.setObjectName(f"downloadgroup{num}")
                dgroupVLayout = QVBoxLayout(downloadgroup)
                dgroupVLayout.setObjectName(f"dgroupVLayout{num}")
                dgroupHLayout = QHBoxLayout()
                dgroupHLayout.setObjectName(f"dgroupHLayout{num}")
                labelTitle = QLabel(downloadgroup)
                labelTitle.setObjectName(f"labelTitle{num}")
                if len(i) > 20:
                	i = i[0:20] + '...'
                labelTitle.setText(i)
                dgroupHLayout.addWidget(labelTitle)
                toolButtonDo = QPushButton(downloadgroup)
                toolButtonDo.setMinimumSize(QtCore.QSize(72, 0))
                toolButtonDo.setObjectName(f"QPushButton{num}")
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/SVG/下载.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                toolButtonDo.setIcon(icon)
                dgroupHLayout.addWidget(toolButtonDo)
                dgroupHLayout.setStretch(0, 5)
                dgroupHLayout.setStretch(1, 2)
                dgroupVLayout.addLayout(dgroupHLayout)
                progressBarDo = QProgressBar(downloadgroup)
                progressBarDo.setProperty("value", 0)
                progressBarDo.setObjectName(f"progressBarDo{num}")
                dgroupVLayout.addWidget(progressBarDo)
                self.ui.scrollVLayout.addWidget(downloadgroup)
                num += 1
                toolButtonDo.clicked.connect(self.downloadstart)
                # toolButtonDo.clicked.connect(self.avcombine)
                self.pgbarlist = self.ui.scrollAreaWidgetContents.findChildren(QProgressBar)
                self.grouplist = self.ui.scrollAreaWidgetContents.findChildren(QGroupBox)
        elif intt == 2 and self.picturen:
            self.picturen = False
            data = Go(self.pic, default_headers).content
            img = QtGui.QImage.fromData(data)
            piximg = QtGui.QPixmap.fromImage(img)
            self.picitem = QGraphicsPixmapItem(piximg)
            self.scene = QGraphicsScene()
            self.scene.addItem(self.picitem)
            self.ui.graphicsView.setScene(self.scene)
    def handlestyle(self):
        sender = self.sender()
        if sender == self.ui.actionxp:
            QApplication.setStyle(QStyleFactory.create('Windows'))
        elif sender == self.ui.actionwindows:
            QApplication.setStyle(QStyleFactory.create('windowsvista'))
        elif sender == self.ui.actionfusion:
            QApplication.setStyle(QStyleFactory.create('fusion'))
    def downloadstart(self):
        sender = self.sender()
        index = int(sender.objectName().replace('QPushButton',''))
        pgBar = self.pgbarlist[index]
        pgBar.setMaximum(0)
        sender.setEnabled(False)
        sender.setText('下载中...')
        threadnums = self.ui.spinBoxThreads.value() # 线程数
        pgBar.thr = threadnums
        self.downrecord.append(index)
        filesave = self.ui.filesave # 视频保存目录
        filerecycle = self.ui.filerec # 中间视频保存目录
        xml = self.ui.radButtonXML.isChecked() # XML弹幕文件
        ass = self.ui.radButtonASS.isChecked()
        dams = filesave + "/" + self.title[index] + f'{index}'
        if ass:
            self.dam = downloadASS(self.cid[index], dams, self.dim[index][0], self.dim[index][1])
            self.dam.start()
        elif xml:
            self.dam = downloadXML(self.cid[index], dams)
            self.dam.start()
        if len(self.title) == 1:
            self.t = downloadThread(self.page_1, self.title[0]+f'{index}', threadnums, filesave, filerecycle, 0,self.cid[0])
            # self.t.signalx.connect(self.updateprogressbar)
            self.t.start()
        else:
            self.t = downloadThread(self.page_1 +f'?p={index+1}', self.title[index]+f'{index}', threadnums,
            filesave, filerecycle, index,self.cid[index])
            # self.t.signalx.connect(self.updateprogressbar)
            self.t.start()
        if self.flp:
            self.timer.start()
            self.flp = False
    def putprogressbar(self):
        if not self.downrecord:
            self.flp = True
            self.timer.stop()
        else:
            for i in self.downrecord:
                if nowv:=len(container[i]):
                    tp = self.pgbarlist[i]
                    if odc[i] is None:
                        todu = 2*tp.thr
                        tp.setMaximum(100)
                        tp.setValue(100*nowv//(todu))
                        if nowv == todu:
                            self.downrecord.remove(i)
                            self.notesi.emit(i)
                    else:
                        todu = odc[i]*tp.thr
                        tp.setMaximum(100)
                        tp.setValue(100*nowv//(todu))
                        if nowv == todu:
                            self.downrecord.remove(i)
                            self.noteodd.emit(i)

    def odcombinebe(self, intt):
        lenth = odc[intt]
        lst = []
        outfile = self.ui.filesave+'/'+self.title[intt]+f'{intt}'
        MakeDir(outfile)
        for i in range(lenth):
            lst.append(self.ui.filerec+'/'+self.title[intt]+f'{intt}'+f'_{i+1}.flv')
        textp = '\n'.join(lst)
        self.cnv = Combinev1(textp, outfile, '.flv',intt)
        self.cnv.signac1.connect(self.complete)
        self.cnv.start()
           
    def downloadall(self):
        self.ui.pushButtonAllDownLoad.setEnabled(False)
        self.ui.pushButtonAllDownLoad.setText('全部下载中...')
        self.timera = QtCore.QTimer()
        self.timera.stop()
        self.timera.setInterval(5000)
        self.timera.timeout.connect(self.do_download)
        self.timera.start()
        self.do_download()
    def do_download(self):
        global countn
        if len(self.downrecord) < 3:
            countn += 1
            if countn + 1 > len(self.title):
                if not self.downrecord:
                    self.timera.stop()
                    self.ui.pushButtonAllDownLoad.setEnabled(True)
                    self.ui.pushButtonAllDownLoad.setText('全部下载')
            else:
                pushbutton_list = self.ui.scrollAreaWidgetContents.findChildren(QPushButton)
                pushbutton_list[countn].click()
    def combinebe(self, index):
        titlex = self.title[index]+f'{index}'
        self.avc = ThreadCombine(
            index,
            self.ui.filerec+"\\"+titlex+"_video.flv",
            self.ui.filerec+"\\"+titlex+"_audio.flv",
            self.ui.filesave+"\\"+titlex+'.flv'
        )
        self.avc.signaly.connect(self.complete)
        self.avc.start()
    def complete(self,intt):
        self.ui.scrollAreaWidgetContents.findChildren(QPushButton)[intt].setText('完成')
    # def deleteall(self):
    #     self.ui.deleteALL()



    def smallerp(self):
        self.picitem.setScale(self.picitem.scale()-0.1)


    def bigp(self):
        self.picitem.setScale(self.picitem.scale()+0.1)


    def rotationp(self,intt):
        degree = intt*180//99
        if degree > 90:
            self.picitem.setRotation(degree-180)
        else:
            self.picitem.setRotation(+degree)
    

    def downloadp(self):
        formatp = self.pic.split('.')[-1]
        filename = self.ui.filesave + "/" + self.title[0] + '.'+formatp
        self.picd = pdownload(self.pic, filename)
        self.picd.start()


    def combinev(self):
        textp = self.ui.plainTextEdit_4.toPlainText()
        if not textp:
            return None
        self.ui.pBcombine.setEnabled(False)
        self.ui.pBcombine.setText('合并中...')
        tt = textp.split('\n')[0]
        _, formatp = path.splitext(tt)
        basep = path.dirname(tt)
        self.uv = Combinev(textp, basep, formatp)
        self.uv.signac.connect(self.cconvert)
        self.uv.start()
    def cconvert(self):
        self.ui.pBcombine.setEnabled(True)
        self.ui.pBcombine.setText('开始')
    def openf(self):
        if (sender := self.sender()) == self.ui.tBopen2:
            filename, _ = QFileDialog.getOpenFileName(self, "打开文件", './', "Video(*.mp4 *.flv *mkv *mpeg)")
            ff = filename.strip()
            self.ui.label_10.setText(ff)
        elif sender == self.ui.toolButton:
            filename, _ = QFileDialog.getOpenFileName(self, "打开文件", './', "Video(*.mp4 *.flv *mkv *mpeg)")
            ff = filename.strip()
            self.ui.label_8.setText(ff)
        elif sender == self.ui.tBopen1:
            filename, _ = QFileDialog.getOpenFileName(self, "打开文件", './', "danmu(*.xml)")
            ff = filename.strip()
            self.ui.lEdanmu.setText(ff)
        elif sender == self.ui.toolButton_2:
            filename, _ = QFileDialog.getOpenFileName(self, "打开文件", './', "Video(*.mp4 *.flv *mkv *mpeg)")
            ff = filename.strip()
            self.ui.label_22.setText(ff)
    def cutst(self):
        ff = self.ui.label_10.text().strip()
        if not ff:
            return None
        _, formatp = path.splitext(ff)
        starttime = Tconvert(self.ui.lineEdit_3.text())
        endtime = Tconvert(self.ui.lineEdit_2.text())
        self.mycut = cutv(ff, starttime, endtime, formatp)
        self.mycut.start()
    def convertto(self):
        ff = self.ui.label_8.text().strip()
        if not ff:
            return None
        self.ui.convertpbButton.setEnabled(False)
        self.ui.convertpbButton.setText('转码中..')
        filepath = path.dirname(ff)
        toformat = self.ui.comboBox.currentText()
        fileout = filepath + '/' + f'output.{toformat}'
        self.myconv = conv(ff,fileout)
        self.myconv.signcv.connect(self.convertcomplete)
        self.myconv.start()
    def convertcomplete(self):
        self.ui.convertpbButton.setEnabled(True)
        self.ui.convertpbButton.setText('转码')
    def prettifydanmu(self):
        filename = self.ui.lEdanmu.text()
        basep, _ = path.splitext(filename)
        outfile = basep + '.ass'
        fontsize = self.ui.sBfontsize.value()
        font = self.ui.cBfont.currentText()
        sizewh = self.ui.lEsize.text().split('x')
        danmupacity = self.ui.dsBopacity.value()
        velocity = self.ui.sBvelocity.value()
        still = self.ui.sBstill.value()
        danmufilter = self.ui.pTEreg.toPlainText()
        self.danmup = danmupre(filename, outfile, fontsize, font, sizewh, danmupacity, velocity, still, danmufilter)
        self.danmup.start()
    
    def gifdo(self):
        filename = self.ui.label_22.text().strip()
        if not filename:
            return None
        starttime = Tconvert(self.ui.lineEdit_6.text())
        endtime = Tconvert(self.ui.lineEdit_7.text())
        resize = self.ui.lineEdit_5.text()
        framerate = self.ui.spinBox.value()
        self.gi = gifto(filename, starttime, endtime, resize, framerate)
        self.gi.start()
    def danmutov(self):
        self.ui.pBbegin.setEnabled(False)
        self.ui.pBbegin.setText('进行中...')
        fl = self.ui.pTEfile.toPlainText().split('\n')
        if fl[0].split('.')[-1] in ['ass','srt']:
            filename1 = fl[0]
            filename2 = fl[1]
        else:
            filename1 = fl[1]
            filename2 = fl[0]
        self.sl = danmutovideo(filename1, filename2)
        self.sl.signald.connect(self.danmucp)
        self.sl.start()
    def danmucp(self):
        self.ui.pBbegin.setEnabled(True)
        self.ui.pBbegin.setText('烧录')
    def dkoudai(self):
        self.timer1 = QtCore.QTimer()
        self.timer1.stop()
        self.timer1.setInterval(1000)
        self.timer1.timeout.connect(self.putprogressbar1)
        if not self.ui.newLE.text():
            url = self.ui.myclipboard.text()
            self.ui.newLE.setText(url)
        else:
            url = self.ui.newLE.text().strip()
        self.timer1.start()
        self.ui.newPG.setMaximum(0)
        self.kou = koudaigo(url)
        self.kou.start()
    def putprogressbar1(self):
        if not DownLoad_M3U8.ck:
            pass
        else:
            total = DownLoad_M3U8.ck[0]
            lc = len(DownLoad_M3U8.koudaicc)
            self.ui.newPG.setMaximum(100)
            self.ui.newPG.setValue(100*lc//total)
            if lc == total:
                self.timer1.stop()
                DownLoad_M3U8.ck = []
                DownLoad_M3U8.koudaicc = []
                DownLoad_M3U8.Counts = 0
                self.ui.newLE.clear()
                self.ui.newPG.setValue(0)

class koudaigo(QtCore.QThread):
    signald = QtCore.pyqtSignal()
    def __init__(self, url):
        super(koudaigo, self).__init__()
        self.url = url
    def run(self):
        MakeDir('./temp')
        DownLoad_M3U8(self.url).begin()

class danmutovideo(QtCore.QThread):
    signald = QtCore.pyqtSignal()
    def __init__(self, filename1, filename2):
        super(danmutovideo, self).__init__()
        self.file1 = filename1
        self.file2 = filename2
    def run(self):
        basep, vft = path.splitext(self.file2)
        _, danmuft = path.splitext(self.file1)
        copyfile(self.file1, f'./tempf{danmuft}')
        copyfile(self.file2, f'./tempf{vft}')
        t = f'tempfout{vft}'
        basep = basep.split('/')[-1]
        if danmuft == '.ass':
            cmd(['ffmpeg', '-i', f'tempf{vft}', '-vf', f'ass=tempf{danmuft}', '-vcodec', 'libx264', '-acodec', 'copy', '-y',t])
        else:
            cmd(['ffmpeg', '-i', f'tempf{vft}', '-vf',f"subtitles=tempf{danmuft}:force_style='Fontsize=11'", '-y',t])
        self.signald.emit()
        remove(f'./tempf{danmuft}')
        remove(f'./tempf{vft}')
        rename(t, f'{basep}{vft}')

        # ffmpeg -i 1.flv -vf ass=1.ass -vcodec libx264 -acodec copy 2.flv
class danmupre(QtCore.QThread):
    def __init__(self, filename, outfile, fontsize, font, sizewh, danmupacity, velocity, still, danmufilter):
        super(danmupre, self).__init__()
        self.filename = filename
        self.outfile = outfile
        self.fz = fontsize
        self.ft = font
        self.sz = sizewh
        self.py = danmupacity
        self.v = velocity
        self.s = still
        self.fr = danmufilter
    def run(self):
        if not self.fr:
            self.fr = None
        import XmlToAss
        XmlToAss.Danmaku2ASS(self.filename,
        'autodetect', self.outfile, int(self.sz[0]), int(self.sz[1]),
        font_face=self.ft,text_opacity=self.py,font_size=float(self.fz),duration_marquee=float(self.v), duration_still=float(self.s),
        comment_filter=self.fr)
class downloadThread(QtCore.QThread):
    signalx = QtCore.pyqtSignal(str)
    def __init__(self, url, title, threadnum, save_file, rec_file, index,cid):
        super(downloadThread, self).__init__()
        self.url = url
        self.title = title
        self.threadnum = threadnum
        self.save_file = save_file
        self.index = index
        self.rec = rec_file
        self.cid = cid
    def run(self):
        download(self.url,self.title,self.threadnum,self.save_file, self.rec, self.index,self.cid).newORold()

class ThreadCombine(QtCore.QThread):
    signaly = QtCore.pyqtSignal(int)
    def __init__(self,index,filename1,filename2,filename3,**KWARGS):
        super().__init__(**KWARGS)
        self.filename1=filename1
        self.filename2=filename2
        self.filename3=filename3
        self.sign = index
    def run(self):
        cmd(['ffmpeg','-i',self.filename1,'-i',self.filename2,
            '-map' ,'0:v', '-map' ,'1:a' ,'-c:a', 'copy' ,'-c:v', 'copy','-y',self.filename3,'-loglevel', 'quiet'])
        self.signaly.emit(int(self.sign))
class gifto(QtCore.QThread):
    def __init__(self, filename, starttime, endtime, resize, framerate):
        super().__init__()
        self.fn = filename
        self.st = starttime
        self.et = endtime
        self.re = resize
        self.ft = framerate
    def run(self):
        filen, _ = path.splitext(self.fn)
        outf = filen+'.gif'
        realf = self.fn.replace('/', '\\\\')
        realout = outf.replace('/', '\\\\')
        cmd(['ffmpeg', '-ss', self.st, '-i', realf, '-t', self.et, '-s', self.re, '-r', str(self.ft), '-y',realout])
class conv(QtCore.QThread):
    signcv = QtCore.pyqtSignal()
    def __init__(self, inputf, outputf):
        super().__init__()
        self.input1 = inputf.replace('/', '\\\\')
        self.output = outputf.replace('/', '\\\\')
        self.formatv = outputf.split('.')[-1]
    def run(self):
        cmd(['ffmpeg', '-i', self.input1, '-y', self.output])
        self.signcv.emit()
def Tconvert(string):
    if not '.' in string:
        return string
    else:
        aa = string.split('.')
        ab = []
        for i in aa:
            ab.append(i.rjust(2, '0'))
        return ':'.join(ab)
class cutv(QtCore.QThread):
    def __init__(self, filename, x, y, z):
        super().__init__()
        self.filename = filename.replace('/', '\\\\')
        self.x = x
        self.y = y
        filepath = path.dirname(filename)+'/'+f'cut{z}'
        self.filepath = filepath.replace('/', '\\\\')
    def run(self):
        cmd(['ffmpeg', '-ss', self.x, '-i', self.filename, '-to', self.y, '-c', 'copy', '-copyts', '-y', self.filepath])

class Combinev(QtCore.QThread):
    signac = QtCore.pyqtSignal()
    def __init__(self,filetext, outpath, formatp):
        super().__init__()
        self.filetext = 'file ' + filetext.replace('\n', '\nfile ')
        self.txtp = outpath + '/' + 'ifo.txt'
        self.txtp = self.txtp.replace('/',"\\\\")
        self.outfile = outpath + '/' + f'combine{formatp}'
        self.outfile = self.outfile.replace('/',"\\\\")
    def run(self):
        with open(self.txtp, 'w') as f:
            f.write(self.filetext)
        cmd(['ffmpeg','-f','concat','-safe','0','-i',self.txtp,'-c','copy','-y',self.outfile])
        self.signac.emit()

class Combinev1(QtCore.QThread):
    signac1 = QtCore.pyqtSignal(int)
    def __init__(self,filetext, outpath, formatp,intt):
        super().__init__()
        self.filetext = 'file ' + filetext.replace('\n', '\nfile ')
        self.txtp = outpath + '/' + 'ifo.txt'
        self.txtp = self.txtp.replace('/',"\\\\")
        self.outfile = outpath + '/' + f'combine{formatp}'
        self.outfile = self.outfile.replace('/',"\\\\")
        self.intt = intt
    def run(self):
        with open(self.txtp, 'w') as f:
            f.write(self.filetext)
        cmd(['ffmpeg','-f','concat','-safe','0','-i',self.txtp,'-c','copy', '-y', self.outfile])
        self.signac1.emit(self.intt)

class pdownload(QtCore.QThread):
    def __init__(self, url, filename, **KWARGS):
        super().__init__(**KWARGS)
        self.url = url
        self.filename = filename
    def run(self):
        data = Go(self.url, default_headers).content
        with open(self.filename, 'wb') as fileob:
            fileob.write(data)

class downloadASS(QtCore.QThread):
    def __init__(self, cid, filepath, xx, yy, **KWARGS):
        super().__init__(**KWARGS)
        self.cid = cid
        self.filepath = filepath
        self.wt = int(xx)
        self.ht = int(yy)
    def run(self):
        URL = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(self.cid)
        data = Go(URL, default_headers).content
        with open(self.filepath + '.xml', 'wb') as fileob:
            fileob.write(data)
        import XmlToAss
        XmlToAss.Danmaku2ASS(self.filepath + '.xml',
        'autodetect', self.filepath + '.ass', self.wt, self.ht, font_size=float(45), font_face="simsunb", text_opacity=0.8, duration_marquee=float(6))  
class downloadXML(QtCore.QThread):
    def __init__(self, cid, filepath, **KWARGS):
        super().__init__(**KWARGS)
        self.cid = cid
        self.filepath = filepath
    def run(self):
        URL = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(self.cid)
        data = Go(URL, default_headers).content
        with open(self.filepath + '.xml', 'wb') as fileob:
            fileob.write(data)
QApplication.setStyle(QStyleFactory.create('fusion'))
app = QApplication([])
downloadwindow = myui()
downloadwindow.show()
sys.exit(app.exec_())
