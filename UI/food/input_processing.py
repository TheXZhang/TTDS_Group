import string
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from spellchecker import SpellChecker

# recipe_database = [
#     {
#         "name": "bagel",
#         "ingredients": ["onion", 'bread'],
#         "description": "this is a description of bagel",
#         "url": "http://www.baidu.com"
#     }
# ]

# add abb in this function !!!!!!!!
# check the word is food
def if_food(word):

    syns = wn.synsets(str(word), pos = wn.NOUN)

    for syn in syns:
        if 'food' in syn.lexname():
            return 1
    return 0

# tokenise string into list of words and remove punctuation
def token(input):
    # set a translator to translate punctuation to empty space
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    # remove punctuation and split string into list
    split_input = input.translate(translator).split()
    return split_input

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

# spell check, check words length longer than 2
def correction(input):
    spell = SpellChecker()
    valid_input = []
    for wor in input:
        # if the length of word larger than 2, then check correction
        if len(wor) > 2:
            wor = spell.correction(wor)
            valid_input.append(wor)
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

    # if stem is True, then process
    if stem == True:
        stem_input = stemm(food_list)
    else:
        stem_input = food_list

    return stem_input

def handle(request):
    # read user input for search
    recipe_name = request.form.get("recipe")
    # read user input for dislike food
    dislike_list = []
    if request.form.get("dislike_list"):
        dislike_list = request.form.get("dislike_list").split(",")

    # verify input and return result for user
    list_of_food_user = validation(recipe_name, tok=True, corr=True)

    # after verified, return list a stemmed word for server
    list_of_food_server = validation(recipe_name, tok=True, sto=True, corr=True, check_food=True, stem=True)

    # verify the dilike food
    list_of_dislike = validation(dislike_list, corr=True, check_food=True, stem=True)

    return list_of_food_user, list_of_dislike, list_of_food_server
