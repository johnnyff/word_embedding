#-*- coding: utf-8 -*-

# Developer : Jeong Wooyoung, EGLAB, Hongik University
# Contact   : gunyoung20@naver.com

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
import random
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
from multiprocessing import Pool

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

from multiprocessing import Process, Lock, Pool

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
#DEVELOPER_KEY = 'AIzaSyDSDBOFqqpM52K62zO04jHMRPb9dUKJuVc'


# AIzaSyDSDBOFqqpM52K62zO04jHMRPb9dUKJuVc
# AIzaSyC5ChTI9hmytxp-SWXA4PSpkj5qKnymzVU

# YOUTUBE_API_SERVICE_NAME = 'youtube'
# YOUTUBE_API_VERSION = 'v3'

# from lxml.cssselect import CSSSelector

# YOUTUBE_COMMENTS_URL = 'https://www.youtube.com/all_comments?v={youtube_id}'
# YOUTUBE_COMMENTS_AJAX_URL = 'https://www.youtube.com/comment_ajax'
# USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

#

def progressBar(value, endvalue,  bar_length=60):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rCalculating practice: [{0}] {1}% ".format(arrow + spaces, int(round(percent * 100)) ))
def find_value(html, key, num_chars=2):
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find('"', pos_begin)
    return html[pos_begin: pos_end]
def extract_comments(html):
    tree = lxml.html.fromstring(html)
    item_sel = CSSSelector('.comment-item')
    text_sel = CSSSelector('.comment-text-content')
    #text_sel = CSSSelector('.content-text')
    
    time_sel = CSSSelector('.time')
    author_sel = CSSSelector('.user-name')
#content-text
    for item in item_sel(tree):
        yield {'cid': item.get('data-cid'),
               'text': text_sel(item)[0].text_content(),
               'time': time_sel(item)[0].text_content().strip(),
               'author': author_sel(item)[0].text_content()}
def extract_reply_cids(html):
    tree = lxml.html.fromstring(html)
    sel = CSSSelector('.comment-replies-header > .load-comments')
    return [i.get('data-cid') for i in sel(tree)]
def ajax_request(session, url, params, data, retries=10, sleep=20):
    for _ in range(retries):
        response = session.post(url, params=params, data=data)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
            return response_dict.get('page_token', None), response_dict['html_content']
        else:
            time.sleep(sleep)
def contents_limit(contents):
    #limit_length = 131072
    limit_length = 20000
    contents = contents.replace('\n','.')
    temp = [ contents[i:i+limit_length] for i in range(0,len(contents),limit_length)]
    return temp
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
            contents += temp.strip()
        contents = re.sub('^[\n]+|[\n]+$', '', contents)
        contents = re.sub('([ ]?[\n][ ]?){2,}', '\n\n', contents)

        contents = re.sub('[a-zA-Z\-_.]+[ ]?=[ ]?[a-zA-Z\-_.]+[ ][|]+[ ][(){}\[\] ]+;[\n]?', '', contents)
        contents = re.sub('[a-zA-Z\-_.]+[\[({]+[\n]?', '', contents)
        contents = re.sub('[a-zA-Z\-_.]+[ ]?:[ ]?[a-zA-Z\-_.\' ]+[,]?[\n]?', '', contents)
        contents = re.sub('[)}\]]+;[\n]?', '', contents)
        contents = re.sub('^[\n]+|[\n]+$', '', contents)

        return contents
    '''
    def template_list_crawling(self,keyword):
       return docs [url,title]
    def template_doc_crawling(self,document):
       return document  [url,title,time,author,contents]
    def template_docs_crawling(self, process, keyword, docs):
        sys.stdout.flush()
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.template_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.savetemplateDoc(keyword, document)
#            else:
#                print('Error occur from template site : '+doc[0])
        return
    '''
    
    def navernews_list_crawling(self,keyword):
        docs = []
        query = self.quote(keyword)
        page =1
        had_url = self.sh.loadURL('navernews',keyword)
        had_contents = self.sh.loadContents('navernews',keyword)
        before_url = ""
        while_flag = True
        while while_flag:
            search_url = 'https://m.search.naver.com/search.naver?where=m_news&sm=mtb_pge&query='+query+'&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=81&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all&start='+str(page)
            response = self.getResponse(search_url)
            if not response : return
            ##sys.stdout.write(search_url)
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            author = ""
            
            try:
                ul = soup.find("ul",{"class":"list_news"})
                
            except:
  
                pass
            try:
                lis = ul.find_all("li")
            except:
                #print("error navernews lis")
                pass
            Flag = True
            for li in lis:
                try:
                    a = li.find("div",{"class":"news_wrap"}).find("a",{"class":"news_tit"})
                except:
                    continue
                try:
                    author = li.find("div",{"class":"news_wrap"}).find("div",{"class":"news_info"}).find("div",{"class":"info_group"}).find("a",{"class":"info press"}).text
                    
                    
                except Exception as e:
                    pass
                try:
                    temp = a['href'].split('https://')
                    temp = temp[1].split('/')
                    if temp[0] == 'm.news.naver.com':
                        #이것만 추가
                        url = a['href']
                        title = a.text
                        if Flag:
                            if url == before_url :
                                while_flag = False
                                break
                            Flag = False; before_url = url
                        if url in had_url: continue
                        else: had_url.append(url)
                        docs.append([url,title,author])
                except:    
                    continue
                    
                
                    
                    
            page+=15

        return docs #[url,title]
    def navernews_doc_crawling(self,document):
        search_url =  document[0]
        response = self.getResponse(search_url)
        if not response : return
        soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
        content = ""
        author = document[-1]
        time = ""
        try: 
            time = (soup.find("span",{"class":"media_end_head_info_datestamp_time _ARTICLE_DATE_TIME"}).text).replace('.','-')

        except Exception as e:
            pass
        try:
            contents = self.parseContents(soup.find("div",{"id":"dic_area"}).text)
            
        except:
            return document
        contents+= '/t'
        document[2] = time
        document += [author,contents]

        return document  #[url,title,time,author,contents]
    def navernews_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in tqdm(docs):
            document = self.navernews_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.saveNavernewsDoc(keyword, document)
#            else:
#                print('Error occur from template site : '+doc[0])
        return

    



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
                    title = a.text+'/t'
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
                    comment += "/t"
                except:
                    print("error on span")
                    while_flag = False
                    break
            page+=1
        contents = self.parseContents(comment)
        print("before document : ", document)
        document+=[time,author,contents]
        # document +=[contents]
        driver.close()
        return document # [url,title,time,author,contents]
    def daum_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in tqdm(docs):
            document = self.daum_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.saveDaumDoc(keyword, document)
