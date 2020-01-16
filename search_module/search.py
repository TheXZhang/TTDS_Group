import json
import re
import shlex
import math
import nltk

stopword_dir= "/afs/inf.ed.ac.uk/user/s16/s1604556/ttds/englishST.txt"

#open the json file and retrieve the dictionary created in the preprocessing
with open('index_index_data.json', 'r') as fp:
    data = json.load(fp)

#read all the document IDs and split it so we have a list of IDs
all_doc_ID=open("all_document_ID.txt").read().split('\n')
#delete the final character as its a empty string
del all_doc_ID[-1]


def single_word(query):
    #this is for single word query
    global data
    #stem the word
    ps=nltk.stem.PorterStemmer()
    word=ps.stem(query)
    #find out all of of document ID under this word using dictionary
    print(list(data[word].keys()))
    print(len(list(data[word].keys())))

    return (list(data[word].keys()))

def boolean_search(query):
    global all_doc_ID
    global data
    term1_docID=None
    term2_docID=None
    operator=""
    negation_found=False
    negation_position=0
    boolean_result=[]
    ps=nltk.stem.PorterStemmer()

    #first split by space, then loop every term in the list.
    #if we have a NOT, we need to do negation for one of the term
    #then find out if the operator is AND or OR
    query_split_by_space=query.split()
    for i in range(len(query_split_by_space)):

        current_String=query_split_by_space[i]

        if current_String== 'NOT':
            negation_found=True
            negation_position=i
            print(negation_position)

        if current_String== 'AND' or current_String== 'OR':
            operator=current_String

    #then we split the original query by the operator we found then we have somehing like [term1,term2]
    #where term1 and term2 can be an phrase search itself or just a single word
    #and term1 or term2 can have NOT in front of them like ['NOT term1','term2']
    query_split_by_operator=query.split(" "+operator+" ")
    term1=query_split_by_operator[0]
    term2=query_split_by_operator[1]
    #then if negation is found, and its position is 0, first term is negated
    #so we split the first term again ,and take the second element
    #i think using python split is enough. but it is working so I didnt bother to test it
    #same apply to second term if NOT is not found in position 0
    if negation_found:
        if negation_position==0:
            term1=(shlex.split(term1))[1]
        else:
            term2=(shlex.split(term2))[1]

    #then we check if term 1 or term 2 contain quotation marks,
    #if they do, they are phrase search, call phrase search def and obtain result
    for char in term1:
        if char == '\"':
            term1_docID=phrase_search(shlex.split(term1))
            break

    for char in term2:
        if char == '\"':
            term2_docID=phrase_search(shlex.split(term2))
            break

    #if any of the two term are not phrase searchs,
    #then the result list will still be none
    #we know it must be just a single word
    #so we stem the word
    if term1_docID==None:
        term1=(shlex.split(term1))[0]
        term1=ps.stem(term1)
        term1_docID=data[term1]

    if term2_docID==None:
        term2=ps.stem(term2)
        term2_docID=data[term2]


    #if NOT is found, and is the first term that is negated
    if negation_found:
        if negation_position==0:
            #the negation of a word is all the document that does not contain the word
            #so for every document ID in the entire text, if its not one of those ID that contain term1
            #create a list to store all the result of the list comprehension
            negated_term1=[DocID for DocID in all_doc_ID if DocID not in term1_docID]
            #if operator is AND, we need overlapped IDs in both list
            if operator == 'AND':
                boolean_result=[DocID for DocID in negated_term1 if DocID in term2_docID]
                boolean_result.sort(key=int)
            #if operator is OR. we just add both list and remove dupulicates
            if operator == 'OR':
                boolean_result=list(set(negated_term1 + term2_docID))
                boolean_result.sort(key=int)

        else:
            #exact same operation here, but negation is applied for term2
            negated_term2=[DocID for DocID in all_doc_ID if DocID not in term2_docID]
            if operator == 'AND':
                boolean_result=[DocID for DocID in term1_docID if DocID in negated_term2]
                boolean_result.sort(key=int)
            if operator == 'OR':
                boolean_result=list(set(term1_docID + negated_term2))
                boolean_result.sort(key=int)

    else:
        #again, exact same operation as above, but not negation is applied to anything
        if operator == 'AND':
            boolean_result=[DocID for DocID in term1_docID if DocID in term2_docID]
            boolean_result.sort(key=int)
        if operator == 'OR':
            boolean_result=list(set(term1_docID + term1_docID))
            boolean_result.sort(key=int)


    print(boolean_result)
    print(len(boolean_result))
    return boolean_result


def phrase_search(query):
    global data
    ps=nltk.stem.PorterStemmer()
    #the query argument that pass into this def is like ['word1 word2']
    #so we take out this string and split by space
    word_phrase=query[0].split()
    #stem both word
    word1=ps.stem(word_phrase[0])
    word2=ps.stem(word_phrase[1])
    word1_docs=data[word1]
    word2_docs=data[word2]
    phrase_search_result=[]
    #find out all the document IDs both words appears in
    overlap_docID=[docID for docID in data[word1] if docID in data[word2]]
    #for all theses document, and all of the positions for both word
    #if pos of word 2 is 1 more than pos of word 1, then they are one after another
    #we have a match and store the document ID
    for ID in overlap_docID:
        for w1_pos in data[word1][ID]:
            for w2_pos in data[word2][ID]:
                if (int(w1_pos) + 1)==int(w2_pos):
                    phrase_search_result.append(ID)

    #remove dupulicated IDs and sort in ascending order
    phrase_search_result=list(set(phrase_search_result))
    phrase_search_result.sort(key=int)

    print(phrase_search_result)
    print(len(phrase_search_result))
    return phrase_search_result

