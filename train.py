import os
import pickle
import suggestion
import nltk

# Example reading from a sample text file
""" base_file = open('sample_text.txt', 'rt')
raw_text = base_file.read()
base_file.close()
print("Text read from file : ",raw_text[:200]) """

nltk.download('gutenberg')

print(nltk.corpus.gutenberg.fileids())

raw_text = nltk.corpus.gutenberg.raw('austen-emma.txt')

tokens = suggestion.tokenize(raw_text)
model = suggestion.train(tokens, num=5)

print("\nSample token list : ", tokens[:10])
print("\nTotal Tokens : ",len(tokens))

with open('data/ngram_model.pickle', 'wb') as handle:
    pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)


