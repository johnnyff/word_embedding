#-*- coding: utf-8 -*-
import time
import os
import urllib
import re

from selenium import webdriver
from scrapy.selector import Selector
from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException
from storage_handler import StorageHandler


class Scraper:
    def __init__(self):
        self.opened = False
#        self.webdriver = './chromedriver.exe'
        self.webdriver = './chromedriver'
        walker = os.walk('.')
        for x in walker:
            if 'chromedriver' in x[2]:
                self.webdriver = x[0]+'/chromedriver'
                break
        #for x in walker:
        #    if 'chromedriver.exe' in x[2]:
        #        self.webdriver = x[0]+'/chromedriver.exe'
        #        break
    def open(self):
        if not self.opened:
            while True:
                try:
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-dev-shm-usage')
#                    chrome_options.add_argument('--incognito')
#                    chrome_options.add_argument('--disable-application-cache')
                    self.browser = webdriver.Chrome(self.webdriver, chrome_options=chrome_options)
                    break
                except WebDriverException:
                    self.close()
                    time.sleep(1)
                    continue
            self.opened = True
    def close(self):
        if self.opened:
            StorageHandler().clearTemporary()
            try:
                self.browser.delete_all_cookies()
                self.browser.close()
            except Exception: pass
            finally:
                self.browser.quit()
                self.opened = False
    def getSelector(self, url, delay=0):
        while True:
            try:
                self.browser.get(url)
                break
            except UnexpectedAlertPresentException:
                self.close()
                self.open()
                break
            except WebDriverException:
                self.close()
                self.open()
        time.sleep(delay)
        html = self.browser.find_element_by_xpath('//*').get_attribute('outerHTML')
        selector = Selector(text=html)
        return selector

    def extractDateFromDateLine(self, date_line):
        am = u'오전'
        pm = u'오후'
        date_part = re.findall('[1-9][0-9]{3}[\.\-/][01][0-9][\.\-/][0-3][0-9]', date_line)[0]
        time_part = re.findall('((('+am+'|'+pm+')? [0-2]?[0-9]:[0-5][0-9])(:[0-5][0-9])?)', date_line)[0][0]
        if pm in time_part :
            hour = int(time_part[time_part.find(' '):time_part.find(':')])
            if hour < 12 :
                time_part = ' ' + str(hour+12) + time_part[time_part.find(':'):]
            else:
                time_part = time_part[time_part.find(' '):]
        else :
            time_part = time_part[time_part.find(' '):]

        date = date_part.replace('.','-').replace('/','-') + time_part
        return date.encode('utf-8')
    def normalizeWebContents(self, content):
        # terminate scope
        normalized_content = re.sub('\<[^\<\>]+\>', ' ', content)
        # normalized_content = re.sub('\([^\(\)]+\)', ' ', normalized_content)
        # normalized_content = re.sub('\{[^\{\}]+\}', ' ', normalized_content)
        # normalized_content = re.sub('\[[^\[\]]+\]', ' ', normalized_content)

        # terminate email, url
        normalized_content = re.sub('((file|gopher|news|nntp|telnet|https?|ftps?|sftp):\/\/)?([a-z0-9\-_]+\.)+[a-z0-9]{2,4}.*', ' ', normalized_content)

        # terminate special character
        normalized_content = normalized_content.replace('!', '.').replace(';', '.').encode('utf-8')
        # normalized_content = re.sub('[^a-zA-Z0-9가-힣\.\,\?\n ]', ' ', normalized_content)

        # terminate witespace, repeated newline
        normalized_content = re.sub('[\.]{2,}', '.', normalized_content)
        normalized_content = re.sub('[ ]{2,}', ' ', normalized_content)
        normalized_content = re.sub('[ ]+[\n]', '\n', normalized_content)
        normalized_content = re.sub('[\n]{2,}', '\n', normalized_content)

        # transfer from html character to normalized character(<,#,&..)
        normalized_content = self.transFromHtml(normalized_content)

        return normalized_content
    def transFromHtml(self, str):
        str = str.replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp', ' ').replace('&amp;', '&').replace('&quot;', '"').replace('&35;', '#')
        return str
