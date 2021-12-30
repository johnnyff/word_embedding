'''

import os
import sys
import json
import nltk
import random
import logging
import tensorflow as tf
import sentencepiece as spm

from glob import glob
from tensorflow.keras.utils import Progbar

sys.path.append("bert")

from bert import modeling, optimization, tokenization
from bert.run_pretraining import input_fn_builder, model_fn_builder

regex_tokenizer = nltk.RegexpTokenizer("\w+")

def normalize_text(text):
  # lowercase text
  text = str(text).lower()
  # remove non-UTF
  text = text.encode("utf-8", "ignore").decode()
  # remove punktuation symbols
  text = " ".join(regex_tokenizer.tokenize(text))
  return text

def count_lines(filename):
  count = 0
  with open(filename) as fi:
    for line in fi:
      count += 1
  return count


RAW_DATA_FPATH = "corpus.txt" #@param {type: "string"}
PRC_DATA_FPATH = "prc_corpus.txt" #@param {type: "string"}

# apply normalization to the dataset
# this will take a minute or two

total_lines = count_lines(RAW_DATA_FPATH)
bar = Progbar(total_lines)

with open(RAW_DATA_FPATH,encoding="utf-8") as fi:
  with open(PRC_DATA_FPATH, "w",encoding="utf-8") as fo:
    for l in fi:
      fo.write(normalize_text(l)+"\n")
      bar.add(1)

MODEL_PREFIX = "tokenizer" #@param {type: "string"}
VOC_SIZE = 32000 #@param {type:"integer"}
SUBSAMPLE_SIZE = 12800000 #@param {type:"integer"}
NUM_PLACEHOLDERS = 256 #@param {type:"integer"}

SPM_COMMAND = ('--input={} --model_prefix={} '
               '--vocab_size={} --input_sentence_size={} '
               '--shuffle_input_sentence=true ' 
               '--bos_id=-1 --eos_id=-1').format(
               PRC_DATA_FPATH, MODEL_PREFIX, 
               VOC_SIZE - NUM_PLACEHOLDERS, SUBSAMPLE_SIZE)

spm.SentencePieceTrainer.Train(SPM_COMMAND)

def read_sentencepiece_vocab(filepath):
  voc = []
  with open(filepath, encoding='utf-8') as fi:
    for line in fi:
      voc.append(line.split("\t")[0])
  # skip the first <unk> token
  voc = voc[1:]
  return voc

snt_vocab = read_sentencepiece_vocab("{}.vocab".format(MODEL_PREFIX))
print("Learnt vocab size: {}".format(len(snt_vocab)))
print("Sample tokens: {}".format(random.sample(snt_vocab, 10)))
def parse_sentencepiece_token(token):
    if token.startswith("▁"):
        return token[1:]
    else:
        return "##" + token

bert_vocab = list(map(parse_sentencepiece_token, snt_vocab))
ctrl_symbols = ["[PAD]","[UNK]","[CLS]","[SEP]","[MASK]"]
bert_vocab = ctrl_symbols + bert_vocab
bert_vocab += ["[UNUSED_{}]".format(i) for i in range(VOC_SIZE - len(bert_vocab))]
print(len(bert_vocab))
VOC_FNAME = "vocab.txt" #@param {type:"string"}

with open(VOC_FNAME, "w") as fo:
  for token in bert_vocab:
    fo.write(token+"\n")


'''

import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel

# OPTIONAL: if you want to have more information on what's happening, activate the logger as follows
import logging
#logging.basicConfig(level=logging.INFO)
from transformers import AutoTokenizer, AutoModel, AutoModelWithLMHead
from transformers import ElectraModel, ElectraTokenizer, BertModel

from tokenization_kobert import KoBertTokenizer

import matplotlib.pyplot as plt
#plt.show()
# Load pre-trained model tokenizer (vocabulary)
# tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
# tokenizer = ElectraTokenizer.from_pretrained("monologg/koelectra-small-v2-discriminator")
tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')

text = "사과 먹고싶다"
marked_text = "[CLS] " + text + " [SEP]"

# Tokenize our sentence with the BERT tokenizer.
tokenized_text = tokenizer.tokenize(marked_text)
tokenized_text = ["[CLS] " , text , " [SEP]"]
# Print out the tokens.
indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
# inputs = tokenizer(
#         text, 
#         return_tensors='pt',
#         truncation=True,
#         max_length=256,
#         pad_to_max_length=True,
#         add_special_tokens=True
#         )
# input_ids = inputs['input_ids'][0]
# attention_mask = inputs['attention_mask'][0]
# Display the words with their indeces.
# for tup in zip(tokenized_text, indexed_tokens):
#     print('{:<12} {:>6,}'.format(tup[0], tup[1]))

