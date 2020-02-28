

# --------- Read the preprocessed document from the collection (if you don't have the collection saved after preprocessing, then read the document from the collection then apply preprocessing to it).


from nltk import PorterStemmer
import re
import string
import time
import json
# below is the function for doing tokenize, remove stop_words, punctuation and stem（preprocess）
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
    f= open("index2.txt","w", encoding='utf-8')
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

# Perform the operation: Here we assume that the top2 file is used to extract keywords N = 2 Take the words of the first 2 articles:
import math

def wordScore(positional_iied, n):
    dictunSort=dict()
    for sth in positional_iied:
        word = sth
        Scoredvalue = 0
        # print(word)
        # print(positional_iied[sth]) #{'2': [124]}
        # print(" df " + str(len(positional_iied[sth]))) #
        for x in positional_iied[sth]:
            # print(x)  #no of file
            # print(positional_iied[sth][x])#list
            # print(len(positional_iied[sth][x]))#freq

            value = (1+math.log10(len(positional_iied[sth][x])))*math.log10(n/len(positional_iied[sth]))
            Scoredvalue+= value
            # print(Scoredvalue)
        dictunSort[word]=Scoredvalue

    return sorted(dictunSort, key=dictunSort.get, reverse=True)[:2]



def main(topNDoc):

    filtered_words= tokenize_lower_noPunc_remove_stop_stem(topNDoc)
    # print("-----------top N Doc")
    # print(filtered_words)
    cleaned = before_pii(filtered_words)
    # print(cleaned)
    positional_iied = positional_ii(cleaned)
    n = 20
    outScore= wordScore(positional_iied,n)
    print(outScore)
    return outScore

if __name__== "__main__":
  main()
