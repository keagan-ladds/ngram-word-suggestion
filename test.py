import suggestion
import pickle
import nltk



with open('data/ngram_model.pickle', 'rb') as handle:
    model = pickle.load(handle)

print(model.suggest('the wisdom of father was '))

#print(predictor.suggest('This is probbly'))