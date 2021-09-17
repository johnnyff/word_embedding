#-*- coding: utf-8 -*-

# Developer : Jeong Wooyoung
# Contact   : gunyoung20@naver.com
from __future__ import print_function
import getpass, os, stat, shutil, re
import file_handler as fh
import numpy as np
import time


class StorageHandler :
    fh.dir = '%s/community_crawler/resources'%(os.getcwd())
    print(fh.dir)
    #fh.dir = '%s\\resources'%(os.getcwd())
    temp_dir = 'C:/Users/'+getpass.getuser()+'/AppData/Local/Temp'

    #########################################################################################################
    # Content(Text)
    #########################################################################################################
    # community document = [url, title, date_line, author, contents]  if len(contents) >131072 : [url, title, date_line,author, [contents] ] where [contents] = [ contents[i:i+131072] for i in range (0, len(contents), 131072]
    # youtube document = [Youtube No, Youtube Id,Title, Published Time, Channel Id, Description]
    # youtube comment = [Comment No,Comment Id,Time,Author,Content]
    def getContents(self, keyword):
        documents = self.getDocuments(keyword)
        #comments = self.getComments(keyword)
        contents = []
        print(len(documents))
        try:
            for doc in documents:
                temp = ""
                i = 0
                if len(doc) == 7:#7:humoruniv 
                    i = 6
                elif len(doc) == 4:#4:instagram
                    i = 3
                elif len(doc) == 5:# 나머지..
                    i = 4
                #print(len(doc))
                # if i ==0:
                #     print(len(doc))
                while True:
                    temp += doc[i]
                    # temp += doc[1]
                    #print(doc[i])
                    #time.sleep(2)
                    i+=1
                    if i >= len(doc):
                        break
                content = self.reformContent(temp)
                if len(content) > 0:
                    contents.append(content)
        except Exception as e:
            print(e)
        print(len(contents))
        return contents
        """
        for doc in documents:
            # doc[4] ~ doc[len(doc)-1]
            temp = ""
            i=4
            while True:
                temp += doc[i]
                if i == len(doc):
                    break
            content = self.reformContent(temp)
#            content = self.reformContent(doc[len(doc)-1])
#            content = self.reformContent(doc[4])
            if len(content) > 0:
                contents.append(content)
#        for com in comments:
#            content = self.reformContent(com[len(com)-1])
#            content = self.reformContent(com[4])
#            if len(content) > 0:
#                contents.append(content)
        print(len(contents))
        return contents
        """

    def getDocuments(self, target):
        documents = []
        for c_dir in fh.community_dirs:
            try:
                docs = self.loadDoc(c_dir, target)
            except:
                continue
            if not docs is None:
                documents += docs
        return documents
    def getComments(self, target):
        comments = []
        for c_dir in fh.comment_dirs:
            path = c_dir + '/comments/' + target
            print(path)
            if( os.path.isdir(path)):
                files = os.listdir(path)
                for file in files:
                    coms = fh.loadCSV(path, file)
                    comments += coms
        return comments

    def saveDoc(self, dir, target, document, columns=[['URL', 'Title', 'Date Time', 'Author', 'Contents']]):
        if os.path.isfile(fh.reformPath(dir, target)):
            fh.addCSVLine(dir, target, document)
        else:
            fh.saveCSV(dir, target, document, columns)
    def loadDoc(self, dir, target):
        if os.path.isfile(fh.reformPath(dir, target)):
            return fh.loadCSV(dir, target)
        return None
    #########################################################################################################
    # vectorization
    #########################################################################################################
    def saveVectorizedContents(self, contents, path=None, file='vectorized_contents', using_dict=False):
        if path is None: path = '%s/Backup' % (os.getcwd()).replace('\\', '/')
        path += '/using_dict' if using_dict else '/un_using_dict'
        fh.clearDirs(path)
        for i, c in enumerate(contents):
            fh.saveCSV(path, '%s_%d.csv' % (file, i + 1), c)
    def loadVectorizedContents(self, path=None, file='vectorized_contents', using_dict=False):
        if path is None: path = '%s/Backup' % (os.getcwd()).replace('\\', '/')
        path += '/using_dict' if using_dict else '/un_using_dict'
        contents = np.array(fh.loadCSV(path, '%s_1.csv' % (file)), dtype=np.float_)
        contents = contents.reshape(1, contents.shape[0], contents.shape[1])
        files = os.listdir(path)
        for i in range(1, len(files)):
            content = np.array(fh.loadCSV(path, 'vectorized_contents_%d.csv' % (i + 2)), dtype=np.float_)
            try:
                contents = np.concatenate((contents, [content]), axis=0)
            except Exception as e:
                print(e)
        return np.array(contents)

    #########################################################################################################
    # sentiment analysis
    #########################################################################################################
    # def getSentiDictionary(self):
    #     lines = fh.loadCSV(os.getcwd(), 'NS.csv', column_rows=1, encode='MS949')
    #     dict = {}
    #     for w, p, s in lines:
    #         ogn = re.sub('(다|하다|이다)$', '', p)
    #         if len(ogn) < 2 :
    #             ogn = p[:-1]
    #             if len(ogn) < 2 : ogn = p
    #         if not ogn in dict.keys():
    #             dict[ogn] = float(s)
    #         else:
    #             dict[ogn] = (dict[ogn] + float(s)) / 2
    #     return dict
    # def getSentiDictionary(self):
    #     lines = fh.loadCSV(os.getcwd(), 'ND.csv', column_rows=1, encode='MS949')
    #     dict = {}
    #     for w, p, s in lines:
    #         ogn = re.sub('(다|하다|이다)$', '', p)
    #         if len(ogn) < 2 :
    #             ogn = p[:-1]
    #             if len(ogn) < 2 : ogn = p
    #         if not ogn in dict.keys():
    #             dict[ogn] = float(s)
    #         else:
    #             dict[ogn] = (dict[ogn] + float(s)) / 2
    #     return dict
    # def getSentiDictionary(self):
    #     lines = fh.loadCSV(os.getcwd(), 'sd.csv', column_rows=1, encode='MS949')
    #     dict = {}
    #     for w, p, s in lines:
    #         ogn = re.sub('(다|하다|이다)$', '', w)
    #         if len(ogn) < 2 :
    #             ogn = w[:-1]
    #             if len(ogn) < 2 : ogn = w
    #         if not ogn in dict.keys():
    #             dict[ogn] = float(s)
    #         else:
    #             dict[ogn] = (dict[ogn] + float(s)) / 2
    #     return dict
    def getSentiDictionary(self):
        lines = fh.loadCSV(os.getcwd(), 'New adjective.csv', column_rows=1, encode='MS949')
        #print(lines)
        dict = {}
        for w, p, s, k in lines:
            ogn = re.sub('(다|하다|이다)$', '', w)
            if len(ogn) < 2 :
                ogn = w[:-1]
                if len(ogn) < 2 : ogn = w
            if not ogn in dict.keys():
                dict[ogn] = float(s)
            else:
                dict[ogn] = (dict[ogn] + float(s)) / 2
        return dict
    #########################################################################################################
    # calculation
    #########################################################################################################
    def saveElmoWords(self,result,num_of_words,path=None,file='Vectors'):
        print("Start saveElmoScore")
        self.saveElmoScore(result,num_of_words,path,file)
        print("Start saveElmoRelated")
        self.saveElmoRelated(result,num_of_words,path,file)
        
    def saveBertWords(self,result,num_of_words,path=None,file='Vectors'):
        print("Start saveBertScore")
        self.saveElmoScore(result,num_of_words,path,file)
        print("Start saveBertRelated")
        self.saveElmoRelated(result,num_of_words,path,file)

    def saveElmoScore(self,result,num_of_words,path=None,file='Vectors'):
        line = []
        for w in result.keys():
            if num_of_words[w] > 9:
                line.append([w,num_of_words[w],result[w]['score']['total'],result[w]['count']['total'],result[w]['score']['p'],result[w]['count']['p'],
                result[w]['score']['n'],result[w]['count']['n']])
        line.sort(key = lambda x:x[1],reverse = True)  # 점수 / 빈도수로
        if path is None: path = '%s/Results/Scores' % (os.getcwd()).replace('\\', '/')
        fh.saveCSV(path, file, line, columns=[['Word', 'Count', 'Score', 'Senti-Count', 'P_Score', 'P_Count', 'N_Score', 'N_Count']])
        return 

    def saveElmoRelated(self,result,num_of_words,path=None,file='Vectors'):
        lines = []
        line =[]
        for w in result:
            if num_of_words[w] >9:
                related = result[w]['related']
                #print(related)
                st_words = sorted(related.items(), key=(lambda x:x[1]['count']), reverse=True)
                line=[w,num_of_words[w]]#,result[w]]
                for rw, info in st_words:
                    #print(info)
                    if info['count'] >= 5:
                        #print(info['count'])
                        line+=(['%s(%f, %d)'%(rw, info['score'], info['count'])])
                        # print(line)
                        #lines.append(line+(['%s(%f, %d)'%(rw, info['score'], info['count'])]))
                lines.append(line)
                #lines.append([w,num_of_words[w],result[w]]+['%s(%f, %d)'%(rw, info['score'], info['count']) for rw, info in st_words])
        #print(lines)
        lines.sort(key = lambda x: x[1],reverse = True)
        
        if path is None: path = '%s/Results/Related' % (os.getcwd()).replace('\\', '/')
        fh.saveCSV(path, file, lines, columns=[['Word', 'Related word & Score("word(score, count)")']])
        return  




    def saveSentiWords(self, selected_words, num_of_words, senti_words, path=None, file='Vectors'):
        self.saveScoreOfWords(selected_words, num_of_words, senti_words, path, file)
        self.saveRelatedOfWords(selected_words, senti_words, path, file)

    # selected_words = [word]
    # num_of_words = {word:count}
    # senti_words_in_sentence = {word:{'score':__score__, 'count':__count__}}
    # score = {'P':positive score, 'N':negative score, 'total':sum score}
    # count = {'P':positive count, 'N':negative count, 'total':sum count}
    # senti_words = {word:{'score':score,'count':count, 'related':senti_words_in_sentence}}
    def saveScoreOfWords(self, selected_words, num_of_words, senti_words, path=None, file='Vectors'):
        lines = []
        for w in selected_words:
            score = senti_words[w]['score']
            count = senti_words[w]['count']
            lines.append([w, num_of_words[w], score['total'], count['total'], score['P'], count['P'], score['N'], count['N']])
        if path is None: path = '%s/Results/Scores' % (os.getcwd()).replace('\\', '/')
        fh.saveCSV(path, file, lines, columns=[['Word', 'Count', 'Score', 'Senti-Count', 'P_Score', 'P_Count', 'N_Score', 'N_Count']])
    def loadScoreOfWords(self, path=None, file='Vectors.csv'):
        if path is None: path = '%s/Results/Scores' % (os.getcwd()).replace('\\', '/')
        lines = fh.loadCSV(path, file, column_rows=1)
        selected_words = []
        num_of_words = {}
        senti_words_of_score = {}
        for line in lines:
            w = line[0]
            selected_words.append(w)
            num_of_words[w] = int(line[1])

            score = {'total':float(line[2]), 'P':float(line[4]), 'N':float(line[6])}
            count = {'total':int(line[3]), 'P':int(line[5]), 'N':int(line[7])}
            senti_words_of_score[w] = {'score':score, 'count':count}

        return selected_words, num_of_words, senti_words_of_score

    # senti_words_in_sentence = {word:{'score':__score__, 'count':__count__}}
    # score = {'P':positive score, 'N':negative score, 'total':sum score}
    # count = {'P':positive count, 'N':negative count, 'total':sum count}
    # senti_words = {word:{'score':score,'count':count, 'related':senti_words_in_sentence}}
    def saveRelatedOfWords(self, selected_words, senti_words, path=None, file='Vectors'):
        lines = []
        for w in selected_words:
            related = senti_words[w]['related']
            st_words = sorted(related.items(), key=(lambda x:x[1]['count']), reverse=True)
            lines.append([w]+['%s(%f, %d)'%(rw, info['score'], info['count']) for rw, info in st_words])
        if path is None: path = '%s/Results/Related' % (os.getcwd()).replace('\\', '/')
        fh.saveCSV(path, file, lines, columns=[['Word', 'Related word & Score("word(score, count)")']])
    def loadRelatedOfWords(self, path=None, file='Vectors.csv'):
        if path is None: path = '%s/Results/Related' % (os.getcwd()).replace('\\', '/')
        lines = fh.loadCSV(path, file, column_rows=1)
        selected_words = []
        related_senti_words = {}
        for line in lines:
            word = line[0]
            selected_words.append(word)

            senti_words_in_sentence = {}
            for row in line[1:]:
                w = row[:row.find('(')]
                score = float(row[row.find('(')+1:row.find(',')])
                count = int(row[row.find(',')+1:row.find(')')])
                senti_words_in_sentence[w] = {'score':score, 'count':count}
            related_senti_words[word] = senti_words_in_sentence

        return selected_words, related_senti_words

    #########################################################################################################
    #########################################################################################################
    def reformContent(self, content):
        tmp = content
        tmp = re.sub('[ ]?-[ a-zA-Z\']+$', '', tmp)
        tmp = re.sub('[ㄱ-ㅎㅏ-ㅣ]+', '', tmp)
        tmp = re.sub('[ ]{2,}|[.]{2,}', ' ', tmp)
