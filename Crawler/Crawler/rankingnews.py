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
            contents = contents.replace('\n', ' ').replace('#', ' ')
            # print(contents)
        except Exception as e:
            pass
        try:
            lis = soup.select('#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li')
            for li in lis:
                comment = li.select_one('div > div > div.u_cbox_text_wrap > span').text
                comment = comment.replace('\n', ' ').replace('#', ' ')
                contents = contents + ' ' + comment
        except:
            pass
        try:
            element = WebDriverWait(driver,1).until(
            EC.presence_of_element_located((By.XPATH,'//*[@id="articleTitle"]')))
            title = driver.find_element_by_xpath('//*[@id="articleTitle"]').text
            title = title.replace('\n', ' ').replace('#', ' ')
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