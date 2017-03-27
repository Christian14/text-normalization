from __future__ import division
from collections import OrderedDict
from unidecode import unidecode
import hunspell
import json
import csv
import collections
import doctest
import pprint
import codecs
import math
import aspell
import subprocess
from subprocess import Popen, PIPE
# /usr/share/hunspell/es_PE.aff
# /usr/share/hunspell/es_PE.dic
spellchecker = hunspell.HunSpell('/usr/share/hunspell/es_PE.dic',
                                 '/usr/share/hunspell/es_PE.aff')

aspell = aspell.Speller('lang', 'es')

def correct_words(aspell, spellchecker, words, add_to_dict=[]):

    if add_to_dict:
        for w in add_to_dict:
            spellchecker.add(w)
    
    for word, value in words.iteritems():
        if(words[word]['status'] == 0):
            ok = spellchecker.spell(word)
            if not ok:
                w_without_repetitions = "".join(OrderedDict.fromkeys(word))
                suggestions_with_repetitions = spellchecker.suggest(word)
                suggestion_without_repetitions = spellchecker.suggest(w_without_repetitions)
                #aspell_suggestion = aspell.suggest(word)
                #aspell_suggestion = [print w.decode("utf-8") for w in aspell_suggestion]
                #aspell_suggestion_without_repetitions = aspell.suggest(w_without_repetitions)
                #aspell_suggestion_without_repetitions = [unicode(w, "utf-8") for w in aspell_suggestion_without_repetitions]
                #print aspell_suggestion
                #print aspell_suggestion_without_repetitions

                suggestions = suggestions_with_repetitions + suggestion_without_repetitions

                if suggestions:
                    for suggestion in suggestions:
                        words[word][suggestion] = {"Levensthein": 0, "2gram": 0,"3gram": 0, "4gram": 0, "Phonetic": 0} 
                else:
                    words[word]['status'] = 2 #No especifica
            else:
                words[word]['status'] = 1 #Palabra corregida

    return words

def hunspell_correction(words):

    return correct_words(aspell, spellchecker, words)

def to_dictionary(tweet):
    dictionary = {}
    words = tweet.split(' ')
    special_characters = ['.', ',', '!', '?','\n','\t']

    for word in words:
        dictionary[word.translate(None, ''.join(special_characters))] = {"status": 0}

    return dictionary

def find_capitals(words):
    with open('files/capitals.txt') as capitals:
        capitals_reader = capitals.readlines()

    for word, value in words.iteritems():
        for names in capitals_reader:
            names = names.replace('\n', '')
            names = names.split(' ')
            if word in names:
                words[word]['status'] = 1
                print "Esta palabra existe en forenames: " + word
                break
    capitals.close()

    return words

def find_abreviaturas(words):

    for word, value in words.iteritems():
        with open('files/abreviaturas.csv', "r") as abreviaturas_file:
            abreviaturas_reader = csv.reader(abreviaturas_file)
            for abreviaturas_row in abreviaturas_reader:
                abreviatura = abreviaturas_row[0].replace('\n', '').lower().split(' ')
                if word in abreviatura and word != '':
                    words[word]['status'] = 1
                    print "Esta palabra existe en abreviaturas: " + word
                    break
    abreviaturas_file.close()

    return words


def find_acronimos(words):

    for word, value in words.iteritems():
        with open('files/acronimos.csv', "r") as acronims_file:
            acronims_reader = csv.reader(acronims_file)
            for acronims_row in acronims_reader:
                acronim = acronims_row[0].replace('\n', '').lower()
                if word in acronim and word != '':
                    words[word]['status'] = 1
                    print "Esta palabra existe en acronimos: " + word
                    break

    acronims_file.close()

    return words


def find_forenames(words):
    with open('files/forenames.txt') as forenames:
        forenames_reader = forenames.readlines()

    for word, value in words.iteritems():
        for names in forenames_reader:
            names = names.replace('\n', '')
            names = names.split(' ')
            if word in names:
                words[word]['status'] = 1
                print "Esta palabra existe en forenames: " + word
                break
    forenames.close()

    return words

def find_titles(words):

    with open('files/titles.txt') as titles:
        titles_reader = titles.readlines()

    for word, value in words.iteritems():
        for names in titles_reader:
            names = names.replace('\n', '').lower()
            if word == names:
                words[word]['status'] = 1
                print "Esta palabra existe en titulos: " + word
                break
    titles.close()

    return words

def find_person_names(words):

    with open('files/person-names.txt') as names_file:
        names_reader = names_file.readlines()

    for word, value in words.iteritems():
        for names in names_reader:
            names = names.replace('\n', '')
            if word == names:
                words[word]['status'] = 1
                print "Esta palabra existe en Person names: " + word
                break
    names_file.close()

    return words

