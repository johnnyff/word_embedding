#-*- coding: utf-8 -*-

# Developer : Jeong Wooyoung, EGLAB, Hongik University
# Contact   : gunyoung20@naver.com

import getpass, os, stat, shutil
from file_handler import FileHandler


class StorageHandler :
    fh = FileHandler('%s\\resources'%(os.getcwd()))
    #temp_dir = 'C:/Users/'+getpass.getuser()+'/AppData/Local/Temp'
    temp_dir = os.getcwd()+'/Temp'

    # document = [url, title, date_line, author, contents]
    def savetistoryDoc(self, target, document): self.fh.saveDoc(self.fh.tistory_dir, target, document)
    def saveDcinsideDoc(self, target, document): self.fh.saveDoc(self.fh.dcinside_dir, target, document)
    def saveRuliwebDoc(self, target, document): self.fh.saveDoc(self.fh.ruliweb_dir, target, document)
    def saveMlbparkDoc(self, target, document): self.fh.saveDoc(self.fh.mlbpark_dir, target, document)
    def saveInvenDoc(self, target, document): self.fh.saveDoc(self.fh.inven_dir, target, document)
    def saveTodayhumorDoc(self, target, document): self.fh.saveDoc(self.fh.todayhumor_dir, target, document)
    def savePpomppuDoc(self, target, document): self.fh.saveDoc(self.fh.ppomppu_dir, target, document)
    def saveClienDoc(self, target, document): self.fh.saveDoc(self.fh.clien_dir, target, document)
    def saveInstizDoc(self, target, document): self.fh.saveDoc(self.fh.instiz_dir, target, document)
    def saveCook82Doc(self, target, document): self.fh.saveDoc(self.fh.cook82_dir, target, document)
    def saveNaverDoc(self, target, document): self.fh.saveDoc(self.fh.naver_dir, target, document)
    def savePannDoc(self, target, document): self.fh.saveDoc(self.fh.pann_dir,target,document)
    def saveBobaeDoc(self,target, document): self.fh.saveDoc(self.fh.bobae_dir,target,document)
    def saveFmkoreaDoc(self,target, document): self.fh.saveDoc(self.fh.fmkorea_dir,target,document)
    def saveTheqooDoc(self,target, document): self.fh.saveDoc(self.fh.theqoo_dir,target,document)
    def saveEtolandDoc(self,target, document): self.fh.saveDoc(self.fh.etoland_dir,target,document)
    def saveHumorunivDoc(self,target, document): self.fh.saveDoc(self.fh.humoruniv_dir,target,document)
    def saveYgosuDoc(self,target, document): self.fh.saveDoc(self.fh.ygosu_dir,target,document)
    def saveSlrclubDoc(self,target, document): self.fh.saveDoc(self.fh.slrclub_dir,target,document)
    def saveHygallDoc(self,target, document): self.fh.saveDoc(self.fh.hygall_dir,target,document)
    def saveRankingNews(self,target,document): self.fh.saveDoc(self.fh.RankingNews_dir, target, document)
    def saveRankingNewsURL(self,target,document): self.fh.saveURL(self.fh.RankingNews_dir, target, document)
    # def saveInstaDoc(self,target, document): self.fh.saveDoc(self.fh.insta_dir,target,document)
    # def saveInstaURL(self,target,document): self.fh.saveURL(self.fh.insta_dir,target,document)
    def saveInsta(self,target, document): self.fh.saveDoc(self.fh.insta_dir,target,document)

    def saveFacebookDoc(self,target, document): self.fh.saveDoc(self.fh.facebook_dir,target,document)
    def saveNavercafeDoc(self,target, document): self.fh.saveDoc(self.fh.navercafe_dir,target,document)
    def saveDaumDoc(self,target, document): 
        print(document)
        self.fh.saveDoc(self.fh.daum_dir,target,document)
    def saveNavernewsDoc(self,target, document): self.fh.saveDoc(self.fh.navernews_dir,target,document)
    def saveYoutubeDoc(self,target, document): self.fh.saveDoc(self.fh.youtube_dir,target,document)
    def saveNaverblogDoc(self,target, document): self.fh.saveDoc(self.fh.naverblog_dir,target,document)
    # document = [Youtube No, Youtube Id,Title, Published Time, Channel Id, Description]
    def saveYoutubeDocs(self, target, document):
        documents = []
        for uid, video in zip(uids, videos):
            documents.append([uid, video['title'], video['publishedAt'], video['channelId'], video['description']])
        self.fh.writeCSVLines(self.fh.youtube_dir, target, documents, columns=[['Youtube Id','Title','Published Time','Channel Id','Description']])
    def saveYoutubeCom(self, target, comments): 
        self.fh.writeCSVLines(self.fh.youtube_dir+'/comments', target, comments, columns=[['Comment No','Comment Id','Time','Author','Content']])

    def loadURL(self, community, target, url_idx=0):
        return self.fh.loadURL(community, target, url_idx=url_idx)
    def loadContents(self,community,target):
        return self.fh.loadContents(community,target)
    def loadTitle(self,community, target, url_idx=1):
        return self.fh.loadTitle(community, target, url_idx=url_idx)
    

    def clearTemporary(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True, onerror=self.remove_readonly)
        except Exception as e:
            pass
    def remove_readonly(self, func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)
