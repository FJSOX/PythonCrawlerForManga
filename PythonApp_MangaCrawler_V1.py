#__author__='FJSOX'
#__date__='2020-10-15'
#爬取https://m.acgzone.net/上的漫画，自动爬取所选章节的漫画并存入本地电脑。
import re
import requests
from lxml import etree
import os
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time


#目录页面链接
url="https://m.acgzone.net/manhua/woliyubaiwanshengmingzhishang/"

class CRAWLER():
    def __init__(self, *args, **kwargs):
        #初始目录
        self.path="D:\\mydir\\Manga"
        self.chapternum=0#用于记录章节数
        self.biglist=[]#用于存放所需下载章节的地址列表

    
    #获取各个章节的url
    def getChapterUrlList(self,url):
        req=requests.get(url)
        selector=etree.HTML(req.text)
        #print(req.text)

        #获取章节url list
        getlist=selector.xpath("/html/body/div[1]/div[1]/div[5]/div[2]/div[2]/div/ul//a[@href and @class]/@href")
                               #/html/body/div[1]/div[1]/div[5]/div[1]  正常漫画此处取div[1]
        #将章节url转换为str放入urllist并计算章节数
        i=0
        urllist=[]
        for urlx in getlist:
            urllist.append(str(urlx))
            #f.write(str(urlx)+"\n")
            i=i+1

        #打开ChapterUrlList记录文件
        f=open(self.path+"\\ChapterUrlList.txt", "w+")
        #将每个url末尾加上换行符
        f.writelines(url+"\n" for url in urllist)
        #关闭文件
        f.close()

        #输出章节数
        print("章节数={0}".format(i))
        self.chapternum=i

        return urllist


    #创建漫画目录
    def makeDir(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)


    #获取所有图片的下载链接
    def getImgUrlList(self,chapterlist,beginnum,endnum):
        # 设置chrome为无界面浏览器
        options = Options()
        options.add_argument('--headless')
 
        # 打开浏览器
        browser = webdriver.Firefox(options=options)

        #biglist=[]

        #遍历所选章节列表
        for i in range(beginnum, endnum+1):
            chapterpath=self.path+"\\Chapter{}".format(i)
            #构建章节目录
            if not os.path.exists(chapterpath):
                os.mkdir(chapterpath)

            #记录图片链接
            f=open(chapterpath+"\\ImgUrlList.txt","w+")

            pageurllist=[]#图片链接列表
            pagenum=-101#总页数
            j=1#当前页
            while j!=pagenum+1 and j<100:
                url = chapterlist[i-1]+"-{}".format(j)+".html"
                # 利用get请求请求浏览器的一个网页
                browser.get(url=url)
                browser.implicitly_wait(1.5) #隐式等待，设置等待时长1.5秒

                if j==1:
                    #获取当前章节页数
                    string1=browser.find_elements_by_xpath("/html/body/div[1]/div[3]/div/a[2]/div/p")
                    string2=string1[0].text
                    pagenumstr=re.match(r'(.*)/(.*)',string2).group(2)
                    pagenum=int(pagenumstr)
   
                img=browser.find_elements_by_xpath("/html/body/div[1]/div[3]/div/a[2]/div/img")#定位到img
                src=img[0].get_property("src")#获取src属性
                pageurllist.append(src)
                f.write(src+"\n")
                print("Get {},{}".format(i,j))
                with open("D:\\mydir\\Manga\\log.txt","a+") as log:
                    localtime = time.asctime(time.localtime(time.time()))
                    log.write("\tGet {},{}: ".format(i,j)+localtime)

                j=j+1

            #print(page+"\n" for page in pageurllist)
            #将下载连接所在目录放入biglist
            self.biglist.append(chapterpath)
            
            f.close()
            with open("D:\\mydir\\Manga\\log.txt","a+") as log:
                    localtime = time.asctime(time.localtime(time.time()))
                    log.write("{}-OK: ".format(i)+localtime)

        # 关闭浏览器
        browser.close()
 
        # 杀死chrome浏览器的连接桥(chromedriver)的进程
        browser.quit()

        return self.biglist


    #下载图片
    #def downloadImg(self,biglist,beginnum,endnum):
    #    for i in range(beginnum,endnum+1):
    #        chapterlist=biglist[i-beginnum]
    #        for j in range(len(chapterlist)):
    #            f=open(self.path+"\\Chapter{}\\img{}.jpg".format(i,j+1),"wb")
    #            f.write(requests.get(chapterlist[j]).content)
    #            f.close()
    #            print("第{}章第{}张图片下载完成...".format(i,j))

    #下载图片
    def downloadImg(self):
        #获取下载路径，按章节读取
        for path in self.biglist:
            chapterid=re.search(r"\d+",path).group(0)#章节id
            with open(path+"\\ImgUrlList.txt","r") as f:
                i=1
                while True:
                    url=f.readline()

                    #读取结束时退出
                    if url=="":
                        break
                    #写入jpg格式的图片
                    with open(path+"\\img{}.jpg".format(i),"wb") as img:
                        img.write(requests.get(url.strip()).content)
                        print("Get img {},{}".format(chapterid,i))
                        i=i+1

            print("第{}章下载完成！".format(chapterid))


    def Main(self):
        self.makeDir()
        chapterlist=self.getChapterUrlList(url)
        beginnum=int(input("请输入你想要下载的起始章节:"))
        endnum=int(input("请输入你想要下载到的章节:"))
        self.getImgUrlList(chapterlist,beginnum,endnum)
        self.downloadImg()
            
cra=CRAWLER()
cra.Main()