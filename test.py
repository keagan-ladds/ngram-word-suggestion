import suggestion
import pickle
import nltk
from nltk.util import ngrams, everygrams
from nltk.metrics import edit_distance

test = 'The Tortoise never stopped for a moment, walking slowly but steadily, right to the end of the course. The Hare ran fast and stopped to lie down for a rest. But he fell fast asleep. Eventually, he woke up and ran as fast as he could. But when he reached the end, he saw the Tortoise there already, sleeping comfortably after her effort.'
tokens = suggestion.tokenize(test);

model = suggestion.train(tokens, 3)
print('Suggestion: ' , model.suggest('never stopped believing in the'))