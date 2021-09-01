def navercafe_list_crawling(self,keyword):
        
    query = self.quote(keyword)
    docs = []
    had_url = self.sh.loadURL('navercafe',keyword)

    had_title= self.sh.loadTitle('navercafe', keyword)
    #print(had_title)
    #google-chrome --remote-debugging-port=9222 --user-data-dir="~/workspace/test/knowledge_based_sentiment_analysis_community_crawler/ChromeProfile"
    id = 'minamom501'
    pw = 'lalala1983'

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
    ,'appleiphone'#애플 아사모
    ,'dokchi'#독취사
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
    ##############################################################


    url = "none"
    K=0
    handle = 0
    page_cnt = 0
    return_cnt = 0
    random.shuffle(cafe_list)
    '''
    for cafe in cafe_list:
        #if K < len(cafe_list)-1: K+=1;continue
        progressBar(K, len(cafe_list))
        K+=1
        xpath = xpath_dict[cafe]
        cur_url = search_url+cafe
        driver.get(cur_url)
        try:
            element = WebDriverWait(driver,2).until(
                EC.presence_of_element_located((By.ID,'topLayerQueryInput'))
            )
        except: continue
        #time.sleep(2)
        driver.execute_script("document.getElementById('topLayerQueryInput').value =\'"+keyword+"\'")
        try:
            element = WebDriverWait(driver,2).until(
                EC.presence_of_element_located((By.XPATH,xpath))
            )
            
        except: 
            print("error on : "+cafe)
            continue
        try:
            btn = driver.find_element_by_xpath(xpath)
            btn.click()
        except: q
            print("cafe btn xpath error " + cafe)
            continue
        continue
    #
    '''  
    ######################################################################
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
            element = WebDriverWait(driver,5).until(
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
            # if page >1:
            #     if page <=11:
            #         #//*[@id="main-area"]/div[7]/a[1]
            #         try:
            #             btn = driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[%s]' %(page))
            #             page_url = btn.get_attribute("href")
            #             print(page_url[:-1])
            #             btn.send_keys(Keys.ENTER)
                        
            #         except Exception as e:
            #             print("Exception 0")
            #             print(e)
            #             break
            #         #//*[@id="main-area"]/div[7]/a[11]
            #     elif page%10==1:  # 다음 버튼 눌러야하는 경우
            #         try:
            #             driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[12]').send_keys(Keys.ENTER)
            #             #그냥 다음버튼 누르면 됨
            #         except Exception as e:
            #             print("Exception 1")
            #             break
            #     elif page%10!=0:
                    
            #         try:
            #             driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[%s]' %(page%10+1)).send_keys(Keys.ENTER)
            #             #이전버튼이 있기 때문에 +1해줘야함
            #         except Exception as e:
            #             print("Exception 2")
            #             break
            #     else:
            #         try:
            #             driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[%s]' %(page%10+11)).send_keys(Keys.ENTER)
            #         except Exception as e:
            #             print("Exception 3")
            #             break

            
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
                        ###########
                        try:
                            # try:
                            #     element = WebDriverWait(driver,1).until(
                            #     EC.presence_of_element_located((By.XPATH,'//*[@id="main-area"]/div[5]/table/tbody/tr[%s]/td[1]/div[2]/div/a' %(minipage)))
                            #     )#minipage마다의 xpath 찾기//*[@id="main-area"]/div[5]/table/tbody/tr[1]/td[1]/div[2]/div/a[1]//*[@id="main-area"]/div[5]/table/tbody/tr[1]/td[1]/div[2]/div/a[1]
                            # except:
                            #     flag = False
                            #     pass
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
                        ##########
                        # try:
                        #     btn = driver.find_element_by_xpath('//*[@id="main-area"]/div[5]/table/tbody/tr[%s]/td[1]/div[2]/div/a' %(minipage))    
                        # except:
                        #     pass
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
                    element = WebDriverWait(driver,4).until(
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
                    title = self.parseContents(title)
                    
                except:
                    driver.back()
                    continue
                # [url,title,date,author,text]
                
                # if title in had_title:
                #     print("had_title!!")
                #     driver.back()
                #     continue
                #\33 58155734 > div > div > div.comment_text_box > p > span
                # try:
                #     div = soup.find("div",{"class":"article_container"})
                #     ps = div.find("div",{"class":"article_viewer"}).find_all("p")
                #     #print(ps)
                #     for p in ps:
                #         span = p.find("span")
                #         text =text + ' ' + span.text
                #     text = text.replace('\n', ' ')
                #    #print(text)
                # except Exception as e:
                #     print(e)
                #     pass
                try:
                    text = soup.select_one('#app > div > div > div.ArticleContentBox > div.article_container > div.article_viewer > div > div').text
                    #print('#####')
                    #print(div)
                except Exception as e:
                    #print(e)
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
                        comment = comment + ' ' + li.find("div",{"class":"comment_text_box"}).text
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