#-*- coding: utf-8 -*-

# Developer : Dongin Kang
# Contact   : rkd2016@gmail.com  , kw0095@naver.com
from __future__ import print_function
from sklearn.cluster import DBSCAN
import re, sys
import numpy as np

from storage_handler import StorageHandler
import time
import tensorflow_hub as hub
import tensorflow as tf
import os
import warnings
from tqdm import tqdm, trange

import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel
from transformers import AutoTokenizer, AutoModel, AutoModelWithLMHead
from transformers import ElectraModel, ElectraTokenizer, BertModel
from transformers import AutoModelForSequenceClassification
from transformers import TrainingArguments
from transformers import Trainer


from vectorizer import Vectorizer
from konlpy.tag import Mecab
from sklearn.metrics.pairwise import cosine_similarity

from tokenization_kobert import KoBertTokenizer
from kobert_tokenizer import KoBERTTokenizer

from kobert.utils import get_tokenizer
from kobert.pytorch_kobert import get_pytorch_kobert_model
from sklearn.metrics.pairwise import cosine_similarity

import logging
warnings.filterwarnings(action='ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
sh = StorageHandler()

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
tf.get_logger().setLevel(logging.ERROR)
tf.autograph.set_verbosity(1)


#########################################################################################################
# Viewer
#########################################################################################################
def progressBar(value, endvalue,  bar_length=60):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rCalculating practice: [{0}] {1}% ".format(arrow + spaces, int(round(percent * 100)) ))
    #sys.stdout.flush()
def progressBarwith_time(value, endvalue, start_time, bar_length=60):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rCalculating practice: [{0}] {1}%  {2}sec".format(arrow + spaces, int(round(percent * 100)),time.time()-start_time ))
    #sys.stdout.flush()
    

#########################################################################################################
# calculation
#########################################################################################################
def clustering(vectors):
    word_vectors = vectors['word_vectors']
    num_of_words = vectors['num_of_words']

    word_set = [word for word in word_vectors.keys()]
    vec_set = [word_vectors[word] for word in word_set]
    cluster = DBSCAN(min_samples=5, metric='cosine')
    labels = cluster.fit_predict(vec_set)

    cluster_group = {}
    for label, word in zip(labels, word_set):
        if label in cluster_group.keys():
            cluster_group[label][word] = num_of_words[word]
        else:
            cluster_group[label] = {word:num_of_words[word]}

    return cluster_group

def selectUsableWords(cluster_group, max_select=5):
    selected_words = []
    for label in cluster_group.keys():
        sorted_by_count = sorted(cluster_group[label].items(), key=(lambda x:x[1]), reverse=True)

        words_in_group = []
        for w in sorted_by_count:
            if len(w[0]) > 1: words_in_group.append(w[0])
            # words_in_group.append(w[0])
        if len(words_in_group) > max_select: selected_words += words_in_group[:max_select]
        else: selected_words += words_in_group
    return selected_words

def getSentimentScoreOnSelectedWords(tokenized_contents, selected_words):
    total = len(tokenized_contents)
    one_per = int(total/100)

    senti_dict = sh.getSentiDictionary()

    # ?????? ????????? ????????? ???????????? ??????????????? ????????????, ????????????
    senti_words = {}
    for i, t_content in enumerate(tokenized_contents):
        # ?????? ????????? ????????? ?????? ?????? ??????
        selected_words_in_sentence = []
        # token list??? sentence ???????????? ??????
        sentence = ''
        for word in t_content:
            sentence += word+' '
            if word in selected_words: selected_words_in_sentence.append(word)
        sentence = sentence[:-1]

        # ??????????????? ?????? ????????? ?????? ????????? ?????????????????? ?????? ?????? ?????? ??? ?????? ?????? ?????? ??????
        score = {'P':0.0, 'N':0.0, 'total':0.0}
        count = {'P':0, 'N':0, 'total':0}
        # ????????? ????????? ?????? ?????? ??? ?????? ??????
        senti_words_in_sentence = {}
        for s in senti_dict.keys():
            match = re.search('[ ]?'+s+'[^ ]*', sentence)
            # ??????????????? ?????? ?????? s??? ?????? ????????? ??????
            if not match is None:
                if senti_dict[s] > 0:
                    score['P'] += senti_dict[s]
                    count['P'] += 1
                elif senti_dict[s] < 0:
                    score['N'] += senti_dict[s]
                    count['N'] += 1

                score['total'] += senti_dict[s]
                count['total'] += 1

                senti_words_in_sentence[s] = {'score':senti_dict[s], 'count':1}

        # ?????? ????????? ????????? ???????????? ?????? ????????? ???????????? ??????
        for word in selected_words_in_sentence:
            if word in senti_words.keys():
                senti_words[word]['score']['P'] += score['P']
                senti_words[word]['score']['N'] += score['N']
                senti_words[word]['score']['total'] += score['total']

                senti_words[word]['count']['P'] += count['P']
                senti_words[word]['count']['N'] += count['N']
                senti_words[word]['count']['total'] += count['total']

                for w in senti_words_in_sentence.keys():
                    if w in senti_words[word]['related'].keys():
                        cnt = int(senti_words_in_sentence[w]['count'])
                        senti_words[word]['related'][w]['count'] += cnt
                    else:
                        senti_words[word]['related'][w] = senti_words_in_sentence[w]
            else:
                senti_words[word] = {'score':score.c,'count':count, 'related':senti_words_in_sentence}
        if (one_per>0):
            if (i+1)%one_per == 0:
                progressBar(i+1, total)
    # senti_words_in_sentence = {word:{'score':__score, 'count':__count}}
    # score = {'P':positive score, 'N':negative score, 'total':sum score}
    # count = {'P':positive count, 'N':negative count, 'total':sum count}
    # senti_words = {word:{'score':score,'count':count, 'related':senti_words_in_sentence}}
    return senti_words


#######################################################################################################################



# return ?????? vectors
def getElmoVector(contents , first):
    start_time = time.time()
    vectors = {'word_vectors': {}, 'num_of_words' : {}}
    total = len(contents)
    file = open("./stopwords.txt", "r")
    stop_list = file.read().split()
    one_per = int(total/100)
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
	    # Currently, memory growth needs to be the same across GPU
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        except RuntimeError as e:
            print(e)
        # Memory growth must be set before GPUs have been initialized
    embed = hub.load("https://tfhub.dev/google/elmo/3")
    for num,temp in enumerate(contents):
        
        # t : ????????? ?????????+????????? corpus??? tokenized??? word list  ex) ['??????','???','??????']
        sentence = ''
        t = []        
        for word in temp:
        # t??? string????????? ???????????? ????????????, ????????? ??????
            if word in stop_list:
                continue
            sentence+= word+' '
            t.append(word)
        # ????????? ????????? vectors??? ??????        
        tf_sentence = tf.constant([sentence])
        #print(len(temp))
        try:
            sentence_output = embed.signatures['default'](tf_sentence)
            sentence_vec = sentence_output['word_emb']
        except :
            continue
        #print(sentence_vec.shape)
        
        # sentence_vec = [ v1,v2,v3,.......vn] , v1??? temp[1]??? ?????? vector???
        
        for index,word in enumerate(t):
            if word not in vectors['word_vectors']: vectors['word_vectors'][word] = sentence_vec[0][index]; vectors['num_of_words'][word]=1
            else:
                if first:
                    # ??? ?????? ????????? ???????????? ??????, vectors['word_vectors']??? ?????? ???????????? ?????? ??????
                    vectors['num_of_words'][word]+=1
                else:
                    #????????? ????????? ???????????? ??????
                    vectors['word_vectors'][word] = sentence_vec[0][index]; vectors['num_of_words'][word]+=1
        if (one_per>0):
            progressBar(num+1, total)
        
    # ??? vector?????? .numpy()??? ?????? float??? ????????????
    # vectors = {  'word_vectors': [], 'num_of_words' : []}
    # embeding ???, vectors['word_vectors'][word] ??? ??????
    # ??? ?????? ????????? ???????????? ??????,
    # if word not in vectors['word_vectors']: vectors['word_vectors'][word] = embeding ; vectors['num_of_words'][word] = 1
    # else: vectors['num_of_words'][word]+=1
    # ????????? ????????? ???????????? ??????,
    # if word not in vectors['word_vectors']: vectors['word_vectors'][word] = embeding ; vectors['num_of_words'][word] = 1
    # else: vectors['word_vectors'][word] = embeding ; vectors['num_of_words'][word]+=1
        


    print("Vectorizing time : ",end='')
    print(time.time() - start_time,end='')
    print(" sec")
    return vectors




########################################################################################################################


def tokenize_function(examples):
    tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
    return tokenizer(examples, padding="max_length", truncation=True)


# def new_getBertScore(contents, keyworkd, num_of_words):


def getBertScore(contents,keyword,  num_of_words):
    start_time = time.time()
    total = len(contents)
    file = open("./stopwords.txt", "r")
    stop_list = file.read().split()

    one_per = int(total/100)
    result = {}
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
	    # Currently, memory growth needs to be the same across GPU
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        except RuntimeError as e:
            #print(e)
            pass
        # Memory growth must be set before GPUs have been initialized
    senti_dict = sh.getSentiDictionary()
    tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
    model = BertModel.from_pretrained('monologg/kobert')

    keyword_vector_sum = []
    
    keyword_vector_cnt = 0
    kw = ['[CLS]' , keyword , '[SEP]']
    kw_indexed_tokens = tokenizer.convert_tokens_to_ids(kw)
    kw_segments_ids = [1] * len(kw_indexed_tokens)
    kw_tokens_tensor = torch.tensor([kw_indexed_tokens])
    kw_segments_tensors = torch.tensor([kw_segments_ids])
    kw_output, _ = model(kw_tokens_tensor, kw_segments_tensors)
    kw_vec = kw_output[0][1]
    for num, temp in enumerate(contents):
        # s_time = time.time()
        sentence = ''
        keyword_vector_avg = []
        # print("temp :", temp)
        t = []
        word_in_sentence = {}
        temp.insert(0,'[CLS]')
        temp.append('[SEP]')
        #tokenized_text = tokenizer.tokenize(temp)
        tokenized_text = temp
        indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
        segments_ids = [1] * len(tokenized_text)
        for num_1, word in enumerate(tokenized_text):
            print(word)
            if num_1 == 0 | num_1 == len(tokenized_text)-1:
                continue
            elif word in stop_list:
                continue
            elif word in num_of_words.keys():
                num_of_words[word]+=1
            else:
                num_of_words[word]= 1
            t.append(word)
        tokens_tensor = torch.tensor([indexed_tokens])
        segments_tensors = torch.tensor([segments_ids])
        try:
            outputs, _ = model(tokens_tensor, segments_tensors)
            # print(outputs)
        except Exception as e:
            # print(e)
            continue
        score = {'total':0.0,'p':0.0,'n':0.0}
        count = {'total':0,'p':0,'n':0}
        # print(time.time()-s_time)
        # print(t)
        
        # token??? ?????? text??? ????????? ???????????? keyword??? ????????? ????????? ????????? ????????? ?????? token??? index ?????? ???????????? key_flag = 1??? ??????
        for num_1, kw in enumerate(tokenized_text):
            if kw == keyword:
                # print(keyword)
                key_vec = outputs[0][num_1]
                key_flag = 1
                break
            else:
                key_flag = 0
        if key_flag == 0: # text??? keyword ??? ?????????
            key_vec = kw_vec    # vec ?????? ?????? ????????? ??????
            # print("key_vec!!",key_vec)
        # else:
        #     keyword_vector_sum += key_vec   #keyword??? ????????? 
        #     keyword_vector_cnt += 1
            
        #     # print(type(keyword_vector_sum))
        #     for i, k in enumerate(keyword_vector_sum):
        #         keyword_vector_avg.append(k / keyword_vector_cnt) 
        #     # print("kw avg update!!",keyword_vector_avg)

        for i in range(0,len(t)):
            if t[i] in senti_dict.keys():
                # print(key_vec)
                # print(outputs[0][i])
                
                temp = (key_vec-outputs[0][i])
                if temp[0] == 0:
                    continue
                # print(type(temp))
                temp *= temp
                temp_distance = 0
                for d in temp:
                    temp_distance += d.detach().numpy()
                senti_score = senti_dict[t[i]]
                if senti_score>0:
                    score['p'] += senti_score/temp_distance
                    count['p']+=1
                else:
                    score['n'] += senti_score/temp_distance
                    count['n']+=1
                score['total'] += senti_dict[t[i]]/temp_distance
                count['total']+=1
                if t[i] in word_in_sentence.keys():
                    word_in_sentence[t[i]]['count']+=1
                else:
                    word_in_sentence[t[i]] = {'score': senti_dict[t[i]], 'count':1}
        for word in t:
            if word in result.keys() and word not in stop_list:
                score2 = score.copy(); count2 = count.copy()
                result[word]['score']['p']+= score2['p']
                result[word]['score']['n']+= score2['n']
                result[word]['score']['total']+= score2['total']
                result[word]['count']['p']+= count2['p']
                result[word]['count']['n']+= count2['n']
                result[word]['count']['total']+= count2['total']
                # ?????? ????????????, 
                
                for w in word_in_sentence:
                    if w in result[word]['related'].keys():
                        #cnt = int( word_in_sentence[w]['count'])
                        result[word]['related'][w]['count'] += 1
                    else:
                        result[word]['related'][w] = word_in_sentence[w].copy()
            else:
                score2 = score.copy(); count2 = count.copy()
                word2 = word_in_sentence.copy()
                result[word] = { 'score':{'total':score2['total'],'p':score2['p'],'n':score2['n']}, 'count':{'total':count2['total'],'p':count2['p'],'n':count2['n']} , 'related': word2  }
            
        if (one_per>0):
            progressBarwith_time(num+1, total,start_time)
    print("Total # "+str(total)+" sentences.")
    
    print("Vectorizing and calculating time : ",end='')
    print(time.time() - start_time,end='')
    print(" sec")
    return result

def new_bertmodel(contents, keyword, num_of_words_pos, num_of_words_neg):
    start_time = time.time()
    # Setting based on the current model type 
    tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
    batch_size = 1
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    pad_token_id = tokenizer.pad_token_id
    
   
    cls_token_segment_id=0
    pad_token_segment_id=0
    sequence_a_segment_id=0
    mask_padding_with_zero=True

    device = "cuda" if torch.cuda.is_available() else "cpu"

    if not os.path.exists('./model'):
        raise Exception("Model doesn't exists! Train first!")

    try:
        model = AutoModelForSequenceClassification.from_pretrained('./model')  # Config will be automatically loaded from model_dir
        model.to(device)
        model.eval()
    except:
        raise Exception("Some model files might be missing...")

    file = open("./stopwords.txt", "r")
    stop_list = file.read().split()
    mecab = Mecab()

    # Load Data
    sh = StorageHandler()
    senti_dict = sh.getSentiDictionary2()
    target = keyword
    tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
    tokenized_contents =[]
    max_seq_len = 50
    cnt = 0
    total_word = []
    result_pos = {}
    result_neg = {}
    sentence_based_positive = 0
    sentence_based_negative = 0
    total_sentence_cnt =0
    positive_sentences = []
    negative_sentences = []

    kw = ['[CLS]' , keyword , '[SEP]']
    print(kw)
    kw_input_id = tokenizer.convert_tokens_to_ids(kw)
    kw_padding_length = max_seq_len - len(kw_input_id)

    kw_input_ids = kw_input_id + ([pad_token_id] * kw_padding_length)
    kw_attention_mask = [1 if mask_padding_with_zero else 0] * len(kw_input_id)
    kw_attention_mask = kw_attention_mask + ([0 if mask_padding_with_zero else 1] * kw_padding_length)

    kw_input_tensor = torch.tensor([kw_input_ids])
    kw_attention_tensor = torch.tensor([kw_attention_mask])


    kw_output = model(kw_input_tensor.to(device), kw_attention_tensor.to(device))
    kw_vec = kw_output[0]

    for c in tqdm(contents):
        for line in c.split('t'):
            cnt+=1
            line =line.strip()

            tokens = tokenizer.tokenize(line)
            special_tokens_count = 2
            # Account for [CLS] and [SEP]
            if len(tokens) > max_seq_len - special_tokens_count:
                tokens = tokens[:max_seq_len-special_tokens_count]
            
            # Add [SEP] token
            tokens += [sep_token]
            token_type_ids = [sequence_a_segment_id] * len(tokens)

            # Add [CLS] token
            tokens = [cls_token] + tokens
            token_type_ids = [cls_token_segment_id] + token_type_ids

            input_ids = tokenizer.convert_tokens_to_ids(tokens)

            # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
            attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)

            # Zero-pad up to the sequence length.
            padding_length = max_seq_len - len(input_ids)
            input_ids = input_ids + ([pad_token_id] * padding_length)
            attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
            token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)

            input_ids = torch.tensor([input_ids], dtype=torch.long)
            attention_mask = torch.tensor([attention_mask], dtype=torch.long)
            token_type_ids = torch.tensor([token_type_ids], dtype=torch.long)


          
            output = model(input_ids.to(device), attention_mask.to(device))
           

            logits = output[0]
        
            preds = logits.detach().cpu().numpy()
            
            if (np.argmax(preds))==1 :
                sentence_based_positive+=1
                positive_sentences.append(line)
                
            else :
                sentence_based_negative +=1
                negative_sentences.append(line)
            
            total_sentence_cnt +=1
    print("positive : ", sentence_based_positive)
    print("negative : ", sentence_based_negative)
    print("total : ", total_sentence_cnt)
    

    p_score = {'total':0.0,'p':0.0,'n':0.0}
    p_count = {'total':0,'p':0,'n':0}

    n_score = {'total':0.0,'p':0.0,'n':0.0}
    n_count = {'total':0,'p':0,'n':0}

    vec = Vectorizer()
    ## positive_sentences_analysis
    # tokenized_positive = vec.tokenizing(positive_sentences)
    # one_per = int(len(tokenized_positive)/100)
    # total=len(tokenized_positive)
    # print("toeknized_psitive :" , tokenized_positive)
    mecab = Mecab()
    bertmodel, vocab = get_pytorch_kobert_model()
    bertmodel.to(device)
    
    #????????? 1??????
    
    kw_token_type_ids = [sequence_a_segment_id] * 1
    kw_input_ids = tokenizer.convert_tokens_to_ids([keyword])
    kw_attention_mask = [1 if mask_padding_with_zero else 0] * 1


    kw_input_ids = torch.tensor([kw_input_ids], dtype=torch.long).to(device)
    kw_attention_mask = torch.tensor([kw_attention_mask], dtype=torch.long).to(device)
    kw_token_type_ids = torch.tensor([kw_token_type_ids], dtype=torch.long).to(device)
    

    kw_vector, _ = bertmodel(kw_input_ids, kw_attention_mask, kw_token_type_ids)
    kw_vector = kw_vector.squeeze().detach().cpu().numpy().reshape(1,-1)

    total_cnt = 0
    totals = 0
    print("positive length : ", len(positive_sentences))
    for i, st in tqdm(enumerate(positive_sentences)):
    # for num, temp in tqdm(enumerate(tokenized_positive)):
        word_in_sentence = {}
        t_positive=[]
        pos_positive = []
        for num_1, (word,po) in enumerate(mecab.pos(st)):
            if po not in ['NNG','NNP','NNB','NR','NP',"VV",'VX','VCP','VCN',"XR",'SL']:
                continue
            if (po in ['NNG','NNP','NNB','NR','NP']) and len(word)==1 :
                continue
            if num_1 == 0 :
                continue
            elif word in stop_list:
                continue
            elif word in num_of_words_pos.keys():
                num_of_words_pos[word]+=1
            else:
                num_of_words_pos[word]= 1

            t_positive.append(word)
            pos_positive.append(po)

        if len(t_positive) > max_seq_len - special_tokens_count:
            t_positive = t_positive[:max_seq_len-special_tokens_count]
        if len(t_positive)==0 or len(t_positive)==1:
            continue
        token_type_ids = [sequence_a_segment_id] * len(t_positive)
        input_ids = tokenizer.convert_tokens_to_ids(t_positive)
        attention_mask = [1 if mask_padding_with_zero else 0] * len(t_positive)

    
        input_ids = torch.tensor([input_ids], dtype=torch.long).to(device)
        attention_mask = torch.tensor([attention_mask], dtype=torch.long).to(device)
        token_type_ids = torch.tensor([token_type_ids], dtype=torch.long).to(device)
        output1, _= bertmodel(input_ids, attention_mask, token_type_ids)

        output1 = output1.squeeze()
        output1 = output1.detach().cpu().numpy()

  
        for i in range(0,len(t_positive)):
            totals +=1
            if t_positive[i] in senti_dict.keys():
                total_cnt+=1
                cosine_sim = cosine_similarity(output1[i].reshape(1,-1),kw_vector)[0][0]

                # print(outputs[0][i])
                
                senti_score = senti_dict[t_positive[i]]
                if senti_score>0:
                    p_score['p'] += senti_score * cosine_sim
                    p_count['p']+=1
                else:
                    p_score['n'] += senti_score * cosine_sim
                    p_count['n']+=1
                p_score['total'] += senti_score * cosine_sim
                p_count['total']+=1
                if t_positive[i] in word_in_sentence.keys():
                    word_in_sentence[t_positive[i]]['count']+=1
                else:
                    word_in_sentence[t_positive[i]] = {'score': senti_dict[t_positive[i]],'count':1}
        
        for i, word in enumerate(t_positive):
            # print(word, pos_positive[i])
            if word in result_pos.keys() and word not in stop_list:
                score2 = p_score.copy(); count2 = p_count.copy()
                result_pos[word]['score']['p']+= score2['p']
                result_pos[word]['score']['n']+= score2['n']
                result_pos[word]['score']['total']+= score2['total']
                result_pos[word]['count']['p']+= count2['p']
                result_pos[word]['count']['n']+= count2['n']
                result_pos[word]['count']['total']+= count2['total']
                # ?????? ????????????, 
                
                for w in word_in_sentence:
                    if w in result_pos[word]['related'].keys():
                        #cnt = int( word_in_sentence[w]['count'])
                        result_pos[word]['related'][w]['count'] += 1
                    else:
                        result_pos[word]['related'][w] = word_in_sentence[w].copy()
            else:
                score2 = p_score.copy(); count2 = p_count.copy()
                word2 = word_in_sentence.copy()
                result_pos[word] = {'pos': pos_positive[i],'score':{'total':score2['total'],'p':score2['p'],'n':score2['n']}, 'count':{'total':count2['total'],'p':count2['p'],'n':count2['n']} , 'related': word2  }
        # if (one_per>0):
        #     progressBarwith_time(num+1, total,start_time)
        
    ##negative_sentence_analysis
    # tokenized_negative = vec.tokenizing(negative_sentences)
    # one_per = int(len(tokenized_negative)/100)
    # total=len(tokenized_negative)
    for i, st in tqdm(enumerate(negative_sentences)):
        word_in_sentence = {}
        t_negative=[]
        pos_negative = []

        for num_1, (word,po) in enumerate(mecab.pos(st)):

            if po not in ['NNG','NNP','NNB','NR','NP',"VV",'VX','VCP','VCN',"XR",'SL']:
                continue
            if (po in ['NNG','NNP','NNB','NR','NP']) and len(word)==1 :
                continue
            if num_1 == 0 :
                continue
            elif word in stop_list:
                continue
            elif word in num_of_words_neg.keys():
                num_of_words_neg[word]+=1
            else:
                num_of_words_neg[word]= 1

            t_negative.append(word)
            pos_negative.append(po)

        if len(t_negative) > max_seq_len - special_tokens_count:
            t_negative = t_negative[:max_seq_len-special_tokens_count]
        if len(t_negative)==0 or len(t_negative)==1:
            continue
        token_type_ids = [sequence_a_segment_id] * len(t_negative)
        input_ids = tokenizer.convert_tokens_to_ids(t_negative)
        attention_mask = [1 if mask_padding_with_zero else 0] * len(t_negative)

    
        input_ids = torch.tensor([input_ids], dtype=torch.long).to(device)
        attention_mask = torch.tensor([attention_mask], dtype=torch.long).to(device)
        token_type_ids = torch.tensor([token_type_ids], dtype=torch.long).to(device)
        output2, _= bertmodel(input_ids, attention_mask, token_type_ids)

        output2 = output2.squeeze()
        output2 = output2.detach().cpu().numpy()

        for i in range(0,len(t_negative)):
            totals +=1
            if t_negative[i] in senti_dict.keys():
                total_cnt+=1
                cosine_sim = cosine_similarity(output2[i].reshape(1,-1), kw_vector)[0][0]
                
                senti_score = senti_dict[t_negative[i]]
                if senti_score>0:
                    n_score['p'] += senti_score * cosine_sim
                    n_count['p']+=1
                else:
                    n_score['n'] += senti_score * cosine_sim
                    n_count['n']+=1
                n_score['total'] += senti_score * cosine_sim
                n_count['total']+=1
                if t_negative[i] in word_in_sentence.keys():
                    word_in_sentence[t_negative[i]]['count']+=1
                else:
                    word_in_sentence[t_negative[i]] = {'score': senti_dict[t_negative[i]], 'count':1}
        for i, word in enumerate(t_negative):
            if word in result_neg.keys() and word not in stop_list:
                score3 = n_score.copy(); count3 = n_count.copy()
                result_neg[word]['score']['p']+= score3['p']
                result_neg[word]['score']['n']+= score3['n']
                result_neg[word]['score']['total']+= score3['total']
                result_neg[word]['count']['p']+= count3['p']
                result_neg[word]['count']['n']+= count3['n']
                result_neg[word]['count']['total']+= count3['total']
                # ?????? ????????????, 
                
                for w in word_in_sentence:
                    if w in result_neg[word]['related'].keys():
                        #cnt = int( word_in_sentence[w]['count'])
                        result_neg[word]['related'][w]['count'] += 1
                    else:
                        result_neg[word]['related'][w] = word_in_sentence[w].copy()
            else:
                score3 = n_score.copy(); count3 = n_count.copy()
                word3 = word_in_sentence.copy()
                result_neg[word] = {'pos' : pos_negative[i], 'score':{'total':score3['total'],'p':score3['p'],'n':score3['n']}, 'count':{'total':count3['total'],'p':count3['p'],'n':count3['n']} , 'related': word3  }
    print("total cnt : ",total_cnt)
    print("total  : ",totals)

    return result_pos, result_neg