#            else:
#                print('Error occur from hygall site : '+doc[0])
        return
   
    def naverblog_list_crawling(self,keyword):
        query = self.quote(keyword)
        docs = []
        page = 1
        had_url = self.sh.loadURL('naverblog', keyword)
        
        #google-chrome --remote-debugging-port=9222 --user-data-dir="~/workspace/test/knowledge_based_sentiment_analysis_community_crawler/ChromeProfile"
        chrome_options = webdriver.ChromeOptions()
        

        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--ignore-certificate-error")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        time.sleep(1)
        search_url = 'https://section.blog.naver.com/Search/Post.nhn?pageNo='+str(page)+'&rangeType=ALL&orderBy=sim&keyword='+query
        driver.get(search_url)
        urls = []
        page_cnt = 0
        handle = 0
        while True:
            #print(page)
            minipage = 1
            for minipage in range(1,8):
                comment = ""
                try:
                    if minipage ==1:
                        try:
                            element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,'//*[@id="content"]/section/div[2]/div[%s]/div/div[1]/div/a[1]' %(minipage))))
                        except Exception as e:
                            print("1st text none")
                            print(e)
                            continue
                        try:
                            btn = driver.find_element_by_xpath('//*[@id="content"]/section/div[2]/div[%s]/div/div[1]/div/a[1]' %(minipage))
                            url = btn.get_attribute('href')
                            #print(url)
                        except Exception as e:
                            print('btn url error')
                            print(e)
                            continue
                        if url in had_url: continue
                        had_url.append(url)
                        urls.append(url)
                    else:
                        # //*[@id="content"]/section/div[2]/div[2]/div/div[1]/div/a[1]
                        # //*[@id="content"]/section/div[2]/div[3]/div/div[1]/div/a[1]
                        try:
                            element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,'//*[@id="content"]/section/div[2]/div[%s]/div/div[1]/div/a[1]' %(minipage))))
                        except Exception as e:
                            print("2nd over text none")
                            print(e)
                            continue
                        try:
                            btn = driver.find_element_by_xpath('//*[@id="content"]/section/div[2]/div[%s]/div/div[1]/div/a[1]' %(minipage))
                            url = btn.get_attribute('href')
                            #print(url)
                        except Exception as e:
                            print('btn url error')
                            print(e)
                            continue
                        if url in had_url: continue
                        had_url.append(url)
                        urls.append(url)
                except Exception as e:
                    print(e)
                    break
            page+=1
            if page >20: break
            idx = page%10
            if idx!=1:
                if idx==0:
                    try:
                        driver.find_element_by_xpath('//*[@id="content"]/section/div[3]/span[10]/a').click()
                        page_cnt += 1
                    except Exception as e:
                        print(e)
                        break
                else:
                    try:
                        driver.find_element_by_xpath('//*[@id="content"]/section/div[3]/span[{}]/a'.format(str(idx))).click()
                        page_cnt += 1
                    except Exception as e:
                        print(e)
                        break  
            elif page == 11:
                try:
                    driver.find_element_by_xpath('//*[@id="content"]/section/div[3]/a').click() 
                    page_cnt += 1
                except Exception as e:
                    print(e)
                    break
            elif idx == 1:
                try:
                    driver.find_element_by_xpath('//*[@id="content"]/section/div[3]/a[2]').click()
                    page_cnt += 1
                except Exception as e:
                    print(e)
                    break
        total_url = len(urls)
        doc_cnt = 0
        print("crawling document : %d" %total_url)
        for url in tqdm(urls):
            if page_cnt == 500 :
            #driver.execute_script('window.open("https://naver.com");')
                handle +=1
                time.sleep(random.random())
                            #driver.close()
                driver.switch_to_window(driver.window_handles[handle%5])
                time.sleep(random.random())
                page_cnt = 0
            driver.get(url)
            
            page_cnt += 1
            time.sleep(1)
            #print(url)
            
            driver.switch_to_frame('mainFrame')
            try:
                try:
                    tit = driver.find_element_by_xpath('//*[@id="title_1"]/span[1]').text
                    title = self.parseContents(tit)
                    #print(title)
                except Exception as e:
                    pass
                try:
                    body = driver.find_element_by_xpath('//*[@id="postViewArea"]').text.replace('\n', ' ')
                    text = self.parseContents(body)
                    #print(text)
                except Exception as e:
                    pass
                
                try:
                    author = driver.find_element_by_xpath('//*[@id="nickNameArea"]').text
                    # print(author)
                    # print(11111111111111111111)
                except Exception as e:
                    pass
                try:
                    date = driver.find_element_by_xpath('//*[@id="printPost1"]/tbody/tr/td[2]/table/tbody/tr/td/p[1]').text
                    #print(date)
                except Exception as e:
                    pass
                
                #docs.append(return_list)
                
                #self.sh.saveNaverblogDoc(keyword, return_list)
            except:
                pass
            try:
                try:
                    tit = driver.find_element_by_css_selector('div.pcol1>div>p>span').text
                    #SE-e0358fba-3cb0-4ec8-b005-f3909edd0366 > div > div
                    title = self.parseContents(tit)+'/t'
                    #print(title)
                except Exception as e:
                    pass
                try:
                    author = driver.find_element_by_css_selector('div.blog2_container>span').text
                    #SE-e0358fba-3cb0-4ec8-b005-f3909edd0366 > div > div
                    author = self.parseContents(author)
                    #print(author)
                except Exception as e:
                    pass
                try:
                    spans = driver.find_elements_by_css_selector('div.blog2_container>span')
                    date = spans[1].text
                except Exception as e:
                    pass
                try:
                    text = driver.find_element_by_css_selector('div.se-main-container').text.replace('\n', '/t')
                except Exception as e:
                    pass
            except:
                pass
            if len(title) ==0:
                continue
            try:
                return_list = [url,title,date,author,text]
                self.sh.saveNaverblogDoc(keyword, return_list)
            except Exception as e:
                pass
            doc_cnt += 1
            msg ='\r진행률 : %f%%\tdoc_cnt : %d' %(doc_cnt/total_url*100, doc_cnt)
            print(' '*len(msg), end='')
            print(msg, end ='')
            time.sleep(0.1)
        return

    def copy_input(self, xpath, input):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        #headless 탐지 막는 옵션추가
        #chrome_options.add_argument('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36')
        #플러그인 개수로 막힐 수도 있음
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--incognito')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        pyperclip.copy(input)
        driver.find_element_by_xpath(xpath).click()
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(1)

    def multiprocessing_navercafe(self,keyword):
        cafe_list = [
        'ilovegm1'
        ,'dongtanmom'
        ,'isajime'
        ,'ghdi58'#닌텐도
        ,'imsanbu'
        ,'skybluezw4rh'
        ,'cosmania'
        ,'jaegebal'
        ,'msbabys'
        ,'malltail'
        ,'3dpchip'
        ,'dgmom365'
        ,'mktsesang'
        #,'mom79'
        ,'junkart'
        #,'kyungmammo'
        ,'masanmam'
        ,'anycallusershow'#삼성핸드폰
        ,'inmacbook'#맥북
        ,'sssw'#나이키
        ,'costco12'#코스트코
        ,'komusincafe'#곰신
        ,'campingfirst'#캠핑
        ,'fx8300'#AMD
        ,'bebettergirls'#취업대학교
        ,'bodygood'#헬스매니아
        ,'movie02'#네영카
        ,'hotellife'#스사사
        ,'xst'#샤오미
        ,'shopjirmsin'#쇼핑지름신
        ,'zzang9daddy'#짱구대디
        ,'no1sejong'#세종시
        ,'singeriu'#아이유
        ,'steamindiegame'# 우왁굳
        ,'iroid'#싼타페
        ,'byungs94'#수원맘
        ,'toeicamp'#토익캠프
        ,'drhp'#닥터헤드폰
        ,'camsbaby'#천아베베
        ,'koreakmc'#송파강동맘
        ,'05425' # 맨살모임
        ,'playbattlegrounds'#배틀그라운드
        ,'futurefight' #퓨처파이트
        ,'sevenknights'#세븐나이츠
        ,'lolkor'#롤
        ,'dfither'#던파
        ,'peopledisc'#척추질환
        ,'ketogenic'#저탄고지
        ,'appleiphone'#애플 아사모,
        'dokchi'#독취사
        #,'kig' # 피터팬 방구하기
        ,'specup'#스펙업
        ,'onepieceholicplus'#월급쟁이 재테크
        ,'momingrnyj'#구리 남양주맘
        ,'workee'#직장인
        ,'sujilovemom'#용인수지맘
        ,'momakakao'#모두의 마블
        ,'fifaco'#피파온라인
        ,'ps3friend'#ps5와 친구들
        ,'xbox360korea'#xbox
        ,'cookierun' #쿠키런
        ,'bestani' #애니타운
        ,'logosesang'#로고세상
        #,'tmfql8967'#소녀시대
        ,'bigbang2me'#빅뱅
        ,'hmckorea'#현대차
        ,'shootgoal'#벤츠
        ,'nds07'# 배달세상  등업필요
        ,'scottycameron'#클럽카메론
        ,'star2mania'#테슬라
        ,'dieselmania'#디젤매니아
        ,'bk1009'#급매물과 반값매매
        ,'stockstudys' #세뇨르의 성공적인 투자를 위한 주식공부방
        ,'30talmo'#탈모방
        ,'themukja'#더먹자
        ,'w3fate'# 창업
        ,'jihosoccer123' # 아프니까 사장이다.
        ,'guamfree'#괌
        ,'wecando7'#월급쟁이 부자들.
        ,'ishift'#내집장만 아카데미
        ,'dohak27'#굿싱
        ,'perfumelove'#향수사랑
        ,'smartbargain'#스마트 바겐
        ,'jpnstory'#네일동
        ,'warcraftgamemap'#다낭고스트
        ,'firenze' #유럽여행
        ,'pnmath'#포만한
        ,'rksghwhantk'#/..
        ,'mhs01'#마이스터고
        ,'hillstate1800'#현명한 소비
        ,'rainup'#아름다운 내집갖기
        ,'formsunmyeong'#잠백이
        ,'culturebloom'#컬쳐블룸
        ,'bikecargogo'# 바튜매
        ,'temadica' # 사진동호회
        ,'develoid' # 디벨로이드
        ,'army58cafe'#군인아들부모님
        ,'a60a70' #제네시스
        ,'tocop' # 경공
        ,'akdongfan' #악뮤
        ,'idiolle' #제주도한달살기
        ,'sbstvdocu' #그알
        ,'hotdealcommunity'
        , 'likeusstock' #미주미
        ,'onimobile' #좀비 고등학교 모바일
        ,'chuldo' #철도청
        ,'remonterrace'#레몬테라스
        ,'lilka' #릴카
        ,'youloveu'#레드벨벳
        ,'jellyfishkimsejung'#김세정
        ,'rapsup' # 힙합
        ,'lessoninfo' #래슨인포
        ,'as6060' #맨유
        ,'lfckorea'
        ,'dogpalza'#강사모
        ]
        self.distributeList(2, keyword, 'navercafe',cafe_list, self.navercafe_list_crawling)


    def distributeList(self, n, keyword, proc_name, list, func):
        
        


        length = len(list)
        if length < 1: return
        if length < n:
            n = length # n = p_cnt list 개수, length가 p_cnt 보다 작으면 p_cnt값을 줄여라
        print (proc_name+' Multi-Process :'+str(n)+', List :'+str(length))
        each = int(length/n)
        remains = length%n
        allocated = 0
        procs = []
        for i in range(1, n+1):
            if allocated+each < length :
                end_index = allocated + each
                if remains > 0:
                    end_index = end_index+1
                    remains = remains-1
                docs = list[allocated:end_index]
                allocated = end_index
            else :
                docs = list[allocated:]
            procs.append(Process(target=func, args=(i,keyword, docs)))

        for p in procs :
            p.start()
        for p in procs :
            p.join()

    



    def navercafe_list_crawling(self,i,keyword, cafe_list):
        query = self.quote(keyword)
        docs = []
        had_url = self.sh.loadURL('navercafe',keyword)

        had_title= self.sh.loadTitle('navercafe', keyword)
        #print(had_title)
        #google-chrome --remote-debugging-port=9222 --user-data-dir="~/workspace/test/knowledge_based_sentiment_analysis_community_crawler/ChromeProfile"
        id = 'minamom501'
        pw = 'lalala1983'

        # cafe_list = [
        # 'ilovegm1'
        # ,'dongtanmom'
        # ,'isajime'
        # ,'ghdi58'#닌텐도
        # ,'imsanbu'
        # ,'skybluezw4rh'
        # ,'cosmania'
        # ,'jaegebal'
        # ,'msbabys'
        # ,'malltail'
        # ,'3dpchip'
        # ,'dgmom365'
        # ,'mktsesang'
        # #,'mom79'
        # ,'junkart'
        # #,'kyungmammo'
        # ,'masanmam'
        # ,'anycallusershow'#삼성핸드폰
        # ,'inmacbook'#맥북
        # ,'sssw'#나이키
        # ,'costco12'#코스트코
        # ,'komusincafe'#곰신
        # ,'campingfirst'#캠핑
        # ,'fx8300'#AMD
        # ,'bebettergirls'#취업대학교
        # ,'bodygood'#헬스매니아
        # ,'movie02'#네영카
        # ,'hotellife'#스사사
        # ,'xst'#샤오미
        # ,'shopjirmsin'#쇼핑지름신
        # ,'zzang9daddy'#짱구대디
        # ,'no1sejong'#세종시
        # ,'singeriu'#아이유
        # ,'steamindiegame'# 우왁굳
        # ,'iroid'#싼타페
        # ,'byungs94'#수원맘
        # ,'toeicamp'#토익캠프
        # ,'drhp'#닥터헤드폰
        # ,'camsbaby'#천아베베
        # ,'koreakmc'#송파강동맘
        # ,'05425' # 맨살모임
        # ,'playbattlegrounds'#배틀그라운드
        # ,'futurefight' #퓨처파이트
        # ,'sevenknights'#세븐나이츠
        # ,'lolkor'#롤
        # ,'dfither'#던파
        # ,'peopledisc'#척추질환
        # ,'ketogenic'#저탄고지
        # ,'appleiphone'#애플 아사모,
        # 'dokchi'#독취사
        # #,'kig' # 피터팬 방구하기
        # ,'specup'#스펙업
        # ,'onepieceholicplus'#월급쟁이 재테크
        # ,'momingrnyj'#구리 남양주맘
        # ,'workee'#직장인
        # ,'sujilovemom'#용인수지맘
        # ,'momakakao'#모두의 마블
        # ,'fifaco'#피파온라인
        # ,'ps3friend'#ps5와 친구들
        # ,'xbox360korea'#xbox
        # ,'cookierun' #쿠키런
        # ,'bestani' #애니타운
        # ,'logosesang'#로고세상
        # #,'tmfql8967'#소녀시대
        # ,'bigbang2me'#빅뱅
        # ,'hmckorea'#현대차
        # ,'shootgoal'#벤츠
        # ,'nds07'# 배달세상  등업필요
        # ,'scottycameron'#클럽카메론
        # ,'star2mania'#테슬라
        # ,'dieselmania'#디젤매니아
        # ,'bk1009'#급매물과 반값매매
        # ,'stockstudys' #세뇨르의 성공적인 투자를 위한 주식공부방
        # ,'30talmo'#탈모방
        # ,'themukja'#더먹자
        # ,'w3fate'# 창업
        # ,'jihosoccer123' # 아프니까 사장이다.
        # ,'guamfree'#괌
        # ,'wecando7'#월급쟁이 부자들.
        # ,'ishift'#내집장만 아카데미
        # ,'dohak27'#굿싱
        # ,'perfumelove'#향수사랑
        # ,'smartbargain'#스마트 바겐
        # ,'jpnstory'#네일동
        # ,'warcraftgamemap'#다낭고스트
        # ,'firenze' #유럽여행
        # ,'pnmath'#포만한
        # ,'rksghwhantk'#/..
        # ,'mhs01'#마이스터고
        # ,'hillstate1800'#현명한 소비
        # ,'rainup'#아름다운 내집갖기
        # ,'formsunmyeong'#잠백이
        # ,'culturebloom'#컬쳐블룸
        # ,'bikecargogo'# 바튜매
        # ,'temadica' # 사진동호회
        # ,'develoid' # 디벨로이드
        # ,'army58cafe'#군인아들부모님
        # ,'a60a70' #제네시스
        # ,'tocop' # 경공
        # ,'akdongfan' #악뮤
        # ,'idiolle' #제주도한달살기
        # ,'sbstvdocu' #그알
        # ,'hotdealcommunity'
        # , 'likeusstock' #미주미
        # ,'onimobile' #좀비 고등학교 모바일
        # ,'chuldo' #철도청
        # ,'remonterrace'#레몬테라스
        # ,'lilka' #릴카
        # ,'youloveu'#레드벨벳
        # ,'jellyfishkimsejung'#김세정
        # ,'rapsup' # 힙합
        # ,'lessoninfo' #래슨인포
        # ,'as6060' #맨유
        # ,'lfckorea'
        # ,'dogpalza'#강사모
        # ]
        
        #cafe_list = ['iroid']

        #미주알 고주알  >> 등업필요
        xpath_dict = {}
        
        
        #xpath_dict['']
        xpath_dict['ilovegm1'] = xpath_dict['sssw'] = xpath_dict['anycallusershow'] = xpath_dict['costco12'] = xpath_dict['emsibt'] = xpath_dict['akdongfan']\
        = xpath_dict['bodygood']= xpath_dict['byungs94'] = xpath_dict['steamindiegame'] = xpath_dict['zzang9daddy'] = xpath_dict['wecando7'] = xpath_dict['sbstvdocu']\
        = xpath_dict['camsbaby'] = xpath_dict['playbattlegrounds'] = xpath_dict['ketogenic'] = xpath_dict['sujilovemom'] = xpath_dict['dohak27']\
        = xpath_dict['momakakao'] = xpath_dict['ps3friend'] = xpath_dict['bestani'] = xpath_dict['temadica'] = xpath_dict['mom79'] = xpath_dict['hillstate1800'] \
        = xpath_dict['hmckorea'] = xpath_dict['nds07'] = xpath_dict['scottycameron'] = xpath_dict['star2mania'] =  xpath_dict['dgmom365'] = xpath_dict['a60a70']\
        = xpath_dict['isajime'] = xpath_dict['imsanbu'] =  xpath_dict['skybluezw4rh'] =  xpath_dict['msbabys'] = xpath_dict['3dpchip'] = xpath_dict['formsunmyeong']\
        = xpath_dict['bikecargogo'] = xpath_dict['temadica'] = xpath_dict['likeusstock'] = xpath_dict['lilka'] = xpath_dict['rapsup'] = xpath_dict['youloveu']= xpath_dict['jellyfishkimsejung']\
        = '//*[@id="info-search"]/form/button'

        xpath_dict['gangmok'] = xpath_dict['inmacbook'] = xpath_dict['komusincafe'] = xpath_dict['campingfirst'] = xpath_dict['fifaco']\
        = xpath_dict['fx8300']= xpath_dict['movie02'] = xpath_dict['bebettergirls'] = xpath_dict['no1sejong'] = xpath_dict['kookminlease']\
        = xpath_dict['hotellife']= xpath_dict['iroid'] = xpath_dict['xst']= xpath_dict['shopjirmsin'] = xpath_dict['dongtanmom']\
        = xpath_dict['singeriu'] = xpath_dict['drhp'] = xpath_dict['toeicamp'] = xpath_dict['koreakmc']= xpath_dict['w3fate'] = xpath_dict['hotdealcommunity']\
        = xpath_dict['05425'] = xpath_dict['futurefight'] = xpath_dict['sevenknights'] = xpath_dict['lolkor'] = xpath_dict['jihosoccer123']\
        = xpath_dict['dfither'] = xpath_dict['peopledisc'] = xpath_dict['appleiphone'] = xpath_dict['dokchi'] = xpath_dict['guamfree'] = xpath_dict['dogpalza'] \
        = xpath_dict['kig'] = xpath_dict['specup'] = xpath_dict['onepieceholicplus'] = xpath_dict['momingrnyj'] = xpath_dict['ishift']\
        = xpath_dict['workee'] = xpath_dict['ghdi58'] = xpath_dict['xbox360korea'] = xpath_dict['cookierun'] = xpath_dict['bk1009'] = xpath_dict['tocop']\
        = xpath_dict['logosesang'] = xpath_dict['tmfql8967'] = xpath_dict['bigbang2me'] = xpath_dict['shootgoal'] =  xpath_dict['dieselmania'] \
        = xpath_dict['gumimom7'] = xpath_dict['cosmania'] = xpath_dict['jaegebal'] = xpath_dict['malltail'] =  xpath_dict['mktsesang']\
        = xpath_dict['junkart'] = xpath_dict['kyungmammo'] = xpath_dict['masanmam'] = xpath_dict['30talmo'] = xpath_dict['themukja'] = xpath_dict['idiolle']\
        = xpath_dict['perfumelove'] =xpath_dict['smartbargain'] = xpath_dict['jpnstory'] = xpath_dict['warcraftgamemap'] = xpath_dict['firenze']\
        =xpath_dict['jpnstory'] = xpath_dict['pnmath']=xpath_dict['mhs01'] = xpath_dict['rainup'] = xpath_dict['develoid'] = xpath_dict['army58cafe']\
        = xpath_dict['onimobile']= xpath_dict['chuldo'] = xpath_dict['remonterrace'] = xpath_dict['lessoninfo']= xpath_dict['as6060'] = xpath_dict['lfckorea'] \
        ='//*[@id="cafe-search"]/form/button'
     
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        #headless 탐지 막는 옵션추가
        #chrome_options.add_argument('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36')
        #플러그인 개수로 막힐 수도 있음
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--incognito')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)#driver 변수 만들 때 단순히 chromedriver 위치만 적어주는 게 아니라 chrome_options라는 이름의 인자를 같이 넘겨줘야함

        #이 인자 값으로 위에 추가적인 인자를 넘겨줌
        driver.implicitly_wait(3)
        driver.switch_to_window(driver.window_handles[i-1])
        # pyautogui.keyDown('ctrl')
        # pyautogui.keyDown('shift')
        # pyautogui.keyDown('n')


        #############자동로그인####################
        # 로봇방지설문이 나올 수 있어서 일단은 직접 로그인 하고 진행
        # driver.get('https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com')    

        # self.copy_input('//*[@id="id"]', id)
        # time.sleep(1)
        # self.copy_input('//*[@id="pw"]', pw)
        # time.sleep(1)
        # driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
        # time.sleep(1)
        url = "none"
        K=0
        handle = 0
        page_cnt = 0
        return_cnt = 0
        random.shuffle(cafe_list)

        for cafe in cafe_list:
            #if K < len(cafe_list)-1: K+=1;continue
            progressBar(K, len(cafe_list))
            K+=1
            xpath = xpath_dict[cafe]
            search_url = "https://cafe.naver.com/"
            cur_url = search_url+cafe
            driver.get(cur_url)
            page_cnt+=1
            
            try:
                element = WebDriverWait(driver,2).until(
                    EC.presence_of_element_located((By.ID,'topLayerQueryInput'))
                    #navercafe에서 id값이 topLayerQueryInput인게 존재할때 까지 2초 기다려라
                )
            except: continue
            #time.sleep(2)
            driver.execute_script("document.getElementById('topLayerQueryInput').value =\'"+keyword+"\'")
            #document.getElementsByName('id')[0].value=\' 는 자바스크립트에서 사용되는 함수
            try:
                element = WebDriverWait(driver,3).until(
                    EC.presence_of_element_located((By.XPATH,xpath))
                )
            except: 
                print("error on : "+cafe)
                continue
            try:
                btn = driver.find_element_by_xpath(xpath).send_keys(Keys.ENTER)
                
            except: 
                print("cafe btn xpath error " + cafe)
                continue
            
            page=1
            ######################################################################
            #검색
            try:
                element = WebDriverWait(driver,2).until(
                EC.presence_of_element_located((By.ID,"cafe_main")))
                #IFrame을 찾는 작업 존재하냐
                
            except: continue
            driver.switch_to.frame("cafe_main")#IFrame을 cafe_main으로 변경
            if page == 1:
                try:
                    btn = driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[%s]' %(page))
                    page_url = btn.get_attribute("href")
                    page_url = page_url[:-1]
                except:
                    continue
                #print(page_url)
            while True:
            #while False:
                #time.sleep(0.3)
                #print(page)
               
                cur_url = page_url + str(page)
                try:
                    driver.get(cur_url)
                except:
                    driver.refresh()
                    pass
                try:
                    element = WebDriverWait(driver,2).until(
                        EC.presence_of_element_located((By.ID,"cafe_main"))
                        #IFrame을 찾는 작업 존재하냐
                    )
                except: break
                
                
                time.sleep(0.3)
                driver.switch_to.frame("cafe_main")#IFrame을 cafe_main으로 변경
                minipage=1
                try:
                    first_page = last_page = ''
                    first_page = driver.find_element_by_xpath('//*[@id="main-area"]/div[5]/table/tbody/tr[1]/td[1]/div[2]/div/a[1]').get_attribute('href')
                    last_page = driver.find_element_by_xpath('//*[@id="main-area"]/div[5]/table/tbody/tr[15]/td[1]/div[2]/div/a[1]').get_attribute('href')
                except:
                    pass
                if first_page in had_url:
                    if last_page in had_url:
                        page+=1
                        continue
                    else:
                        pass
                for minipage in range(1,16):
                    comment = ""
                    flag = True
                    url = title = date = author = text= ""
                    # [url,title,date,author,text]
                    #print(driver.window_handles)
                    if page_cnt == 500 :
                        #driver.execute_script('window.open("https://naver.com");')
                        handle +=1
                        time.sleep(1)
                        #driver.close()
                        driver.switch_to_window(driver.window_handles[handle%15])
                        time.sleep(1)
                        driver.get(cur_url)
                        page_cnt = 0
                    
                    try:
                        if minipage==1:
                            try:
                              
                                try:    
                                    element = WebDriverWait(driver,1).until(
                                    EC.presence_of_element_located((By.XPATH,'//*[@id="main-area"]/div[5]/table/tbody/tr[%s]/td[1]/div[2]/div/a[1]' %(minipage)))
                                    )#minipage마다의 xpath 찾기
                                    flag = True
                                except:
                                    flag = False
                                    pass
                            except: pass
                            if flag == False: break
                         
                            try:
                                btn = driver.find_element_by_xpath('//*[@id="main-area"]/div[5]/table/tbody/tr[%s]/td[1]/div[2]/div/a[1]' %(minipage))    
                            except:
                                pass
                            url = btn.get_attribute('href')
                            if url in had_url: continue
                            had_url.append(url)
                            #print("btn click")
                            try:
                                #driver.get('https://cafe.naver.com/kyungmammo?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D22897837%2526page%3D95%2526inCafeSearch%3Dtrue%2526searchBy%3D0%2526query%3D%25EA%25B3%25B5%25EA%25B8%25B0%25EC%25B2%25AD%25EC%25A0%2595%25EA%25B8%25B0%2526includeAll%3D%2526exclude%3D%2526include%3D%2526exact%3D%2526searchdate%3Dall%2526media%3D0%2526sortBy%3Ddate%2526articleid%3D4253006%2526referrerAllArticles%3Dtrue')
                                #driver.get('https://cafe.naver.com/byungs94?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D13276223%2526page%3D39%2526inCafeSearch%3Dtrue%2526searchBy%3D0%2526query%3D%25EA%25B3%25B5%25EA%25B8%25B0%25EC%25B2%25AD%25EC%25A0%2595%25EA%25B8%25B0%2526includeAll%3D%2526exclude%3D%2526include%3D%2526exact%3D%2526searchdate%3Dall%2526media%3D0%2526sortBy%3Ddate%2526articleid%3D6013557%2526referrerAllArticles%3Dtrue')
                                btn.send_keys(Keys.ENTER)#url 추가하고 btm 클릭                    
                            except:
                                driver.refresh()
                                btn.send_keys(Keys.ENTER)#url 추가하고 btm 클릭
                                pass
                            
                            page_cnt+=1
                        else:
                            #print("switch frame")
                            driver.switch_to.frame("cafe_main") #driver frame을 care_main으로 복귀
                            ###########
                            try:
                                element = WebDriverWait(driver,1).until(
                                EC.presence_of_element_located((By.XPATH,'//*[@id="main-area"]/div[5]/table/tbody/tr[%s]/td[1]/div[2]/div/a[1]' %(minipage)))
                                )
                            except Exception as e:
                                #print(e)
                                continue
                            ##########
                            btn = driver.find_element_by_xpath('//*[@id="main-area"]/div[5]/table/tbody/tr[%s]/td[1]/div[2]/div/a[1]' %(minipage))
                            url = btn.get_attribute('href')
                            if url in had_url: 
                                if last_page in had_url:
                                    break
                                continue
                            had_url.append(url)
                            try:
                                btn.send_keys(Keys.ENTER)#url 추가하고 btm 클릭                    
                            except:
                                driver.refresh()
                                btn.send_keys(Keys.ENTER)#url 추가하고 btm 클릭
                                pass

                            
                            page_cnt+=1
                    except Exception as e:
                        #print(e)
                        break
                    time.sleep(0.4)
                    ###########글에 들어가 면 바로 iframe 변경!
                    #driver.switch_to.frame("cafe_main")
                    try:
                        element = WebDriverWait(driver,1).until(
                        EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/div/div[2]/div[2]/div[1]'))
                        )
                    except: driver.back();continue
                    #########등업 필요한 글들은 pass###########
                    try:
                        p = driver.find_element_by_xpath(By.XPATH,'//*[@id="app"]/div/div/div/p[1]')
                        driver.back()
                        continue
                    except:
                        pass
                    #####################3
                    text = ''
                    response = driver.page_source
                    
                    if not response:
                        print("not response!!")
                        break
                    soup = BeautifulSoup(response,"lxml")
                    try:
                        t_div = soup.find("div",{"class":"article_header"})
                        author = t_div.find("div",{"class":"nick_box"}).text
                        author = self.parseContents(author)
                        date = t_div.find("span",{"class":"date"}).text.replace('.','-')
                        title = t_div.find("div",{"class":"title_area"}).find("h3").text
                        title = title.replace("\n", ' ')
                        title = self.parseContents(title)+'/t'
                        
                    except:
                        driver.back()
                        continue
             
                    try:
                        text = soup.select_one('#app > div > div > div.ArticleContentBox > div.article_container > div.article_viewer > div > div').text +'/t'
            
                    except Exception as e:
                        pass
                    
                    return_list = [url,title,date,author,self.parseContents(text)]
                    if len(text) == 0:
                        print(return_list)
                    #print(return_list)
                    try: #댓글 읽기
                        soup = BeautifulSoup(response,"lxml")
                        lis = soup.select('#app > div > div > div.ArticleContentBox > div.article_container > div.CommentBox > ul > li')
                        
                        
                        #print(len(lis))
                        for li in lis:
                            comment = comment + li.find("div",{"class":"comment_text_box"}).text+'/t'
                            #print(comment)
                        return_list = [url,title,date,author,self.parseContents(text+comment)]
                    except Exception as e:
                        docs.append(return_list)
                        self.sh.saveNavercafeDoc(keyword, return_list)
                        return_cnt += 1
                        #print(return_list,cafe)
                        driver.back()
                        continue
                    self.sh.saveNavercafeDoc(keyword, return_list)  #바로바로 저장
                    return_cnt += 1
                    #print(return_cnt)
                    ##rint(return_list,cafe)                
                    driver.back()
                if flag == False: break
                driver.switch_to.default_content()
                page+=1
        driver.close()
        return docs  # [url,title,date,author,text]

    def facebook_list_crawling(self,keyword):
        query = self.quote(keyword)
        docs = []
        news_list = [['yonhap','/html/body/div[1]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[3]/div[1]/div/div/div[1]/div/div[1]/div/div/div/div/'], ['news1kr','//*[@id="PageTimelineSearchPagelet_204993636204108"]/div/div/div/div/'],['newsis.news','//*[@id="PageTimelineSearchPagelet_146136618768529"]/div/div/div/div/'],['chosun','//*[@id="PageTimelineSearchPagelet_376570488117"]/div/div/div/div/'],['joongang','//*[@id="PageTimelineSearchPagelet_155192444524300"]/div/div/div/div/'],['dongamedia','//*[@id="PageTimelineSearchPagelet_253942034624352"]/div/div/div/div/'],['hankyoreh','//*[@id="PageTimelineSearchPagelet_113685238657736"]/div/div/div/div/'],['kyunghyangshinmun','//*[@id="PageTimelineSearchPagelet_161649467207997"]/div/div/div/div/'],['OhmyNewsKorea','//*[@id="PageTimelineSearchPagelet_167079259973336"]/div/div/div/div/'],['sisain','//*[@id="PageTimelineSearchPagelet_154189147958193"]/div/div/div/div/'],['ytn.co.kr','//*[@id="PageTimelineSearchPagelet_237776059583039"]/div/div/div/div/'],['MBCnews','//*[@id="PageTimelineSearchPagelet_136802662998779"]/div/div/div/div/'],['kbsnews','//*[@id="PageTimelineSearchPagelet_121798157879172"]/div/div/div/div/'],['SBS8news','//*[@id="PageTimelineSearchPagelet_181676841847841"]/div/div/div/div/'],['jtbcnews','//*[@id="PageTimelineSearchPagelet_240263402699918"]/div/div/div/div/'],['hkilbo','//*[@id="PageTimelineSearchPagelet_157370204315766"]/div/div/div/div/'],['nocutnews','//*[@id="PageTimelineSearchPagelet_193441624024392"]/div/div/div/div/'],['mt.co.kr','//*[@id="PageTimelineSearchPagelet_119675661434875"]/div/div/div/div/'],['kukmindaily','//*[@id="PageTimelineSearchPagelet_118992638190529"]/div/div/div/div/'],['segyetimes' ,'//*[@id="PageTimelineSearchPagelet_146119315469421"]/div/div/div/div/']]
        search_url = 'https://www.facebook.com'
        had_url = self.sh.loadURL('facebook',keyword)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        driver.get(search_url)
        try :
            Id = driver.find_element_by_name('email')
            Id.send_keys('elapinsta@gmail.com')
            password = driver.find_element_by_id('pass')
            password.send_keys('##sangsoo1')
            password.submit()
            time.sleep(1)
            keyword_area = driver.find_element_by_xpath('p')
            keyword_area.send_keys(keyword)
            keyword_area.submit()
        except : pass
        
        time.sleep(1)  # login complete
        temp_list = [['yonhap',''] ]
        for news in temp_list:        
            search_url = 'https://www.facebook.com/pg/'+news[0]+'/posts/?ref=page_internal'
            driver.get(search_url)
            time.sleep(10)
            blank = driver.find_element_by_class_name('_58al')
            blank.send_keys(keyword)
            button = driver.find_element_by_class_name('_3fbq._4jy0._4jy3._517h._51sy._42ft').click()
            
    #        public = driver.find_element_by_class_name('_55sh._1ka1').click()
    #        time.sleep(1)
            last_height = driver.execute_script("return document.body.scrollHeight")