segments_ids = [1] * len(tokenized_text)

print (segments_ids)

tokens_tensor = torch.tensor([indexed_tokens])
segments_tensors = torch.tensor([segments_ids])

# model = ElectraModel.from_pretrained("monologg/koelectra-small-discriminator")
model = BertModel.from_pretrained('monologg/kobert')

with torch.no_grad():
    outputs, _ = model(tokens_tensor, segments_tensors)
    print("outputs!!!!!")
   
    
    # Evaluating the model will return a different number of objects based on 
    # how it's  configured in the `from_pretrained` call earlier. In this case, 
    # becase we set `output_hidden_states = True`, the third item will be the 
    # hidden states from all layers. See the documentation for more details:
    # https://huggingface.co/transformers/model_doc/bert.html#bertmodel
    # hidden_states = 
print(outputs)
outputs = outputs.tolist()
aa = []
aa += outputs
print(aa[0][0]/2)
for num, vec in enumerate(outputs[0]):
  print(num)
  vec = vec.tolist()
  print(vec[0]-0.1)

print ("Number of layers:", len(outputs), "  (initial embeddings + 12 BERT layers)")
layer_i = 0

print ("Number of batches:", len(outputs[layer_i]))
batch_i = 0

print ("Number of tokens:", len(outputs[layer_i][batch_i]))
token_i = 0

print ("Number of hidden units:", len(outputs[layer_i][batch_i][token_i]))

token_embeddings = torch.stack(outputs, dim=0)

token_embeddings.size() # torch.Size([12, 1, 22, 768])

token_embeddings = torch.squeeze(token_embeddings, dim=1)

token_embeddings.size()  # torch.Size([12, 22, 768])

token_embeddings = token_embeddings.permute(1,0,2)

token_embeddings.size()  # torch.Size([22, 12, 768])

token_vecs_sum = []

for token in token_embeddings:
    
    sum_vec = torch.sum(token[-4:], dim=0)
    
    token_vecs_sum.append(sum_vec)
    
print ('Shape is: %d x %d' % (len(token_vecs_sum), len(token_vecs_sum[0])))


# mecab 적용한 데이터 저장
# ex) 1 line: '어릴 때 보 고 지금 다시 봐도 

# import sentencepiece as spm
# parameter = '--input={} --model_prefix={} --vocab_size={} --user_defined_symbols={}'

# input_file = 'corpus.txt'
# vocab_size = 32000
# prefix = 'bert_kor'
# user_defined_symbols = '[PAD],[UNK],[CLS],[SEP],[MASK]'
# cmd = parameter.format(input_file, prefix, vocab_size,user_defined_symbols)

# spm.SentencePieceTrainer.Train(cmd)
# id = []
# sp = spm.SentencePieceProcessor()
# sp.Load('{}.model'.format(prefix))
# token = sp.EncodeAsPieces('나는 오늘 아침밥을 먹었다.')
# ids = sp.encode_as_ids('나는 오늘 아침밥을 먹었다.')
# id.append(ids)
# print(id)
# print(token)


# import pandas as pd
# import sentencepiece as spm
# import urllib.request
# import csv

# urllib.request.urlretrieve("https://raw.githubusercontent.com/e9t/nsmc/master/ratings.txt", filename="ratings.txt")
# naver_df = pd.read_table('ratings.txt')
# naver_df[:5]
# print('리뷰 개수 :',len(naver_df)) # 리뷰 개수 출력
# print(naver_df.isnull().values.any())
# naver_df = naver_df.dropna(how = 'any') # Null 값이 존재하는 행 제거
# print(naver_df.isnull().values.any()) # Null 값이 존재하는지 확인
# print('리뷰 개수 :',len(naver_df)) # 리뷰 개수 출력

# with open('naver_review.txt', 'w', encoding='utf8') as f:
#     f.write('\n'.join(naver_df['document']))

# spm.SentencePieceTrainer.Train("--input=naver_review.txt --model_prefix=naver --vocab_size=5000  --user_defined_symbols='[PAD],[UNK],[CLS],[SEP],[MASK]'  --model_type=bpe --max_sentence_length=9999")
# vocab_list = pd.read_csv('naver.vocab', sep='\t', header=None, quoting=csv.QUOTE_NONE)
# vocab_list[:10]    
# len(vocab_list)
