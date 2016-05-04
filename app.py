"""Gets a UD def."""

from flask import Flask
from flask import request
from flask import render_template

import requests
from lxml import html


app = Flask(__name__)


def get_ud_string(word):

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
            top_def_str = "{}: {}".format(tup[0].strip().lower(), tup[1].strip())

    return top_def_str


def get_ud_def(word):

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


def chunk_text(input_text):

    return input_text.split(' ')


def evaluate_text(input_text):

    text = chunk_text(input_text)

    word_dict = {}
    for word in text:
        ud_def = get_ud_def(word.lower())

        if ud_def is not None:
            word_dict[ud_def[0]] = ud_def[1]

    return word_dict


def format_return(input_text):

    final_str = ""

    for word in chunk_text(input_text):

        ud_def = get_ud_string(word.lower())

        if ud_def is not None:

            final_str += ud_def + "\n\n"

    return final_str


@app.route('/')
def my_form():
    return render_template("input-form.html")


@app.route('/', methods=['POST'])
def my_form_post():

    text = request.form['text']

    formatted_defs = format_return(text)

    return render_template("output-page.html",
                           input_text=text,
                           formatted_input=formatted_defs)

    # return format_return(text)

if __name__ == '__main__':
    app.run()
