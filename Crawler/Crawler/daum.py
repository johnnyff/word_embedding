from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

import pyperclip

#import pyautogui

import pandas as pd
#import chromedriver_autoinstaller

import urllib
from bs4 import BeautifulSoup
import cfscrape
import re, time
import datetime 
from multiprocessing import Lock
from storage_handler import StorageHandler
from scraper import Scraper

import requests, argparse, json
import lxml.html
import io
from tqdm import tqdm

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser


####youtube live 스트리밍 
import sys
import pyperclip

import random


import uuid
import rsa
import lzstring
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from file_handler import FileHandler


class CrawlingHandler :
    def __init__(self):
        self.lock = Lock()
        self.sh = StorageHandler()
        self.scraper = cfscrape.create_scraper()
        self.browser_scraper = Scraper()
    def quote(self, text): return urllib.parse.quote(text) #한글 텍스트를 퍼센트 인코딩하기
    def progressBar(self,value, endvalue,bar_length=60):
        percent = float(value) / endvalue
        arrow = '-' * int(round(percent * bar_length)-1) + '>'
        spaces = ' ' * (bar_length - len(arrow))
        sys.stdout.write("\rCalculating practice: [{0}] {1}%  ".format(arrow + spaces, int(round(percent * 100)), ))
    def getResponse(self, address):
        for i in range(0, 100):
            try:
                response = self.scraper.get(address)
            except :
                time.sleep(1)
                continue
            return response
        return None
    def parseContents(self, contents):
        contents = contents.replace('\r','').replace('\t',' ').replace('#','')
        contents = re.sub('[ ]+',' ',contents)
        split = contents.split('\n')
        contents = ' '
        for temp in split:
            contents += temp.strip()+'\n'
        contents = re.sub('^[\n]+|[\n]+$', '', contents)
        contents = re.sub('([ ]?[\n][ ]?){2,}', '\n\n', contents)

        contents = re.sub('[a-zA-Z\-_.]+[ ]?=[ ]?[a-zA-Z\-_.]+[ ][|]+[ ][(){}\[\] ]+;[\n]?', '', contents)
        contents = re.sub('[a-zA-Z\-_.]+[\[({]+[\n]?', '', contents)
        contents = re.sub('[a-zA-Z\-_.]+[ ]?:[ ]?[a-zA-Z\-_.\' ]+[,]?[\n]?', '', contents)
        contents = re.sub('[)}\]]+;[\n]?', '', contents)
        contents = re.sub('^[\n]+|[\n]+$', '', contents)

        return contents
            
    def daum_list_crawling(self,keyword):
        docs = []
        query = self.quote(keyword)
        page =77
        had_url = self.sh.loadURL('daum',keyword)
        #https://search.daum.net/search?w=cafe&DA=PGD&q= keyword &sort=accuracy&ASearchType=1&lpp=10&rlang=0&req=cafe&p=1 
        # 이전 페이지의 첫번째 url이 지금 url과 같다면 새로운 페이지가 생기지 않은 것
        before_url = ""
        while_flag = True
        while while_flag:
            if page > 100: break
            search_url = 'https://search.daum.net/search?w=cafe&DA=PGD&q='+query+'&sort=accuracy&ASearchType=1&lpp=10&rlang=0&req=cafe&p='+str(page)
            response = self.getResponse(search_url)
            flag = True
            if not response : return
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            try:
                ul = soup.find("ul",{"id":"cafeResultUL"})
                
            except:
                
                page+=1
                continue
            try:
                lis = ul.find_all("li")
            except Exception as e:
                page+=1
                pass
            try:
                for li in lis:
                    wrap_cont = li.find("div",{"class":"wrap_cont"})
                    cont_inner = wrap_cont.find("div",{"class":"cont_inner"})
                    wrap_tit = cont_inner.find("div",{"class":"wrap_tit mg_tit"})
                    a = wrap_tit.find("a",{"class":"f_link_b"})
                    url = a['href']
                    if url in had_url:
                        continue
                    else:
                        had_url.append(url)
                    title = a.text
                    docs.append([url,title])
                if len(lis) <10:
                    break
            except:
                print("Daum err lis")
                
                pass
            page+=1
        print("total page : "+str(page))
        return docs
    def daum_doc_crawling(self,document):
        # document[0] 에 url저장되어있음
        # webdriver로 페이지 열고
        # window.commentPaging.getCommentList(str(page));
        # div class="comment_view"  가 없다면 댓글 없는 것
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        driver.get(document[0])
        author = ""
        time = ""
        
        #댓글 중에선, li의 data-is-hidden arrtibute 가 false인 것만 찾으면됨
        page = 1
        #driver.execute_script("document.getElementById('topLayerQueryInput').value =\'"+keyword+"\'")
        try:
            element = WebDriverWait(driver,2).until(
                        EC.presence_of_element_located((By.ID,"down"))
                    )
        except: print("no down"+document[0]); return document
        driver.switch_to.frame("down")
        source = driver.page_source
        if not source : return document
        soup = BeautifulSoup(source,"lxml")
        try:
            read=soup.find("div",{"class":"search_read_area"})
            
        except:
            print("read")
        try:
            bbs = read.find("div",{"class":"bbs_read_tit"})
            
        except:
            print("bbs")
        try:
            info_desc = bbs.find("div",{"class":"info_desc"})
        except:
            print("infodesc")
            return
        try:
            coverinfo = info_desc.find("div",{"class":"cover_info"})
        except:
            print("no info about author and time")
        try:
            author = coverinfo.find("a").text
            
        except:
            print("no info about author")
        try:
            time = coverinfo.find_all("span")
            time = '20'+(time[2].text).replace('.','-')
            
            
        except:
            print("no info about time")
        
        comment = " "
        while_flag = True
        while while_flag:
            driver.execute_script("window.commentPaging.getCommentList("+str(page)+")")
            element = WebDriverWait(driver,2).until(
                        EC.presence_of_element_located((By.ID,"comment-list"))
                    )
            source = driver.page_source
            if not source : break
            soup = BeautifulSoup(source,"lxml")
            try:
                comment_list = soup.find("div",{"id":"comment-list"})
            except:
                print("error on comment_list")
                while_flag = False
                break
            try:
                comment_ul = comment_list.find("ul")
            except:
                print("no comment ever")
                while_flag = False
                break
            try:
                lis = comment_ul.find_all("li",{"data-is-hidden":"false"})
                if len(lis)<=1:
                    while_flag= False
                    break
            except:
                print("error on li")
                while_flag = False
                break
            for li in lis:
                try:
                    comment_section = li.find("div",{"class":"comment_section"})
                except:
                    print("error on comment_section")
                    while_flag = False
                    break
                try:
                    comment_info = comment_section.find("div",{"class":"comment_info"})
                except:
                    print("error on comment_info")
                    while_flag = False
                    break
                try:
                    comment_post = comment_info.find("div",{"class":"comment_post"})
                except:
                    print("error on comment_post")
                    while_flag = False
                    break
                try:
                    box_post= comment_post.find("div",{"class":"box_post"})
                except:
                    print("error on box_post")
                    while_flag = False
                    break
                try:
                    p = box_post.find("p")
                except:
                    print("error on p")
                    while_flag = False
                    break
                try:
                    text = p.find("span").text
                    
                    comment+=text
                except:
                    print("error on span")
                    while_flag = False
                    break
            page+=1
        contents = self.parseContents(comment)
        document+=[time,author,contents]
        driver.close()
        return document # [url,title,time,author,contents]
    def daum_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.daum_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.saveDaumDoc(keyword, document)
    #            else:
    #                print('Error occur from hygall site : '+doc[0])
        return