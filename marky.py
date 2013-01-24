#!/usr/bin/env python
import collections
import functools
import itertools
import random
import re
import sys


class MarkovLookup(object):
    def __init__(self, word):
        self.word = word
        self.number_w = 0
        self._words = collections.defaultdict(int)

    def add_word(self, word):
        self.number_w += 1
        self._words[word] += 1

    def get_rand_word(self, rand, acceptable):
        r = rand(0, self.number_w + 1)
        w = None
        for word in itertools.ifilter(lambda x: r > 0, filter(functools.partial(acceptable, self.word), self._words.keys())):
            w = word
            r -= self._words[word]
        return w


class MarkovChain(object):
    """A markov chain, which can be used to generate psuedo-random text.

    A Markov Chain is really a mathematical concept, not a text-generation or even NLP one, however it works very well for generating text.
    The basic idea is to take a large passage (source text), and count what words appear after other words.
    For example, take this excerpt:
        The Sun came up upon the left, Out of the sea came he!
        And he shone bright, and on the right Went down into the sea.
    Two things immediately jump out: this isn't bog-standard English, and there's a few words repeated.
    Markov chains exploit the second to work with the first. When processing this into a markov chain, the chain
    would see that two words come after the word 'came' in different situations: 'up' and 'he'. So if the current state
    of the markov chain was 'came', it would randomly choose either 'up' or 'he'. This can lead to the construct 'came he',
    which you would never see in normal english but is common in olde-timey literature like this. Thus, the generated text
    would resemeble the source.

    Of course, markov chains are far from perfect. Since they only use 1 word of context, they don't follow grammar conventions
    at all. The text you get out won't make sense, besides rare flashes of intelligence. However, it can certainly produce
    interesting texts.

    Class members:
    self.last_word -- the last word returned by get_word()/next()
    """
    def __init__(self, step, words, rand=random.randint):
        """Create a new MarkovChain instance. You should generally use the shorter function chain() unless you need specific functionality of the full constructor,

        Arguments:
        step -- the step to read in the source text. The amount is the number of words ahead to pair words, the sign is forwards or backwards.
            For example: a step of 1 in (apple, orange, peach) would pair (apple, orange), (orange, peach); 2 would pair (apple, peach); and -2 would pair (peach, apple).
        words -- the tokenized words. You can use the module-level function word_tokenize to do this if you have installed nltk.
        rand -- (default random.randint) -- how to pick words. Needs to conform to the same signature as rand.randint: (min inclusive, max exclusive) -> number
        """
        self._generate_word_tree(step, words)
        self.rand = rand
        self.last_word = None

    def _generate_word_tree(self, step, words):
        self.word_tree = {}
        w_list = words
        if step < 0:
            w_list.reverse()
        for w, n in zip(w_list, w_list[abs(step):]):
            w, n = w.lower(), n.lower()
            if not is_punc(w) and not is_punc(n):
                if not w in self.word_tree:
                    self.word_tree[w] = MarkovLookup(w)
                self.word_tree[w].add_word(n)

    def reset(self, start_at=None):
        """Reset the markov chain as if it hadn't been run and had last_word set. 

        Arguments:
        start_at (optional) -- What to set last_word to instead of None, if you got a word out of something else (another markov chain, for example)
        """
        self.last_word = start_at

    def get_word(self, acceptable=lambda word1, word: True):
        """Get a word based on the current state.

        As discussed in the class doc. If last_word is None, return a random word from all words known.

        Arguments:
        acceptable (optional): a function, taking the current and proposed next state, and returning if it's ok.
            This is used in the poetry example to check if two words rhyme to generate the rhyming lines, for example.
            Defaults to always true.
        """
        ok = self.last_word and self.last_word in self.word_tree
        if ok:
            self.last_word = self.word_tree[self.last_word].get_rand_word(self.rand, acceptable)
        if not ok or not self.last_word:  # word with no follow / not initialized
            accepted = filter(functools.partial(acceptable, None), self.word_tree.keys())
            if not accepted:
                return None #Nothing accepted....
            self.last_word = random.choice(accepted)
        return self.last_word

    def __iter__(self):
        return self

    def next(self):
        return self.get_word()


def chain(step, words):
    """Return a markov chain with specified step and words"""
    return MarkovChain(step, words)


def is_punc(word):
    """Simple regular expression tester, tests that there are not **any** letters/numbers in the word."""
    return not bool(re.findall('[a-zA-Z0-9]+', word)) #include things like hiv/aids


def take(iterable, n):
    """Take n elements from the iterator.
    take(chain(1, words), 100) - generate 100 words from the markov chain"""
    return list(itertools.islice(iterable, n))

def strip_end_punc(word):
    """Strip broken punctuation caused by nltk.word_tokenize from the ends of words."""
    for i in xrange(1, len(word) + 1):
        if not is_punc(word[-i:]):
            return word[:-(i - 1)] if i > 1 else word

def fix_passage_punc(passage):
    """Fix trailing punctuation for a whole passage"""
    return map(lambda word: strip_end_punc(word) if not is_punc(word) else word, passage)

def word_tokenize(passage):
    """Tokenize a passage into individual words/punctuation. Requires nltk (nltk.org / pip install nltk) and raises ImportError if it's not installed.
    Sometimes messes up and leaves periods on the end of words (seems to happen most often in passages... loosely obeying grammar rules, like internet rants)
    You can easily strip those with fix_passage_punc if you want to."""
    try:
        import nltk
    except ImportError:
        raise ImportError('word_tokenize requires nltk to be installed (nltk.org / pip install nltk)')
    return nltk.word_tokenize(passage)

if __name__ == '__main__':
    mark = chain(1, fix_passage_punc(word_tokenize(open(sys.argv[1]).read())))
    print ' '.join(take(mark, 100))
