# ---------for top n file 此处只取前十个 此处我们假装取了十个
# f = open("results.ranked.txt", "r")
# nlistAll = []
# for x in f:
#     x = x.split()
#     nlistAll.append(x)
#     # print(flagList)
# # print(nlistAll)
#
# adic = dict()
# flag = '0'
# aa = []
# for li in nlistAll:
#     if flag !=li[0]:
#         adic[flag] = aa
#         aa =[]
#         flag = li[0]
#     else:
#         aa.append(li)
# del adic['0']
# # print(adic)

# 输出： {'1': [['1', '0', '3533', '0', '7.753', '0'], ['1', '0', '3562', '0', '5.693', '0'], ['1', '0', '3608', '0', '5.639', '0'], ['1', '0', '92', '0', '5.461', '0'], ['1', '0', '141', '0', '5.294', '0'], ['1', '0', '361', '0', '5.294', '0'], ['1', '0', '3734', '0', '5.197', '0'], ['1', '0', '3829', '0', '5.15', '0'], ['1', '0', '3420', '0', '5.108', '0']], '2': [['2', '0', '305', '0', '9.85', '0'], ['2', '0', '288', '0', '9.57', '0'], ['2', '0', '223', '0', '8.842', '0'].....}


# --------- Read the preprocessed document from the collection (if you don't have the collection saved after preprocessing, then read the document from the collection then apply preprocessing to it).


from nltk import PorterStemmer
import re
import string
import time
import json
# below is the function for doing tokenize, remove stop_words, punctuation and stem（预处理）
def tokenize_lower_noPunc_remove_stop_stem(file):
    stop_words =[line.strip() for line in open('stop_words.txt')]
    ps = PorterStemmer()
    remove = string.punctuation
    pattern = r"[{}]".format(remove)

    tokenized_text = []
    tokenized_rx = r"\w+(?:'\w+)?|[^\w\s]"
    for sentence in file :
        # print(sentence)
        sentence = sentence.lower()
        sentence = re.sub(pattern, " ", sentence)
        sentence = re.sub(r"[{\\}]", " ", sentence)
        words = re.findall(tokenized_rx, sentence)
        words = [ps.stem(word) for word in words if word not in stop_words]
        tokenized_text.append(words)
    return tokenized_text

def before_pii(test):
    clean = []
    for x in range(len(test)):
        if len(test[x]) == 2 and test[x][0] == 'id':
            clean.append(test[x])
        else:
            if len(test[x-1]) == 2 and test[x-1][0] == 'id':
                clean.append(test[x])
            else:
                clean[-1]+=test[x]
    return clean

# 找到相对的文档，假装输入 问题‘1’相对的
# print(adic.get('1'))
# doc10 = adic.get('1')
# doxID = []
# for dox in doc10:
#     doxID.append(dox[2])
# print(doxID)
# 输出doc id 前十个['3533', '3562', '3608', '92', '141', '361', '3734', '3829', '3420']




# value calculation
# below is the function doing indexing
def positional_ii(texts):
    myDict = dict()
    id = []
    te = []
    for x in range(len(texts)):
        if texts[x][0] == 'id':
            id.append(''+texts[x][1])
        else:
            te.append(texts[x])

    index_te = 0
    for ele in id:
        myDict.setdefault(ele, []).append(te[index_te])
        index_te +=1

    # #--------------------------------------------------
    # bulid up the single word to single index dictionary, output for myDict example:
    # original_dict={'1': [['text', 'like', 'wink', 'like', 'drink']], '3': [['text', 'thing', 'like', 'drink', 'ink']]}

    flipped = {}
    word_list=[]
    for key, value in myDict.items():
        t = value[0]
        index = 0
        for term in t:

            if term not in word_list:
                word_list.append(term)
                doc_index = (key,t.index(term))
                flipped[term] = [doc_index]
            else:
                doc_index = (key,index)
                flipped[term].append(doc_index)
            index+=1

    # # ------------------------------------------------------
    # output for flipped below:
    # # example = {'text': [('1', 0), ('2', 0), ('3', 0), ('4', 0), ('5', 0)]}
    set2 = []
    for u,v in flipped.items():
         doc = ''
         set = []
         for doc_index in v:
             if doc_index[0] != doc:
                 doc = doc_index[0]
                 set.append(doc)
                 set.append(doc_index[1])
             else:
                 set.append(doc_index[1])
         set2.append(set)

    positioned_index=dict()
    # write to the .txt file in this step
    f= open("index2.txt","w")
    for i in range(len(flipped)):

        term = list(flipped.keys())[i]
        positioned_index[term]={}
        bar = ''
        last_call = ''
        f.write('\n'+term+': ')
        for doc_index in set2[i]:
            if isinstance(doc_index, str):
                last_call = 'str'
                f.write('\n  ' + doc_index+": " )
                bar = doc_index
                positioned_index[term][doc_index] = {}
            if isinstance(doc_index, int):
                if last_call == 'str':
                    positioned_index[term][bar]=[doc_index]
                    f.write('' + str(doc_index) )
                else:
                    positioned_index[term][bar].append(doc_index)
                    f.write("," + str(doc_index) )


                last_call = 'int'

    f.close()
    return(positioned_index)

# 进行运算：此处我们假设取top2的文件进行提取关键词 N=2 对前2个的文章取词：
import math

def wordScore(positional_iied, n):
    dictunSort=dict()
    for sth in positional_iied:
        word = sth
        Scoredvalue = 0
        # print(word)
        # print(positional_iied[sth]) #{'2': [124]}
        # print(" df " + str(len(positional_iied[sth]))) #多少文件df
        for x in positional_iied[sth]:
            # print(x)  #表第几个文件ID
            # print(positional_iied[sth][x])#出现在此文件的list
            # print(len(positional_iied[sth][x]))#出现在此文件的频率

            value = (1+math.log10(len(positional_iied[sth][x])))*math.log10(2/len(positional_iied[sth]))
            Scoredvalue+= value
            # print(Scoredvalue)
        dictunSort[word]=Scoredvalue

    return sorted(dictunSort, key=dictunSort.get, reverse=True)[:2]

# 读取trec.asmple.txt


def main(topNDoc):

    filtered_words= tokenize_lower_noPunc_remove_stop_stem(topNDoc)
    cleaned = before_pii(filtered_words)
    # print(cleaned)
    positional_iied = positional_ii(cleaned)
    n = 20
    outScore= wordScore(positional_iied,n)
    print(outScore)
    return outScore

if __name__== "__main__":
  main()
