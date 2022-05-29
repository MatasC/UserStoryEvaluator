import spacy
from file_reader import prepare_story

import numpy
import json
import pickle
from datetime import datetime

import tflearn
import tensorflow as tf

import tkinter as tk
from tkinter import ttk

import spacy

LARGE_FONT = ('Verdana', 16)
NORMAL_FONT = ('Verdana', 12)
SMALL_FONT = ('Verdana', 10)
BG_GRAY = "#ABB2B9"
BG_COLOR = "#03547C"
DIVIDER_BG_COLOR = "#899499"
TEXT_COLOR = "#EAECEE"


class EvaluatorApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        tk.Tk.wm_title(self, "User Story Evaluator")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, minsize=600, weight=1)
        container.grid_columnconfigure(0, minsize=500, weight=1)

        ttk.Style().configure("TButton", padding=6, relief="flat",
                              background=BG_COLOR)

        self.frames = {}

        frame = AutomaticEvaluator(container, self)

        self.frames[AutomaticEvaluator] = frame

        frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(AutomaticEvaluator)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class AutomaticEvaluator(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=BG_COLOR)

        label = tk.Label(self, text='Automatic Evaluator', font=LARGE_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        label.place(relx=0.28, rely=0.015)

        divider = tk.Frame(self, bg=DIVIDER_BG_COLOR, height=1, bd=0)
        divider.place(relx=0, rely=0.08, relheight=0.01, relwidth=1)

        entered_user_story_label = tk.Label(self, text="Your User Story", font=NORMAL_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        entered_user_story_label.place(relx=0.32, rely=0.15)

        self.entered_user_story_text = tk.Text(self, wrap="word")
        self.entered_user_story_text.place(relx=0.055, rely=0.20, relheight=0.15, relwidth=0.89)
        self.entered_user_story_text.insert('insert', "The User Story entered for evaluation will be displayed here.")
        self.entered_user_story_text.configure(cursor="arrow", state='disabled')

        evaluation_results_label = tk.Label(self, text="Evaluation result", font=NORMAL_FONT,
                                            bg=BG_COLOR, fg=TEXT_COLOR)
        evaluation_results_label.place(relx=0.32, rely=0.38)

        self.evaluation_results_text = tk.Text(self, wrap="word")
        self.evaluation_results_text.place(relx=0.055, rely=0.43, relheight=0.07, relwidth=0.89)
        self.evaluation_results_text.insert('insert',
                                            "The results of evaluating given user story will be displayed here.")
        self.evaluation_results_text.configure(cursor="arrow", state='disabled')

        submit_field_label = tk.Label(self, text="Enter your User Story here", font=NORMAL_FONT,
                                      bg=BG_COLOR, fg=TEXT_COLOR)
        submit_field_label.place(relx=0.24, rely=0.55)

        self.submit_field_text = tk.Text(self, wrap="word")
        self.submit_field_text.place(relx=0.055, rely=0.60, relheight=0.15, relwidth=0.89)
        self.submit_field_text.focus()
        self.submit_field_text.bind("<Return>", self._on_enter_pressed)

        submit_button = ttk.Button(self, text="Submit", width=20, command=lambda: self._on_enter_pressed(None))
        submit_button.place(relx=0.055, rely=0.78, relheight=0.15, relwidth=0.89)

    def _on_enter_pressed(self, event):
        user_story = self.submit_field_text.get(1.0, 'end')
        self._insert_message(user_story)

    def _insert_message(self, user_story):
        if not user_story:
            return

        self.submit_field_text.delete(1.0, 'end')

        self.entered_user_story_text.configure(state='normal')
        self.entered_user_story_text.delete(1.0, 'end')
        self.entered_user_story_text.insert(1.0, user_story)
        self.entered_user_story_text.configure(cursor="arrow", state='disabled')

        self.evaluation_results_text.configure(state='normal')
        self.evaluation_results_text.delete(1.0, 'end')
        self.evaluation_results_text.insert(1.0, get_response(user_story))
        self.evaluation_results_text.configure(cursor="arrow", state='disabled')


nlp = spacy.load('en_core_web_sm')

with open("data.json") as file:
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
    net = tflearn.fully_connected(net, 8, activation="Tanh")
    net = tflearn.fully_connected(net, 8, activation="Tanh")
    net = tflearn.fully_connected(net, 8, activation="Tanh")
    net = tflearn.fully_connected(net, 8, activation="Tanh")
    net = tflearn.fully_connected(net, len(output[0]), activation='softmax')
    net = tflearn.regression(net)

    model = tflearn.DNN(net)

    model.load('model.tfl')

except:
    tf.compat.v1.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8, activation="Tanh")
    net = tflearn.fully_connected(net, 8, activation="Tanh")
    net = tflearn.fully_connected(net, 8, activation="Tanh")
    net = tflearn.fully_connected(net, 8, activation="Tanh")
    net = tflearn.fully_connected(net, len(output[0]), activation='softmax')
    net = tflearn.regression(net)

    log_dir = "logs/fit/" + datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    model = tflearn.DNN(net, tensorboard_dir=log_dir, tensorboard_verbose=3)
    model.fit(training, output, n_epoch=10000, batch_size=8, show_metric=True)

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

    return numpy.array(bag)


def get_response(written_story):
    results = model.predict([bag_of_words(written_story, words)])
    results_index = numpy.argmax(results)
    tag = labels[results_index]
    if results[0][results_index] > 0.7:
        for tg in data["data"]:
            if tg['tag'] == tag:
                return tg['responses'][0]

    return "Could not evaluate provided User Story."


if __name__ == "__main__":

    app = EvaluatorApp()
    app.mainloop()