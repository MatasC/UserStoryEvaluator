import spacy
from spacy import displacy
from file_reader import manual_nlp
from file_reader import prepare_story

import os
import numpy
import json
import pickle
from datetime import datetime

import keras as keras

import tflearn
import tensorflow as tf

# from tensorflow.keras.callbacks import TensorBoard

nlp = spacy.load('en_core_web_sm')

with open("F:/Univeras/Univeras_4_pav/Bakis/UserStoryEvaluator/data.json") as file:
    data = json.load(file)

try:
    with open("data.pickle", 'rb') as file:
        words, labels, training, output = pickle.load(file)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data['data']:
        for pattern in intent['patterns']:
            words.extend(pattern.split())
            docs_x.append(pattern)
            docs_y.append(intent['tag'])

        if intent['tag'] not in labels:
            labels.append(intent['tag'])

    words = [w.lower() for w in words]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for i in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = [0 for i in range(len(words))]

        print(bag)

        wrds = [w.lower() for w in doc.split()]

        for w in wrds:
            for i, word in enumerate(words):
                if w == word:
                    bag[i] += 1

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", 'wb') as file:
        pickle.dump((words, labels, training, output), file)

try:
    tf.compat.v1.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation='softmax')
    net = tflearn.regression(net)

    model = tflearn.DNN(net)

    model.load('model.tfl')

except:
    tf.compat.v1.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation='softmax')
    net = tflearn.regression(net)

    # model = tflearn.DNN(net, tensorboard_dir='log', tensorboard_verbose=3)
    model = tflearn.DNN(net)
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)

    model.save('model.tfl')


def bag_of_words(story, words):
    bag = [0 for i in range(len(words))]

    nlp = spacy.load('en_core_web_sm')

    story = nlp(story)

    new_doc = []

    for word in story:
        if word.is_stop == False and word.is_punct == False:
            new_doc.append(word.text)
    story = nlp(" ".join(new_doc).strip())

    story_words = prepare_story(story)

    for s_word in story_words:
        for i, word in enumerate(words):
            if s_word == word:
                bag[i] += 1
    print(numpy.array(bag))

    return numpy.array(bag)


def get_response(written_story):
    results = model.predict([bag_of_words(written_story, words)])
    print(results)
    results_index = numpy.argmax(results)
    tag = labels[results_index]
    if results[0][results_index] > 0.7:
        for tg in data["data"]:
            if tg['tag'] == tag:
                return tg['responses'][0]

    return "I'm sorry. Could you rephrase the question?"


while True:
    story = str(input("Enter a user story:"))
    print(get_response(story))

    # choice = str(input("enter 'yes' to try again - "))

    # if choice == 'yes':
    #     continue
    # else:
    #     break