#            for i in range(0,1):
            while True:
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                time.sleep(1)
                cur_height = driver.execute_script("return document.body.scrollHeight")
                response = driver.page_source
                if not response: return docs
                soup = BeautifulSoup(response,"lxml")
                containers = soup.find("div",{"class":"_1yt"}).find_all("div")
                for container in containers:
                    try:
                        div = container.find("div",{"class":"_o02"}).find("div",{"class":"_307z"}).find_all("div")
                        comment = div[-1].find("span",{"class":"_78k8"}).find("a")
                        a = comment['href']
                        if a in had_url: pass
                        had_url.append(a)
             #           print(a)
                        docs.append([a,keyword,news])
                    except Exception as e:
                        pass
                try:
                    button = driver.find_element_by_class_name('pam.uiBoxLightblue.uiMorePagerPrimary').click()
                except Exception as e:
                    print(e)
                    break
            #    print(last_height)
            #    print(cur_height)
                last_height = cur_height
            for document in docs:
                try:
                    driver.get(document[0])
                except Exception as e: print(e);continue
                time.sleep(4)
                author = ""; 
                contents = ""
             #   print(document[0])
                response = driver.page_source
                if not response: continue
                soup = BeautifulSoup(response,"lxml")
                try:
                    contents = soup.find("span",{"class":"hasCaption"}).text
             #       print(contents)
                except Exception as e: pass
                try:
                    lis = soup.find("div",{"class":"_6iiv _6r_e"}).find("ul",{"class":"_77bp"}).find_all("li")
                except Exception as e: pass
                comments =''
                try:
                    for li in lis:
                        comments += li.find("div",{"class":"_72vr"}).find("span",{"dir":"ltr"}).find("span",{"class":"_3l3x"}).text
                except Exception as e: print(e);continue
                if len(contents+comments)>0:
                    #contemts = contents_limit(contents+comments)
                    contents +=comments
                    document+= [author,self.parseContents(contents)]
                    self.sh.saveFacebookDoc(keyword,document)

        driver.close()

        return docs
    def facebook_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.facebook_doc_crawling(doc)
            if document and len(document) >2:
#                print('crawl site : '+doc[0])
                with self.lock:
                    self.sh.saveFacebookDoc(keyword, document)
#            else:
#                print('Error occur from facebook site : '+doc[0])
        return
    def RankingNews_list_crawling(self,keyword):
        docs = []
        check_cnt = 0
        new_num = 0
        try:
            had_url = self.sh.loadURL('RankingNews',keyword+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('RankingNews',keyword+'2'+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('RankingNews',keyword+'3'+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('RankingNews',keyword+'4'+'_URL')
        except Exception as e:
            print(e)
            pass
        had_url+=self.sh.loadURL('RankingNews',keyword)
        had_url = set(had_url)
        had_url = list(had_url)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        chrome_options.add_argument("User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        #path를 한번에 인자로 넣음
        while True:
            dt_now = datetime.datetime.now()
            dt = dt_now - datetime.timedelta(days = check_cnt)
            dt_year = dt.year
            dt_month = dt.month
            dt_day = dt.day
                    
            date = str(dt_year) + str(dt_month).zfill(2)+ str(dt_day).zfill(2)
            print(date)
            check_cnt += 1
            search_url = 'https://news.naver.com/main/ranking/popularDay.naver?date='+date
            driver.get(search_url)
            time.sleep(2)
            url = []
            response = driver.page_source
            soup = BeautifulSoup(response,"lxml")
            rbs = soup.find_all('div',attrs={"class":"rankingnews_box"})
            for rb in rbs:
                lis = rb.select('div > ul > li')
                for li in lis:
                    try:
                        a = li.find('a')
                        # print(a)
                    
                        href = a['href']
                        u = 'https://news.naver.com'+href
                        # print(u)
                    except Exception as e:
                        # print(e)
                        continue
                    
                    #print(a)
                    if u in had_url: continue
                    had_url.append(u)
                    url.append(u)
                    #print(a)
                    docs.append([u,keyword])
                    if len(had_url)<20000:
                            self.sh.saveRankingNewsURL(keyword, [u])
                    elif len(had_url)<40000:
                        self.sh.saveRankingNewsURL(keyword+'2', [u])
                    elif len(had_url)<60000:
                        self.sh.saveRankingNewsURL(keyword+'3',[u])
                    else:
                        self.sh.saveRankingNewsURL(keyword+'4',[u])
                    new_num += 1
                # print(new_num)
            if check_cnt == 180:
                break
        return new_num   

    def RankingNews_contents_crawling(self,keyword):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)

        had_finished = self.sh.loadURL('RankingNews',keyword)

        try:
            had_url = self.sh.loadURL('RankingNews',keyword+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('RankingNews',keyword+'2'+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('RankingNews',keyword+'3'+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('RankingNews',keyword+'4'+'_URL')
        except Exception as e:
            print(e)
            pass
        print("RankingNews Documents crawling start. documents count : "+str(len(had_url)))
        page_cnt = 0
        docs = []
        RankingNews_handle = 0
        for _url in had_url:
            if _url in had_finished:
                continue
            document = [_url]
            try:
                driver.get(document[0])
                page_cnt += 1
                time.sleep(2.2)
                response = driver.page_source
                #driver.page_source: 브라우저에 보이는 그대로의 HTML, 크롬 개발자 도구의 Element 탭 내용과 동일.
                if not response: continue
                soup = BeautifulSoup(response,'lxml')
                #soup = BeautifulSoup(response,'lxml')
                # title = self.parseContents(soup.find("title").text)
                # doc[1] += title
                contents = title =  comments =author = date = ''
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver,1).until(
                EC.presence_of_element_located((By.XPATH,'//*[@id="articleBodyContents"]')))
                contents = driver.find_element_by_xpath('//*[@id="articleBodyContents"]').text
                contents = contents.replace('\n', '/t').replace('#', ' ')
                # print(contents)
            except Exception as e:
                pass
            try:
                lis = soup.select('#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li')
                for li in lis:
                    comment = li.select_one('div > div > div.u_cbox_text_wrap > span').text
                    comment = comment.replace('\n', ' ').replace('#', ' ')
                    contents = contents + ' ' + comment+'/t'
            except:
                pass
            try:
                element = WebDriverWait(driver,1).until(
                EC.presence_of_element_located((By.XPATH,'//*[@id="articleTitle"]')))
                title = driver.find_element_by_xpath('//*[@id="articleTitle"]').text
                title = title.replace('\n', ' ').replace('#', ' ')+'/t'
            except:
                pass
            try:
                element = WebDriverWait(driver,1).until(
                EC.presence_of_element_located((By.XPATH,'//*[@id="main_content"]/div[1]/div[3]/div/span[1]')))
                date = driver.find_element_by_xpath('//*[@id="main_content"]/div[1]/div[3]/div/span[1]').text
                date = date.replace('\n', ' ').replace('#', ' ')
            except:
                pass

            try:
                element = WebDriverWait(driver,1).until(
                EC.presence_of_element_located((By.XPATH,'//*[@id="articleBody"]/div[2]/div/div/div/div[1]/div/div[1]/div/div/div/div/div[2]')))
                author = driver.find_element_by_xpath('//*[@id="articleBody"]/div[2]/div/div/div/div[1]/div/div[1]/div/div/div/div/div[2]').text
                author = author.replace('\n', ' ').replace('#', ' ')
                # print(author)
            except:
                pass
            return_list = [_url,title,date,author,self.parseContents(contents)]
            self.sh.saveRankingNews(keyword, return_list)  #바로바로 저장
            docs.append(return_list)
            # print(return_list)
            if page_cnt % 1000 == 0 :
                        #driver.execute_script('window.open("https://naver.com");')
                RankingNews_handle +=1
                time.sleep(1)
                driver.switch_to_window(driver.window_handles[RankingNews_handle%15])
                time.sleep(1)
                
            msg = '\r진행률 : %f%%\tdoc_cnt : %d\tnew_cnt : %d\r' %((len(had_finished) + page_cnt)/len(had_url)*100,(len(had_finished) + page_cnt), page_cnt)
            print(' '*len(msg), end='')
            print(msg, end ='')
            time.sleep(0.1)
        return docs



    def instagram_crawler(self, keyword):
        query = self.quote(keyword)
        docs = []
        search_url = 'https://www.instagram.com'
        had_url = self.sh.loadURL('instagram',keyword)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        driver.get(search_url)
        try :
            Id = driver.find_element_by_name('username')
            Id.send_keys('elapinsta@gmail.com')
            password = driver.find_element_by_id('password')
            password.send_keys('##sangsoo1')
            password.submit()
            time.sleep(4)
            # keyword_area = driver.find_element_by_xpath('p')
            # keyword_area.send_keys(keyword)
            # keyword_area.submit()
        except : 
            print("log in error")
            pass

        try :
            element = WebDriverWait(driver,10).until(
                EC.presence_of_element_located((By.XPATH,'/html/body/div[6]/div/div/div/div[3]/button[2]')))
            element.click()
        except:
            pass
        
        driver.get("https://www.instagram.com/explore/tags/"+keyword)
        
        first_poster = WebDriverWait(driver,10).until(
                EC.presence_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div[1]/div[2]')))

        first_poster.click()
        date_object_css="div.k_Q0X.NnvRN > a.c-Yi7 > time._1o9PC.Nzb55" 
        main_text_object_css="div.C7I1f.X7jCj > div.C4VMK > span" 
        comment_more_btn="button.dCJp8.afkep" 
        comment_texts_objects_css="ul.Mr508 > div.ZyFrc > li.gElp9.rUo9f > div.P9YgZ > div.C7I1f > div.C4VMK > span" 
        print_flag=True
        next_arrow_btn_css1="._65Bje.coreSpriteRightPaginationArrow" 
        next_arrow_btn_css2="._65Bje.coreSpriteRightPaginationArrow"



        
        wish_num = 10000
        count_extract = 0 

        check_arrow = True 

        while True:
            if(count_extract %30 ==0):
                time.sleep(random.randint(0,10))
            upload_ids = [] 
            date_times = [] 
            date_titles = [] 
            main_texts = [] 
            comments = [] 
          
            if count_extract > wish_num: 
                break 
            time.sleep(3.0+random.random()) # 
            if check_arrow == False: 
                break 
                
            # 날짜
            try: 
                date_object = driver.find_element_by_css_selector(date_object_css) 
                date_time = date_object.get_attribute("datetime") 
                date_title = date_object.get_attribute("title") +'/t'
            except: 
                date_time = None 
                date_title = None 
                
            # 본문 
            try: 
                main_text_object = driver.find_element_by_css_selector(main_text_object_css) 
                main_text = main_text_object.text +'/t'
            except: main_text = None 

            # 댓글
            ## 더보기 버튼 클릭 
            try: 
                while True: 
                    try: 
                        more_btn = driver.find_element_by_css_selector(comment_more_btn) 
                        more_btn.click() 
                    except: break 
            except: 
                print("----------------------fail to click more btn----------------------------------") 
                continue 
        ## 댓글 데이터  
            try: 
                comment_data = " "
                comment_texts_objects = driver.find_elements_by_css_selector(comment_texts_objects_css) 
                try: 
                    for i in range(len(comment_texts_objects)): 
                        comment_data += comment_texts_objects[i].text +'/t'
                except: 
                    print("fail") 
            except: 
                continue
   
    
            date_times.append(date_time) 
            date_titles.append(date_title) 
            main_texts.append(main_text) 
            comments.append(comment_data) 
            if print_flag: 
                # print("upload id : ", upload_id) 
                # print("main : ", main_text) 
                # print("comment : ", comment_data) 
                print(count_extract)
            try: 
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, next_arrow_btn_css1))) 
                driver.find_element_by_css_selector(next_arrow_btn_css2).click() 
            except: check_arrow = False 

            try:
                
                return_list = ["url_info",date_time,main_text,"none",comment_data]
                self.sh.saveInsta(keyword, return_list)
            except Exception as e:
                pass
            
            count_extract += 1


    def insta_dumper_list_crawling(self,keyword):
        try:
            had_url = self.sh.loadURL('insta',keyword)
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('insta',keyword)
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('insta',keyword)
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('insta',keyword)
        except Exception as e:
            print(e)
            pass
        had_url+=self.sh.loadURL('insta',keyword)
        #print(len(had_url))
        had_url = set(had_url)
        had_url = list(had_url)
        docs = []
        query = self.quote(keyword)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        chrome_options.add_argument("User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        search_url = 'https://dumpor.com/t/'+query

        driver.get(search_url)
        time.sleep(5)
        url = []
        check_cnt = 0
        last_scrollHeight = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(2)
        
        while True:
            docs = []
            print("\rnewurl = {}".format(check_cnt))
            cur_scrollHeight = driver.execute_script("return document.body.scrollHeight")
            newnum=0
            response = driver.page_source
            soup = BeautifulSoup(response,"lxml")
            #react-root > section > main > article > div.EZdmt > div > div
            divs = soup.select('body > div.hashtag > div > div.content > div.content__list.grid.cards.infinite_scroll.tags_posts > div')
            for div in divs:
                try:
                    vl = div.select_one('div>a')
                    # print(vl)
                except Exception as e:
                    continue
                try:
                    href = vl['href']
                except:
                    continue
                
                a = 'https://dumpor.com'+ href
                try:
                    content_text = div.select_one('div > div.content__text')
                    # print(content_text)
                    text = content_text.text
                    # print(text)
                except:
                    print("!!!!")
                    pass
                check_cnt +=1
                #print(a)
                if a in had_url: continue
                had_url.append(a)
                url.append(a)
                #print(a)
                date = author = ""
                return_list = [a,keyword,date,author,self.parseContents(text)]
                
                if len(had_url) + check_cnt <20000:
                    self.sh.saveInstaDoc(keyword, return_list)
                elif len(had_url) + check_cnt<40000:
                    self.sh.saveInstaDoc(keyword+'2',return_list)
                elif len(had_url) + check_cnt<60000:
                    self.sh.saveInstaDoc(keyword+'3',return_list)
                elif len(had_url) + check_cnt<80000:
                    self.sh.saveInstaDoc(keyword+'4',return_list)
                newnum+=1
                
            ## scroll down
            driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            time.sleep(5.2)
            if len(url) > 100000:
                break
            if cur_scrollHeight == last_scrollHeight:
                #print("first try")
                driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                time.sleep(5)
                #한 번더 스크롤 내려보고 그래도 같으면 종료
                cur_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")
                if cur_scrollHeight==last_scrollHeight:
                    #print("second try")
                    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                    time.sleep(2)
                    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                    time.sleep(2)
                    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                    time.sleep(5)
                    driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                    cur_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")    
                    try_cnt = 1
                    if cur_scrollHeight==last_scrollHeight:
                        while True:
                            if try_cnt>3:
                                break
                            print("try %d" %(try_cnt))
                            driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                            time.sleep(5*try_cnt)
                            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                            time.sleep(2+try_cnt)
                            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                            time.sleep(5+try_cnt)
                            for m in range(10):    
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                            time.sleep(5)
                            for i in range(10+try_cnt*2):
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)  
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)    
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)  
                                time.sleep(1)
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)    
                                time.sleep(1)    
                            for m in range(10):                                
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                            time.sleep(3)    
                            driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                            time.sleep(2+try_cnt)
                            cur_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")
                            if cur_scrollHeight!=last_scrollHeight:
                                break
                            else:
                                try_cnt+=1
                        if cur_scrollHeight==last_scrollHeight:
                            print("cur_scrollHeight==last_scrollHeight")
                            #print(url[-1])
                            break
                        
            elif newnum==0:
                print("newurl = {}".format(newnum))
            last_scrollHeight = cur_scrollHeight
            print("\rurl len : "+str(len(url)))
            #print("check_cnt : "+str(check_cnt))   
        total = len(had_url)
        return newnum
    

    def insta_list_crawling(self,keyword):

        docs = []
        query = self.quote(keyword)
        search_url = 'https://www.instagram.com/explore/tags/'+query
        #had_url = self.sh.loadURL('insta',keyword)
        #had_url = []
        # filename = keyword+'_URL'
        try:
            had_url = self.sh.loadURL('insta',keyword+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('insta',keyword+'2'+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('insta',keyword+'3'+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('insta',keyword+'4'+'_URL')
        except Exception as e:
            print(e)
            pass
        had_url+=self.sh.loadURL('insta',keyword)
        #print(len(had_url))
        had_url = set(had_url)
        had_url = list(had_url)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        chrome_options.add_argument("User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        #path를 한번에 인자로 넣음
        driver.get(search_url)
        time.sleep(5)
#       print(search_url)
        url = []
        check_cnt = 0
        last_scrollHeight = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(2)
        
        while True:
            cur_scrollHeight = driver.execute_script("return document.body.scrollHeight")
            newnum=0
            response = driver.page_source
            soup = BeautifulSoup(response,"lxml")
            #react-root > section > main > article > div.EZdmt > div > div
            a_list = soup.find_all('div',attrs={"class":"Nnq7C weEfm"})
            for div in a_list:
                vl = div.select('div>a')
                try:
                    for di in vl:
                        #print(di)
                        href = di['href']
                        #print(href)
                        a = 'https://www.instagram.com'+ href
                        check_cnt +=1
                        #print(a)
                        if a in had_url: continue
                        had_url.append(a)
                        url.append(a)
                        #print(a)
                        docs.append([a,keyword])
                        
                        if len(had_url)<20000:
                            self.sh.saveInstaURL(keyword, [a])
                        elif len(had_url)<40000:
                            self.sh.saveInstaURL(keyword+'2', [a])
                        elif len(had_url)<60000:
                            self.sh.saveInstaURL(keyword+'3',[a])
                        else:
                            self.sh.saveInstaURL(keyword+'4',[a])
                        newnum+=1
                except Exception as e:
                    continue
                    #break
            ## scroll down
            driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            time.sleep(2.2)
            if len(url) > 100000:
                break
            if cur_scrollHeight == last_scrollHeight:
                #print("first try")
                driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                time.sleep(3)
                #한 번더 스크롤 내려보고 그래도 같으면 종료
                cur_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")
                if cur_scrollHeight==last_scrollHeight:
                    #print("second try")
                    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                    time.sleep(2)
                    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                    time.sleep(2)
                    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                    time.sleep(5)
                    driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                    cur_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")    
                    try_cnt = 1
                    if cur_scrollHeight==last_scrollHeight:
                        while True:
                            if try_cnt>3:
                                break
                            print("try %d" %(try_cnt))
                            driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                            time.sleep(5*try_cnt)
                            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                            time.sleep(2+try_cnt)
                            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                            time.sleep(5+try_cnt)
                            for m in range(10):    
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                            time.sleep(5)
                            for i in range(10+try_cnt*2):
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)  
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)    
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)  
                                time.sleep(1)
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)    
                                time.sleep(1)    
                            for m in range(10):                                
                                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                            time.sleep(3)    
                            driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                            time.sleep(2+try_cnt)
                            cur_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")
                            if cur_scrollHeight!=last_scrollHeight:
                                break
                            else:
                                try_cnt+=1
                        if cur_scrollHeight==last_scrollHeight:
                            print("cur_scrollHeight==last_scrollHeight")
                            #print(url[-1])
                            break
                        
            elif newnum==0:
                print("newurl = {}".format(newnum))
            last_scrollHeight = cur_scrollHeight
            print("\rurl len : "+str(len(url)))
            #print("check_cnt : "+str(check_cnt))   
        total = len(had_url)
        return newnum
    
    def insta_comment_crawling(self,keyword):
        
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        
        #document자체는 [url,keyword,title,````] list임
        #document[0]은 수집한 url을 의미함
        #print(document[0])
