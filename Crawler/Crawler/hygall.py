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
            title = a.text
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
        contents = self.parseContents(soup.find("div",{"class":"cntBody"}).find("div").text)
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
            contents += self.parseContents(comment +'.')
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
