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
        if page >570: break
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
    for url in urls:
        if page_cnt == 500 :
        #driver.execute_script('window.open("https://naver.com");')
            handle +=1
            time.sleep(1)
                        #driver.close()
            driver.switch_to_window(driver.window_handles[handle%15])
            time.sleep(1)
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
                title = self.parseContents(tit)
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
                text = driver.find_element_by_css_selector('div.se-main-container').text.replace('\n', ' ')
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