#       response = self.getResponse(document[0])
        
        #bs모듈에 html parser는 내장되어 있으나 lxml의 속도가 더 빠�� 사용법은 같다
        #soup = BeautifulSoup(response,'html.parser')로 사용해도 같다.
        #윤리적인 크롤링 및 스크래핑 url/robots.txt로 확인할 것
        #contents = self.parseContents(soup.find("title").text)
        
        pre_contents = ''
        insta_handle = 0
        fail_cnt = same_cnt = doc_cnt = nopage_cnt = error_cnt = 0
        
        had_finished = self.sh.loadURL('insta',keyword)
       
        try:
            had_url = self.sh.loadURL('insta',keyword+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('insta',keyword+'2'+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('insta',keyword+'3'+'_URL')
        except Exception as e:
            print(e)
            pass
        try:
            had_url += self.sh.loadURL('insta',keyword+'4'+'_URL')
        except Exception as e:
            print(e)
            pass

        print("Instagram Documents crawling start. documents count : "+str(len(had_url)))
#       soup = BeautifulSoup(response.text,"lxml")
        page_cnt = 0
        for _url in had_url:
            if _url in had_finished:
                continue
            document = [_url]
            error_url =['https://www.instagram.com/p/CJF2GUYh7jy/','https://www.instagram.com/p/CLsqPm9jmKG/','https://www.instagram.com/p/CK_muQ9jOTW/','https://www.instagram.com/p/CK_mkErDgGD/','https://www.instagram.com/p/CK_mFVrHLyb/','https://www.instagram.com/p/CK_lcMFjDEK/','https://www.instagram.com/p/CK_lr2HHWZq/','https://www.instagram.com/p/CK_lb05nraJ/','https://www.instagram.com/p/CJw4w75no4o/','https://www.instagram.com/p/CJvcYkEBbiv/','https://www.instagram.com/p/CJi4IsAHX7S/','https://www.instagram.com/p/CJXmGtOjKzb/','https://www.instagram.com/p/CLMkUf5lpfS/','https://www.instagram.com/p/CK-yahyHrj9/','https://www.instagram.com/p/CK-yahyHrj9/','https://www.instagram.com/p/CLYBAlxjbVR/','https://www.instagram.com/p/CLQ1W6yMv8X/','https://www.instagram.com/p/CLEnHjnh0na/','']
            if document[0] in error_url:
                continue
            
            try:
                driver.get(document[0])
                page_cnt += 1
                time.sleep(2.2)
                response = driver.page_source
                #driver.page_source: 브라우저에 보이는 그대로의 HTML, 크롬 개발자 도구의 Element 탭 내용과 동일.
                if not response: continue
                soup = BeautifulSoup(response,'lxml')
                #soup = BeautifulSoup(response,'lxml')
                # title = self.parseContents(soup.find("title").text)
                # doc[1] += title
                contents =message =  comments =author = date = ''
            except Exception as e:
                pass
            if same_cnt >20:
                #os.system('google-chrome --remote-debugging-port=9242 --user-data-dir="~/workspace/test/knowledge_based_sentiment_analysis_community_crawler/ChromeProfile"')
                break
            if error_cnt >5:
                break
            if fail_cnt > 10:
                break
            if nopage_cnt > 10:
                break
            if error_cnt>10:
                break 
            try:
                btns = driver.find_elements_by_css_selector('ul.Mr508 > li > ul > li > div > button')
                for btn in btns:
                    btn.send_keys('\n')
            except:
                pass
            
            #죄송합니다. 페이지를 사용할 수 없습니다.
            try:
                message = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/h2').text
                print()
                nopage_cnt += 1
                if nopage_cnt == 100:
                    for i in range(3):
                        print("refresh"+str(i))
                        driver.refresh()
                        #print(e)
                        #print("try %s" %(str(i)))
                        time.sleep(30*i)
                        driver.get(document[0])
                        driver.refresh()
                    #print(contents)
                continue

            except Exception as e:
                nopage_cnt = 0
                pass      
            #
            # 가 발생했습니다
            try:
                message = driver.find_element_by_xpath('/html/body/div/div[1]/div/div/h2').text
                print()
                error_cnt += 1
                # if fail_cnt == 3:
                #     for i in range(5):
                #         print("refresh"+str(i))
                #         driver.refresh()
                #         #print(e)
                #         #print("try %s" %(str(i)))
                #         time.sleep(30*i)
                #         driver.get(document[0])
                #         driver.refresh()
                print(message)
                print(error_cnt)
                    #print(contents)
            except Exception as e:
                error_cnt = 0
                pass 
            #{"message":"몇 분 후에 다시 시도해주세요.","status":"fail"}
            try:
                message = driver.find_element_by_xpath('/html/body/pre').text
                print(contents)
                fail_cnt += 1
                for i in range(5):
                    print("try %s" %(str(i)))
                    time.sleep(120*i)
                    driver.get(document[0])
                    driver.refresh()
                    try:
                        contents = driver.find_element_by_xpath('/html/body/pre').text
                    except:
                        pass
                    #print(contents)
            except Exception as e:
                fail_cnt = 0
                pass
                
            #내용 읽어오기
            try:
                element = WebDriverWait(driver,1).until(
                EC.presence_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span')))
                contents = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span').text
                contents = contents.replace('\n', ' ').replace('#', ' ')
                #print(contents)
            except Exception as e:
                #print("2222")
                pass

            # #댓글
            # try:
            #     element = WebDriverWait(driver,1).until(
            #     EC.presence_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul[1]/div/li/div/div[1]/div[2]/span')
            #     ))
            #     elements = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul[1]/div/li/div/div[1]/div[2]/span').text
            #     elements = elements.replace('\n', ' ').replace('#', ' ')
            #     #print(contents)
                
            # except Exception as e:
            #     #print("3333")
            #     pass
            

                
            #댓글+대댓글 읽어오기
            try:
                spans = driver.find_elements_by_css_selector('div.C4VMK > span')
                spans = spans[1:]
                for span in spans:
                    comment = span.text
                    comment = comment.replace('\n', ' ').replace('#', ' ')
                    comments += ' '
                    comments += comment
                if len(contents) != 0 & pre_contents == contents:
                    #print("same contents!!")
                    time.sleep(10)
                    driver.refresh()
                    same_cnt += 1
                    continue
                else:
                    same_cnt = 0
            except:
                pass
            #시간읽어오기
            try:
                response = driver.page_source
                soup = BeautifulSoup(response,"lxml")
                date_sub = soup.select_one('#react-root > section > main > div > div.ltEKP > article > div.eo2As > div.k_Q0X.NnvRN > a > time')
                date = date_sub['title']
                date = date.replace('년 ','-').replace('월 ','-').replace('일','')
            except:
                #print("date error!")
                pass
            #author 읽어오기
            try:
                author = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/header/div[2]/div[1]/div[1]/span/a').text
            except:
                #print("author error!")
                pass
            try:
                author = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/header/div[2]/div[1]/div[1]/a').text
                #print(author)
            except:
                #print("author error!")
                pass
            if len(author)==0:
                continue
            contents = contents + ' ' + comments
            # contents = contents_limit(self.parseContents(contents))
            #print(contents)
            document += [date, author, self.parseContents(contents)]
            return_list = document
            #self.sh.saveInstaDoc(doc[1], return_list)
            # print(return_list[3])
            # print(len(return_list[3]))
            if len(return_list[3]) == 0:
                continue
            if len(had_finished) + doc_cnt <20000:
                self.sh.saveInstaDoc(keyword, return_list)
            elif len(had_finished) + doc_cnt<40000:
                self.sh.saveInstaDoc(keyword+'2',return_list)
            elif len(had_finished) + doc_cnt<60000:
                self.sh.saveInstaDoc(keyword+'3',return_list)
            elif len(had_finished) + doc_cnt<80000:
                self.sh.saveInstaDoc(keyword+'4',return_list)
            doc_cnt+=1
            if page_cnt == 200 :
                        #driver.execute_script('window.open("https://naver.com");')
                insta_handle +=1
                time.sleep(1)
                        #driver.close()
                driver.switch_to_window(driver.window_handles[insta_handle%15])
                time.sleep(1)
                page_cnt = 0
            msg = '\r진행률 : %f%%\tdoc_cnt : %d\tnew_cnt : %d\r' %((len(had_finished) + doc_cnt)/len(had_url)*100,(len(had_finished) + doc_cnt), doc_cnt)
            print(' '*len(msg), end='')
            print(msg, end ='')
            time.sleep(0.1)
            
            pre_contents = contents
            if doc_cnt % 500 == 0:
                time.sleep(3600)
        #print("doc_cnt : "+str(doc_cnt))
        #time.sleep(300)
        driver.close()
        return 
        
    def insta_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.insta_doc_crawling(doc)
            if document and len(document) >2:
                count += 1
#                print('crawl site : '+doc[0])
                with self.lock:
                    self.sh.saveInstaDoc(keyword, document)

            #else:
#                print('Error occur from insta site : '+doc[0])

    def tistory_list_crawling(self, keyword):
        page = 1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('tistory', keyword)
        had_title = self.sh.loadTitle('tistory', keyword)
        flag = True
        prev_url = ""
        while True:
            search_url = 'https://search.daum.net/search?w=blog&DA=PGD&enc=utf8&q='+query+'&f=section&SA=tistory&page='+str(page)
            response = self.getResponse(search_url)
            if not response: break
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
                
            try:
                blogcoll = soup.select_one('#blogColl')
            except Exception as e:
                pass
                
            try:
                lis = blogcoll.select('div.coll_cont > ul > li')
            except Exception as e:
                print(e)
            # print('lis length')
            # print(len(lis))
            # print(lis)
            
            for li in lis:
                try:
                    a = li.select('div.cont_inner > div > a')
                except Exception as e:
                    print("a error")
                url = a[0]['href']
                #print(url)
                title = a[0].text+'/t'
                #print(title)
                if url == prev_url:
                    flag = False
                    break
                if url in had_url or title in had_title: continue
                had_url.append(url)
                had_title.append(title)
                docs.append([url,title]) 
            prev_url = lis[0].select('div.cont_inner > div > a')[0]['href']
            #print(prev_url)
            if flag == False:
                break           
            page+=1
        print(page)
        return docs
    def tistory_doc_crawling(self,document):
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.content,'html.parser', from_encoding='utf-8')
        contents = ""
        author = "none"
        date = ""
        contents = ""
        #print(document[0])
        # print(document[1])
       


        ############################################################################33
        #text 형식이 매우 다양함 -->  error 페이지 나오는 족족 추가할 것.
        try:
            ps = soup.select('div.tt_article_useless_p_margin > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('div.entry-content > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('div.article > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            divs = soup.select('#content > article > div.article > div')
            for div in divs:
                contents += self.parseContents(div.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#content > article > div:nth-child(4) > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#mArticle > div > div.area_view > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#container > main > div > div.area-view > div.article-view > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select_one('#mArticle > div > div.area_view').select('p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#content > article > div > div.e-content.post-content.fouc > div')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#mArticle > div.area_view > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#content_permallink_article > div > div > div.box_article > div > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#content > div.inner > div.entry-content > div.tt_article_useless_p_margin')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#__permalink_article > div.article.content__permalink > article > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#content > div.inner > div.entry-content')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#content > div.entry > div.entrayContentsWrap > div.article > div')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#content_permallink_article > div > div > div.box_article > div')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#content > div.inner > div.entry-content > div:nth-child(3) > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#body > div.article > div:nth-child(1) > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#main > div > div.category_list.index_type_common.index_type_horizontal > ul > li > div > div > div.article_view > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#content_permallink_article > div > div > div.box_article > div > div')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass

        try:
            ps = soup.select('#content > div.inner > div.entry-content > div')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#tt-body-page > div.jb-page.jb-hide-menu-icon.jb-typography-3 > div.jb-background.jb-background-main > div > div > div.jb-column.jb-column-content > div.jb-cell.jb-cell-content.jb-cell-content-article > article > div.jb-content.jb-content-article > div.jb-article > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#article > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#tt-body-page > div.jb-page.jb-youtube-auto.jb-typography-3.jb-post-title-show-line.jb-another-category-1 > div.jb-background.jb-background-main > div > div > div.jb-column.jb-column-content > div.jb-cell.jb-cell-content.jb-cell-content-article > article > div.jb-content.jb-content-article > div.jb-article > div > div > p')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
        try:
            ps = soup.select('#mArticle > div.area_view > div > div')
            for p in ps:
                contents += self.parseContents(p.text)+'/t'
            #print(contents)
        except Exception as e:
            pass
         ###########################################################################3
        #author, date 를 형식 별로 수집 author이 없는 경우도 있음
        try:
            author = soup.select_one('div.content-wrap > article > div > div.post-cover > div.inner > span > span.author').text.replace('by ', '')
            date = soup.select_one('div.content-wrap > article > div > div.post-cover > div.inner > span > span.date').text
            author = self.parseContents(author)
            date = self.parseContents(date)
        except Exception as e:
            pass
       ############################################################################# 
        try:
            auth = soup.select('header.hd > div > div > span')
            #select one으로 해줘야 text가 나옴 select는 리스트로 나오므로 불가                  
            author = self.parseContents(auth[1].text)
            date = soup.select_one('header.hd > div > div > abbr').text
            date = self.parseContents(date)
            #print(author)
        except Exception as e:
            pass

            ####################################################################
            #type3
        try:
            author = soup.select_one('section.container > article > div > div > div > span.author').text
            date =  soup.select_one('section.container > article > div > div > div > span.date').text
            #select one으로 해줘야 text가 나옴 select는 리스트로 나오므로 불가             
            author = self.parseContents(author)
            date = self.parseContents(date)     
            #print(title)
        except Exception as e:
            pass

        #택스트는 형식 동일
        ############################################################################3
        #type4
        try:
            date = soup.select_one('div.titleWrap > div > span.date').text
            author = soup.select_one('div.titleWrap > div > a').text
            author = self.parseContents(author)
            date = self.parseContents(date)
            #print(date)
            #select one으로 해줘야 text가 나옴 select는 리스트로 나오므로 불가                 
            
        except Exception as e:
            pass
        try:
            date = soup.select_one('div.titleWrap > div > div.date').text
            author = soup.select_one('div.titleWrap > div > a').text
            author = self.parseContents(author)
            date = self.parseContents(date)
            #print(date)
            #select one으로 해줘야 text가 나옴 select는 리스트로 나오므로 불가                 
        except Exception as e:
            pass
        ##################################################################################3
        try:
            auth = soup.select_one('div.area_title > span').text[:-40]
            date = soup.select_one('div.area_title > span').text[-40:]
            author = self.parseContents(auth)
            date = self.parseContents(date)
            #select one으로 해줘야 text가 나옴 select는 리스트로 나오므로 불가                 	
        except Exception as e:
            pass
        #######################################################################################
        try:
            author = soup.select_one('div.inner-header > div > div > span.writer').text
            date =  soup.select_one('div.inner-header > div > div > span.date').text
            #select one으로 해줘야 text가 나옴 select는 리스트로 나오므로 불가             
            author = self.parseContents(author)
            date = self.parseContents(date)     
            #print(title)
        except Exception as e:
            pass
        ########################################################################################
        try:
            date = soup.select_one('div.date').text
            date = self.parseContents(date)     
        except Exception as e:
            pass
        ########################################################################################
        try:
            date = soup.select_one(' #global-header > div > ul > li.digit').text
            date = self.parseContents(date)     
        except Exception as e:
            pass
        ########################################################################################
        try:
            date = soup.select_one('#tt-body-page > div.jb-page.jb-youtube-auto.jb-typography-3.jb-post-title-show-line.jb-another-category-1 > div.jb-background.jb-background-main > div > div > div.jb-column.jb-column-content > div.jb-cell.jb-cell-content.jb-cell-content-article > article > header > div > div > ul > li:nth-child(2) > span').text
            date = self.parseContents(date)     
        except Exception as e:
            pass
        #######################################################################################
        try:
            date = soup.select_one('#content > article > span.articleDate').text
            date = self.parseContents(date)     
        except Exception as e:
            pass
        try:
            date = soup.select_one('#main > div > div.category_list.index_type_common.index_type_horizontal > ul > li > div > div > div.info_post > div > span').text         
            date = self.parseContents(date) 
        except Exception as e:
            pass
        ############################################################################################3
        #content > article > div.author
        try:
            author = soup.select_one('#content > article > div.author').text.replace("Posted by", '')
            author = self.parseContents(author)     
        except Exception as e:
            pass
        ##########################################################################################
        try:
            date = soup.select_one('#content > div.entry > div.titleWrap > p > span.date').text
            author = soup.select_one('#content > div.entry > div.titleWrap > p > span.category > a').text
            author = self.parseContents(author)
            date = self.parseContents(date)
        except Exception as e:
            pass
        #######################################################################################33
        try:
            date = soup.select_one('#content_permallink_article > div > div > div.box_article_tit > div > p > span.date').text
            author = soup.select_one('#content_permallink_article > div > div > div.box_article_tit > div > p > span.name > span').text
            author = self.parseContents(author)
            date = self.parseContents(date)
        except Exception as e:
            pass
        #####################################################################################
        try:
            date = soup.select_one('#tt-body-page > div.jb-page.jb-hide-menu-icon.jb-typography-3 > div.jb-background.jb-background-main > div > div > div.jb-column.jb-column-content > div.jb-cell.jb-cell-content.jb-cell-content-article > article > header > div > div > ul > li:nth-child(2) > span').text
            author =  soup.select_one('#tt-body-page > div.jb-page.jb-hide-menu-icon.jb-typography-3 > div.jb-background.jb-background-main > div > div > div.jb-column.jb-column-content > div.jb-cell.jb-cell-content.jb-cell-content-article > article > header > div > div > ul > li:nth-child(1) > span > a').text
            author = self.parseContents(author)
            date = self.parseContents(date)
        except Exception as e:
            pass
        
        if len(contents) == 0: return document
        document += [date, author, contents]
        #print(document)
        return document


    def tistory_docs_crawling(self,process,keyword, docs):
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.tistory_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.savetistoryDoc(keyword, document)
            else:
                print('Error occur from tistory site : '+doc[0])
                print(doc)
        return

    def hygall_list_crawling(self,keyword):
        page =1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('hygall',keyword)
        had_title = self.sh.loadTitle('hygall',keyword)
        while True:
            
            search_url = 'https://hygall.com/index.php?mid=hy&search_target=title_content&search_keyword='+query+'&page='+str(page)
            response = self.getResponse(search_url)
            if not response: break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            try:
                now_page = int(soup.find("div",{"class":"exPagNav a1"}).find("strong").text)
            except Exception as e: break
            if not page == now_page: break
            
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from hygall.')
            flag = True
            try:
                trs = soup.find_all("tr",{"class":"docList exBg0"})
            except Exception as e:
                print(e)
                #sys.stdout.write(search_url)
                continue
            for tr in trs:
                if flag:
                    flag = False
                    continue
                a = tr.find("td",{"class":"title"}).find("a")
                url = a['href']
                title = a.text+'/t'
                if url in had_url or title in had_title: continue
                had_url.append(url)
                had_title.append(title)
                docs.append([url,title])
                
            page+=1
        return docs
 
    def hygall_doc_crawling(self,document):
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
        comment = '\n'
        authors = "none"
        try:
            time_line =self.parseContents(soup.find("div",{"class":"date"}).text.replace(".","-"))
        except Exception as e:
            time_line = "none"
        try:
            contents = self.parseContents(soup.find("div",{"class":"cntBody"}).find("div").text)+'/t'
        except Exception as e:
            return document
        try:
            divs = soup.find("div",{"class":"exRepBox"}).find_all("div",{"class":re.compile(r'repItm.+')})
        except Exception as e:
            #contents = contents_limit(contents)

            document +=[time_line,authors,contents]
            return document
        try:
            for div in divs:
                comment = div.find("div",{"class":"repCnt"}).find("div").text
                contents += self.parseContents(comment +'.')+'/t'
        except Exception as e:
            pass
        #contents = contents_limit(contents)

        document += [time_line,authors,contents]
        return document





    def hygall_docs_crawling(self, process, keyword, docs):
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.hygall_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.saveHygallDoc(keyword, document)
#            else:
#                print('Error occur from hygall site : '+doc[0])
        return

    def slrclub_list_crawling(self,keyword):
        page =1
        xpath_num = 1
        first = True
        urls = []
        docs=[]
        Id = 'wotkddl21'
        Pw = 'araelap12!'
        query = self.quote(keyword)
        had_url = self.sh.loadURL('slrclub',keyword)
        had_title = self.sh.loadTitle('clrclub',keyword)
######################## login process ##################################
        login_url = 'http://www.slrclub.com/'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--incognito')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        driver.get(login_url)
        try:
            uid = driver.find_element_by_name('user_id')
            uid.clear()
            uid.send_keys(Id)
            uid = driver.find_element_by_name('password')
            uid.clear()
            uid.send_keys(Pw)
            uid.submit()
        except:
            pass
        time.sleep(1)
        response = driver.page_source
        soup = BeautifulSoup(response,"lxml")
##########################login complete ###############################
        keyword_area = driver.find_element_by_name('keyword')
        keyword_area.clear()
        keyword_area.send_keys(keyword)
        keyword_area.submit()
        while True:
    #        if page >10:
    #            break
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from slrclub.')
            response = driver.page_source
            soup = BeautifulSoup(response,"lxml")
            lis = soup.select('#content > div.mainWrap > div > ul.list > li')
            try:
                for li in lis:
                    a = li.find("p",{"class":"title"}).find("a")
                    url = 'http://slrclub.com'+a['href']
                    title = a.text+'/t'
                    if url in had_url or title in had_title: continue
                    docs.append([url,title])
                    had_url.append(url)
                    had_title.append(title)
            except Exception as e:
                return docs
    
            try:
                if xpath_num>10:
                    xpath_num = 1
                if first:
                    first = False
                    driver.find_element_by_xpath('//*[@id="bbs_foot"]/tbody/tr/td[2]/table/tbody/tr/td/a[%s]' %(xpath_num)).click()  # 1 clicki
                else:
                    if page <=10:
                        if xpath_num+1 == 11:
                            xpath_num = 11
                        driver.find_element_by_xpath('//*[@id="bbs_foot"]/tbody/tr/td[2]/table/tbody/tr/td/a[%s]' %(xpath_num+1)).click() # 3~11 click where xpath_num : 2~10
                    else:
                        if xpath_num+3 == 13:
                            xpath_num = 11
                        driver.find_element_by_xpath('//*[@id="bbs_foot"]/tbody/tr/td[2]/table/tbody/tr/td/a[%s]' %(xpath_num+3)).click()
            except Exception as e:
#                print(e)
                return docs
            xpath_num+=1
            page+=1
            # if page == 10:
            #     return docs
        return docs
    def slrclub_doc_crawling(self,document):
        
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--incognito')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        driver.get(document[0])
#        response = self.getResponse(document[0])
        response = driver.page_source
        if not response: return document
#        soup = BeautifulSoup(response.text,"lxml")
        soup = BeautifulSoup(response,'lxml')
        comment = '\n'
        author = ""
        time_line = ""
        contents = ""
        ######################## time_line, author, contents #################
        try:
#            tr = soup.find("table",{"class":"bbs_tbl_layout"}).find_all("tr")[1]
            author = self.parseContents(soup.find("td",{"class":"nick"}).text)
            time_line = self.parseContents((soup.find("td",{"class":"date bbs_ct_small"}).text).replace('/','.'))
            contents = self.parseContents(soup.find("div",{"id":"userct"}).text)
        except Exception as e:
#            print(e)
            return document
        ########################## comments #########################
        try:
            driver.find_element_by_xpath('//*[@id="comment_pgc"]/img[2]').click()
        except:
            pass
        contents += '/t'
        time.sleep(1)
        response = driver.page_source
        if not response: return document
        soup = BeautifulSoup(response,"lxml")
        try:
            divs = soup.find_all("div",{"class":"cmt-contents"})
            for div in divs:
                comment = self.parseContents(div.text)
                comment += '/t'
                # contents += comment +'.'
            document += [time_line,author,contents]
        except Exception as e:
            #contents = contents_limit(contents)
            document += [time_line,author,contents]

        return document

    def slrclub_docs_crawling(self, process, keyword, docs):
        
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.slrclub_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
#                print("crawl from : "+doc[0])
                with self.lock:
                    self.sh.saveSlrclubDoc(keyword, document)
#            else:
#                print('Error occur from slrclub site : '+doc[0])
        return



    def ygosu_list_crawling(self,keyword):
        page =1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('ygosu',keyword)
        while True:
            search_url = 'https://www.ygosu.com/all_search/?type=board&add_search_log=Y&keyword='+query+'&order=1&page='+str(page)
            response = self.getResponse(search_url)
            #sys.stdout.write(search_url)
            if not response: break
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            try:
                now_page = int(soup.find("div",{"class":"paging"}).find("span",{"class":"num"}).find("b").text)
            except Exception as e: 
                print(e)
                #sys.stdout.write(search_url)
                break
            if not page == now_page: break
            lis = soup.find("ul",{"class":"type_board2"}).find_all("li")
            print ('"'+keyword+'" list is crawling page '+str(page)+' from ygosu.')
            url =""
            for li in lis:
                b = li.find_all("a")
                url = b[0]['href']
                title = b[0].text+'/t'
                if url in had_url: continue
                docs.append([url,title])
                had_url.append(url)
            page+=1
        return docs
 
    def ygosu_doc_crawling(self,document):
        
        response = self.getResponse(document[0])
        if not response: return document
#        soup = BeautifulSoup(response.text,"lxml")
        soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
        comment = '\n'
        try:
            time_line =soup.find("div",{"class":"bottom"}).find("div",{"class":"date"}).text.replace('.','-')
        except:
            time_line = '0000-00-00'
        try:
            author = soup.find("div",{"class":"contain_user_info"}).find("div",{"class":"nickname"}).find("a").text
        except:
            author = 'none'
        
        try:
            contents = soup.find("div",{"class":"container"}).text +'/t'
            
        except:
            return document
        try:
            table = soup.find("table",{"id":"reply_list_layer"})
            tbody = table.find("tbody")
            trs = tbody.find_all("tr")
        except:
            document += [time_line,author,contents]
            return document
        for tr in trs:
            try:
                comment += self.parseContents(tr.find("td",{"class":"comment"}).text) +'/t'
            except:
                pass
        contents+=comment
       # contents = contents_limit(contents)
        document += [time_line,author,contents]
        #except Exception as e:
        #    return document
        return document





    def ygosu_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.ygosu_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.saveYgosuDoc(keyword, document)
            else:
                print('Error occur from ygosu site : '+doc[0])



    def humoruniv_list_crawling(self,keyword):
        page =1
        docs = []
        temp = 'site:http://web.humoruniv.com '+keyword
        query = self.quote(temp)
        had_url = self.sh.loadURL('humoruniv',keyword)
        flag = True
        temp1=""
        while True:
            search_url = 'https://search.daum.net/search?w=web&q='+temp+'&DA=PGD&detail_query='+self.quote(keyword)+'&p='+str(page)
            
            response = self.getResponse(search_url)
            
            if not response:
                break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            
            lis = soup.find("ul",{"class":"list_info clear"}).find_all("li")
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from humoruniv.')
            if temp1 == lis[0].find("a")['href']:
                
                break
            else: temp1 = lis[0].find("a")['href']
            for li in lis:
                
                a = li.find("a")
                url = a['href']
                title = a.text +'/t'
                try:
                    time_line = li.find("span",{"class":"f_date date"}).text.replace('.','-')
                except:
                    time_line = "none"
                if url in had_url: continue
                docs.append([url,title,time_line])
                had_url.append(url)
                
            page+=1
        return docs
 
    def humoruniv_doc_crawling(self,document):
        
        response = self.getResponse(document[0])
        if not response: return document
#        soup = BeautifulSoup(response.text,"lxml")
        soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
        comment = ' '
        try:
            author = self.parseContents(soup.find("span",{"class":"hu_nick_txt"}).text)
            contents = self.parseContents(soup.find("span",{"id":"ai_cm_content"}).text)+'/t'
            try:
                tr = soup.find_all("tr",{"id":re.compile(r'comment_span_[0-9]+')})
                for com in tr:
                    comment += com.find("td",{"width":"380"}).find("span",{"class":"cmt_list"}).text +'/t'
                comment = self.parseContents(comment)
                #contents = contents_limit(contents+comment)
                contents+=comment
                # document+= [author,contents+comment]
            except Exception as e:
                print(e)
                pass
            document+= [author,contents]
        except Exception as e:
            return document
        return document





    def humoruniv_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.humoruniv_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.saveHumorunivDoc(keyword, document)
#            else:
#                print('Error occur from humoruniv site : '+doc[0])
        return 


    def etoland_list_crawling(self,keyword):
        page =1
        docs = []
        temp = 'site:http://etoland.co.kr '+keyword
        query = self.quote(temp)
        had_url = self.sh.loadURL('etoland',keyword)
        flag = True
        temp = ""
        while True:
            search_url = 'https://search.daum.net/search?w=web&q='+query+'&DA=PGD&detail_query='+self.quote(keyword)+'&p='+str(page)
            response = self.getResponse(search_url)
            if not response: break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            lis = soup.find("ul",{"class":"list_info clear"}).find_all("li")
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from etoland.')
            if temp == lis[0].find("a",{"class":"f_url"})['href']: break
            else: temp = lis[0].find("a",{"class":"f_url"})['href']
            for li in lis:
                a = li.find("a",{"class":"f_url"})
                url = a['href']
                title = a.text+'/t'
                if url in had_url: continue
                docs.append([url,title])
                had_url.append(url)
            page+=1
        return docs

    def etoland_doc_crawling(self,document):
        
        response = self.getResponse(document[0])
        if not response: return document
#        soup = BeautifulSoup(response.text,"lxml")
        soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
        comment = '\n'

        table = soup.find_all("table",{"class":"mw_basic_comment_content"})
        try:
            td = soup.find("td",{"class":"mw_basic_view_title"})
            time_line =self.parseContents(td.find("span",{"class":"mw_basic_view_datetime"}).text.replace(".","-"))
            author = self.parseContents(td.find("span",{"class":"member"}).text)
            td = soup.find("td",{"class":"mw_basic_view_content"})
            contents = self.parseContents(td.find("div").text)+'/t'
            try:
                table = soup.find_all("table",{"class":"mw_basic_comment_content"})
                for td in table:
                    comment += td.text+'/t'
                #contents = contents_limit(contents+comment)
                contents+=comment
                document += [time_line,author,contents]
            except Exception as e:
#                contents = contents_limit(contents)
                document+=[time_line,author,contents]
        except Exception as e:
            return document
        return document





    def etoland_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.etoland_doc_crawling(doc)
            if document and len(document) >3:
                count += 1
                with self.lock:
                    self.sh.saveEtolandDoc(keyword, document)
#            else:
#                print('Error occur from etoland site : '+doc[0])
        return 

    def theqoo_list_crawling(self,keyword):
        page =1
        docs = []
        temp = 'site:https://theqoo.net '+keyword
        query = self.quote(temp)
        had_url = self.sh.loadURL('theqoo',keyword)
        flag = True
        temp = ""
        while True:
            search_url = 'https://search.daum.net/search?w=web&q='+query+'&DA=PGD&detail_query='+self.quote(keyword)+'&p='+str(page)
            response = self.getResponse(search_url)
            if not response: break
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            lis = soup.find("ul",{"class":"list_info clear"}).find_all("li")
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from theqoo.')
            if temp == lis[0].find("a")['href']: break
            else: temp = lis[0].find("a")['href']
            for li in lis:
                a = li.find("a")
                url = a['href']
                title = a.text+'/t'
                if url in had_url: continue
                docs.append([url,title])
                had_url.append(url)
            page+=1
        return docs
 
    def theqoo_doc_crawling(self,document):
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        driver.get(document[0])
        
        clicknum=0
        while True:
            try:
                driver.find_element_by_class('show_more comment_header').click()
            except Exception as e: break
            clicknum+=1
        try:
            response = driver.page_source
        except:
            print(document[0])
        if not response: return document
        soup = BeautifulSoup(response,"lxml")
        commentnum=1
        comments='\n'
        try:
            btm_area = soup.find("div",{"class":"btm_area clear"})
            time_line = self.parseContents(btm_area.find("div",{"class":"side fr"}).text.replace(".","-"))
            author = self.parseContents(btm_area.find("div",{"class":"side"}).text)
            contents = self.parseContents(soup.find("article",{"itemprop":"articleBody"}).text)+'/t'
            try:
                lis = soup.find("ul",{"class":"fdb_lst_ul"}).find_all("li")
                for li in lis:
                    div = li.find_all("div")
                    comments += (div[1].text).strip()+'/t'
                #contents = contents_limit(contents+comments)
                contents+=comments
                document += [time_line,author,contents+comments]
            except Exception as e:
#                contents = contents_limit(contents)
                document += [time_line,author,contents]
        except Exception as e:
            driver.close()
            return document
        driver.close()
        return document





    def theqoo_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.theqoo_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.saveTheqooDoc(keyword, document)
#            else:
#                print('Error occur from fm_korea site : '+doc[0])
        return 







    def fmkorea_list_crawling(self,keyword):
        page =1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('fmkorea',keyword)
        while True:
            
            search_url = 'https://www.fmkorea.com/index.php?act=IS&is_keyword='+query+'&mid=home&where=document&page='+str(page)
            response = self.getResponse(search_url)
            if not response: break
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            #sys.stdout.write(search_url)
            try:
                now_page = int(soup.find("div",{"class":"pagination a1"}).find("strong").text)
            except Exception as e: 
                print(e)
                #sys.stdout.write(search_url)
                break
            if not page == now_page: break
            lis = soup.find("ul",{"class":"searchResult"}).find_all("li")
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from fm_korea.')
            for li in lis:
                a = li.find("a")
                url = 'https://www.fmkorea.com'+a['href']
                title = a.text+'/t'
                if url in had_url: continue
                docs.append([url,title])
                had_url.append(url)
            page+=1
        return docs

    def fmkorea_doc_crawling(self,document):
        
        time.sleep(1)
        response = self.getResponse(document[0])
        if not response: return document
#        soup = BeautifulSoup(response.text,"lxml")
        soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
        temp = ""
        try:
            time_line =self.parseContents(soup.find("div",{"class":"top_area ngeb"}).find("span").text.replace(".","-"))
            author = self.parseContents(soup.find("div",{"class":"btm_area clear"}).find("div",{"class":"side"}).find("a").text)
            contents = self.parseContents(soup.find("article").text)+'/t'
            document += [time_line,author,contents]
        except Exception as e:
            return document
        return document

    def fmkorea_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+" fm_korea Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.fmkorea_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.saveFmkoreaDoc(keyword, document)
#            else:
#                print('Error occur from fm_korea site : '+doc[0])

        return

    def bobae_list_crawling(self,keyword):   # 보배드림
        page =1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('bobae',keyword)
        ####################################### 자유게시판 ######################################
        while True:
            search_url = 'https://m.bobaedream.co.kr/board/new_writing/freeb/'+str(page)+'?keyword='+query+'&s_cate=Body'
            response = self.getResponse(search_url)
            if not response: break
            #sys.stdout.write(search_url)
            #soup = BeautifulSoup(response.text,"lxml")
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            try:
                now_page = int(soup.find("div",{"class":"page"}).find("span",{"class":"num"}).find("a",{"class":"on"}).text)
            except Exception as e:  break
            if not page == now_page: break
            
            lis = soup.find("ul",{"class":"rank"}).find_all("li")
            
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from bobaedream free board.')
            for li in lis:
                info = li.find("div",{"class":"info"})
                a = info.find("a")
                test = a['href'].split('/')
                url ='https://m.bobaedream.co.kr/'+ test[1]+'/'+test[2]+'/'+test[3]+'/'+test[4]+'/'+test[5]+'/'+str(page)+'?keyword='+query+'&s_cate=Subject'
                title = a.find("div",{"class":"txt"}).find("span",{"class":"cont"}).text
                if url in had_url: continue
                docs.append([url,title])
                had_url.append(url)
            page+=1
        ####################################### 정치게시판 ######################################
        page =1
        
        while True:
            search_url = 'https://m.bobaedream.co.kr/board/new_writing/politic/'+str(page)+ '?keyword='+query+'&s_cate=Body'
            response = self.getResponse(search_url)
            if not response: break
            #soup = BeautifulSoup(response.text,"lxml")
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            try:
                now_page = int(soup.find("div",{"class":"page"}).find("span",{"class":"num"}).find("a",{"class":"on"}).text)
            except Exception as e: break
            if not page == now_page: break
            lis = soup.find("ul",{"class":"rank"}).find_all("li")
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from bobaedream politic board.')
            for li in lis:
                info = li.find("div",{"class":"info"})
                a = info.find("a")
                test = a['href'].split('/')
                url ='https://m.bobaedream.co.kr/'+ test[1]+'/'+test[2]+'/'+test[3]+'/'+test[4]+'/'+test[5]+'/'+str(page)+'?keyword='+query+'&s_cate=Subject'
                title = a.find("div",{"class":"txt"}).find("span",{"class":"cont"}).text
                if url in had_url: continue
                docs.append([url,title])
                had_url.append(url)
            page+=1






        ####################################### 유머게시판 ######################################
        page =1
        while True:
            search_url = 'https://m.bobaedream.co.kr/board/new_writing/strange/'+str(page)+ '?keyword='+query+'&s_cate=Body'
            response = self.getResponse(search_url)
            if not response: break
           # soup = BeautifulSoup(response.text,"lxml")
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            try:
                now_page = int(soup.find("div",{"class":"page"}).find("span",{"class":"num"}).find("a",{"class":"on"}).text)
            except Exception as e: break
            if not page == now_page: break
            lis = soup.find("ul",{"class":"rank"}).find_all("li")
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from bobaedream humor board.')
            for li in lis:
                info = li.find("div",{"class":"info"})
                a = info.find("a")
                test = a['href'].split('/')
                url ='https://m.bobaedream.co.kr/'+ test[1]+'/'+test[2]+'/'+test[3]+'/'+test[4]+'/'+test[5]+'/'+str(page)+'?keyword='+query+'&s_cate=Subject'
                title = a.find("div",{"class":"txt"}).find("span",{"class":"cont"}).text
                if url in had_url: continue
                docs.append([url,title])
                had_url.append(url)
            page+=1

        return docs  # [  [url,title], [url,title], [url,title] ]      
    def bobae_doc_crawling(self,document):
        
        response = self.getResponse(document[0])
        if not response: return document
#        soup = BeautifulSoup(response.text,"lxml")
        soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
        comment = '\n'
        try:
            article = soup.find("article",{"class":"article"})
            header = article.find("header",{"class":"article-tit"})
            time_line =self.parseContents(header.find("div",{"class":"util"}).find("time").text.replace(".","-"))
            author = self.parseContents(header.find("div",{"class":"util2"}).find("div",{"class":"info"}).find("span").text)
            contents = article.find("div",{"class":"article-body"}).text
        except:
            return document
        try:
            lis = soup.find("div",{"class":"reply-area"}).find("div",{"class":"reple_body"}).find("ul").find_all("li")
            for li in lis:
                try:
                    text = li.find("div",{"class":"con_area"}).find("div",{"class":"reply"}).text
                    comment += text+'\n'
                except:
                    pass
            document +=[time_line,author,(contents + self.parseContents(comment))]
        except Exception as e:
            document += [time_line,author,contents]
        return document  #[ url,title,time,author,contents ]

        
    def bobae_docs_crawling(self, process, keyword, docs):
        count = 1
        total = len(docs)
        print("Process "+str(process)+" bobae Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.bobae_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.saveBobaeDoc(keyword, document)
            else:
                print("Error on : "+doc[0])
        return

    def pann_list_crawling(self,keyword):    #네이트 판
        page = 1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('pann',keyword)
#        while True:
        while True:
            search_url = 'https://pann.nate.com/search/talk?q='+query+'&page='+str(page)
            response = self.getResponse(search_url)
            if not response: break
            soup = BeautifulSoup(response.text, "lxml")
            #sys.stdout.write(search_url)
            try:
                now_page = int(soup.find("div",{"class":"paginate"}).find("strong",{"class":"current"}).text)
                
            except Exception as e: break
            if page == 100: break
            if not page == now_page: break
            lis = soup.find("ul",{"class":"s_list"}).find_all("li")
            #print ('"'+keyword+'" list is crawling page '+str(page)+' from talk talk pann.')
            for li in lis:
                a = li.find("a",{"class":"subject"})
                url = 'https://pann.nate.com'+a['href']
                if url in had_url : continue
                title = a.text+'/t'
                docs.append([url,title])
                had_url.append(url)
            page+=1
        #톡톡 clear
        page=1
#        while True:
        for t in range(0,1):
            search_url = 'https://pann.nate.com/search/fantalk?q='+query+'&page='+str(page)
            response = self.getResponse(search_url)
            if not response: break
            soup = BeautifulSoup(response.text, "lxml")
            try:
                now_page = int(soup.find("div",{"class":"paginate"}).find("strong",{"class":"current"}).text)
            except Exception as e: break
            if not page == now_page: break
            lis = soup.find("ul",{"class":"s_list"}).find_all("li")
            for li in lis:
                a = li.find("a",{"class":"subject"})
                url = 'https://pann.nate.com'+a['href']
                if url in had_url : continue
                title = a.text+'/t'
                docs.append([url,title])
            page+=1
        #팬톡 clear
        return docs

    def pann_doc_crawling(self,document):
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        # print(document[0])
        try:
            driver.get(document[0])
            time.sleep(1.5)
        except Exception as e:
            pass
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")
        comments = '\n'
        try:
            info = soup.find("div",{"class":"info"})
            author = info.find("a",{"class":"writer"}).text
            date_line = info.find("span",{"class":"date"}).text.replace(".","-")
            contents = soup.find("div",{"class":"posting"}).find("div",{"id":"contentArea"}).text
        except Exception as e:
            return document
        page=1
        author = self.parseContents(author)
        contents = self.parseContents(contents+comments)+'/t'
        while True:
            response = driver.page_source
            try:
                cmt_list = soup.find("div",{"class":"cmt_list"}).find_all("dl")
                for cmt in cmt_list:
                    comments+= cmt.find("dd",{"class":"usertxt"}).find("span").text +'/t'
            except Exception as e:
                #contents = contents_limit(contents+comments)
                contents+=comments
                document += [author,date_line,contents]
                return document
            page+=1
            try:
                driver.find_element_by_xpath('//*[@id="commentDiv"]/div[2]/a[%s]' %((page-1)%11)).click()
#                        //*[@id="commentDiv"]/div[2]/a[1]  //*[@id="commentDiv"]/div[2]/a[2]  //*[@id="commentDiv"]/div[2]/a[10]
            except Exception as e:
                break
        document += [author,date_line, contents]

        return document
    def pann_docs_crawling(self, process, keyword, docs):
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+" Pann Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.pann_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.savePannDoc(keyword, document)
#            else:
#                print('Error occur from pann site : '+doc[0])
        return

        
    def naver_list_crawling(self,keyword):
        urls=[]
        page =1
        query = self.quote(keyword)
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        had_url = self.sh.loadURL('naver',keyword)
        had_title = self.sh.loadTitle('naver',keyword)
        
        while True:
#        for i in range(0,10):
            
            search_url = 'https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery='+query+'&pagingIndex='+str(page)+'&pagingSize=20&productSet=total&query='+query+'&sort=review&timestamp=&viewType=list'
            driver.get(search_url)
            elem = driver.find_element_by_tag_name("body")
            pagedowns=1
            while pagedowns <30:
                elem.send_keys(Keys.PAGE_DOWN)
                pagedowns+=1
            response = driver.page_source
#            response = self.getResponse(search_url)
            if not response: 
#                print("no")
                return
#            soup = BeautifulSoup(response.text,"lxml")
            #print(page)
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from Naver.')
            soup = BeautifulSoup(response,"lxml")
            try:
                temp_now_page = soup.find("div",{"class":"pagination_num__-IkyP"}).find("span",{"class":"pagination_btn_page__FuJaU active"}).text
                now_page = re.findall("\d+",temp_now_page)
            except Exception as e: break
            if not page == int(now_page[0]): break
            lists = soup.find_all("div",{"class":"basicList_title__3P9Q7"})
            prev_urls=[]
            current_urls=[]
            
            for item in lists:
                flag = False
                a = item.find("a")
                url = a['href']
                title = a.text+'/t'
                driver.get(url)
                try:
                    rs = driver.page_source
                    bs = BeautifulSoup(rs,"lxml")
                    loading = bs.find("div",{"class":"loading_area"}).text
                    if loading :
                        flag = True  # 네이버쇼핑이 아니고 다른 쇼핑몰로 넘어가는 경우 loading == 해당 쇼핑몰로 이동중입니다.
                except Exception as e:
                    pass
                if url in had_url or flag or title in had_title: continue
                urls.append([url,title])
                if page == 1:
                    prev_urls.append(url)
                else:
                    current_urls.append(url)
                had_url.append(url)
                had_title.append(title)
            flag = False
            if len(current_urls) == len(prev_urls) and len(current_urls)!=0:
                flag = True
                for j in range(0,len(prev_urls)):
                    if current_urls[j] != prev_urls[j] :
                        flag = False
            if flag:
                driver.close()
                return urls                  
            else:
                prev_urls = current_urls
            page+=1
            
#쇼핑 검색 목록 url모음
        driver.close()
        return urls
    
    def naver_doc_crawling(self, document):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        driver.get(document[0])
        elem = driver.find_element_by_tag_name("body")
        page=1
        contents = ""
        authors = ""
        time_line = ""
        response = driver.page_source
        soup = BeautifulSoup(response,"lxml")
        flag = True
        try:
#            test = soup.find("a",{"class":"_purchase_review_tab link N=a:tab.review"}).text
#            test = soup.find("a",{"href":"#revw"})
            test = soup.find_all("li",{"class":"thumb_nail"})[0].find("div",{"class":"atc_area"})
            flag = True
        except Exception as e:
            flag = False
        if flag:
            xpath_num=2
            while True:
                elem = driver.find_element_by_tag_name("body")
                pagedowns=1
                while pagedowns <30:
                    elem.send_keys(Keys.PAGE_DOWN)
                    pagedowns+=1
                response = driver.page_source
                if not response:
                    return
                soup = BeautifulSoup(response,"lxml")
                try:
                    lis = soup.find_all("li",{"class":"thumb_nail"})
                    for li in lis:
                        try:
                            content = li.find("div",{"class":"atc_area"}).find("div",{"class":"atc"}).text
                            author = li.find("span",{"class":"info"}).find_all("span",{"class":"info_cell"})[1].text
                            content = self.parseContents(content)
                            author = self.parseContents(author)
                            contents += content +'/t'
                            authors += author + '.'
                        except Exception as e:
                            if len(contents)<=1:
                                return document
                            else:
                                #contents = contents_limit(contents)
                                document +=[time_line,authors,contents]
                            return document
                except Exception as e:
                    return document
                try:
                    if xpath_num>11:  # 2~11
                        xpath_num=2
                    if page >10:
                        driver.find_element_by_xpath('//*[@id="_review_paging"]/a[%s]' %(xpath_num+1)).click()  # 3~12
                    else:
                        driver.find_element_by_xpath('//*[@id="_review_paging"]/a[%s]' %(xpath_num-1)).click()  # 1~10
                except Exception as e:
                    try:
                        if page>10:
                            driver.find_element_by_xpath('//*[@id="area_review_list"]/nav/a[%s]' %(xpath_num+1)).click()  # 3~12
                        else:
                            driver.find_element_by_xpath('//*[@id="area_review_list"]/nav/a[%s]' %(xpath_num)).click()  # 2~11
                    except Exception as e:
                        try:
                            if page>10:
                                driver.find_element_by_xpath('//*[@id="area_review_list"]/div[4]/a[%s]'%(xpath_num+1)).click()  # 3~12
                            else:
                                driver.find_element_by_xpath('//*[@id="area_review_list"]/div[4]/a[%s]'%(xpath_num-1)).click()  # 1~10
                        except:
                            break 



                page+=1
                xpath_num+=1
            if len(contents)<=1:
                return document
            #contents = contents_limit(contents)
            document +=[time_line,authors,contents]
        else:
            xpath_num=2
            driver.get(document[0]+'#revw')
            while True:
                response = driver.page_source
                soup = BeautifulSoup(response,"lxml")
                try:
                    lis = soup.find("div",{"class":"area_review"}).find("div",{"class":"detail_list_review _review_list"}).find("ul").find_all("li",{"class":"item_review _review_list_item_wrap"})
                    for li in lis:
                        content = li.find("span",{"class":"text"}).text
                        author = li.find("div",{"class":"area_status_user"}).find("span").text
                        contents += self.parseContents(content)+'\n'
                        authors += self.parseContents(author)+'\n'
                except Exception as e:
                    if len(contents)<=1:
                        return document
                    else:
                        #contents = contents_limit(contents)
                        document += [time_line,authors,contents]
                    return document
                try:
                    if xpath_num>11:  
                        xpath_num=2
                    if page >10:  # 3~12
                        driver.find_element_by_xpath('//*[@id="area_review_list"]/nav/a[%s]' %(xpath_num+1)).click()
                    else: # 2~11
                        driver.find_element_by_xpath('//*[@id="area_review_list"]/nav/a[%s]' %(xpath_num)).click()
                except Exception as e:
                    try:
                        if page>10:
                            driver.find_element_by_xpath('//*[@id="area_review_list"]/div[4]/a[%s]' %(xpath_num+1)).click()
                        else:
                            driver.find_element_by_xpath('//*[@id="area_review_list"]/div[4]/a[%s]' %(xpath_num-1)).click()
                    except Exception as e:
                        break
                page+=1
                xpath_num+=1
            if len(contents)<=1:
                return document
            #contents = contents_limit(contents)
            document+=[time_line,authors,contents]
        driver.close()
        print(document)
        return document
        
    def dcinside_list_crawling(self, keyword) :
        page = 1
        docs = []
        had_url = self.sh.loadURL('dcinside',keyword)
        while True :
            search_url = 'http://search.dcinside.com/post/p/'+str(page)+'/sort/latest/q/'+self.quote(keyword)
            response = self.getResponse(search_url)
            
            if not response: break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.text, "lxml")

            try:
                now_page = int(soup.find("div", {"id":"dgn_btn_paging"}).find("em").text)
            except Exception as e: break
            if not page == now_page: break
 #           print ('"'+keyword+'" list is crawling page '+str(page)+' from Dcinside.')
            ul = soup.find("ul",{"class":"sch_result_list"}).find_all("li")
            for li in ul :
                url = li.find("a",{"class":"tit_txt"})["href"]
                if url in had_url: continue
                date_line = li.find("span",{"class":"date_time"}).text.replace(".","-")
                title = li.find("a",{"class":"tit_txt"}).text+'/t'
                docs.append([url, title, date_line])
                had_url.append(url)
            page += 1

        return docs 
    
    def ruliweb_list_crawling(self, keyword) :
        page =1
        docs = []
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        query = self.quote(keyword)
        had_url = self.sh.loadURL('ruliweb',keyword)
        flag = True
        
        while True:
            
            search_url = 'https://bbs.ruliweb.com/search?q='+query +'&page='+ str(page) +'#board_search&gsc.tab=0&gsc.q='+query+'&gsc.page=1'
            driver.get(search_url)
            response = requests.get(search_url,headers = headers)
            
            if not response: break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.text,"lxml")
            try:
                for i in range(1,16):
                    try:
                        li = driver.find_element_by_css_selector('#board_search > div > ul > li:nth-child('+str(i)+') > div > div > a.title.text_over')
                    except:
                        pass                    
                    url = li.get_attribute('href')
                    title = li.text+'/t'
                    # print(url)
                    # print(title)
                    if url in had_url: continue
                    had_url.append(url)
                    docs.append([url,title])
                    # print(url,title)
            except Exception as e:
                flag = False
                pass
            page+=1
            # try:
            #     for li in lis:
            #         a = li.select('div > div[1] > a')
            #         title = a.text
            #         print(title)
            # try:
            #     div = soup.find("div",{"id":"comment_search"})
            #     print(div)
            # except:
                
            #     print("div")
            #     break
            # try:
            #     ul = div.find("ul",{"class":"search_result_list"})
            # except:
                
            #     print("ul")
            #     break
            # try:
            #     print(ul)
            #     lis = ul.select("li:nth-child(1)")
            # except:
            #     print("lis")
            #     break
            # try:
            #     for li in lis:
            #         a = li.find("a",{"class":"title text_over"})
            #         url = a['href']
            #         title = a.text
            #         if url in had_url: continue
            #         had_url.append(url)
            #         docs.append([url,title])
            #         print(url,title)

            # except:
            #     print("for li")
            #     break
            # except:
            #     print('??')
            #     pass

            if flag == False:
                break
        return docs
    def ruliweb_doc_crawling(self, document) :
        
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")
        comments = '\n'
        news = True
        mainview = soup.find("div",{"class":"board_main_view"})
        try:
            contents = mainview.find("div",{"class":"view_content rss_news autolink"}).find("article").text
            news = True
            return document
        except Exception as e:
            news = False
        try:
            author = soup.find("div",{"class":"user_info"}).find("strong",{"class":"nick"}).text
        except:
            author = 'none'
        try:
            time_line = (soup.find("div",{"class":"user_info"}).find("strong",{"class":"regdate"}).text).replace('.','-')
        except:
            time_line = '0000.00.00'
        try:
            contents = soup.find("div",{"class":"board_main"}).find("div",{"class":"view_content"}).find("div").text+'/t'

        except Exception as e:
            return document  # 본문 없을경우
        try:
            cmt_list = soup.find("table",{"class":"comment_table"}).find("tbody").find_all("tr")
            for cmt in cmt_list:
                comment = cmt.find("td",{"class":"comment"}).find("div",{"class":"text_wrapper"}).find("span",{"class":"text"}).text
                comment = self.parseContents(comment)
                comments+=comment+'/t'
        except Exception as e:
            author = self.parseContents(author)
            # contents = self.parseContents(contents)
            document +=[time_line,author,contents]
            return document   # 댓글이 없는 경우
        author = self.parseContents(author)
        contents = self.parseContents(contents+comments)
        document += [time_line,author, contents]
        return document

        """
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")

        if re.match(r'http[s]?://bbs\.ruliweb\.com/news[a-z0-9/?&=.]+', document[0]) :
            print('News script :',document[0])
            return document
        elif re.match(r'http[s]?://bbs\.ruliweb\.com/[a-z0-9/?&=.]+', document[0]) :
            try:
                title = soup.find("span",{"class":"subject_text"}).text
                date_line = soup.find("span",{"class":"regdate"}).text.replace(".","-").replace("(", "").replace(")", "")
                author = soup.find("strong", {"class":"nick"}).text
                contents = soup.find("div",{"class":"view_content"}).text
            except Exception as e:
                print(e)
                return document
        elif re.match(r'http[s]?://mypi\.ruliweb\.com/[a-z0-9/?&=.]+&ncate=[0-9]?&page=[0-9]?', document[0]) :
            print('Unscraping script :',document[0])
            return document
        elif re.match(r'http[s]?://mypi\.ruliweb\.com/m/[a-z0-9/?&=.]+', document[0]) :
            try:
                '//*[@id="content"]/div/ul/li/p/span[1]'
                title = soup.find("span",{"class":"subject"}).text
                date_line = soup.find("span",{"class":"date"}).text
                if 'AM' in date_line :
                    date_line = date_line.replace('AM ','')
                elif 'PM' in date_line:
                    hour = int(date_line[date_line.find('PM ')+len('PM '):date_line.find(':')])+12
                    date_line = date_line[:date_line.find('PM ')]+str(hour)+date_line[date_line.find(':'):]
                    date_line = date_line.replace('PM ','')
                author = soup.find("a", {"id":"title"}).text
                author = author.replace('"', '')
                contents = soup.find("div",{"id":"view_txt"}).text
            except Exception as e:
                print (e)
                return document
        elif re.match(r'http[s]?://mypi\.ruliweb\.com/m/[a-z0-9/?&=.]+', document[0]) :
            try:
                '//*[@id="content"]/div/ul/li/p/span[1]'
                title = soup.find("td",{"class":"m1"}).find("a").text
                date_line = soup.find("td",{"class":"m1"}).text
                date_line = date_line[date_line.find(title)+len(title):]
                date_line = date_line.replace("/","-").replace("(", "").replace(")", "")
                if 'AM' in date_line :
                    date_line = date_line.replace('AM ','')
                elif 'PM' in date_line:
                    hour = int(date_line[date_line.find('PM ')+len('PM '):date_line.find(':')])+12
                    date_line = date_line[:date_line.find('PM ')]+str(hour)+date_line[date_line.find(':'):]
                    date_line = date_line.replace('PM ','')
                author = soup.find("div", {"class":"mypiNick"}).text
                author = author[:author.find('접속')].replace('"', '')
                contents = soup.find("div",{"class":"story"}).text
            except Exception as e:
                print (e)
                return document
        else:
            print('Unknown Format :',document[0])
            return document
        title = title[title.find(']')+1:]

        title = self.parseContents(title)
        date_line = self.parseContents(date_line)
        author = self.parseContents(author)
        contents = self.parseContents(contents)
        document += [title, date_line, author, contents]

        return document
        """

    def mlbpark_list_crawling(self, keyword) :
        page = 1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('mlbpark',keyword)
        while True :
            search_url = 'http://mlbpark.donga.com/mp/b.php?p='+str(page)+'&m=search&b=bullpen&query='+query+'&select=sct&user='
            response = self.getResponse(search_url)
            # print(search_url)
            if not response: break
            soup = BeautifulSoup(response.text, "lxml")
            #sys.stdout.write(search_url)
            try:
                now_page = (int(soup.find("div", {"class":"page"}).find("strong").text)-1)*30+1
            except Exception as e: break
            if not page == now_page: break
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from Mlbpark.')
            table = soup.find("table", {"class":"tbl_type01"}).find("tbody").find_all("tr")
            for tr in table :
                a = tr.select("td.t_left > div.tit > a")
                # print(a)
                url = a[0]["href"]
                # print(url)
                if url in had_url: continue
                title = self.parseContents(a[0].text)+'/t'
                docs.append([url, title])
                had_url.append(url)
            page += 30

        return docs

    def mlbpark_doc_crawling(self, document) :
        
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")
        comment ='\n'
        try:
            date_line = soup.find("div",{"class":"text3"}).find("span",{"class":"val"}).text
            author = soup.find("div",{"class":"text1"}).find("span",{"class":"nick"}).text
            contents = soup.find("div",{"id":"contentDetail"}).text
            date_line = self.parseContents(date_line)
            author = self.parseContents(author)
            contents = self.parseContents(contents)+'/t'
            try:
                reply_list = soup.find("div",{"class":"index"}).find("div",{"id":"container"}).find("div",{"class":"contents"}).find("div",{"class":"left_cont"}).find("div",{"class":"reply_list"})
                other_cons = reply_list.find_all("div",{"class":"other_con"})
                my_cons = reply_list.find_all("div",{"class":"my_con"})
                for other_con in other_cons:
                    text = other_con.find("div",{"class":"other_reply"}).find("div",{"class":"txt_box"}).find("div").find("span",{"class":"re_txt"}).text
                    comment+=text.strip()+'/t'
                for my_con in my_cons:
                    text = my_con.find("div",{"class":"my_reply"}).find("div",{"class":"txt_box"}).find("div").find("span",{"class":"re_txt"}).text
                    comment+=text.strip()+'/t'
                document += [date_line,author,contents+self.parseContents(comment)]
            except Exception as e:
                document += [date_line,author,contents]
        except Exception as e:
            return document

        return document

    def inven_list_crawling(self, keyword) :
        page = 1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('inven',keyword)
        while True :
#            search_url = 'http://www.inven.co.kr/webzine/news/?sw='+query+'&sclass=0&page='+str(page)
            search_url = 'http://m.inven.co.kr/search/webzine/article/'+query+'/'+str(page)
            response = self.getResponse(search_url)
            if not response: break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.text, "lxml")

            now_page = int(soup.find("span", {"class":"currentpg pg"}).text)
            if not page == now_page: break
            #print ('"'+keyword+'" list is crawling page '+str(page)+' from Inven.')
            try:
#                table = soup.find("div", {"class":"webzineNewsList tableType2"}).find("table").find("tbody").find_all("tr")
                table = soup.find("div",{"class":"sectin_body"}).find("ul").find_all("li")
            except Exception as e: break
            for tr in table :
#                a = tr.find("td",{"class":"left name"}).find("span",{"class":"title"}).find("a")
                a = tr.find("a",{"class":"name ellipsis"})
                url = a["href"]
                if url in had_url: continue
                title = a.text+'/t'
#                if title.find("]") > 0:
#                    title = title[title.find("]")+2:]
#                info = tr.find("span",{"class":"info"}).text.split("|")
#                author = info[1][1:]
#                date_line = info[2][1:]
                info = tr.find("div",{"class":"item_info clearfix"})
                author = info.find("a",{"class":"board"}).text
                date_line = info.find("p",{"class":"date"}).text
                docs.append([url, title, date_line, author])
                had_url.append(url)
            page += 1

        return docs

    
    def inven_doc_crawling(self, document) :
        
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")
        comment = '\n'
        try:
            contents = soup.find("div",{"id":"imageCollectDiv"}).text.strip()+'/t'
            try:
                lis = soup.find("div",{"id":"powerbbsCmt2"}).find("div",{"class":"cmtWrap"}).find("div",{"class":"cmtMain"}).find("div",{"class":"commentList1"}).find("ul").find_all("li")
                for li in lis:
                    text = li.find("div",{"class":"cmtOne cmtSt2"}).find("div",{"class":"comment"}).text
                    comment += self.parseContents(text)+'/t'
                document.append(contents+comment)
            except Exception as e:
                document.append(self.parseContents(contents))+'/t'
        except Exception as e:
            return document

        return document

    def todayhumor_list_crawling(self, keyword) :
        page = 1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('todayhumor',keyword)
        while True :
            search_url = 'http://www.todayhumor.co.kr/board/list.php?table=&page='+str(page)+'&kind=search&keyfield=subject&keyword='+query
            response = self.getResponse(search_url)
            if not response: break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.text, "lxml")
            
            try:
                table = soup.find("table", {"class":"table_list"}).find_all("tr",{"class":re.compile(r"view list_tr_[a-z]+")})
            except Exception as e: 
                
                break
            if not table or len(table) < 1: 
                
                break
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from Todayhumor.')
            for tr in table :
                a = tr.find("td",{"class":"subject"}).find("a")
                url = 'http://www.todayhumor.co.kr'+a["href"]
                if url in had_url: continue
                title = a.text+'/t'
                author = tr.find("td",{"class":"name"}).text
                date_line = "20"+tr.find("td",{"class":"date"}).text.replace("/","-")
                docs.append([url, title, date_line, author])
                had_url.append(url)
            page += 1
            print(page)
        return docs

    
    def todayhumor_doc_crawling(self, document) :
        
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")
        comments='\n'
        try:
            contents = soup.find("div",{"class":"viewContent"}).text.strip()+'/t'
            memoDiv = soup.find_all("div",{"class":"memoDiv"})
            memowrapper = soup.find_all("div",{"class":"memoWrapperDiv rereMemoWrapperDiv"})
            for memo in memoDiv:
                comments += self.parseContents(memo.find("div",{"class":"memoContent"}).text).strip() +'/t'
            for memo in memowrapper:
                comments += self.parseContents(memo.find("div",{"class":"memoDiv rereMemoDiv"}).find("div",{"class":"memoContent"}).text).strip()+'/t'
        except Exception as e:
            pass
#            return document
        contents += comments
        document.append(contents)

        return document
    

    def ppomppu_list_crawling(self, keyword) :
        page = 1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('ppomppu',keyword)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        end_flag = 0
        while True : 
            search_url = 'http://www.ppomppu.co.kr/search_bbs.php?search_type=sub_memo&page_no='+str(page)+'&keyword='+query+'&page_size=50&bbs_id=&order_type=date&bbs_cate=2'
            try:
                driver.get(search_url)
                time.sleep(1)
            except Exception as e:
                print(search_url)
                print(e)
                continue
            for cnt in range(1,51):
                try:
                    conts = driver.find_element_by_xpath('/html/body/div/div[2]/div[5]/div/form/div/div['+str(cnt)+']/div/span/a')                    
                except Exception as e: 
                    end_flag = 1
                    break
                #print ('"'+keyword+'" list is crawling page '+str(page)+' from Ppomppu.')
                try:
                    url = conts.get_attribute('href')
                    # print(url)
                    if not url : continue
                except Exception as e: 
                    print(e)
                    continue
                if url in had_url: continue
                title = conts.text+'/t'
                # print(title)
                docs.append([url, title])
                had_url.append(url)
                #####################
            if end_flag ==1:
                break
            page += 1
            # print(page)
        return docs
    
    def ppomppu_doc_crawling(self, document) :
        
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")
        comment ='\n'
        contents=""
        try:
            contents = soup.find("td",{"class":"board-contents"}).text
            contents = self.parseContents(contents)+'/t'
            #date_line = date_line[date_line.find(u'등록일: ')+len(u'등록일: '):date_line.find(u'조회수')].replace('\r','').replace('\n','')
        except Exception as e:
            contents = ""
        try:
            author = soup.find("font",{"class":"view_name"}).text
        except:
            author = "none"
        try:
            t = soup.find("div",{"class":"sub-top-text-box"}).text
        except:
            t = "none"
        document += [t,author,contents]
        
        return document

    def clien_list_crawling(self, keyword) :
        page = 0
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('clien',keyword)
        while True :
            search_url = 'https://www.clien.net/service/search?q='+query+'&sort=recency&p='+str(page)+'&boardCd=&isBoard=false'
            response = self.getResponse(search_url)
            if not response: break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.text, "lxml")

            try:
                now_page = int(soup.find("div", {"class":"board-pagination"}).find("a", {"class":"board-nav-page active"}).text)
            except Exception as e: break
#            print ('"'+keyword+'" list is crawling page '+str(page+1)+' from Clien.')
            if not page == now_page-1: break
            list = soup.find("div", {"class":"contents_jirum"}).find_all("div", {"data-role":"list-row"})
            for row in list :
                a = row.find("a",{"data-role":"list-title-text"})
#                url =a["href"]
                url = 'https://www.clien.net'+ a["href"]
                if url in had_url: continue
                title = re.sub(r'^[\n\t ]+|[\n\t ]+$', '', a.text.replace('\t',''))+'/t'
                date_line = re.sub(r'^[\n\t ]+|[\n\t ]+$', '', row.find("span",{"class":"timestamp"}).text)
                docs.append([url, title, date_line])
                had_url.append(url)
            page += 1

        return docs

    def clien_doc_crawling(self, document) :
        
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")
        comments = '\n'
        try:
            author = soup.find("span", {"class":"contact_name"}).find("span",{"class":"nickname"}).text
            #author = soup.find("span", {"class":"nickname"}).text
            contents = soup.find("div",{"class":"post_content"}).find("article").text
            content = soup.find("div",{"class":"content_view"})
            post = content.find("div",{"class":"post_comment"})
            pcomment = post.find("div",{"class":"comment"})
            comment_row = pcomment.find_all("div",{"class":re.compile(r'comment_ro.+')})
            for comment_content in comment_row:
                try:
                    comment = comment_content.find("div",{"class":"comment_content"}).find("div",{"class":"comment_view"}).text
                    comments += self.parseContents(comment)+'/t'
                except:
                    pass
        except Exception as e:
            return document
        author = self.parseContents(author)
        contents = self.parseContents(contents)+'/t'
        document += [author, contents+comments]
        return document

    def instiz_list_crawling(self, keyword) :
        page =1
        docs = []
        temp = 'site:https://instiz.net '+keyword
        query = self.quote(temp)
        had_url = self.sh.loadURL('instiz',keyword)
        flag = True
        temp = ""
        while True:
            search_url = 'https://search.daum.net/search?w=web&q='+query+'&DA=PGD&detail_query='+self.quote(keyword)+'&p='+str(page)
            response = self.getResponse(search_url)
            if not response: break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.content,'html.parser',from_encoding='utf-8')
            lis = soup.find("ul",{"class":"list_info clear"}).find_all("li")
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from instiz.')
            if temp == lis[0].find("a")['href']: break
            else: temp = lis[0].find("a")['href']
            for li in lis:
                a = li.find("a")
                url = a['href']
                title = a.text+'/t'
                if url in had_url: continue
                docs.append([url,title])
                had_url.append(url)
            page+=1
        return docs

    
    def instiz_doc_crawling(self, document) :
        
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")
        comment = '\n'
        try:
            date_line = soup.find("div", {"class":"tb_left"}).find("span",{"itemprop":"datePublished"})["title"].replace(".","-")
        except Exception as e:
            date_line = "0000-00-00"
        author = u"익명"

        try:            
            contents = soup.find("div",{"id":"memo_content_1"}).text
            contents = self.parseContents(contents)+'/t'
        except Exception as e:
            contents = ""
        try:
            trs = soup.find("table",{"id":"ajax_table"})
            j = trs.find_all("tr")
            for tr in j:
                try:
                    text = self.parseContents(tr.find("td",{"class":"comment_memo"}).find("div",{"comment_line"}).find("span").text).strip()
                    comment += text+'/t'
                except Exception as e:
                    break
            documents += [date_line, author, contents + self.parseContents(comment)]
            return document
        except Exception as e:
            if len(contents)>0:
                document += [date_line, author, contents]
            else:
                return document

        return document

    def cook82_list_crawling(self, keyword):
        page = 1
        docs = []
        query = self.quote(keyword)
        had_url = self.sh.loadURL('cook82',keyword)
        while True :
            search_url = 'http://www.82cook.com/entiz/enti.php?bn=15&searchType=search&search1=1&keys='+query+'&page='+str(page)
            response = self.getResponse(search_url)
            if not response: break
            #sys.stdout.write(search_url)
            soup = BeautifulSoup(response.text, "lxml")

            try:
                list = soup.find("div", {"id":"list_table"}).find("table").find("tbody").find_all("tr",)
            except Exception as e: 
                print(e)
                print(search_url)
                break
            if not list or len(list[0].find_all("td")) < 2: break
