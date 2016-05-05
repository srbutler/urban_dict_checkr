"""Gets a UD def."""

import string

from flask import Flask, request, render_template
from lxml import html
import requests


app = Flask(__name__)


def get_ud_string(word):
    """Get the top UD definition of a word as a 'word: def' string."""

    url = "http://www.urbandictionary.com/define.php?term=%s" % word
    page = requests.get(url)
    tree = html.fromstring(page.content)

    words = tree.xpath('//a[@class="word"]/text()')
    meanings = tree.xpath('//div[@class="meaning"]/text()')
    ranks = tree.xpath('//div[@class="ribbon"]/text()')

    # examples = tree.xpath('//div[@class="example"]/text()')
    # counts = tree.xpath('//div[@class="count"]/text()')

    top_def_str = None

    for tup in zip(words, meanings, ranks):

        if tup[2].strip() == "Top Definition":
            top_def_str = "{}: {}".format(tup[0].strip().lower(),
                                          tup[1].strip())

    return top_def_str


def get_ud_def(word):
    """Get the top UD definition of a word in a (word, def) tuple."""

    url = "http://www.urbandictionary.com/define.php?term=%s" % word
    page = requests.get(url)
    tree = html.fromstring(page.content)

    words = tree.xpath('//a[@class="word"]/text()')
    meanings = tree.xpath('//div[@class="meaning"]/text()')
    ranks = tree.xpath('//div[@class="ribbon"]/text()')

    top_def = None

    for tup in zip(words, meanings, ranks):

        if tup[2].strip() == "Top Definition":
            top_def = (tup[0].strip().lower(), tup[1].strip())

    return top_def


def chunk_text(input_text, chunk_size=4):

    exclude = set(string.punctuation)

    depuncted_text = ''.join(ch.lower() for ch in input_text if ch not in exclude)

    text_list = depuncted_text.split()

    candidates = []

    for i in range(len(text_list)):
        # get candidate phrases up to 3 words away (totally arbitrary length)
        indiv_candidates = [' '.join(text_list[i:i+n]) for n in range(chunk_size)]

        # get rid of empties (not sure why there are any, but this clears them out)
        indiv_candidates = [x for x in indiv_candidates if x != '']

        candidates.extend(indiv_candidates)

    # print(len(candidates))
    return set(candidates)


def filter_stop_words(input_iter, stopwords_file, n_words=100):

    with open(stopwords_file, 'r') as f:
        data = f.readlines()
        data_words = [x.split(' ')[0] for x in data]

    return [w for w in input_iter if w not in data_words[:n_words]]


def evaluate_text(input_text):

    wordlist_file = "data/english_wordlist.txt"

    check_words = filter_stop_words(chunk_text(input_text), wordlist_file)

    word_dict = {}
    for word in check_words:
        ud_def = get_ud_def(word.lower())

        if ud_def is not None:
            word_dict[ud_def[0]] = ud_def[1]

    return word_dict


def format_return(input_text):

    final_str = ""

    wordlist_file = "data/english_wordlist.txt"

    check_words = filter_stop_words(chunk_text(input_text), wordlist_file)

    for word in check_words:
        ud_def_str = get_ud_string(word.lower())

        if ud_def_str is not None:
            final_str += ud_def_str + "<br><br>"

    return final_str


@app.route('/')
def my_form():
    return render_template("input-form.html")


@app.route('/', methods=['POST'])
def my_form_post():

    text = request.form['text']

    word_defs = evaluate_text(text)
    return render_template("output-page.html", word_defs=word_defs)

    # formatted_defs = format_return(text)
    # return render_template("output-page.html",
    #                        input_text=text,
    #                        formatted_input=formatted_defs)


if __name__ == '__main__':
    app.run()
