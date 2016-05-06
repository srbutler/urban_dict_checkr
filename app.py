"""Gets a UD def."""

from collections import OrderedDict
import re

from flask import Flask, flash, request, render_template
from lxml import html
import requests
from wtforms import Form, TextAreaField


app = Flask(__name__)


class InputForm(Form):
    text_input = TextAreaField("")


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

    exclude = set('!"#$%&()*+,-./:;<=>?@[\]^_`{|}~')

    depuncted_text = ''.join(ch.lower() for ch in input_text if ch not in exclude)

    text_list = depuncted_text.split()

    candidates = []

    for i in range(len(text_list)):
        # get candidate phrases up to 3 words away (totally arbitrary length)
        indiv_candidates = [' '.join(text_list[i:i+n]) for n in range(chunk_size)]

        # get rid of empties (not sure why there are any, but this clears them out)
        indiv_candidates = [x for x in indiv_candidates if x != '']

        candidates.extend(indiv_candidates)

    candidate_dict = OrderedDict()

    for cand in candidates:
        candidate_dict[cand] = 0

    return candidate_dict.keys()


def filter_stop_words(input_iter, stopwords_file, n_words=1000):

    with open(stopwords_file, 'r') as f:
        data = f.readlines()
        data_words = [x.split(' ')[0].lower() for x in data]

    return [w for w in input_iter if w not in data_words[:n_words]]


def check_identity(word, returned_word):

    if word == returned_word:
        return True
    elif word == returned_word + "s":
        return True
    elif word == returned_word + "es":
        return True
    else:
        return False


def evaluate_text(input_text):

    wordlist_file = "data/english_wordlist.txt"

    check_words = filter_stop_words(chunk_text(input_text), wordlist_file)
    
    word_dict = OrderedDict()
    for word in check_words:
        ud_def = get_ud_def(word.lower())

        if ud_def is not None:
            if check_identity(word, ud_def[0]):
                if len(ud_def[1]) >= 1:
                    word_dict[ud_def[0]] = ud_def[1]

    return word_dict


def markup_text(input_text, word_defs):

    hl_words = word_defs.keys()

    out_text = input_text

    for word in hl_words:

        pattern = '({})'.format(word)
        repl = '<em>\g<1></em>'
        out_text = re.sub(pattern, repl, out_text)

    return out_text


@app.route('/')
def get_input():
    
    form = InputForm(request.form)
    return render_template("input-form.html", form=form)


@app.route('/output', methods=['POST'])
def show_output():
    
    text = request.form.getlist('text_input')[0]
    word_defs = evaluate_text(text)

    return render_template("output-page.html",
                           input_text=text,
                           word_defs=word_defs)

if __name__ == '__main__':
    app.run(debug=True)
