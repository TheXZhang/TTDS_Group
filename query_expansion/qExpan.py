import csv

# with open('RAW_recipes.csv', newline='') as csvfile:
#     spamreader = csv.reader(csvfile)
#     for row in spamreader:
#         print(row)

# -----------------------------------------此处应该为已经处理过的keyword(spell纠错，提取)，此处读取已有的用户输入数据 论文 https://www.iro.umontreal.ca/~nie/IFT6255/carpineto-Survey-QE.pdf
query_list = []
with open("query.txt") as f:
    content = f.readlines()
    content = [x.strip("\n") for x in content]
    content = [x.split() for x in content]
    query_list += content

# print(query_list)

# -----------------此处为测试用例
query1 = "BBQ chicken"
query2 = "beef"
query3 = "sugar"

# preprocess input

input = ['BBQ', 'chicken']
input1 = ['potato','tomato']

# -----------------------------------------缩写词扩写
# Food abbreviations transformation
import json
def check_abbreviations(input_list,abbs):
    # input_list = ['lrg','liq']
    abbs_out = []
    for word in input_list:
        if word in abbs.keys():
            value = abbs.get(word)
            abbs_out.append(value)

    return abbs_out

# -----------------------------------------User/pseudo/implicit feedback    用户输入的内在含义（同义词，上下级词）使用word net

import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet as wn
# 尝试了pyDic


def all_food():
    food_all_list = []
    # -----------------nltk food list
    food_list= wn.synsets('food')
    fruit_list=wn.synsets('fruit')
    vegetable_list=wn.synsets('vegetable')
    meat_list=wn.synsets('meat')
    food_synset_list = (list(set().union(fruit_list,food_list,vegetable_list,meat_list)))

    for syn in food_synset_list:
        food_all_list += [w for s in syn.closure(lambda s:s.hyponyms()) for w in s.lemma_names()]
    food_all_list = list(set(food_all_list))

    return food_all_list

def synonyms_hyponyms_hypernyms(input_word,food_all_list):
    # -----------------input to list of synsets
    in_list= wn.synsets(input_word)
    # -----------------all the 同义词 下位词 上位词 into list
    all_synonyms_hyponyms_hypernyms = []
    # -----------------同义词
    synonyms = []
    for syn in in_list:
        for lm in syn.lemmas():
                 synonyms.append(lm.name())#adding into synonyms
    all_synonyms_hyponyms_hypernyms += synonyms
    # 问题1
    # ['boeuf', 'crab', 'beef', 'grouse']会出现不相关的词 怎么办
    # print(out)
    # -----------------下位词
    hyponyms = []
    for syn in in_list:
        types_word_sys = syn.hyponyms()
        out2 = (sorted([lemma.name() for synset in types_word_sys for lemma in synset.lemmas()]))
        hyponyms+=out2
    all_synonyms_hyponyms_hypernyms += hyponyms
    # print(hyponyms)
    # -----------------上位词
    hypernyms = []
    for syn in in_list:
        types_word_sys = syn.hypernyms()
        out_hyper = (sorted([lemma.name() for synset in types_word_sys for lemma in synset.lemmas()]))
        hypernyms+=out_hyper
    all_synonyms_hyponyms_hypernyms += hypernyms
    # print(hyponyms)
    # ----------------整合
    all_synonyms_hyponyms_hypernyms = list(set(all_synonyms_hyponyms_hypernyms).intersection(food_all_list))
    processed_synonyms_hyponyms_hypernyms = []
    for word in all_synonyms_hyponyms_hypernyms:
        word = word.replace('_',' ')
        processed_synonyms_hyponyms_hypernyms.append(word)

    return processed_synonyms_hyponyms_hypernyms




# -----------------------------------------Display learnt terms with search    由其他用户的输入判断
# 假设我们输入的query的 keywords 都存入 query.txt
from collections import Counter
from itertools import groupby

# write into query dataset 但是这一部分需要随机写入，因为不保证每个都是有效的 e.g.有人输入很多次 b + c则数据库b/c部分会无意义填充进很多b + c的组合.
def read_query_file():
    query_list = []
    with open("query.txt") as f:
        content = f.readlines()
        content = [x.strip("\n") for x in content]
        content = [x.split() for x in content]
        query_list += content

    return query_list
def write_to_query_file(query):
    query_file = open("query.txt","a")
    query_file.write(query+'\n')
    query_file.close()

def give_sugges_by_query_dataset(origin_qfile,query):
    processed_querys = []
    # print(origin_qfile)
    # print(query)
    for querys in origin_qfile:
        removed = []
        if all(elem in querys  for elem in query):
            removed = [que for que in querys if que not in query]
        processed_querys +=removed
    # processed_querys = []
    # for querys in query_list:
    #     removed = []
    #     if all(elem in querys  for elem in input1):
    #         removed = [query for query in querys if query not in input1]
    #     processed_querys +=removed
    # print(processed_querys)
    freqs = groupby(Counter(processed_querys).most_common(), lambda x:x[1])
    # pick off the first group (highest frequency)
    freq_mode_list = [val for val,count in next(freqs)[1]]
    return freq_mode_list


# number_of_words = processed_querys.count(most_freq_word)
# if number_of_words/len(processed_querys) > 0.5:
#     print(most_freq_word)
#     print('0.5')
# -----------------------------------------数据库内菜谱搜索 相关的其他keyword






# ----------------------------------------- We select the top K images after retrieval and aggregate their features and query feature by average . We use the aggregated feature as a new query and perform the retrieval again to obtain the final ranking list.   论文： https://ieeexplore.ieee.org/document/5995601




# ----------------------------------------- Query expansion using GloVe and Word2Vec ipnb
# https://github.com/alejgh/query_expansion/blob/master/documentacion/Query%20expansion%20using%20GloVe%20and%20Word2Vec.ipynb






def main():

  # ----------------------------------------- 同义词相关词查询
  food_all_list = all_food()
  synonyms_hyponyms_hypernyms_all = synonyms_hyponyms_hypernyms('beef',food_all_list)
  # ----------------------------------------- 扩写缩写词
  abbs = dict()
  with open('abb.json') as f:
    abbs = json.load(f)
  abbs_in_input = check_abbreviations(['lrg','liq'],abbs)
  # print(abbs_in_input)
  # ----------------------------------------- 由其他用户输入判断
  # 假装输入
  query = 'chicken'
  origin_qfile = read_query_file()
  write_to_query_file(query)
  query1 = ['chicken']
  print(give_sugges_by_query_dataset(origin_qfile,query1))


if __name__== "__main__":
  main()
