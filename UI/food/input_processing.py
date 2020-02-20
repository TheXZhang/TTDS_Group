import string
import nltk
import re
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from spellchecker import SpellChecker
import json

# -------------the place where data stored
nltk_food=[]
with open("nltk_food.txt", "r") as f:
    nltk_food = [i for line in f for i in line.split()]
# recipe_database = [
#     {
#         "name": "bagel",
#         "ingredients": ["onion", 'bread'],
#         "description": "this is a description of bagel",
#         "url": "http://www.baidu.com"
#     }
# ]
# add abb in this function !!!!!!!!
abbs = dict()
with open('abb.json') as f:
  abbs = json.load(f)


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
origin_qfile = read_query_file()
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
# -----------------------------------------User/pseudo/implicit feedback    用户输入的内在含义（同义词，上下级词）使用word net

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

# check the word is food
def if_food(word):

    if word in nltk_food:
        return 1
    return 0

# tokenise string into list of words and remove punctuation
def token(input):
    # set a translator to translate punctuation to empty space
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    # remove punctuation and split string into list
    split_input = input.translate(translator).split()
    return split_input
# -----------------------------------------缩写词扩写
# Food abbreviations transformation
def check_abbreviations(input_list,abbs):
    # input_list = ['lrg','liq']
    abbs_out = []
    for word in input_list:
        if word in abbs.keys():
            value = abbs.get(word)
            abbs_out.append(value)
        else:
            abbs_out.append(word)

    return abbs_out


# remove stop words from the list
def remove_stopword(input):
    # read english stop words
    s_words = stopwords.words("english")
    no_stop_input = []
    # remove stop words
    for word in input:
        if word not in s_words:
            no_stop_input.append(word)
    return no_stop_input

def correction(input):
    spell = SpellChecker()
    valid_input = []
    for wor in input:
        # if the length of word larger than 2, then check correction
        if len(wor) > 2:
            word_checked = spell.correction(wor)
            lower_word = wor.lower()
            # check is the input is a proper word, if it isn't, process to futher check
            if word_checked != wor:
                # if the word is food after correction after correction, output it
                if if_food(word_checked) == 1:
                    valid_input.append(word_checked)
                # otherwise correct the input word to food in nltk food set
                else:
                    corpus_length = len(nltk_food)
                    word_length = len(lower_word)
                    count = 1
                    found = False
                    # if no match found in the food set, keep search
                    while found is False:
                        for fo in nltk_food:
                            # if match found in the food set, output it and stop the loop
                            if re.match(lower_word[:word_length], fo) != None:
                                valid_input.append(fo)
                                found = True
                                break
                            else:
                                count += 1

                            # if search reach end, run the search loop again
                            if count == corpus_length:
                                word_length = word_length - 1
                                count = 0
                                found = False
            # if the input word is a word, then output it
            else:
                valid_input.append(word_checked)
        # if lenght of word less than 2, don't check
        else:
            valid_input.append(wor)
    return valid_input

# stem word
def stemm(input):
    ps = PorterStemmer()
    stemmed_input = []
    for word in input:
        stemmed_input.append(ps.stem(word))
    return stemmed_input

# check input validation for different situatinos
def validation(input, tok=False, sto=False, corr=False, check_food=False, stem=False):

    # if tokenise is True, then process
    if tok == True:
        token_input = token(input)
    else:
        token_input = input
    # find abbreviations
    token_input = check_abbreviations(token_input,abbs)

    # if stop word is True, then process to remove stop word
    if sto == True:
        stop_input = remove_stopword(token_input)
    else:
        stop_input = token_input

    # if correction is True, then process
    if corr == True:
        corrected_input = correction(stop_input)
    else:
        corrected_input = stop_input

    # if food check is True, then process
    food_list = []
    if check_food == True:
        for fo in corrected_input:
            if if_food(fo) == 1:
                food_list.append(fo)
    else:
        food_list = corrected_input
    # print(food_list)

    write_to_query_file(' '.join(food_list))

    # food_list = synonyms_hyponyms_hypernyms(food_list,nltk_food)
    food_list_new = []
    for food_elem in food_list:
            food_list_new+=synonyms_hyponyms_hypernyms(food_elem,nltk_food)

    # if stem is True, then process
    if stem == True:
        stem_input = stemm(food_list_new)
        food_list = stemm(food_list)
    else:
        stem_input = food_list_new
        food_list = food_list
    stem_input = list(set(stem_input))

    # -----------------------user suggest stem_input 包括同义词搜索 与 food_list可替换
    stem_input += give_sugges_by_query_dataset(origin_qfile,food_list)
    food_list += give_sugges_by_query_dataset(origin_qfile, food_list)

    return food_list





def handle(request):
    # read user input for search
    recipe_name = request.form.get("recipe")
    # read user input for dislike food
    dislike_list = []
    if request.form.get("dislike_list"):
        dislike_list = request.form.get("dislike_list").split(",")

    # verify input and return result for user
    list_of_food_user = ' '.join(validation(recipe_name, tok=True, corr=True))

    # after verified, return list a stemmed word for server
    list_of_food_server = validation(recipe_name, tok=True, sto=True, corr=True, check_food=True, stem=True)

    # dislike food list for user
    list_of_dislike_user = validation(dislike_list, corr=True)

    # verify the dilike food
    list_of_dislike_server = validation(dislike_list, corr=True, check_food=True, stem=True)

    return list_of_food_user, list_of_dislike_server, list_of_dislike_user,list_of_food_server
