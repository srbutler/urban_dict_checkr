"""Gets a UD def."""

from flask import Flask
from flask import request
from flask import render_template

import requests
from lxml import html


app = Flask(__name__)


def get_ud_def(word):

    url = "http://www.urbandictionary.com/define.php?term=%s" % word
    page = requests.get(url)
    tree = html.fromstring(page.content)

    words = tree.xpath('//a[@class="word"]/text()')
    meanings = tree.xpath('//div[@class="meaning"]/text()')
    # examples = tree.xpath('//div[@class="example"]/text()')
    ranks = tree.xpath('//div[@class="ribbon"]/text()')
    # counts = tree.xpath('//div[@class="count"]/text()')

    top_def = None

    for tup in zip(words, meanings, ranks):

        word = tup[0].strip().lower()
        meaning = tup[1].strip()
        rank = tup[2].strip()

        if rank == "Top Definition":
            top_def = "{}: {}".format(word, meaning)

    return top_def


def chunk_text(input_text):

    import string

    exclude = set(string.punctuation)

    depuncted_text = ''.join(ch.lower() for ch in input_text if ch not in exclude) 

    text_list = depuncted_text.split()

    candidates = []

    for i in range(len(text_list)-3):
        # get candidate phrases up to 3 words away (totally arbitrary length)
        indiv_candidates = [' '.join(text_list[i:i+n]) for n in range(4)]

        # get rid of empties (not sure why there are any, but this clears them out)
        indiv_candidates = [x for x in indiv_candidates if x!='']

        candidates.extend(indiv_candidates)

    # print(len(candidates))
    return set(candidates)


def format_return(input_text):

    final_str = "<b>Input: </b>" + input_text + "<br><br>"

    for word in chunk_text(input_text):

        ud_def = get_ud_def(word.lower())

        if ud_def is not None:

            final_str += ud_def + "<br><br>"

    return final_str


@app.route('/')
def my_form():
    return render_template("input-form.html")


@app.route('/', methods=['POST'])
def my_form_post():

    text = request.form['text']

    return format_return(text)

if __name__ == '__main__':
    app.run()
