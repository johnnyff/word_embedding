
#-*- coding: utf-8 -*-

# Developer : Jeong Wooyoung, EGLAB, Hongik University
# Contact   : gunyoung20@naver.com

from multiprocessing import Process, Lock, Pool
from crawling_handler import CrawlingHandler
from storage_handler import StorageHandler



class MultiCrawler :
    def __init__(self):
        self.lock = Lock()
        self.worked = 0

    def multiCrawlingNaverNews(self,keyword,p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from Navernews.')
        documents = crawler.navernews_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from navernews.')
        self.distributeList(p_cnt,'Navernews',keyword,documents,crawler.navernews_docs_crawling)
    # processes handle
    def multiCrawlingDaum(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from Daum.')
        documents = crawler.daum_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from daumcafe.')
        self.distributeList(p_cnt,'Daum',keyword,documents,crawler.daum_docs_crawling)


    def multiCrawlingNavercafe(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        
        print('"'+keyword+'" list crawling start from navercafe.')
        # crawler.navercafe_list_crawling(keyword)
        crawler.multiprocessing_navercafe(keyword)
     
    def multiCrawlingNaverblog(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from naverblog.')
        crawler.naverblog_list_crawling(keyword)

    def multiCrawlingFacebook(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from facebook.')
        
        crawler.facebook_list_crawling(keyword)
        
 #       print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from facebook.')
 #       self.distributeList(p_cnt,'facebook',keyword,documents,crawler.facebook_docs_crawling)
    def multiCrawlingInstaDumper(self,keyword, p_cnt = 2):  
        crawler = CrawlingHandler()# 클래스 변수 생성
        print('"'+keyword+'" list crawling start from insta_dumper.')
        print(p_cnt) #argument로 16을 받아서 16으로 출력됨
        
        url_len = crawler.insta_dumper_list_crawling(keyword)
        while True:
            url_len = crawler.insta_dumper_list_crawling(keyword)
            if url_len==0:
               break
        
        crawler.insta_comment_crawling(keyword)
        
    def multiCrawlingInsta(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()# 클래스 변수 생성
        print('"'+keyword+'" list crawling start from insta.')
        print(p_cnt) #argument로 16을 받아서 16으로 출력됨
        
        # url_len = crawler.insta_list_crawling(keyword)
        # while True:
        #     url_len = crawler.insta_list_crawling(keyword)
        #     if url_len==0:
        #        break
        
        crawler.instagram_crawler(keyword)
        #print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from insta.')
        #self.distributeList(p_cnt,'insta',keyword,documents,crawler.insta_docs_crawling)
    def multiCrawlingRankingNews(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()# 클래스 변수 생성
        print('news crawling start from RankingNews.')
        crawler.RankingNews_list_crawling(keyword)       
        crawler.RankingNews_contents_crawling(keyword)
    def multiCrawlingYgosu(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from ygosu.')
        documents = crawler.ygosu_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from ygosu.')
        self.distributeList(p_cnt,'Ygosu',keyword,documents,crawler.ygosu_docs_crawling)
    
    def multiCrawlingHygall(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from hygall.')
        documents = crawler.hygall_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from hygall.')
        self.distributeList(p_cnt,'Hygall',keyword,documents,crawler.hygall_docs_crawling)

    def multiCrawlingSlrclub(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from slrclub.')
        documents = crawler.slrclub_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from slrclub.')
        self.distributeList(p_cnt,'Slrclub',keyword,documents,crawler.slrclub_docs_crawling)

    def multiCrawlingHumoruniv(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from humoruniv.')
        documents = crawler.humoruniv_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from humoruniv.')
        self.distributeList(p_cnt,'Humoruniv',keyword,documents,crawler.humoruniv_docs_crawling)

    def multiCrawlingtistory(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from tistory.')
        documents = crawler.tistory_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from tistory.')
        self.distributeList(p_cnt,'tistory',keyword,documents,crawler.tistory_docs_crawling)
    def multiCrawlingNaver(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from naver.')
        documents = crawler.naver_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from NaverShopping.')
        self.distributeList(p_cnt,'Naver',keyword,documents,crawler.naver_docs_crawling)

    def multiCrawlingTheqoo(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from theqoo.')
        documents = crawler.theqoo_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from theqoo.')
        self.distributeList(p_cnt,'Theqoo',keyword,documents,crawler.theqoo_docs_crawling)

    def multiCrawlingEtoland(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from etoland.')
        documents = crawler.etoland_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from etoland.')
        self.distributeList(p_cnt,'Theqoo',keyword,documents,crawler.etoland_docs_crawling)

    def multiCrawlingFmkorea(self,keyword, p_cnt=2):
        crawler = CrawlingHandler()
        print('"'+keyword+'" list crawling start from fmkorea.')
        documents = crawler.fmkorea_list_crawling(keyword)
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from fmkorea.')
        self.distributeList(p_cnt,'Fmkorea',keyword,documents,crawler.fmkorea_docs_crawling)

    def multiCrawlingPann(self,keyword,p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from pann.')
        documents = crawler.pann_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from pann.')
        self.distributeList(p_cnt, 'Pann', keyword, documents, crawler.pann_docs_crawling)


    def multiCrawlingBobae(self,keyword,p_cnt=2):
        crawler = CrawlingHandler() 
        print ('"'+keyword+'" list crawling start from bobae.')
        documents = crawler.bobae_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from bobae.')
        self.distributeList(p_cnt, 'Bobae', keyword, documents, crawler.bobae_docs_crawling)


    def multiCrawlingDcinside(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from Dcinside.')
        documents = crawler.dcinside_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from Dcinside.')
        
        self.distributeList(p_cnt, 'Dcinside', keyword, documents, crawler.dcinside_docs_crawling)
    def multiCrawlingRuliweb(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from Ruliweb.')
        documents = crawler.ruliweb_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from Ruliweb.')
        self.distributeList(p_cnt, 'Ruliweb', keyword, documents, crawler.ruliweb_docs_crawling)
    def multiCrawlingMlbpark(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from Mlbpark.')
        documents = crawler.mlbpark_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from Mlbpark.')
        self.distributeList(p_cnt, 'Mlbpark', keyword, documents, crawler.mlbpark_docs_crawling)
    def multiCrawlingInven(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from Inven.')
        documents = crawler.inven_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from Inven.')
        self.distributeList(p_cnt, 'Inven', keyword, documents, crawler.inven_docs_crawling)
    def multiCrawlingTodayhumor(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from Todayhumor.')
        documents = crawler.todayhumor_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from Todayhumor.')
        self.distributeList(p_cnt, 'Todayhumor', keyword, documents, crawler.todayhumor_docs_crawling)
    def multiCrawlingPpomppu(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from Ppomppu.')
        documents = crawler.ppomppu_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from Ppomppu.')
        self.distributeList(p_cnt, 'Ppomppu', keyword, documents, crawler.ppomppu_docs_crawling)
    def multiCrawlingClien(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from Clien.')
        documents = crawler.clien_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from Clien.')
        self.distributeList(p_cnt, 'Clien', keyword, documents, crawler.clien_docs_crawling)
    def multiCrawlingInstiz(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from Instiz.')
        documents = crawler.instiz_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from Instiz.')
        self.distributeList(p_cnt, 'Instiz', keyword, documents, crawler.instiz_docs_crawling)
    def multiCrawlingCook82(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from 82Cook.')
        documents = crawler.cook82_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from 82Cook.')
        self.distributeList(p_cnt, '82cook', keyword, documents, crawler.cook82_docs_crawling)
    def multiCrawlingYoutube(self, keyword, p_cnt=2):
        crawler = CrawlingHandler()
        # get document list
        print ('"'+keyword+'" list crawling start from youtube.')
        documents= crawler.youtube_list_crawling(keyword)

        # distribute list to process
        print ('"'+keyword+'" documents '+str(len(documents))+' crawling start from youtube.')
        self.distributeList(p_cnt, 'Youtube', keyword, documents, crawler.youtube_docs_crawling)

    # distribute list
    def distributeList(self, n, proc_name, keyword, list, func):
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
            procs.append(Process(target=func, args=(i, keyword, docs)))

        for p in procs :
            p.start()

        for p in procs :
            p.join()

    def distributeProcess(self, keyword, processes):
        length = len(processes)
        print ('Multi-Process :',length)
        procs = []
        for process in processes:
            procs.append(Process(target=process, args=(keyword, 16)))

        for p in procs :
            p.start()

        for p in procs :
            p._Popen=p
            p.join()