#            print ('"'+keyword+'" list is crawling page '+str(page)+' from 82Cook.')
            for row in list :
                try:
                    a = row.find("td",{"class":"title"}).find("a")
                except:
                    continue
                url = "http://www.82cook.com/entiz/"+a["href"]
                if url in had_url: continue
                title = re.sub(r'^[\n\t ]+|[\n\t ]+$', '', a.text.replace('\t',''))+'/t'
                date_line = re.sub(r'^[\n\t ]+|[\n\t ]+$', '', str(row.find("td",{"class":"regdate numbers"}).text))
                docs.append([url, title, date_line])
                had_url.append(url)
            page += 1

        return docs
    
    # crawling document
    def dcinside_doc_crawling(self, document) :
        
        author = 'none';contents =''
        response = self.getResponse(document[0])
        if not response: document += [author,document[1]];return document
        soup = BeautifulSoup(response.text, "lxml")
        comments = ''+document[1]
        try:
            author = soup.find("span", {"class":"nickname"}).text
        except:
            author = "none"
        try:
            contents = soup.find("div",{"class":"writing_view_box"}).text
        except Exception as e:
            document +=[author,comments]
            return document
        author = self.parseContents(author)
        contents = self.parseContents(contents)+'/t'
        try:
            lis= soup.find("ul",{"class":"cmt_list"}).find_all("li",{"class":"ub-content"})
            for li in lis:
                comments += li.find("p",{"class":"usertxt ub-word"}).text +'/t'
        except Exception as e: #댓글 없는 경우
            pass
        contents += self.parseContents(comments)
        #contents = contents_limimt(contents)
        document +=[author,contents]
        return document
     
    def cook82_doc_crawling(self, document) :
        
        response = self.getResponse(document[0])
        if not response: return document
        soup = BeautifulSoup(response.text, "lxml")
        comments = '\n'
        try:
            author = soup.find("div", {"class":"readLeft"}).find("strong").text
            contents = soup.find("div",{"id":"articleBody"}).text
            author = self.parseContents(author)
            contents = self.parseContents(contents).strip()+'/t'
            try:
                lis = soup.find("ul",{"class":"reples"}).find_all("li")
                for li in lis:
                    comments += self.parseContents(li.find("p").text).strip()+'/t'
                contents = contents+comments
                document += [author,contents]
            except Exception as e:
                document +=[author,contents]
        except Exception as e:
            pass
        return document


    # crawling documents for multi-process
    def dcinside_docs_crawling(self, process, keyword, docs) :
        
        total = len(docs)
        i=1
        print("Process "+str(process)+" Dcinside Documents crawling start. documents count : "+str(total))
        for doc in docs:
            for i in range(1, 11):
                document = self.dcinside_doc_crawling(doc)
                if document and len(document) > 4:
                    with self.lock:
                        self.sh.saveDcinsideDoc(keyword, document)
                    break
