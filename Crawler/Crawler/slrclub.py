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
                title = a.text
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
    time.sleep(1)
    response = driver.page_source
    if not response: return document
    soup = BeautifulSoup(response,"lxml")
    try:
        divs = soup.find_all("div",{"class":"cmt-contents"})
        for div in divs:
            comment = self.parseContents(div.text)
            contents += comment +'.'
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