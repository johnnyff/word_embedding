# coding: utf-8

# Developer : Jeong Wooyoung
# Contact   : gunyoung20@naver.com

import os
import numpy as np
from gensim.models import Word2Vec

from soynlp.word import WordExtractor
from soynlp.tokenizer import LTokenizer

import file_handler as fh
from storage_handler import StorageHandler

import pandas as pd
import sentencepiece as spm
import urllib.request
import csv

sh = StorageHandler()

class SentiCorpus:
    def __init__(self, contents, iter_sent = False):
        self.iter_sent = iter_sent
        self.lines = contents
    def __iter__(self):
        for line in self.lines:
            if line == '\n': continue
            yield line
    def __len__(self):
        return len(self.lines)
class Sentence_piece:
    def __init__(self):
        self.tokenizer = None
        self.trained = False
    def getTokenizer(self, contents):
        parameter = '--input={} --model_prefix={} --vocab_size={} --user_defined_symbols={}'

        input_file = 'corpus.txt'
        vocab_size = 32000
        prefix = 'bert_kor'
        user_defined_symbols = '[PAD],[UNK],[CLS],[SEP],[MASK]'
        cmd = parameter.format(input_file, prefix, vocab_size,user_defined_symbols)

        spm.SentencePieceTrainer.Train(cmd)

        sp = spm.SentencePieceProcessor()
        sp.Load('{}.model'.format(prefix))
        print(contents)
        ids = []
        for c in contents:
            id = sp.encode_as_ids(c)
            ids.append(id)
        corpus = SentiCorpus(contents, iter_sent=True)
        word_extractor = WordExtractor(corpus)
        word_extractor.train(corpus)
        words_scores = word_extractor.extract()
        scores = {word: score.cohesion_forward for word, score in words_scores.items()}
        return LTokenizer(scores=scores)
    def tokenizing(self, contents):
        if self.tokenizer is None: 
            self.tokenizer = self.getTokenizer(contents)
        tokenized_contents = []
        for c in contents:         
            tokenized_contents.append(self.tokenizer(c))
        return tokenized_contents
    def vectorize(self, model_path, contents, dims=20, training=True, padding=False, using_dict=True):
        print("start vectorizing")
        if using_dict: dim = dims-1
        else: dim = dims
        if training:
            tokenized_contents = self.tokenizing(contents)

#            word2vec_model = Word2Vec(tokenized_contents, size=dim, window=3, min_count=5, workers=8, iter=1000, sg=1)
            word2vec_model = Word2Vec(tokenized_contents, size=dim, window=3, min_count=5, workers=16, iter=1000, sg=1)
            dir_path = model_path[:model_path.rfind('/')]

            if not os.path.isdir(dir_path): fh.makeDirectories(dir_path)
            word2vec_model.save(model_path)
            self.trained = True
        elif os.path.isfile(model_path):
            tokenized_contents = self.tokenizing(contents)
            word2vec_model = Word2Vec.load(model_path)
        else: return None

        w2v_vectors = word2vec_model.wv
        print("training start")
        # 추후 작업필요(기본형 기준 매칭 정확도 개선필요)
        threshold = 0.2
        if using_dict:
            senti_dict = sh.getSentiDictionary()
            word_vectors = {w:w2v_vectors[w].tolist()+[(-1.0 if senti_dict[w[:2]] < -threshold else 1.0 if senti_dict[w[:2]] > threshold else .0) if w[:2] in senti_dict.keys() else .0] for w in w2v_vectors.vocab.keys()}
        else: word_vectors = {w:w2v_vectors[w].tolist() for w in w2v_vectors.vocab.keys()}
        vectors = {'word_vectors':word_vectors}

        # 문장을 벡터리스트로 전환
        print("vectorize the sentence")
        max_len = 0
        vectorized_contents = []
        usable_contents = []
        num_of_words = {}
        for s in tokenized_contents :
            vectorized_content = []
            usable_content = []
            for w in s:
                if w in word_vectors.keys():
                    vectorized_content.append(word_vectors[w])
                    usable_content.append(w)
                    if w in num_of_words.keys(): num_of_words[w] +=1
                    else: num_of_words[w]=1
            length = len(vectorized_content)
            if length > 0:
                vectorized_contents.append(np.array(vectorized_content))
                usable_contents.append(np.array(usable_content))
            if length > max_len: max_len = length
        vectors['usable_contents'] = usable_contents
        vectors['num_of_words'] = num_of_words

        # 벡터리스트 패딩
        print("padding start")
        if padding:
            padded_contents = np.zeros((1, max_len, dims))
            for v in vectorized_contents:
                size = len(v)
                if size < max_len: padded_contents = np.concatenate((padded_contents, [np.array(np.zeros((max_len-size, dims)).tolist()+v.tolist())]), axis=0)
                else: padded_contents = np.concatenate((padded_contents,[v]), axis=0)
            vectors['vectorized_contents'] = padded_contents[1:]
        else: vectors['vectorized_contents'] = vectorized_contents
        return vectors