#                else:
#                    print('Error occur from dcinside site : '+doc[0]+'\n'+str(len(document)))
#                    time.sleep(1*i)
        return
    def ruliweb_docs_crawling(self, process, keyword, docs) :
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+" Ruliweb Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.ruliweb_doc_crawling(doc)
            if document and len(document) > 4:
                count += 1
                with self.lock:
                    self.sh.saveRuliwebDoc(keyword, document)
            else:
                print('Error occur from ruliweb site : ')
                print(doc)
        return
    def mlbpark_docs_crawling(self, process, keyword, docs) :
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+" MLB Park Documents crawling start. documents count : "+str(total))
        for doc in docs:
            for i in range(1, 11):
                document = self.mlbpark_doc_crawling(doc)
                if document and len(document) > 4:
                    count += 1
                    with self.lock:
                        self.sh.saveMlbparkDoc(keyword, document)
                    break
#                else:
#                    print('Error occur from mlbpark site : '+doc[0])
#                    time.sleep(10*i)
        return
    def inven_docs_crawling(self, process, keyword, docs) :
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+" Inven Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.inven_doc_crawling(doc)
            if document and len(document) > 4:
                count += 1
                with self.lock:
                    self.sh.saveInvenDoc(keyword, document)
#            else:
#                print('Error occur from inven site : '+doc[0] +'\n'+str(len(document)))
        return
    def todayhumor_docs_crawling(self, process, keyword, docs) :
        count = 1
        total = len(docs)
        print("Process "+str(process)+" Todayhumor Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.todayhumor_doc_crawling(doc)
            if document and len(document) > 4:
                count += 1
                with self.lock:
                    self.sh.saveTodayhumorDoc(keyword, document)
#            else:
#                print('Error occur from todayhumor site : '+doc[0])
        return
    def ppomppu_docs_crawling(self, process, keyword, docs) :
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+" Ppomppu Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.ppomppu_doc_crawling(doc)
            if document and len(document) > 4:
                count += 1
                with self.lock:
                    self.sh.savePpomppuDoc(keyword, document)
                
#            else:
#                print('Error occur from ppompu site : '+doc[0])
        #            time.sleep(10*i)
        return
    def clien_docs_crawling(self, process, keyword, docs) :
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+" Clien Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.clien_doc_crawling(doc)
            if document and len(document) > 4:
                count += 1
                with self.lock:
                    self.sh.saveClienDoc(keyword, document)
#            else:
#                print('Error occur from clien site : '+doc[0])
        return
    def instiz_docs_crawling(self, process, keyword, docs) :
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+" Instiz Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.instiz_doc_crawling(doc)
            if document and len(document) > 4:
                count += 1
                with self.lock:
                    self.sh.saveInstizDoc(keyword, document)
#            else:
#                print('Error occur from instiz site : '+doc[0])
        return
    def cook82_docs_crawling(self, process, keyword, docs) :
        
        count = 1
        total = len(docs)
        print("Process "+str(process)+" 82cook Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.cook82_doc_crawling(doc)
            if document and len(document) > 4:
                count += 1
                with self.lock:
                    self.sh.saveCook82Doc(keyword, document)
#            else:
#                print('Error occur from cook82 site : '+doc[0])
        return
    def naver_docs_crawling(self, process, keyword, docs):
        
        count =1
        total = len(docs)
        print("Process "+str(process)+" Naver Reviews crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.naver_doc_crawling(doc)
            if document and len(document)>4:  #url, title, date_time,author, contents
                count+=1
                with self.lock:
                    self.sh.saveNaverDoc(keyword,document)
#            else:
#                print('Error occur from Naver site : '+doc[0] +'\nlength ' +str(len(document)))
        return

    def youtube_list_crawling(self, keyword) :
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        docs = []
        query = self.quote(keyword)
        search_url = 'https://www.youtube.com/results?search_query='+query+'&sp=CAMSAhAB'
        #올해 + 조회수 필터 + '&sp=CAMSBAgFEAE%253D' 
        #이번주 필터 +'&sp=EgIIAw%253D%253D'
        #올해 필터 + '&sp=EgIIBQ%253D%253D'
        #조회수 필터 +'&sp=CAMSAhAB'
        #이번주 + 조회수 필터 + '&sp=CAMSBAgDEAE%253D'
        had_url = self.sh.loadURL('youtube', keyword)
        driver.get(search_url)
        time.sleep(2)
        urls = []
        last_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")
        driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
        time.sleep(2.0)
        while True:
            cur_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")
            newnum = 0
            response = driver.page_source
            soup = BeautifulSoup(response,"lxml")
            videos = soup.select('ytd-video-renderer')
            try:
                for video in videos:
                    a = video.select_one('a')
                    href = a['href']
                    url = 'https://www.youtube.com'+ href
                    #print(url)
                    #print(video.select_one('yt-formatted-string').text)
                    if url in had_url: continue
                    try:
                        title = video.select_one('yt-formatted-string').text+'/t'
                    except:
                        pass
                    #print(title)
                    had_url.append(url)
                    urls.append(url)
                    docs.append([url, title])
                    newnum+=1
            except Exception as e:
                continue
            driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
            time.sleep(1.5)
            if len(urls) > 1000000:
                break
            if cur_scrollHeight == last_scrollHeight:
                driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
                time.sleep(5)
                #한 번더 스크롤 내려보고 그래도 같으면 종료
                cur_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")
                if cur_scrollHeight==last_scrollHeight:
                    print("cur_scrollHeight==last_scrollHeight")
                    break
            elif newnum==0:
                print("newnum = {}".format(newnum))
            last_scrollHeight = cur_scrollHeight
        # theqoprint(len(docs))
        driver.close()
        return docs
       
    def youtube_comments_crawling(self, document):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        #chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
        #print(document[0])
        driver.get(document[0])
        time.sleep(3)
        contents = ''
        last_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight") #맨 아래 스크롤 위치 파악
        time.sleep(2)
        # //*[@id="button"]
        # #more-replies
        # //*[@id="button"]
        #/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]
        comments=""
        date = ""
        try:
            date = driver.find_element_by_xpath('//*[@id="info-strings"]/yt-formatted-string').text
            date=date.split('. ')
            date[-1] = date[-1].replace('.','')
            date = date[:3]
            date = '-'.join(date)
            #print(date)
        except Exception as e:
            print("date error")
        try:
            author = driver.find_element_by_xpath('//*[@id="text"]/a').text
            author = self.parseContents(author)
            #print(author)
            #print(author)
        except Exception as e:
            print("author error")
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(1)
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(1.0)
            cur_scrollHeight = driver.execute_script("return document.documentElement.scrollHeight")
            if cur_scrollHeight == last_scrollHeight:
                break
            last_scrollHeight = cur_scrollHeight
        try:
            btns = driver.find_elements_by_css_selector('#more-replies > a > paper-button')
            #more-replies
            #print(btns)
        except Exception as e:
            pass
        for btn in btns:
            btn.send_keys('\n')
        try:
            replies = driver.find_elements_by_xpath('//*[@id="content-text"]')
            for reply in replies:
                comments = reply.text.strip()+'/t'
            #print(comment)
        except Exception as e:
            print("No content-text")
            pass
        
        response = driver.page_source
        soup = BeautifulSoup(response,"lxml")
        try:
            ytds = soup.select('ytd-comment-renderer > div > div > ytd-expander > div')
        except Exception as e:
            print("no rereplies")
            print(e)
            pass
        for yt in ytds:
            comment = self.parseContents(yt.text).strip()
            comments += comment+'/t'
        document += [date, author, comments]
        #print(document)
        driver.close()
        return document


    def youtube_docs_crawling(self, process, keyword, docs) :

        count = 1
        total = len(docs)
        print("Process "+str(process)+" Youtube Comments crawling start. youtube ids count : "+str(total))
        for doc in docs:
            document = self.youtube_comments_crawling(doc)
            if document and len(document[-1])>0:  #url, title, date_time,author, contents
                count+=1
                with self.lock:
                    self.sh.saveYoutubeDoc(keyword,document)
        
#            else:
#                print('Not have comments into youtube id : '+uid)
#        print("Process "+str(process)+" Youtube Comments crawling finish. youtube ids count : "+str(total))
        return
