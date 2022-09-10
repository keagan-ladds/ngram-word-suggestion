import os
import pickle
import suggestion
import nltk


base_file = open('sample_text.txt', 'rt')
raw_text = base_file.read()
base_file.close()
print("Text read from file : ",raw_text[:200])

nltk.download('gutenberg')

raw_text = nltk.corpus.gutenberg.raw('chesterton-brown.txt')

tokens = suggestion.tokenize(raw_text)
model = suggestion.train(tokens)

print("\nSample token list : ", tokens[:10])
print("\nTotal Tokens : ",len(tokens))

with open('data/ngrams_en_US.pickle', 'wb') as handle:
    pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)