def proximity_search(query):
    global data
    ps=nltk.stem.PorterStemmer()
    #split the query by () , now we have something like [#5, 'abcd qwer'] in the list
    processed_query=re.split('\(|\)',query)
    #then the second character onwards of the first string in the list is distance value
    given_distance=processed_query[0][1:]
    #split the second string in the list by ', ' or ',' or ' ,' the format given query is not consistent, so I have to do this
    word_list=re.split('\, |\,| \,',processed_query[1])
    #stem the two words
    word1=ps.stem(word_list[0])
    word2=ps.stem(word_list[1])
    proximity_search_result=[]
    #find out all the document both words appears in
    overlap_docID=[docID for docID in data[word1] if docID in data[word2]]
    #for all theses document, and all the positions of both word in the document.
    #if the absolute distance is less than or equal to what is given in the query,
    #we have a match and sotre that document ID
    for ID in overlap_docID:
        for w1_pos in data[word1][ID]:
            for w2_pos in data[word2][ID]:
                distance=abs(int(w1_pos)-int(w2_pos))
                if distance<=int(given_distance):
                    proximity_search_result.append(ID)

    #remove dupulicate document IDs
    proximity_search_result=list(set(proximity_search_result))
    proximity_search_result.sort(key=int)
    print (proximity_search_result)
    print (len(proximity_search_result))
    return proximity_search_result


def tfidf(query):
    global data
    global all_doc_ID
    #for tfidf,there maybe a stopword in the query,
    #so we read the stopword file and stem the word
    stopwords=open(stopword_dir).read().split('\n')
    word_split=query.split()
    word_list=[]
    for word in word_split:
        if word not in stopwords:
            ps=nltk.stem.PorterStemmer()
            word_list.append(ps.stem(word.lower()))
    overlapped_docID=[]
    docID_list=[]
    idfs=[]
    tfs=[]
    score=0
    scores=[]
    total_docID=len(all_doc_ID)
    print(word_list)
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



queries=[]
# This commented out section is where I allow user to type query in command line
# num_query= input("Enter the number of queries you have(in integer only): ")
# for i in range(int(num_query)):
#     temp=input("Enter Your query: ")
#     queries.append(temp)

#need to tell the program which txt file to read from.
query_type= input("which queries file do you want to read from?(Enter 1 for queries.boolean.txt, 2 for queries.ranked.txt): ")

#read the queries from txt file and parse the queries to a list of string.
#for tiidf. also remove the punctionation
if query_type == '1':
    f=open('queries.boolean.txt').readlines()
    open("results.boolean.txt","w").close()
    tem_queries=[(line.split(' ',1))for line in f]
    for query in tem_queries:
        queries.append(query[1][:-1])
elif query_type == '2':
    f=open('queries.ranked.txt').readlines()
    open("results.ranked.txt","w").close()
    tem_queries=[(line.split(' ',1))for line in f]
    for query in tem_queries:
        tem_string=' '.join(re.split('\W+',(query[1][:-1])))
        queries.append(tem_string)




def __main__(query):
    #here I try to distinguish all the query type

    query_counter=1
    for query in queries:

        boolean_search_type=False
        phrase_search_type=False
        tfidf_type=False
        single_word_search_type=False
        proximity_search_type=False

        #first split the query using shlex package
        #I use this as it will automaticlly split by quotation marks
        splited_query=shlex.split(query)
        # if the first character of the query is # it is a proximity search
        if query[0] =='#':
            proximity_search_type=True

        #for every word in the splited_query, if we encounter AND or OR,
        #then it is a boolean search
        for word in splited_query:
            if word == "AND" or word == "OR":
                boolean_search_type= True

        #if we see quotation marks , it is a phrase_search
        for char in query:
            if char =='\"':
                phrase_search_type=True

        #if the list is of length1 we with split by space,
        #then it is single word search
        if len(query.split())==1:
            single_word_search_type=True

       #if it is none of the above, since there is no need for input validation, it must be tfidf ranking search
        if not phrase_search_type and not boolean_search_type and not single_word_search_type and not proximity_search_type:
            tfidf_type=True

        print(proximity_search_type)
        print(boolean_search_type)
        print(phrase_search_type)
        print(tfidf_type)
        print(single_word_search_type)

        #and according to with one is true, execute which search
        if proximity_search_type:
            proximity_result=proximity_search(query)
            with open('results.boolean.txt', 'a') as f:
                for docID in proximity_result:
                    string= str(query_counter)+' 0 '+docID+' 0 1 0'+'\n'
                    f.writelines(string)
        elif boolean_search_type:
            boolean_result=boolean_search(query)
            with open('results.boolean.txt', 'a') as f:
                for docID in boolean_result:
                    string= str(query_counter)+' 0 '+docID+' 0 1 0'+'\n'
                    f.writelines(string)
        elif phrase_search_type:
            phrase_result=phrase_search(splited_query)
            with open('results.boolean.txt', 'a') as f:
                for docID in phrase_result:
                    string= str(query_counter)+' 0 '+docID+' 0 1 0'+'\n'
                    f.writelines(string)
        elif single_word_search_type:
            singl_word_result=single_word(query)
            with open('results.boolean.txt', 'a') as f:
                for docID in singl_word_result:
                    string= str(query_counter)+' 0 '+docID+' 0 1 0'+'\n'
                    f.writelines(string)
        elif tfidf_type:
            tfidf_result=tfidf(query)
            with open('results.ranked.txt', 'a') as f:
                for (docID,score) in tfidf_result:
                    string= str(query_counter)+' 0 '+docID+' 0 '+str(score)+' 0'+'\n'
                    f.writelines(string)

        query_counter +=1

__main__(queries)
