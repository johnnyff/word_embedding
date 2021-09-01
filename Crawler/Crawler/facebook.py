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
    Id = driver.find_element_by_name('email')
    Id.send_keys('elapinsta@gmail.com')
    password = driver.find_element_by_id('pass')
    password.send_keys('##sangsoo1')
    password.submit()
    time.sleep(1)
    keyword_area = driver.find_element_by_xpath('q')
    keyword_area.send_keys(keyword)
    keyword_area.submit()
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