def find_gentilicis(words):

    with open('files/gentilicis.txt') as gentilicis:
        gentilicis_reader = gentilicis.readlines()

    for word, value in words.iteritems():
        for names in gentilicis_reader:
            names = names.replace('\n', '')
            names = names.split(' ')
            if word in names:
                words[word]['status'] = 1
                print "Esta palabra existe en Gentilicios: " + word
                break
    gentilicis.close()

    return words


def INSERTION(A, cost=1):
  return cost


def DELETION(A, cost=1):
  return cost


def SUBSTITUTION(A, B, cost=1):
  return cost


Trace = collections.namedtuple("Trace", ["cost", "ops"])


class WagnerFischer(object):

    # Initializes pretty printer (shared across all class instances).
    pprinter = pprint.PrettyPrinter(width=75)

    def __init__(self, A, B, insertion=INSERTION, deletion=DELETION,
                 substitution=SUBSTITUTION):
        # Stores cost functions in a dictionary for programmatic access.
        self.costs = {"I": insertion, "D": deletion, "S": substitution}
        # Initializes table.
        self.asz = len(A)
        self.bsz = len(B)
        self._table = [[None for _ in range(self.bsz + 1)] for
                       _ in range(self.asz + 1)]
        # From now on, all indexing done using self.__getitem__.
        ## Fills in edges.
        self[0][0] = Trace(0, {"O"})  # Start cell.
        for i in range(1, self.asz + 1):
            self[i][0] = Trace(self[i - 1][0].cost + self.costs["D"](A[i - 1]),
                               {"D"})
        for j in range(1, self.bsz + 1):
            self[0][j] = Trace(self[0][j - 1].cost + self.costs["I"](B[j - 1]),
                               {"I"})
        ## Fills in rest.
        for i in range(len(A)):
            for j in range(len(B)):
                # Cleans it up in case there are more than one check for match
                # first, as it is always the cheapest option.
                if A[i] == B[j]:
                    self[i + 1][j + 1] = Trace(self[i][j].cost, {"M"})
                # Checks for other types.
                else:
                    costD = self[i][j + 1].cost + self.costs["D"](A[i])
                    costI = self[i + 1][j].cost + self.costs["I"](B[j])
                    costS = self[i][j].cost + self.costs["S"](A[i], B[j])
                    min_val = min(costI, costD, costS)
                    trace = Trace(min_val, set())
                    # Adds _all_ operations matching minimum value.
                    if costD == min_val:
                        trace.ops.add("D")
                    if costI == min_val:
                        trace.ops.add("I")
                    if costS == min_val:
                        trace.ops.add("S")
                    self[i + 1][j + 1] = trace
        # Stores optimum cost as a property.
        self.cost = self[-1][-1].cost

    def __repr__(self):
        return self.pprinter.pformat(self._table)

    def __iter__(self):
        for row in self._table:
            yield row

    def __getitem__(self, i):
        """
        Returns the i-th row of the table, which is a list and so
        can be indexed. Therefore, e.g.,  self[2][3] == self._table[2][3]
        """
        return self._table[i]

    # Stuff for generating alignments.

    def _stepback(self, i, j, trace, path_back):
        """
        Given a cell location (i, j) and a Trace object trace, generate
        all traces they point back to in the table
        """
        for op in trace.ops:
            if op == "M":
                yield i - 1, j - 1, self[i - 1][j - 1], path_back + ["M"]
            elif op == "I":
                yield i, j - 1, self[i][j - 1], path_back + ["I"]
            elif op == "D":
                yield i - 1, j, self[i - 1][j], path_back + ["D"]
            elif op == "S":
                yield i - 1, j - 1, self[i - 1][j - 1], path_back + ["S"]
            elif op == "O":
                return  # Origin cell, so we"re done.
            else:
                raise ValueError("Unknown op {!r}".format(op))

    def alignments(self):

        queue = collections.deque(self._stepback(self.asz, self.bsz,
                                                 self[-1][-1], []))
        while queue:
            (i, j, trace, path_back) = queue.popleft()
            if trace.ops == {"O"}:
                # We have reached the origin, the end of a reverse path, so
                # yield the list of edit operations in reverse.
                yield path_back[::-1]
                continue
            queue.extend(self._stepback(i, j, trace, path_back))

    def IDS(self):

        npaths = 0
        opcounts = collections.Counter()
        for alignment in self.alignments():
            # Counts edit types for this path, ignoring "M" (which is free).
            opcounts += collections.Counter(op for op in alignment if op != "M")
            npaths += 1
        # Averages over all paths.
        return collections.Counter({o: c / npaths for (o, c) in
                                    opcounts.items()})


def add_levensthein_cost(words):

    for word, value in words.iteritems():
        for key, scores in value.iteritems():
            if key == 'status':
                continue
            else:
                words[word][key]['Levensthein'] = WagnerFischer(word, key).cost
    #execfile( "levensthein-algorithm.py", variables )
    return words

