import sqlite3
import pickle
import nltk
from nltk.util import ngrams, everygrams
from nltk.metrics import edit_distance
from nltk.tokenize.treebank import TreebankWordDetokenizer

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

class SuggestionModel:
    def __init__(self, ngrams, n):
        self.ngrams = ngrams
        self.n = n
        self.thresh = 0.00001
        

    def get_ngram_suggestions(self, tokens, thresh=0.1):
        n = len(tokens)
        nextwords = dict()
        t = dict()
        
        for i in range(1, min(n, self.n-1)+1, 1):
            if tokens[i-n:] in self.ngrams:
                next = self.ngrams[tokens[i-n:]]['next']
                for k in next:
                    if k not in t:
                        t[k] = {'token': k, 'score': next[k]}
                    else:
                        t[k] = {'token': k, 'score': next[k] + t[k]['score']}
                

        a = sorted(t.values(), key=lambda x: x['score'], reverse=True)  
        a = [x for x in a if x['score'] >= thresh]    
        return a

    def generate_suggested_sentences(self, context, next_words, sentence = [], sentences = [], max_depth = 16):

        for next_word in next_words[:5]:
            next_context = context.copy()
            next_sentence = sentence.copy()

            next_context.append(next_word['token'])
            next_sentence.append(next_word['token'])
            n = self.get_ngram_suggestions(tuple(next_context[-(self.n):]), 1.25)
            if len(n) > 0 and len(sentence) < max_depth and not is_end_of_sentence(next_sentence):
                sentences = self.generate_suggested_sentences(next_context, n, next_sentence, sentences)
            else:
                if is_end_of_sentence(next_sentence) and len(next_sentence) > 2:
                    sentences.append(next_sentence)

        return sentences

    def suggest(self, text):
        tokens = tokenize(text, pad_start=True, pad_end=True)
        predicted_next_words = []
        replacement_words = []
        sentences = []

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

        if len(predicted_next_words) > 0:
            sentences = self.generate_suggested_sentences(tokens[-(self.n):], predicted_next_words, sentence=[], sentences=[])
            for sentence in sentences:
                predicted_next_words.insert(0, {'token': detokenize(sentence), 'score': 1})

        predicted_next_words = [word for word in predicted_next_words if word['token'] not in ['<s>', '</s>']]

        return {'next_words': predicted_next_words, 'replacements': replacement_words}

def is_end_of_sentence(sentence):

    if len(sentence) == 0:
        return False

    if sentence[-1] == '</s>':
        return True

    return False

def tokenize(text, pad_start=False, pad_end=False):
    tokens = []
    for sentence in nltk.sent_tokenize(text):
        token_list = nltk.word_tokenize(sentence)
        #token_list2 = [word.replace("'", "") for word in token_list ]
        token_list = list(filter(lambda token: nltk.tokenize.punkt.PunktToken(token).is_non_punct, token_list))
        token_list=[word.lower() for word in token_list ]

        if pad_start == True:
            tokens.append('<s>')

        tokens.extend(token_list)

        if pad_end == True:
            tokens.append('</s>')

    if pad_end == True:
        tokens = tokens[0:-1]

    return tokens

def detokenize(tokens):

    tokens = [word.replace("</s>", ".") for word in tokens ]
    tokens = [word.replace("<s>", "") for word in tokens ]

    tagged_sent = nltk.pos_tag(tokens)
    normalized_sent = [w.capitalize() if t in ["NNP","NNPS"] else w for (w,t) in tagged_sent]
    return TreebankWordDetokenizer().detokenize(normalized_sent) 

def train(tokens, num=3):
    nltk.download('punkt')
    ngrams_list = list(everygrams(tokens, 1, num))
    ngram_counts = dict()
    ngram_probabilities = dict()

    for ngram in ngrams_list:
        if ngram in ngram_counts:
            ngram_counts[ngram] += 1
        else:
            ngram_counts[ngram] = 1

    for ngram in ngram_counts:
        if len(ngram) > 1:
            previous_ngram = ngram[:-1]
            ngram_probabilities[ngram] = ngram_counts[ngram] / ngram_counts[previous_ngram]


    ngram_dict = dict()

    for ngram in ngrams_list:
        n = len(ngram) - 1

        t = ngram[0:n]
        if len(t) > 0:
            if t in ngram_dict:
                ngram_dict[t]['next'][ngram[n]] =  ngram_probabilities[ngram]
            else:
                ngram_dict[t] = {'next':dict()}
                ngram_dict[t]['next'][ngram[n]] = ngram_probabilities[ngram]

    return SuggestionModel(ngram_dict, num)
    

   
