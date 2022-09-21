import suggestion
import pickle
import nltk
from nltk.util import ngrams, everygrams
from nltk.metrics import edit_distance

with open('data/ngram_model.pickle', 'rb') as handle:
    model = pickle.load(handle)

print(model.suggest('The end of time, I was'))