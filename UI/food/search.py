import json
import re
import shlex
import math
import nltk
import sys



def search(recipe, processed_dislike_list,dislike_list, processed_list):
    recipe_list= [
    {
        "id":0,
        "name": "bagel111",
        "ingredients": ["onion", 'bread'],
        "description": "this is a description of bagel,this is a description of bagel，this is a description of bagel, bagel,this is a description of bagel，th, bagel,this is a description of bagel，th",
        "url": ""
    },
    {
        "id":1,
        "name": "bagel222",
        "ingredients": ["onion", 'bread'],
        "description": "this is a description of bagel,this is a description of bagel，this is a description of bagel, bagel,this is a description of bagel，th, bagel,this is a description of bagel，th",
        "url": ""
    }
]
    return {
        "recipe_name": recipe,
        "dislike_list": dislike_list,
        "recipe_list": recipe_list
    }






def tfidf(word_list,data,all_doc_ID):
    #for tfidf,there maybe a stopword in the query,
    #so we read the stopword file and stem the word
    overlapped_docID=[]
    idfs=[]
    tfs=[]
    score=0
    scores=[]
    total_docID=len(all_doc_ID)

    for word in word_list:
        #for every word in the query,
        #find out total number of document that the word appeared in
        total_doc_word_appeared=len(data[word])
        #calculate the idfs using the formula in lecture 7
        idfs.append(math.log10(total_docID/total_doc_word_appeared))
        #find out all the document IDs which at least one of the word in the query
        overlapped_docID += (list(data[word].keys()))
        #remove dupulicate and sort document IDs
    overlapped_docID=list(set(overlapped_docID))
    overlapped_docID.sort(key=int)

    # for all the documents that contain at tleast one of the word
    for ID in overlapped_docID:
        #and for every word in the query
        for word in word_list:
            #try to calculate term frequency
            #if it causes a error. tf is 0, so this word never appeared in this document
            #no need to calculate tfidf for this word in this document, so we give it 0
            try:
                tf=float(len(data[word][ID]))
                tfs.append(1+math.log10(tf))
            except:
                tfs.append(0)

        #then for every word, take their idf and tf for this current document ID
        #calulate a score
        for i in range(len(idfs)):
            score =score+(idfs[i]*tfs[i])

        #append the score and its associated document ID to score list,
        #reset tfs and score, for next document ID
        scores.append((ID,score))
        tfs=[]
        score=0


    #sort the score list in descending order , it is a tuple (ID,score)
    scores.sort(key=lambda tup:tup[1], reverse= True)
    #print(scores)
    #print(len(scores))
    return scores[:1000]





def main(query):
    #open the json file and retrieve the dictionary created in the preprocessing
    with open('index_index_data.json', 'r') as fp:
        data = json.load(fp)

    #read all the document IDs and split it so we have a list of IDs
    all_doc_ID=open("all_document_ID.txt").read().split('\n')
    #delete the final character as its a empty string
    del all_doc_ID[-1]

    score=tfidf(query,data,all_doc_ID)






if __name__ == '__main__':
    query=sys.argv[1]
    print(query)
    main(query)
