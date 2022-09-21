#-----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
#-----------------------------------------------------------------------------------------

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import os

from gevent.pywsgi import WSGIServer

app = Flask(__name__)
CORS(app)


with open('data/ngram_model.pickle', 'rb') as handle:
    model = pickle.load(handle)




@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
  return send_from_directory('./static', path)


@app.route('/')
def root():
  return send_from_directory('./static', 'index.html')

@app.route("/api/v1/suggest", methods = ['GET', 'POST'])
def suggest():
    content = request.json
    phrase = content['text']
    return jsonify(model.suggest(phrase))

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  http_server = WSGIServer(('0.0.0.0', port), app)
  http_server.serve_forever()