class Vectorizer:
    def __init__(self):
        self.tokenizer = None
        self.trained = False
    def getTokenizer(self, contents):
        corpus = SentiCorpus(contents, iter_sent=True)
        word_extractor = WordExtractor(corpus)
        word_extractor.train(corpus)
        words_scores = word_extractor.extract()
        scores = {word: score.cohesion_forward for word, score in words_scores.items()}
        return LTokenizer(scores=scores)
    def tokenizing(self, contents):
        if self.tokenizer is None: 
            self.tokenizer = self.getTokenizer(contents)
            
        tokenized_contents = []
        for c in contents:         
            tokenized_contents.append(self.tokenizer(c))
        return tokenized_contents
    def vectorize(self, model_path, contents, dims=20, training=True, padding=False, using_dict=True):
        print("start vectorizing")
        if using_dict: dim = dims-1
        else: dim = dims
        if training:
            tokenized_contents = self.tokenizing(contents)

#            word2vec_model = Word2Vec(tokenized_contents, size=dim, window=3, min_count=5, workers=8, iter=1000, sg=1)
            word2vec_model = Word2Vec(tokenized_contents, size=dim, window=3, min_count=5, workers=16, iter=1000, sg=1)
            dir_path = model_path[:model_path.rfind('/')]

            if not os.path.isdir(dir_path): fh.makeDirectories(dir_path)
            word2vec_model.save(model_path)
            self.trained = True
        elif os.path.isfile(model_path):
            tokenized_contents = self.tokenizing(contents)
            word2vec_model = Word2Vec.load(model_path)
        else: return None

        w2v_vectors = word2vec_model.wv
        print("training start")
        # 추후 작업필요(기본형 기준 매칭 정확도 개선필요)
        threshold = 0.2
        if using_dict:
            senti_dict = sh.getSentiDictionary()
            word_vectors = {w:w2v_vectors[w].tolist()+[(-1.0 if senti_dict[w[:2]] < -threshold else 1.0 if senti_dict[w[:2]] > threshold else .0) if w[:2] in senti_dict.keys() else .0] for w in w2v_vectors.vocab.keys()}
        else: word_vectors = {w:w2v_vectors[w].tolist() for w in w2v_vectors.vocab.keys()}
        vectors = {'word_vectors':word_vectors}

        # 문장을 벡터리스트로 전환
        print("vectorize the sentence")
        max_len = 0
        vectorized_contents = []
        usable_contents = []
        num_of_words = {}
        for s in tokenized_contents :
            vectorized_content = []
            usable_content = []
            for w in s:
                if w in word_vectors.keys():
                    vectorized_content.append(word_vectors[w])
                    usable_content.append(w)
                    if w in num_of_words.keys(): num_of_words[w] +=1
                    else: num_of_words[w]=1
            length = len(vectorized_content)
            if length > 0:
                vectorized_contents.append(np.array(vectorized_content))
                usable_contents.append(np.array(usable_content))
            if length > max_len: max_len = length
        vectors['usable_contents'] = usable_contents
        vectors['num_of_words'] = num_of_words

        # 벡터리스트 패딩
        print("padding start")
        if padding:
            padded_contents = np.zeros((1, max_len, dims))
            for v in vectorized_contents:
                size = len(v)
                if size < max_len: padded_contents = np.concatenate((padded_contents, [np.array(np.zeros((max_len-size, dims)).tolist()+v.tolist())]), axis=0)
                else: padded_contents = np.concatenate((padded_contents,[v]), axis=0)
            vectors['vectorized_contents'] = padded_contents[1:]
        else: vectors['vectorized_contents'] = vectorized_contents
        return vectors
    

    
