import json
import re
import shlex
import math
import nltk
import sys
import pandas as pd


# def search(recipe, processed_dislike_list, dislike_list, processed_list):
#     main(processed_list,processed_dislike_list)
#     recipe_list= [
#     {
#         "id":0,
#         "name": "bagel111",
#         "ingredients": ["onion", 'bread'],
#         "description": "this is a description of bagel,this is a description of bagel，this is a description of bagel, bagel,this is a description of bagel，th, bagel,this is a description of bagel，th",
#         "url": ""
#     },
#     {
#         "id":1,
#         "name": "bagel222",
#         "ingredients": ["onion", 'bread'],
#         "description": "this is a description of bagel,this is a description of bagel，this is a description of bagel, bagel,this is a description of bagel，th, bagel,this is a description of bagel，th",
#         "url": ""
#     }
# ]








def tfidf(word_list,dislike_list,index,all_doc_ID):
    #for tfidf,there maybe a stopword in the query,
    #so we read the stopword file and stem the word
    overlapped_docID=[]
    idfs=[]
    tfs=[]
    score=0
    scores=[]
    total_docID=len(all_doc_ID)
    result_ID=[]

    new_word_list=[word for word in word_list if word not in dislike_list]

    for word in new_word_list:
        #for every word in the query,
        #find out total number of document that the word appeared in
        total_doc_word_appeared=len(index[word])
        #calculate the idfs using the formula in lecture 7
        idfs.append(math.log10(total_docID/total_doc_word_appeared))
        #find out all the document IDs which at least one of the word in the query
        overlapped_docID += (list(index[word].keys()))
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
                tf=float(len(index[word][ID]))
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
        result_ID.append(str(int(ID)+2))
        tfs=[]
        score=0

    

    
    #sort the score list in descending order , it is a tuple (ID,score)
    scores.sort(key=lambda tup:tup[1], reverse= True)
    #print(scores)
    #print(len(scores))
    result=retrieve_info(result_ID,all_doc_ID)
    return result


def retrieve_info(id_list,all_doc_ID):
    return_result=[]
    skip_id=[ID for ID in all_doc_ID if ID not in id_list]
    df=pd.read_csv('RAW_recipes.csv', skiprows=skip_id, nrows=5, header=0)
    print(df)


    for i in range(len(id_list)):
        result=df.loc[df['Doc_ID'] == int(id_list[i])]
        description=result['description'].values
        ingredients=result['ingredients'].values
        steps=result['steps'].values
        name=result['name'].values
        
        return_result.append({})
        return_result[i]['id']=i
        return_result[i]['name']=name
        return_result[i]['ingredients']=ingredients
        return_result[i]['description']=description
        return_result[i]['url']=''
    return return_result











def main(recipe, processed_dislike_list, dislike_list, processed_list):
    #open the json file and retrieve the dictionary created in the preprocessing
    with open('index_index_data.json', 'r') as fp:
        index = json.load(fp)

    #read all the document IDs and split it so we have a list of IDs
    all_doc_ID=open("all_document_ID.txt").read().split('\n')
    #delete the final character as its a empty string
    del all_doc_ID[-1]
    recipe_list=tfidf(processed_list,processed_dislike_list,index,all_doc_ID)

    return {
        "recipe_name": recipe,
        "dislike_list": dislike_list,
        "recipe_list": recipe_list
        }







if __name__ == '__main__':
    pass
    
