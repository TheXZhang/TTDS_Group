import json
import re
import math
import nltk
import sys
import pandas as pd
import timeit
import pssf
import time




def tfidf(word_list,dislike_list,index,all_doc_ID,last_search_scores=[], first_search=False):
    #for tfidf,there maybe a stopword in the query,
    #so we read the stopword file and stem the word
    overlapped_docID=[]
    dislike_ID=[]
    idfs=[]
    tfs=[]
    score=0
    scores=[]
    total_docID=len(all_doc_ID)
    result_ID=[]


    new_word_list=[word for word in word_list if word not in dislike_list]

    #start = timeit.default_timer()
    try:
        for word in new_word_list:
            #for every word in the query,
            #find out total number of document that the word appeared in
            total_doc_word_appeared=len(index[word])
            print(total_doc_word_appeared)
            #calculate the idfs using the formula in lecture 7
            idfs.append(math.log10(total_docID/total_doc_word_appeared))
            #find out all the document IDs which at least one of the word in the query
            overlapped_docID += (list(index[word].keys()))
            #remove dupulicate and sort document IDs

        for word in dislike_list:
            dislike_ID += list(index[word].keys())
        dislike_ID = list(set(dislike_ID))
        overlapped_docID=list(set(overlapped_docID))
        overlapped_docID=[ID for ID in overlapped_docID if ID not in dislike_ID]
        overlapped_docID.sort(key=int)

        # stop = timeit.default_timer()
        # print('First module Time: ', stop - start)


        # start = timeit.default_timer()

        # for all the documents that contain at tleast one of the word
        for ID in overlapped_docID:
            #and for every word in the query
            for word in new_word_list:
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
            scores.append((str(int(ID)+1),score))
            tfs=[]
            score=0
        # stop = timeit.default_timer()
        # print('Second module Time: ', stop - start)



        #sort the score list in descending order , it is a tuple (ID,score)
        scores.sort(key=lambda tup:tup[1], reverse= True)
        result_ID=[i[0] for i in scores]
        result_ID=result_ID[:20]

        print(result_ID)

        

        if first_search == True:
            print("first search finishes")
            new_list_ID=prep_info(result_ID,all_doc_ID)
            new_list_ID=new_list_ID + word_list
            print("new ID get")
            print(new_list_ID)
            return tfidf(new_list_ID,dislike_list,index,all_doc_ID, scores[:20], first_search=False)
        else:
            print("second search finishes")
            final_score_tuple=[]
            found=False
            print(len(last_search_scores))
            print(len(scores[:20]))
            for score1 in last_search_scores:
                for score2 in scores[:20]:
                    if score1[0]==score2[0]:
                        final_score_tuple.append((score1[0],(0.75*int(score1[1])+0.25*int(score2[1]))))
                        found=True
                        break
                if found:
                    found=False
                    continue
                else:
                    final_score_tuple.append(score1)
                    

            final_score_tuple.sort(key=lambda tup:tup[1], reverse= True)
            final_Doc_ID=[i[0] for i in final_score_tuple]
            print(final_Doc_ID)


            with open('result_ID.txt', 'w', encoding='utf-8') as f:
                for item in final_Doc_ID:
                    f.write(item + "\n")

            result=retrieve_info(final_Doc_ID,all_doc_ID)
            return result
    except:
        return []
        
    return []


def retrieve_info(id_list,all_doc_ID):
    return_result=[]
    skip_id=[int(ID) for ID in all_doc_ID if ID not in id_list]
    df=pd.read_csv('RAW_recipes.csv', skiprows=skip_id, header=0)

    for i in range(len(id_list)):
        result=df.loc[df['Doc_ID'] == int(id_list[i])]
        description=(result['description'].iloc[0]).replace('\'','')
        ingredients=(result['ingredients'].iloc[0]).replace('\'','')
        name=(result['name'].iloc[0]).replace('\'','')

        return_result.append({})
        return_result[i]['id']=int(id_list[i])
        return_result[i]['name']=name
        return_result[i]['ingredients']=ingredients[1:-1]
        return_result[i]['description']=description[1:-1]
        return_result[i]['url']=''
    return return_result


def display_info(ID,all_doc_ID):
    return_result={}
    temp_copy=all_doc_ID.copy()
    skip_id=temp_copy.remove(ID)
    df=pd.read_csv('RAW_recipes.csv', skiprows=skip_id, header=0)


    result=df.loc[df['Doc_ID'] == int(ID)]
    ingredients=(result['ingredients'].iloc[0]).replace('\'','')
    steps=(result['steps'].iloc[0]).replace('\'','')
    name=(result['name'].iloc[0]).replace('\'','')

    return_result['id']=int(ID)
    return_result['name']=name
    return_result['ingredients']=ingredients[1:-1]
    return_result['description']=steps[1:-1]
    return_result['url']=''

    return return_result


def prep_info(id_list,all_doc_ID):
    return_result=[]
    skip_id=[int(ID) for ID in all_doc_ID if ID not in id_list]
    df=pd.read_csv('RAW_recipes.csv', skiprows=skip_id, header=0)

    for i in range(len(id_list)):
        result=df.loc[df['Doc_ID'] == int(id_list[i])]
        description=result['description'].values
        ingredients=result['ingredients'].values
        steps=result['steps'].values
        name=result['name'].values

        return_result.append("ID:" + id_list[i])
        return_result.append((str(name)))
        return_result.append((str(description)))
        return_result.append((str(ingredients)))
        return_result.append((str(steps)))

    new_word_list=pssf.main(return_result)
    print("ready")

    return new_word_list




def main(index,recipe, processed_dislike_list, dislike_list, processed_list):

    #read all the document IDs and split it so we have a list of IDs
    all_doc_ID=open("all_document_ID.txt").read().split('\n')
    #delete the final character as its a empty string
    del all_doc_ID[-1]

    print(processed_list)

    recipe_list=tfidf(processed_list,processed_dislike_list,index,all_doc_ID,first_search=True)

    return {
        "recipe_name": recipe,
        "dislike_list": dislike_list,
        "recipe_list": recipe_list
        }


if __name__ == '__main__':
    pass