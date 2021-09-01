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
            #print("error navernews ul")
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
    document[2] = time
    document += [author,contents]

    return document  #[url,title,time,author,contents]

def navernews_docs_crawling(self, process, keyword, docs):
        
    count = 1
    total = len(docs)
    print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
    for doc in docs:
        document = self.navernews_doc_crawling(doc)
        if document and len(document) >4:
            count += 1
            with self.lock:
                self.sh.saveNavernewsDoc(keyword, document)
#            else:
#                print('Error occur from template site : '+doc[0])
    return