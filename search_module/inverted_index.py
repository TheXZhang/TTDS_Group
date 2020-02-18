import re
import nltk
import time
import json
import pandas as pd
import timeit

#initialising global variables
tokenized_lines=[]
case_fold_tokenized_lines=[]
stemmed_list=[]
word_dic={}



# def preprocessing():
#     #all the preprocessing steps
#     global stemmed_list
#     tokenisation()
#     case_foldng()
#     tokenized_stopword_removed=remove_StopWord()
#     stemmed_list=stemming(tokenized_stopword_removed)
#
# preprocessing()



# def positional_inverted_index():
#     #once all the above preprocessing steps are completed,
#     #start index the processed text
#     global stemmed_list                                                                #the structure of the stemmed_list is a list of lines, and lines are list of words
#     global word_dic
#     all_doc_ID=[]
#     list_length=len(stemmed_list)
#     location_counter=0
#     for i in range(list_length):                                                       #this loop will loop thourgh every single line in the text with their index in the list
#         if stemmed_list[i][0]=='id' and (stemmed_list[i][1]).isdigit():                #if current element is id and the element following that is a digit, we know this is document ID
#             current_docID=stemmed_list[i][1]                                           #if it is a document ID we store it as current_docID
#             all_doc_ID.append(current_docID)                                           #Here I store the document ID which will later be used in query search
#             location_counter=0                                                         #reset location counter to 0 every time we encounter a document ID
#         else:
#             for word in stemmed_list[i]:                                               #if document ID is not seen, then until we see next document ID,
#                 if word in word_dic:                                                   #the following lines are the document content of the current_docID,
#                     try:                                                               #start another loop which loop through every word in the line
#                         word_dic[word][current_docID].append(str(location_counter))    #try to store the word and its position in a dictionary of dictionary,
#                     except:                                                            #where the first key is word, second key is current_docID, used append since we may see one word in a same document multiple times
#                         word_dic[word][current_docID]=[]                               #if it causes a error, it means that this word is never stored for the current_docID and create a empty list first
#                         word_dic[word][current_docID].append(str(location_counter))    # then append the same way as before
#                 else:
#                     word_dic[word]={}                                                  #if it is a word not seem in the dictionary, we will create a empty dictionary for this word
#                     word_dic[word][current_docID]=[(str(location_counter))]            # and store its position
#                 location_counter +=1                                                   # 1 is added to the counter before we move on to next word

#     #store the indexs to a txt file as required
#     with open('inverted_index_print.txt', 'w') as f:
#         for word in word_dic:
#             f.write(word+":\n")
#             for docID in word_dic[word]:
#                 index=','.join(word_dic[word][docID])
#                 final_string="\t"+docID+":"+index+"\n"
#                 f.write(final_string)
#     #store the dictionary as json file so it can be read in another python file
#     with open('index_index_data.json','w') as fp:
#         json.dump(word_dic,fp)

#     #store all document ID appeared for query search
#     with open('all_document_ID.txt','w') as f:
#         for id_ in all_doc_ID:
#             f.write(id_+"\n")



def preprocessing(minutes_list,steps_list,ingredients_list,description_list):
    combined_list=[]
    list_length=len(steps_list)

    for i in range(list_length):
        try:
            temp_string= steps_list[i] + description_list[i] + ingredients_list[i]
        except:
            temp_string= steps_list[i] + ingredients_list[i]
        combined_list.append(temp_string)

        
    

    tokenized=tokenisation(combined_list)
    case_folded=case_foldng(tokenized)
    stopW_removed=remove_StopWord(case_folded)
    stemmed=stemming(stopW_removed)
    preprocessed_list=remove_number(stemmed)

    for i in range(len(preprocessed_list)):
        temp_number=[minutes_list[i]]
        preprocessed_list[i][0:0]=temp_number

    with open('final.txt', 'w') as f:
        for item in preprocessed_list:
            f.write("%s\n" % item)      







def tokenisation(input_list):
    #for each line we use regular expression "\W+" to split by words
    tokenized_list=[re.split('\W+',string) for string in input_list]
    
    return tokenized_list

def case_foldng(tokenized_list):
    #for each line in the tokenized text,
    #lower case every word in the line
    case_fold_tokenized=[]
    for item in tokenized_list:
        case_fold_tokenized.append([word.lower() for word in item])

    return case_fold_tokenized


def remove_StopWord(case_folded_list):
    stopW_removed_list=[]
    #read englishST file to obtain stopword list
    stopwords=open('englishST.txt').read().split('\n')
    for item in case_folded_list:
        #for every word in the tokenized and lower case text if word is not present in the
        #stopword list, add the word to a new list
        stopW_removed_list.append([word for word in item if word not in stopwords])
        #open a file to store the processed text of this stage

    with open('tokenized and stop word removed.txt', 'w') as f:
        for item in stopW_removed_list:
            f.write("%s\n" % item)

    return stopW_removed_list



def stemming(stopW_removed_list):
    #create an instance of the nltk PorterStemmer
    ps=nltk.stem.PorterStemmer()
    stemmed_list=[]
    #for every word in the tokenized,lower case, and stop word removed list,
    #apply stemming to the word and store it in a new list
    for item in stopW_removed_list:
        stemmed_list.append([ps.stem(word) for word in item])
    with open('tokenized and stopword removed and stemmed.txt', 'w') as f:
        for item in stemmed_list:
            f.write("%s\n" % item)

    return stemmed_list

def remove_number(stemmed_list):
    remove_number=[]
    for item in stemmed_list:
        remove_number.append([word for word in item if not word.isdigit()])

    with open('number removed.txt', 'w') as f:
        for item in remove_number:
            f.write("%s\n" % item)      
    return remove_number



def main():
    columns=['name','id','minutes','contributor_id','submitted','tags','nutrition','n_steps','steps','description','ingredients','n_ingredients']
    data=pd.read_csv("RAW_recipes.csv", names = columns, header=0, nrows=1000)

    minutes_list=data.minutes.tolist()
    steps_list=data.steps.tolist()
    ingredients_list=data.ingredients.tolist()
    description_list=data.description.tolist()

    preprocessing(minutes_list,steps_list,ingredients_list,description_list)




if __name__ == '__main__':
    main()



