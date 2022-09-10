import sqlite3
import pickle
import nltk
from nltk.util import ngrams, everygrams
from nltk.metrics import edit_distance

class SuggestionModel:
    def __init__(self, ngrams, n):
        self.ngrams = ngrams
        self.n = n
        self.thresh = 0.00001
        

    def get_ngram_suggestions(self, tokens):
        n = len(tokens)

        nextwords = dict()
        t = dict()
        
        for i in range(n, 0, -1):
            if tokens[i-n:n] in self.ngrams:
                next = self.ngrams[tokens[i-n:n]]['next']
                for k in next:
                    if k not in t:
                        t[k] = {'token':k , 'score': next[k]['count']}
                    else:
                        t[k] = {'token':k , 'score': next[k]['count'] + t[k]['score']}

                if len(next) > 0:
                    nextwords.update(next) 
                  

        a = sorted(t.values(), key=lambda x: x['score'], reverse=True)  
        a = [x for x in a if x['score'] >= self.thresh]    
        return a

    def suggest(self, text):
        tokens = tokenize(text)
        predicted_next_words = []
        replacement_words = []

        predicted_next_words = self.get_ngram_suggestions(tuple(tokens[-(self.n):]))

        if len(predicted_next_words) == 0 and len(tokens) >= 2:
            previous_token = tokens[-1]
            predicted_previous_words = self.get_ngram_suggestions(tuple(tokens[-(self.n):-1]))
            distances = [{'token': token['token'], 'distance': edit_distance(previous_token, token['token']) / len(previous_token)} for token in predicted_previous_words]
            distances = sorted(distances, key=lambda x : x['distance'], reverse=False)
            distances = [x for x in distances if x['distance']<=0.5]
            
            if len(distances)> 0:
                replacement_words.append({'token': previous_token, 'replacement': distances[0]['token']})
                tokens[-1] = distances[0]['token']
                predicted_next_words = self.get_ngram_suggestions(tuple(tokens[-(self.n):]))

        return {'next_words': predicted_next_words, 'replacements': replacement_words}


def tokenize(text):
    nltk.download('punkt')
    

    token_list = nltk.word_tokenize(text)
    token_list2 = [word.replace("'", "") for word in token_list ]
    token_list3 = list(filter(lambda token: nltk.tokenize.punkt.PunktToken(token).is_non_punct, token_list2))
    token_list4=[word.lower() for word in token_list3 ]
    return token_list4

def train(tokens, num=3):
    nltk.download('punkt')
    ngrams_list = list(everygrams(tokens, 1, num))
    print('Total N-grams: ', len(ngrams_list))
    ngrams_dict = dict()

    token_count = len(tokens)

    for i in ngrams_list:
        n = len(i) - 1
        if i in ngrams_dict:
            ngrams_dict[i]['count'] += 1/token_count
        else:
            ngrams_dict[i] = {'count': 1/token_count, 'next': dict()}

    for i in ngrams_list:
        n = len(i) - 1
        t = i[0:n]  

        if len(t) > 0:
            if i[n] in ngrams_dict[t]['next']:
                ngrams_dict[t]['next'][i[n]]['count'] += 1/token_count
            else:
                ngrams_dict[t]['next'][i[n]] = {'count': 1/token_count}
    return SuggestionModel(ngrams_dict, num)
    

   
