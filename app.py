#-----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
#-----------------------------------------------------------------------------------------

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle

app = Flask(__name__)
CORS(app)


with open('data/ngrams_en_US.pickle', 'rb') as handle:
    model = pickle.load(handle)


@app.route("/")
def hello():
    return app.send_static_file("index.html")

@app.route("/api/v1/suggest", methods = ['GET', 'POST'])
def suggest():
    content = request.json
    phrase = content['text']
    return jsonify(model.suggest(phrase))

app.run(host="0.0.0.0", port=5000, threaded=True)








