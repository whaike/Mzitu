#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-16 23:30:11
# Project: meizitu

from pyspider.libs.base_handler import *
import urllib
from lxml import etree
import os
import re
import MySQLdb

class Handler(BaseHandler):
    crawl_config = {
    }
    
    def __init__(self):
        self.start_url = 'http://www.mzitu.com/page/'
        self.page_num = 1 #指定从那一页开始获取
        self.page_nums = 134 #指定获取多少页妹子图
        self.mm_view = 1000000 #选择美女的阅读量 大于100万人次
        self.db_host = "localhost" #数据库地址，不可修改
        self.db = "meizitu" #数据库名，不可修改
        self.db_name = "mmImages" #数据表明，可以修改
        self.db_user = "root" #数据库用户名
        self.db_passwd = "******" #数据库密码
        

        
    @every(minutes=24 * 60)
    def on_start(self):
        self.propMySQL()
        for page in range(self.page_num,self.page_nums+1,1):
            url = self.start_url + str(page)
            self.crawl(url, callback=self.index_page,validate_cert = False)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        #print response.url
        for each in response.doc('#pins li').items():
            #获取美女阅读量
            views = ("".join(each.css('span.view').text().split(" ")[-1].split(",")))[:-1]
            if int(views) >= self.mm_view:
                #print each("a").attr.href
                #如果阅读量大于指定的人数则爬取图片，否则跳过
                self.crawl(each("a").attr.href, callback=self.detail_page,validate_cert = False)


    @config(priority=2)
    def detail_page(self, response):
        mmurl = response.url
        print mmurl
        
        x = response.etree
        #获取每一个美女的名字
        #folders = x.xpath('//h2[@class="main-title"]/text()')[0]
        #folder = self.removeIllegalChars(folders)
        #print folder
        
        #获取每一个美女有多少张图片
        mmspage = x.xpath('//div[@class="pagenavi"]/a[last()-1]/span/text()')[0]
        print mmspage
        
        for i in range(1,int(mmspage)+1,1):
            mmImgUrl = mmurl+'/'+str(i)
            self.crawl(mmImgUrl,callback=self.getImg,validate_cert = False)
            #,save={"folder":folder}
        
    def getImg(self,response):
        #folderr = response.save["folder"]
        str = response.etree
        #获取每一张图片的地址
        fileurl = str.xpath('//div[@class="main-image"]/p/a/img/@src')[0]
        filepostfix = fileurl.split('.')[-1] #后缀
        filen = fileurl.split('.')[-2].split('/')[-1]
        usefolder = 'E:\\Python\\spiders\\'
        #self.mkdir(usefolder)
        filename = usefolder+"\\"+ filen + '.'+ filepostfix
        print filename
        data = urllib.urlopen(fileurl).read()
        f = open(filename,'wb')
        f.write(data)
        print filename+'  is OK'
        f.close()
        self.fileToMysql(fileurl,data)#写入数据库
        
    
        
    def mkdir(self,path):
        path = path.strip()
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            print u"名为",path,'的文件夹已经创建成功'
            return False
        
    def removeIllegalChars(self,filename): #处理文件名中不合法字符  \ / ? : * " > < |
        pattern = r'[\]\[\\/\?:\*"><\|]*'
        return re.sub(pattern,"",filename)
    
    #将图片存入数据库
    def fileToMysql(self,url,data):
        conn = MySQLdb.connect(host=self.db_host,user=self.db_user,passwd=self.db_passwd,db=self.db)
        cur = conn.cursor()
        try:
            #sql = "insert into "+self.db_name+"(urls,images) values("+url+","+data+")"
            sql = 'insert into %s(url,image) values("%s","%s")' % (self.db_name,url,MySQLdb.escape_string(data))
            print sql
            cur.execute(sql)
            conn.commit()
            print "数据写入"
        except Exception,e:
            print e
            
        #读取数据为图片    
        #cur.execute("select image from mmImages limit 1")
        #fout = open('E:\\image.jpg','wb')
        #fout.write(cur.fetchone()[0])
        #fout.close()
        
        cur.close()
        conn.close()
        print "本次完毕"
        

        
    #创建数据表，如果已经存在则先删除后再创建!
    def propMySQL(self):
        conn = MySQLdb.connect(host=self.db_host,user=self.db_user,passwd=self.db_passwd,db=self.db)
        cur = conn.cursor()
        cur.execute("show tables")
        data = cur.fetchone()
        if data:
            print data[0]+"数据表已经创建,准备删除..."
            sql = "drop table if exists "+ data[0]
            try:
                cur.execute(sql)
                conn.commit()
                print data[0] + "数据表已经删除"
                sql = "create table if not exists "+self.db_name+" (id int unsigned not null primary key auto_increment,url varchar(300),image MEDIUMBLOB)"
                try:
                    cur.execute(sql)
                    conn.commit()
                    print "新数据表 "+self.db_name+" 创建成功"
                except Excetion,e:
                    print e
                    
            except Exception,e:
                print e
        else:
            sql = "create table if not exists "+self.db_name+" (id int unsigned not null primary key auto_increment,url varchar(200),image MEDIUMBLOB)"
            try:
                cur.execute(sql)
                conn.commit()
                print "新数据表 "+self.db_name+" 创建成功"
            except Excetion,e:
                print e
        
        cur.close()
        conn.close()