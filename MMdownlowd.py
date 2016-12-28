import urllib.request
import os
import sys
import re
import time


#import traceback
#import sys 
ISOTIMEFORMAT='%Y-%m-%d %X'

def openurl(url):  #打开连接，隐藏和代理
    req = urllib.request.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
    response = urllib.request.urlopen(req)
    html = response.read()
    return html


def removeIllegalChars(filename): #处理文件名中不合法字符  \ / ? : * " > < |
	pattern = r'[\]\[\\/\?:\*"><\|]*'
	return re.sub(pattern,"",filename)

    

def get_AllMMUrl(html):   #获取当页所有MM板块的链接

    pattern = re.compile(r'a href="(http:\/\/www.mzitu.com\/[\d]+)" target')
    imgurllist = re.findall(pattern,html)
    imgurllist = set(imgurllist)


    return imgurllist


def MMpagefile_num(html2):  #获取该网址共多少页MM图片
    try:
        p3 = re.compile(r'<span>(\d+)</span>')
        MM_pagenum = re.findall(p3,html2) 
        #print('共有',MM_pagenum[-1])
    except:
        return 0
    return MM_pagenum[-1]


def get_MMname(eachmmurl):  #获取单个MM的图片集主题名，用以分类存放MM图片集

    mmhtml = openurl(eachmmurl).decode('utf-8')
    p1 = re.compile(r'h2 class="main-title">(.*?)</h2>')
    MM_name = re.findall(p1,mmhtml) #获取MM主题名
    
    p2 = re.compile(r'<span>(\d+)</span>')
    MM_num = re.findall(p2,mmhtml) #获取该主题共多少张MM图片
    #print('总共you美女',MM_num[-1],'张')

        
    return MM_name,MM_num[-1]

def downlowd_MMname_imgs(eachmmurl,pages=1):  #下载MM图
    #print(eachmmurl)
    #input("暂停...")
    #
    try:
        for page in range(1,int(pages)+1):
            everypageurl = eachmmurl+'/'+str(page)
            everypagehtml = openurl(everypageurl).decode('utf-8')
            #print(everypagehtml)
            pp = re.compile(r'img src="([^"]+\.jpg)" alt=')
            MM = re.findall(pp,everypagehtml) #通过正则，得到MM图片的名字用来保存
            time.sleep(0.2)
            #print(MM)
            #input('执行到这里')

            try:
                MM = MM[-1]
                filename = MM.split('/')[-1]
                #print(filename)
                #input('执行到这里')
                urllib.request.urlretrieve(MM,filename,None)
            except:
                pass
    except:
        pass
    #return 

def MMdownlowd(folder='XXOO'):

    #建立OOXX文件夹存储所有将要下载的图片

    os.mkdir(folder)
    os.chdir(folder)
    localpath = os.getcwd()
    
    url = 'http://www.mzitu.com/page/1'
    Main_html = openurl(url).decode('utf-8') #获取主页
    #print(Main_html)
    MMpagefilenums = MMpagefile_num(Main_html) #得到主站共多少页MM链接
    print('发现【',MMpagefilenums,'】页,开始下载')
    #pag = int(input("从第几页【1-%s】开始下载?" % MMpagefilenums))
    
    for pagefile in range(1,int(MMpagefilenums)):
        
        localtime = time.strftime(ISOTIMEFORMAT,time.localtime())
        print("########################### %s ###############################" % localtime)
        print('第',pagefile,'页')
        Main_htmlnew = 'http://www.mzitu.com/page/' + str(pagefile)
        htmlnew = openurl(Main_htmlnew).decode('utf-8')
        
        #print(htmlnew)
        
        MMurldict = get_AllMMUrl(htmlnew) #得到当页所有MM板块的链接字典
        
        for thispageMMurllist in MMurldict:
            ##
            #for eachMMurl in thispageMMurllist: #从链接字典中获取获取单个MM主题链接
                #print(eachMMurl)
                
                
            MMname,MMnum= get_MMname(thispageMMurllist) #从单个链接中得到MM标题名字和张数
            #print(MMname,MMnum)
            ##
            MMnamenow = removeIllegalChars(MMname[0])
            print(MMnamenow,MMnum+"张")
            
            try:
                os.mkdir(MMnamenow)
                os.chdir(MMnamenow)
                #input('.....')
                downlowd_MMname_imgs(thispageMMurllist,MMnum)
                os.chdir(localpath)
            except:
                #pass
                os.chdir(localpath)


    print("下载完毕！有人执行到这里么.....")
    print(time.strftime(ISOTIMEFORMAT,time.localtime()))


if __name__ == '__main__':
    os.system('call F:\\妹子图实验基地\\delOOXX.bat')
    
    MMdownlowd()
