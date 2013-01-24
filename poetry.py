#!/usr/bin/env python
from __future__ import print_function

import itertools
import nltk
import sys

import marky

cmudict = nltk.corpus.cmudict.dict()


def rhyme(a, b):
    if a.lower() not in cmudict or b not in cmudict or a == b:
        return False
    wsa = list(reversed(cmudict[a.lower()][0]))
    wsb = list(reversed(cmudict[b.lower()][0]))
    return len(list(itertools.takewhile(lambda x: x[0] == x[1], zip(wsa, wsb)))) >= min(2, len(list(wsa)))


def make_couplet(words, forward, backward):  # try to make a couplet. Return None if we fail for whatever reason (generate an independent line that can't be rhymed, whatever)
    first_line = marky.take(forward, words)
    rhymed = backward.get_word(acceptable=lambda un, word: rhyme(first_line[-1], word))
    if not rhymed: #couldn't find rhyme, abort to be handled by main
        return None
    second_line = [ rhymed ] + marky.take(backward, words - 1)
    return first_line, reversed(second_line)

if __name__ == '__main__':
    words = marky.word_tokenize(open(sys.argv[1]).read())
    forward_chain = marky.chain(1, words)  # yams everywhere
    backward_chain = marky.chain(-1, words)

    sentence_length = int(sys.argv[2])
    couplets = int(sys.argv[3])
    for i in xrange(couplets):
        r = None
        while not r:
            r = make_couplet(sentence_length, forward_chain, backward_chain)
        print(' '.join(r[0]))
        print(' '.join(r[1]))
        print()
