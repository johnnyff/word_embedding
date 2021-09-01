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
            title = a[0].text
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
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('div.entry-content > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('div.article > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        divs = soup.select('#content > article > div.article > div')
        for div in divs:
            contents += self.parseContents(div.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#content > article > div:nth-child(4) > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#mArticle > div > div.area_view > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#container > main > div > div.area-view > div.article-view > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select_one('#mArticle > div > div.area_view').select('p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#content > article > div > div.e-content.post-content.fouc > div')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#mArticle > div.area_view > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#content_permallink_article > div > div > div.box_article > div > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#content > div.inner > div.entry-content > div.tt_article_useless_p_margin')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#__permalink_article > div.article.content__permalink > article > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#content > div.inner > div.entry-content')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#content > div.entry > div.entrayContentsWrap > div.article > div')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#content_permallink_article > div > div > div.box_article > div')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#content > div.inner > div.entry-content > div:nth-child(3) > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#body > div.article > div:nth-child(1) > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#main > div > div.category_list.index_type_common.index_type_horizontal > ul > li > div > div > div.article_view > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#content_permallink_article > div > div > div.box_article > div > div')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass

    try:
        ps = soup.select('#content > div.inner > div.entry-content > div')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#tt-body-page > div.jb-page.jb-hide-menu-icon.jb-typography-3 > div.jb-background.jb-background-main > div > div > div.jb-column.jb-column-content > div.jb-cell.jb-cell-content.jb-cell-content-article > article > div.jb-content.jb-content-article > div.jb-article > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#article > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#tt-body-page > div.jb-page.jb-youtube-auto.jb-typography-3.jb-post-title-show-line.jb-another-category-1 > div.jb-background.jb-background-main > div > div > div.jb-column.jb-column-content > div.jb-cell.jb-cell-content.jb-cell-content-article > article > div.jb-content.jb-content-article > div.jb-article > div > div > p')
        for p in ps:
            contents += self.parseContents(p.text)
        #print(contents)
    except Exception as e:
        pass
    try:
        ps = soup.select('#mArticle > div.area_view > div > div')
        for p in ps:
            contents += self.parseContents(p.text)
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
