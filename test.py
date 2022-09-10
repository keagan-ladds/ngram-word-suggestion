import suggestion
import pickle
import nltk



with open('data/ngrams_en_US.pickle', 'rb') as handle:
    model = pickle.load(handle)

print(model.suggest('this is the '))

#print(predictor.suggest('This is probbly'))