#        tmp = re.sub('([!?]+([ ]+)?)|([(){}\[\]].+[(){}\[\]])', '', tmp)
        tmp = re.sub('http[s]?://[a-zA-Z\-_0-9]+\.[a-zA-Z\-_0-9.]+(/[a-zA-Z\-_0-9./=&?∣]+)?', '', tmp)
        tmp = re.sub('cafe.[a-zA-Z\-_0-9]+\.[a-zA-Z\-_0-9.]+(/[a-zA-Z\-_0-9./=&?]+)?', '', tmp)
        tmp = re.sub('[a-zA-Z\-_0-9]+@[a-zA-Z\-_0-9]+\.[a-zA-Z\-_0-9.]+', '', tmp)
        tmp = re.sub('[가-힣]+([ ]?[0-9]+)?[ ]?:[ ]?|[0-9]+[ ]?:[ ]?', ' ', tmp)
        tmp = re.sub('[^가-힣0-9a-zA-Z\n\t\r ]+|[.]+', ' ', tmp)
        tmp = re.sub('[\n ]+', ' ', tmp)
        tmp = re.sub('^[ ]+|[ ]+$', '', tmp)
        return tmp


    def clearTemporary(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True, onerror=self.remove_readonly)
        except Exception as e:
            pass
    def remove_readonly(self, func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)