def getElmoScore(contents,keyword,num_of_words):
    # to use GPU
    start_time = time.time()
    total = len(contents)
    file = open("./stopwords.txt", "r")
    stop_list = file.read().split()

    # one_per = int(total/100)
    result = {}
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
	    # Currently, memory growth needs to be the same across GPU
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        except RuntimeError as e:
            #print(e)
            pass
        # Memory growth must be set before GPUs have been initialized
    senti_dict = sh.getSentiDictionary()

    tf_keyword= tf.constant([keyword])
    embed = hub.load("https://tfhub.dev/google/elmo/3")
    keyword_output = embed.signatures['default'](tf_keyword)
    keyword_vec = keyword_output['word_emb']
    #print("keyword_vec : ",keyword_vec)
    #output['word_emb'][0][0]-output1['word_emb'][0][0]
    total_word = 0
    for k in contents:
        total_word+=len(k)
    
    for num,temp in enumerate(contents):
        # t : ????????? ?????????+????????? corpus??? tokenized??? word list  ex) ['??????','???','??????']
        # s_time = time.time()
        sentence = ''
        t = []
        word_in_sentence={}
        for word in temp:
        # t??? string????????? ???????????? ????????????, ?????? ????????? ??????
            if word in stop_list:
                continue
            if word in num_of_words.keys():
                num_of_words[word]+=1
            else:
                num_of_words[word]=1
            sentence+= word+' '
            t.append(word)
        # ???????????? / keyword?????? ????????? ?????? ?????? ??????    
        tf_sentence = tf.constant([sentence])
        try:
            sentence_output = embed.signatures['default'](tf_sentence)
            sentence_vec = sentence_output['word_emb']
            #print("sentence_vec : ",sentence_output['word_emb'])
        except: #????????? ?????? ??? ?????? ( ????????? ?????? ??? ?????? ) ?????? ??????... ?????? ?????? ??????
            continue
        score = {'total':0.0,'p':0.0,'n':0.0}
        count = {'total':0,'p':0,'n':0}
        # print(time.time()-s_time)
        # print(t)
        # print(len(t))
        for i in range(0,len(t)):
            if t[i] in senti_dict.keys():
                temp = (keyword_vec[0][0]-sentence_vec[0][i])
                #print("temp ", temp)
                temp *= temp
                temp_distance = 0
                for d in temp:
                    temp_distance += d.numpy()
                senti_score = senti_dict[t[i]]
                if senti_score>0:
                    score['p'] += senti_score/temp_distance
                    count['p']+=1
                else:
                    score['n'] += senti_score/temp_distance
                    count['n']+=1
                score['total'] += senti_dict[t[i]]/temp_distance
                count['total']+=1
                if t[i] in word_in_sentence.keys():
                    word_in_sentence[t[i]]['count']+=1
                else:
                    word_in_sentence[t[i]] = {'score': senti_dict[t[i]], 'count':1}
        # ??? ????????? (???????????? / ?????? )??? ?????? ??????????????? score update
        for word in t: # t : ???????????? ????????? ?????? ?????? : t
            if word in result.keys() and word not in stop_list:
                score2 = score.copy(); count2 = count.copy()
                result[word]['score']['p']+= score2['p']
                result[word]['score']['n']+= score2['n']
                result[word]['score']['total']+= score2['total']
                result[word]['count']['p']+= count2['p']
                result[word]['count']['n']+= count2['n']
                result[word]['count']['total']+= count2['total']
                # ?????? ????????????, 
                
                for w in word_in_sentence:
                    if w in result[word]['related'].keys():
                        #cnt = int( word_in_sentence[w]['count'])
                        result[word]['related'][w]['count'] += 1
                    else:
                        result[word]['related'][w] = word_in_sentence[w].copy()
            else:
                score2 = score.copy(); count2 = count.copy()
                word2 = word_in_sentence.copy()
                result[word] = { 'score':{'total':score2['total'],'p':score2['p'],'n':score2['n']}, 'count':{'total':count2['total'],'p':count2['p'],'n':count2['n']} , 'related': word2  }
        
        if (one_per>0):
            progressBarwith_time(num+1, total,start_time)
    print("Total # "+str(total)+" sentences.")
    
    print("Vectorizing and calculating time : ",end='')
    print(time.time() - start_time,end='')
    print(" sec")
    return result