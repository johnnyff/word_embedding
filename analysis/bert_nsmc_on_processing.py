# coding: utf-8

# Developer : Jeong Wooyoung
# Contact   : gunyoung20@naver.com

from datetime import datetime
import os
import logging
import argparse
from tqdm import tqdm, trange
import analysis
from tokenization_kobert import KoBertTokenizer

from vectorizer import Vectorizer
from storage_handler import StorageHandler
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from transformers import AutoModelForSequenceClassification


def get_device():
    return "cuda" if torch.cuda.is_available() else "cpu"

def load_model(device):
    # Check whether model exists
    if not os.path.exists('./model'):
        raise Exception("Model doesn't exists! Train first!")

    try:
        model = AutoModelForSequenceClassification.from_pretrained('./model')  # Config will be automatically loaded from model_dir
        model.to(device)
        model.eval()
    except:
        raise Exception("Some model files might be missing...")

    return model

if __name__ == '__main__':
    # Setting based on the current model type

    tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
    batch_size = 32

    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    pad_token_id = tokenizer.pad_token_id
    
    all_input_ids = []
    all_attention_mask = []
    all_token_type_ids = []

    cls_token_segment_id=0
    pad_token_segment_id=0
    sequence_a_segment_id=0
    mask_padding_with_zero=True

    device = get_device()
    model = load_model(device)

    # Load Data
    sh = StorageHandler()
    target = '디퓨저'
    contents = sh.getContents(target)
    tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
    tokenized_contents =[]
    max_seq_len = 50
    cnt = 0
    for c in contents:
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

            all_input_ids.append(input_ids)
            all_attention_mask.append(attention_mask)
            all_token_type_ids.append(token_type_ids)
    print("cnt is ", cnt)
    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long)
    all_attention_mask = torch.tensor(all_attention_mask, dtype=torch.long)
    all_token_type_ids = torch.tensor(all_token_type_ids, dtype=torch.long)

    dataset = TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids)

    sampler = SequentialSampler(dataset)
    data_loader = DataLoader(dataset, sampler=sampler, batch_size=batch_size)

    preds = None

    for batch in tqdm(data_loader, desc="Predicting"):
        batch = tuple(t.to(device) for t in batch)
        with torch.no_grad():
            inputs = {"input_ids": batch[0],
                      "attention_mask": batch[1],
                      "token_type_ids": batch[2],
                      "labels": None}
        
            outputs = model(**inputs)
            logits = outputs[0]

            if preds is None:
                preds = logits.detach().cpu().numpy()
            else:
                preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)

    preds = np.argmax(preds, axis=1)

    # Write to output file
    with open("sample_pred_out.txt", "w", encoding="utf-8") as f:
        for pred in preds:
            f.write("{}\n".format(pred))

    







    # model_path = 'models/word2vec_ko.model'
    # # vectors = {'word_vectors':word_vectors(list), 'vectorized_contents':vectorized_contents(list), 'num_of_words':num_of_words(dict}
    # print('Vectorizing Start. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))
    # vectors = vec.vectorize(model_path, contents, dims=100, using_dict=using_dict, training=False, padding=False)
    # print('Vectorizing Finish. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))
    # word_vectors = vectors['word_vectors']
    # num_of_words = vectors['num_of_words']

    # # Clustering
    # print('Clustering Start. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))
    # # vectors = {word_vectors, num_of_words, vectorized_contents}
    # cluster_group = analysis.clustering(vectors)
    # print('Clustering Finish. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))

    # # select words
    # max_select = 5
    # selected_words = analysis.selectUsableWords(cluster_group, max_select=max_select)
    # print('Done select words. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))

    # # Sentiment Analysis
    # tokenized_contents = vec.tokenizing(contents)
    # print('Calculating Sentiment Start. %d sentences (%s)'%(len(tokenized_contents), datetime.now().strftime('%m-%d %H:%M:%S.%f')))
    # # senti_words = {word:{'score':score,'count':count, 'related':senti_words_in_sentence}}
    # senti_words = analysis.getSentimentScoreOnSelectedWords(tokenized_contents, selected_words)
    # print('\nCalculating Sentiment Finish. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))

    # sh.saveSentiWords(selected_words, num_of_words, senti_words, file=target)

    # print(senti_words)
    # # related = {'소모':{'score':231.0, 'count':25},
    # #            '역시':{'score':-23.0, 'count':32},
    # #            '배선':{'score':800.0, 'count':1345}}
    # # st_words = sorted(related.items(), key=(lambda x: x[1]['count']), reverse=True)
    # # lines = ['%s(%f, %d)' % (rw, info['score'], info['count']) for rw, info in st_words]
    # # print(st_words)