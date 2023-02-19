from copy import deepcopy
from flask import Flask, request, jsonify, render_template
import pickle
import tensorflow as tf
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import os
import tree_mitigator
import sys
sys.setrecursionlimit(10000)
# nltk.download('stopwords')
# nltk.download('wordnet')


IMAGES_FOLDER = os.path.join('static', 'images')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = IMAGES_FOLDER

lemmatizer = WordNetLemmatizer()
tokenizer = pickle.load(open('FNC-tokenizer', "rb"))
model = tf.keras.models.load_model('model-FNC-self-embeddings.h5')


@app.route('/')
def home_general():
    return render_template('index.html')


@app.route('/detection', methods=['GET'])
def home_predict():
    return render_template('detection.html')


@app.route('/mitigation', methods=['GET'])
def home_mitigate():
    return render_template('mitigation.html')


@app.route('/detection', methods=['POST'])
def detection():
    x_given = request.form['detection-input']
    initial_content = x_given
    x = re.sub('[^a-zA-Z]', ' ', x_given)
    edited_content = deepcopy(x)
    x = x.lower()
    lowered_content = deepcopy(x)
    x = x.split()
    split_content = deepcopy(x)
    x = [lemmatizer.lemmatize(word)
         for word in x if not word in stopwords.words('english')]
    lemmatized_content = deepcopy(x)
    x = tokenizer.texts_to_sequences(x)

    x = list(map(lambda v: v[0] if len(v) > 0 else None, x))
    x = [i for i in x if i is not None]
    for i in range(len(x), 1000):
        x = [0] + x

    y_result = model.predict([x])[0][0]
    verdict = "true" if (y_result >= 0.5).astype("int") == 1 else "fake"
    verdict = "Verdict: " + verdict
    text = 'The probability of the news to be true is ' + str(y_result) + '.'

    return render_template('detection.html', unedited_content=initial_content, prediction_text=text, edited=edited_content, lowered=lowered_content, split=split_content, lemmatized=lemmatized_content, verdict=verdict)


@ app.route('/mitigation', methods=['POST'])
def mitigation():
    content = request.form['mitigation-input']

    human_format = True if request.form.get("check-format") else False

    (nd, td, root) = tree_mitigator.to_graphviz(
        content, human_format, os.path.join(IMAGES_FOLDER, 'graph'))\

    flag = True

    while flag:
        for file in os.listdir('.'):
            if file.endswith('.png'):
                flag = False
                break

    img = IMAGES_FOLDER + '/graph.png'

    node_top = []

    node_scores = {i: 0 for i in td}

    for n in node_scores:
        node_scores[n] = tree_mitigator.compute_score_per_node(n, root, nd, td)

    node_scores_sorted = sorted(
        node_scores.items(), key=lambda item: item[1], reverse=True)

    i = 0

    for (key, value) in node_scores_sorted:
        if i == 10:
            break
        current_value = str(key) + ' : ' + str(value)
        node_top.append(current_value)
        i += 1

    return render_template('mitigation.html', image_given=img, scores=node_top, ranking_text="Most harmful nodes ranked by score")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
