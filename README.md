Marky - A Markov Chain Text Generation Library
------------------------------

Marky is a simple library implementing markov-chains of any direction/stepping for text generation.  
Using Marky is incredibly simple.  
You can create a chain like so:
    text = ...
    chain = marky.chain(1, marky.word_tokenize(text))
If you have a problem with nltk leaving punctuation on the ends of words, you can use marky.fix_passage_punc
to strip punctuation from the ends of words.
    text = ...
    chain = marky.chain(1, marky.fix_passage_punc(marky.word_tokenize(text)))

Here, 1 is the step. The step is how far ahead chain pairs words. For example, with a step of 1:
    (a, b, c, d, e) would pair (a, b), (b, c), (c, d), (d, e)
Whereas a step of 2 would pair it to:
    (a, c), (b, d), (c, e)
(notice it drops d since it can't pair with anything)
If the sign is negative, the pairing goes backwards. This is useful for generating from an end word (see the poetry example)
A step of -1 would produce
    (e, d), (d, c), (c, b), (b, a)
And -2 would produce
    (e, c), (d, b), (c, a)

After you have the chain, you can use marky.take(chain, n) to take n generated words. This is based on the itertools.take recipe,
as a MarkovChain instance is also an iterator. If you need to pass more options (check the code for them), you can use the full-featured
get_word method instead of next().

The full simple example code is:

    text = ...
    chain = marky.chain(1, marky.fix_passage_punc(marky.word_tokenize(text)))
    print ' '.join(take(chain, 100))

Note: word_tokenize requires [nltk][1], a python library for NLP.

[1]: http://nltk.org/