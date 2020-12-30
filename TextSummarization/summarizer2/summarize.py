from summarizer2.sumy.nlp.tokenizers import Tokenizer
from summarizer2.sumy.parsers.plaintext import PlaintextParser
from summarizer2.sumy.nlp.tokenizers import Tokenizer
from summarizer2.sumy.nlp.stemmers import Stemmer
from summarizer2.sumy.utils import get_stop_words
from summarizer2.sumy.summarizers.text_rank import TextRankSummarizer
from summarizer2.sumy.summarizers.sum_basic import SumBasicSummarizer
from summarizer2.sumy.summarizers.kl import KLSummarizer
import os
import json


LANGUAGE = "vietnam"
stemmer = Stemmer(LANGUAGE)


def sumbasic_summarizer(text, stemmer, language, sentences_count):
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    summarizer_luhn = SumBasicSummarizer(stemmer)
    summarizer_luhn.stop_words = get_stop_words(language)
    sentences = []
    for sentence in summarizer_luhn(parser.document, sentences_count):
        a = sentence
        sentences.append(str(a))
    return "\n".join(sentences)

def kl_summarizer(text, stemmer, language, sentences_count):
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    summarizer_luhn = KLSummarizer(stemmer)
    summarizer_luhn.stop_words = get_stop_words(language)
    sentences = []
    for sentence in summarizer_luhn(parser.document, sentences_count):
        a = sentence
        sentences.append(str(a))
    return "\n".join(sentences)

def textrank_summarizer(text, stemmer, language, sentences_count):
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    summarizer_luhn = TextRankSummarizer(stemmer)
    summarizer_luhn.stop_words = get_stop_words(language)
    sentences = []
    for sentence in summarizer_luhn(parser.document, sentences_count):
        a = sentence
        sentences.append(str(a))
    return "\n".join(sentences)



def summarize(text, stemmer = stemmer, language = 'vietnam', sentences_count = 2, sum_index = 0):
    def switch(sum_index):
        switcher={
            0: textrank_summarizer(text, stemmer, language, sentences_count),
            1: sumbasic_summarizer(text, stemmer, language, sentences_count),
            2: kl_summarizer(text, stemmer, language, sentences_count),
        }
        return switcher.get(sum_index)
    return switch(sum_index)

