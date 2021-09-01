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
                title = b[0].text
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
            contents = soup.find("div",{"class":"container"}).text
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
                comment += tr.find("td",{"class":"comment"}).text+'\n'
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
