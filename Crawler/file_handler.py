#-*- coding:utf-8 -*-
import os, shutil, stat, getpass, re
import csv,sys

import numpy as np

class FileHandler:
    def __init__(self, dir=os.getcwd().replace('\\','/')+'/resources'):
        self.delimiter = ","
        self.quotechar = '"'
        self.newLine = "\n"
        self.extension = ".csv"
        self.encoding = 'utf-8'
        self.dir = dir
        #self.temp_dir = 'C:/Users/'+getpass.getuser()+'/AppData/Local/Temp'
        self.temp_dir = dir+'/Temp'
        
        self.tistory_dir = self.dir+'/tistory'
        self.naverblog_dir = self.dir+'/naverblog'
        self.dcinside_dir = self.dir+'/dcinside'
        self.ruliweb_dir = self.dir+'/ruliweb'
        self.mlbpark_dir = self.dir+'/mlbpark'
        self.inven_dir = self.dir+'/inven'
        self.todayhumor_dir = self.dir+'/todayhumor'
        self.ppomppu_dir = self.dir+'/ppomppu'
        self.clien_dir = self.dir+'/clien'
        self.instiz_dir = self.dir+'/instiz'
        self.cook82_dir = self.dir+'/cook82'
        self.youtube_dir = self.dir+'/youtube'
        self.naver_dir = self.dir+'/naver'
        self.pann_dir = self.dir+'/pann'
        self.bobae_dir = self.dir+'/bobae'
        self.fmkorea_dir = self.dir+'/fmkorea'
        self.theqoo_dir = self.dir+'/theqoo'
        self.etoland_dir = self.dir+'/etoland'
        self.humoruniv_dir = self.dir+'/humoruniv'
        self.ygosu_dir = self.dir+'/ygosu'
        self.slrclub_dir = self.dir+'/slrclub'
        self.hygall_dir = self.dir+'/hygall'
        self.insta_dir = self.dir+'/insta'
        self.facebook_dir = self.dir+'/facebook'
        self.navercafe_dir = self.dir+'/navercafe'
        self.daum_dir = self.dir+'/daum'
        self.navernews_dir = self.dir+'/navernews'
        self.navercafehome_dir = self.dir+'/navercafehome'
        self.RankingNews_dir = self.dir+'/RankingNews'
    def saveDoc(self, dir, target, document, columns=[['URL','Title','Date Time','Author','Contents']]):
        if os.path.isfile(self.reformPath(dir,target)) :
            self.addCSVLine(dir, target, document)
    
        else :
            self.writeCSVLines(dir, target, [document], columns)
            print("Added")
## On processiong
    def saveDoc2(self, dir, target, document, columns=[['URL','Title','Date Time','Author','Contents']]):
        if os.path.isfile(self.reformPath(dir,target)) :
            self.addCSVLine(dir, target, document)
        else :
            self.writeCSVLines(dir, target, [document], columns)

    def saveURL(self,dir,target,document, columns=[['URL']]):
        target += '_URL'
        if os.path.isfile(self.reformPath(dir,target)):
            self.addCSVLine(dir,target,document)
        else:
            self.URL_writeCSVLines(dir,target,[document],columns)
    def loadDoc(self, dir, target): 
        if os.path.isfile(self.reformPath(dir,target)) :
            docs = self.readCSVLines(dir, target)
        return docs

    def loadURL(self, community, target, url_idx=0):
        lines = self.readCSVLines(self.dir+'/'+community, target)
        if not lines : return []
        return [line[url_idx] for line in lines]
    def loadContents(self,community,target,idx=4):
        lines = self.readCSVLines(self.dir+'/'+community, target)
        if not lines : return []
        return [line[-1] for line in lines]

    def loadTitle(self,community,target,url_idx=1):
        lines = self.readCSVLines(self.dir+'/'+community, target)
        if not lines : return []
        return [line[url_idx] for line in lines]

    def addCSVLine(self, dir, file, line_elements):
        path = self.reformPath(dir, file)
        dir = path[:path.rfind('/')]

        if not line_elements: return
        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(path, "a", newline='\n', encoding=self.encoding) as csv_file:
            cw = csv.writer(csv_file, delimiter=self.delimiter, quotechar=self.quotechar)
            cw.writerow(line_elements)
    
    def URL_writeCSVLines(self, dir, file, records, columns):
        
        file = self.reformFileName(file)
        if ".csv" not in file: file = file+".csv"

        path = self.reformPath(dir, file)
        dir = path[:path.rfind('/')]

        if not list: return
        if not os.path.exists(dir):
            os.makedirs(dir)

        lines = []
        if len(columns) > 0: lines += columns
        lines += records

        with open(path, "w", newline='\n', encoding=self.encoding) as csv_file:
            cw = csv.writer(csv_file, delimiter=self.delimiter, quotechar=self.quotechar)
            for row in lines:
                cw.writerow(row)
    def writeCSVLines(self, dir, file, records, columns):
        file = self.reformFileName(file)
        if ".csv" not in file: file = file+".csv"

        path = self.reformPath(dir, file)
        dir = path[:path.rfind('/')]

        if not list: return
        if not os.path.exists(dir):
            os.makedirs(dir)

        lines = []
        if len(columns) > 0: lines += columns
        lines += records

        with open(path, "w", newline='\n', encoding=self.encoding) as csv_file:
            cw = csv.writer(csv_file, delimiter=self.delimiter, quotechar=self.quotechar)
            for row in lines:
                cw.writerow(row)
    def readCSVLines(self, dir, file):
        path = self.reformPath(dir, file)
        csv.field_size_limit(sys.maxsize)
        if not os.path.exists(path):
            return None

        with open(path, "r", newline='\n', encoding=self.encoding) as csv_file:
            cr = csv.reader(csv_file, delimiter=self.delimiter, quotechar=self.quotechar)
            lines = []
            for line in cr:
                lines.append(line)

        return lines[1:]

    #########################################################################################################
    #########################################################################################################
    def getFileName(self, date): return date[:10].replace('-','')+self.extension

    def reformFileName(self, file):
        file = re.sub('^[/\\\]+', '', file)
        file = re.sub('[\\\]+', '/', file)
        if not '.' in file:
            if '.' in self.extension:
                file = file + self.extension
            else:
                file = file +'.'+ self.extension
        return file
    def reformPath(self, dir, file):
        file = self.reformFileName(file)
        dir = re.sub('[\\\]+', '/', dir)
        if dir[-1:] == '/':
            path = dir + file
        else:
            path = dir +'/'+file
        return path
    def reformContents(self, contents, to_save=True):
        contents = re.sub('([ ]?[,][ ]?)+', ',', contents)
        if to_save:
            contents = re.sub('[,]', '|/|', contents)
        else:
            contents = re.sub('[|][/][|]', ',', contents)

    def clearTemporary(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True, onerror=self.remove_readonly)
    def remove_readonly(self, func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    def removeDirTree(self, dir):
        shutil.rmtree(dir, ignore_errors=True, onerror=self.remove_readonly)
    def removeFile(self, dir, file):
        if not '.' in file:
            if '.' in self.extension:
                file = file + self.extension
            else:
                file = file +'.'+ self.extension
        if dir[-1:] == '/' or dir[-1:] == '\\':
            path = dir + file
        else:
            path = dir +'/'+file

        if os.path.isfile(path):
            os.remove(path)
