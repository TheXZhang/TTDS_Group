import string
import nltk
nltk.download('wordnet')
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from spellchecker import SpellChecker
from textblob import TextBlob

s_words = stopwords.words("english")
translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
ps = PorterStemmer()
spell = SpellChecker()

def if_food(word):

    syns = wn.synsets(str(word), pos = wn.NOUN)

    for syn in syns:
        if 'food' in syn.lexname():
            return 1
    return 0

def search(input):
    s_input = input.translate(translator).split()
    out = [w for w in s_input if w not in s_words]
    output_server = []
    output_web = []
    for wor in out:
        wor = spell.correction(wor)
        b = TextBlob(wor)
        if b.detect_language() == 'en':
            if if_food(wor) == 1:
                output_web.append(wor)
                output_server.append(ps.stem(wor))
    return output_web, output_server

if __name__ == "__main__":
    print(search('apple and banana with orange,car,asdsas,pulë,123097se98r9823'))
