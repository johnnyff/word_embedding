#-*- coding:utf-8 -*-

# Developer : Jeong Wooyoung
# Contact   : gunyoung20@naver.com

import os, shutil, stat, getpass, re
import csv
import time
import numpy as np
import sys
csv.field_size_limit(sys.maxsize)
delimiter = ","
quotechar = '"'
newline = "\n"
extension = ".csv"
encoding = 'utf-8-sig'
dir = os.getcwd().replace('\\','/')+'/community_crawler/resources'
#dir = os.getcwd().replace('\\','/')+'/resources'
temp_dir = 'C:/Users/'+getpass.getuser()+'/AppData/Local/Temp'

dcinside_dir = dir+'/dcinside'
ruliweb_dir = dir+'/ruliweb'
mlbpark_dir = dir+'/mlbpark'
inven_dir = dir+'/inven'
todayhumor_dir = dir+'/todayhumor'
ppomppu_dir = dir+'/ppomppu'
clien_dir = dir+'/clien'
instiz_dir = dir+'/instiz'
cook82_dir = dir+'/cook82'
youtube_dir = dir+'/youtube'
naver_dir = dir+'/naver'
pann_dir = dir+'/pann'
bobae_dir = dir+'/bobae'
fmkorea_dir = dir+'/fmkorea'
theqoo_dir = dir+'/theqoo'
etoland_dir = dir+'/etoland'
humoruniv_dir = dir+'/humoruniv'
ygosu_dir = dir+'/ygosu'
insta_dir = dir+'/insta'
hygall_dir = dir+'/hygall'
navercafe_dir = dir+'/navercafe'
facebook_dir = dir+'/facebook'
daum_dir = dir+'/daum'
navernews_dir = dir+'/navernews'
tistory_dir = dir + '/tistory'
naverblog_dir = dir+'/naverblog'
insta_dir = dir+'/insta'
RankingNews_dir = dir + '/RankingNews'
community_dirs = [
    dcinside_dir, ruliweb_dir, mlbpark_dir, 
    inven_dir, todayhumor_dir, ppomppu_dir, 
    clien_dir, instiz_dir, cook82_dir, 
    naver_dir, pann_dir, bobae_dir, fmkorea_dir, 
    theqoo_dir, etoland_dir, humoruniv_dir, 
    ygosu_dir,insta_dir,hygall_dir,youtube_dir,
    navercafe_dir, facebook_dir,daum_dir
    ,navernews_dir, tistory_dir, naverblog_dir, insta_dir, RankingNews_dir]
    # navercafe_dir]

#community_dirs = [dcinside_dir, ruliweb_dir, mlbpark_dir, inven_dir, todayhumor_dir, ppomppu_dir, clien_dir, instiz_dir, cook82_dir, naver_dir, fmkorea_dir, theqoo_dir, etoland_dir, humoruniv_dir, ygosu_dir,hygall_dir]
#community_dirs = [inven_dir]
#comment_dirs = [youtube_dir]
# ruliweb,ppomppu , pann , fmkorea , theqoo , etoland , humoruniv , ygosu
#########################################################################################################
# File
#########################################################################################################

def getFileName(date): return date[:10].replace('-','')+extension

def reformFileName(file):
    file = re.sub('[\\\]+', '/', file)
    file = re.sub('^[/]+', '', file)
    if not '.' in file:
        if '.' in extension:
            file = file + extension
        else:
            file = file +'.'+ extension
    return file
def reformPath(dir, file):
    file = reformFileName(file)
    dir = re.sub('[\\\]+', '/', dir)
    if dir[-1:] == '/':
        path = dir + file
    else:
        path = dir +'/'+file
    return path

def makeDirectories(directory):
    if '\\' in directory: directory = directory.replace('\\', '/')
    if '/' in directory:
        u_dir = directory[:directory.rfind('/')]
        if not os.path.isdir(u_dir):
            makeDirectories(u_dir)
    if not os.path.isdir(directory):
        os.makedirs(directory)
def clearDirs(dir):
    if not os.path.isdir(dir) : return
    files = os.listdir(dir)
    for file in files:
        if 'tmp' in file:
            if not os.path.isfile(dir+file) :
                try: shutil.rmtree(dir+file)
                except OSError as e: pass
def clearTemporary():
    shutil.rmtree(temp_dir, ignore_errors=True, onerror=remove_readonly)
def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)
def removeDirTree(dir):
    shutil.rmtree(dir, ignore_errors=True, onerror=remove_readonly)
def removeFile(dir, file):
    if not '.' in file:
        if '.' in extension:
            file = file + extension
        else:
            file = file +'.'+ extension
    if dir[-1:] == '/' or dir[-1:] == '\\':
        path = dir + file
    else:
        path = dir +'/'+file

    if os.path.isfile(path):
        os.remove(path)

#########################################################################################################
# CSV
#########################################################################################################

def addCSVLine(dir, file, line_elements):
    path = reformPath(dir, file)
    dir = path[:path.rfind('/')]

    if not line_elements: return
    if not os.path.exists(dir):
        os.makedirs(dir)

    with open(path, "a", newline=newline, encoding=encoding) as csv_file:
        cw = csv.writer(csv_file, delimiter=delimiter, quotechar=quotechar)
        cw.writerow(line_elements)
def saveCSV(dir, file, list, columns=[], mode='w'):
    file = reformFileName(file)
    tm = time.localtime()
    
    if ".csv" not in file: file = file+'_'+str(tm.tm_year)+ str(tm.tm_mon)+str(tm.tm_mday)+'_'+str(tm.tm_hour)+':'+str(tm.tm_min)+':'+str(tm.tm_sec)+".csv"
    else: temp = file.split('.csv'); file = temp[0] +'_'+ str(tm.tm_year)+ str(tm.tm_mon)+str(tm.tm_mday)+'_'+str(tm.tm_hour)+':'+str(tm.tm_min)+':'+str(tm.tm_sec)+".csv"
    path = reformPath(dir, file)
    dir = path[:path.rfind('/')]

    if not list: return
    if not os.path.exists(dir):
        os.makedirs(dir)

    lines = []
    if len(columns) > 0: lines += columns
    lines += list

    with open(path, mode, newline=newline, encoding=encoding) as csv_file:
        cw = csv.writer(csv_file, delimiter=delimiter, quotechar=quotechar)
        for row in lines:
            cw.writerow(row)
def loadCSV(dir, file, column_rows=1, mode='r', encode=None):
    path = reformPath(dir, file)
    if not os.path.exists(path):
        sys.stderr.write(dir+'\n')
        return None
    if encode is None: encode = encoding
    with open(path, mode, newline=newline, encoding=encode) as csv_file:
        cr = csv.reader(csv_file, delimiter=delimiter, quotechar=quotechar)
        lines = []
        for line in cr:
            lines.append(line)

    return lines[column_rows:]

