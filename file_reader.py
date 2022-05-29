import os
import spacy
from spacy import displacy
from pathlib import Path


def choose_range(message, min_value, max_value, step=1):
    while True:
        try:
            choice = int(input(f'{message} ({min_value}-{max_value}): '))
        except ValueError:
            print("Nesuprantama ivestis, bandykite dar karta.")
            continue
        if choice not in range(min_value, max_value + 1, step):
            print("Neteisinga ivestis, iveskite naturaluji skaiciu is nurodyto intervalo.")
            continue
        else:
            return choice


def read_stories(path):
    names = []

    for document in os.listdir(path):
        if document.endswith('.txt'):
            names.append(document)

    print("User story dokumentai, kuriuos galima nuskaityti:")
    k = 0
    for name in names:
        print(f'{k:3} - {name}')
        k += 1
    choice = choose_range("Pasirinkite dokumenta nuskaitymui", 0, k - 1)

    story_file = open(path + "/" + names[choice])

    text = story_file.read()

    return text, names[choice]


def prepare_doc_stories(path):
    text, file_name = read_stories(path)

    nlp = spacy.load('en_core_web_sm')

    doc = nlp(text)

    new_doc = []
    sents = []

    for sent in doc.sents:
        for word in sent:
            if word.is_stop == False and word.is_punct == False:
                new_doc.append(word.text)
        new_doc = nlp(" ".join(new_doc).strip())
        sents.append(new_doc)
        new_doc = []

    file = open(file_name.split('.')[0] + '_new.txt', 'a')

    for sent in sents:
        sent = prepare_story(nlp(sent))
        file.write(" ".join(sent).strip() + "\n")


def manual_nlp(path):
    text, file_name = read_stories(path)

    nlp = spacy.load('en_core_web_sm')

    doc = nlp(text)

    new_doc = []
    sents = []

    for sent in doc.sents:
        for word in sent:
            if word.is_stop == False and word.is_punct == False:
                new_doc.append(word.text)
        new_doc = nlp(" ".join(new_doc).strip())
        sents.append(new_doc)
        new_doc = []

    options = {'distance': 150, 'compact': True}

    svg = displacy.render(sents, style="dep", options=options, page=True)
    output_path = Path(path + '/' + file_name.split('.')[0] + '.svg')
    output_path.open("w", encoding="utf-8").write(svg)

    return 0


def prepare_story(doc):
    words = []

    multi_dependencies = []
    for token in doc:
        if token.dep_ != "ROOT":
            words.append(token.dep_)
        k = 0
        for word in doc:
            if str(word.head) == token.text:
                k += 1

        if k <= 1:
            words.append(str(token.pos_))
        else:
            if token.dep_ == "ROOT":
                words.append(token.pos_ + "_r")
                continue
            t = 1

            if len(multi_dependencies) == 0:
                words.append(str(token.pos_ + "_" + str(t)))
                multi_dependencies.append(str(token.pos_ + "_" + str(t)))
                continue

            while True:
                if str(token.pos_ + "_" + str(t)) not in multi_dependencies:
                    words.append(str(token.pos_ + "_" + str(t)))
                    multi_dependencies.append(str(token.pos_ + "_" + str(t)))
                    break
                else:
                    t += 1
    return [word.lower() for word in words]