def add_2_gram_percentage(words, sentence):

    with open('files/2gram.txt', 'r') as lm_file:
        lm = lm_file.readlines()

    n_words = 0
    pairs = sentence.split(' ')
    pairs = [w.translate(None, ''.join(['\n', '.', '!', '?'])) for w in pairs]

    first_value = words[pairs[0]]
    for index, w in enumerate(pairs):
        if index + 1 > len(pairs) - 1:
            break
        second_value = words[pairs[index+1]]
        key = pairs[index+1]
        for s_key, s_score in second_value.iteritems():
            if(s_key != 'status'):
                for f_key, f_score in first_value.iteritems():
                    if(f_key != 'status'):
                        for line in lm:
                            line = line.replace('\n', '').split(' ')
                            if (line[1] == f_key and line[2] == s_key):
                                words[key][s_key]['2gram'] = pow(10, float(line[0]))
                                break
        first_value = second_value

def add_3_gram_percentage(words, sentence):

    with open('files/3gram.txt', 'r') as lm_file:
        lm = lm_file.readlines()

    n_words = 0
    pairs = sentence.split(' ')
    pairs = [w.translate(None, ''.join(['\n', '.', '!', '?'])) for w in pairs]

    first_value = words[pairs[0]]
    for index, w in enumerate(pairs):
        if index + 2 > len(pairs) - 1:
            break
        second_value = words[pairs[index+1]]
        third_value = words[pairs[index+2]]
        key = pairs[index+2]
        for t_key,  t_score in third_value.iteritems():
            if(t_key != 'status'):
                for s_key, s_score in second_value.iteritems():
                    if(s_key != 'status'):
                        for f_key, f_score in first_value.iteritems():
                            if(f_key != 'status'):
                                for line in lm:
                                    line = line.replace('\n', '').split(' ')
                                    if (line[1] == f_key and line[2] == s_key and line[3] == t_key):
                                        words[key][t_key]['3gram'] = pow(10, float(line[0]))
                                        break
        first_value = second_value

def add_4_gram_percentage(words, sentence):

    with open('files/4gram.txt', 'r') as lm_file:
        lm = lm_file.readlines()

    n_words = 0
    pairs = sentence.split(' ')
    pairs = [w.translate(None, ''.join(['\n', '.', '!', '?'])) for w in pairs]

    first_value = words[pairs[0]]
    for index, w in enumerate(pairs):
        if index + 3 > len(pairs) - 1:
            break
        second_value = words[pairs[index+1]]
        third_value = words[pairs[index+2]]
        fourth_value = words[pairs[index+3]]
        key = pairs[index+3]
        for fourth_key, fourth_score in fourth_value.iteritems():
            if(fourth_key != 'status'):
                for third_key,  third_score in third_value.iteritems():
                    if(third_key != 'status'):
                        for second_key, second_score in second_value.iteritems():
                            if(second_key != 'status'):
                                for first_key, first_score in first_value.iteritems():
                                    if(first_key != 'status'):
                                        for line in lm:
                                            line = line.replace('\n', '').split(' ')
                                            if (line[1] == first_key and line[2] == second_key and line[3] == third_key and line[4] == fourth_key):
                                                words[key][fourth_key]['4gram'] = pow(10, float(line[0]))
                                                break
        first_value = second_value

def print_words(words):

    print json.dumps(words, indent=4, sort_keys=True)
    #print words

def make_transcription(words):

    for word, value in words.iteritems():
        for key, scores in value.iteritems():
            if key == 'status':
                continue
            else:
                perl_script =  subprocess.Popen(["perl", "transcriptor.pl",key], stdin=PIPE, stdout=PIPE, stderr=PIPE)
                words[word][key]['Phonetic'] = perl_script.communicate()[0]

if __name__ == "__main__":

    correct_sentence = "@anngeleescastro gracias grandullona...... Ja claro q te invito.. Y tu pagas vale?? Ja te quiero gracias!!".encode("utf-8")

    with open('files/tweets_dev100.txt', 'r') as tweets_file:
        tweets_info = tweets_file.readlines()

    tweets = [tweet.split('\t')[3] for tweet in tweets_info]

    sentence_test = tweets[57]

    words = to_dictionary(tweets[57])

    find_capitals(words)
    find_gentilicis(words)
    find_titles(words)
    find_forenames(words)
    find_acronimos(words)
    find_abreviaturas(words)
    find_person_names(words)

    hunspell_correction(words)
    add_levensthein_cost(words)
    #sudo ./ngram-count -text input.txt -order 4 -addsmooth 0 -lm 4gram.lm
    add_2_gram_percentage(words, sentence_test)
    add_3_gram_percentage(words, sentence_test)
    add_4_gram_percentage(words, sentence_test)

    make_transcription(words)

    print_words(words)





