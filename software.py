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
import random
import operator
import numpy as np, numpy.random
import re

spellchecker = hunspell.HunSpell('/usr/share/hunspell/es_ES.dic', '/usr/share/hunspell/es_ES.aff')

aspell = aspell.Speller('lang', 'es')

def INSERTION(A, cost=1):
  return cost


def DELETION(A, cost=1):
  return cost


def SUBSTITUTION(A, B, cost=1):
  return cost


Trace = collections.namedtuple("Trace", ["cost", "ops"])


class WagnerFischer(object):

    pprinter = pprint.PrettyPrinter(width=75)

    def __init__(self, A, B, insertion=INSERTION, deletion=DELETION,
                 substitution=SUBSTITUTION):
        self.costs = {"I": insertion, "D": deletion, "S": substitution}
        self.asz = len(A)
        self.bsz = len(B)
        self._table = [[None for _ in range(self.bsz + 1)] for
                       _ in range(self.asz + 1)]

        self[0][0] = Trace(0, {"O"})  # Start cell.
        for i in range(1, self.asz + 1):
            self[i][0] = Trace(self[i - 1][0].cost + self.costs["D"](A[i - 1]),
                               {"D"})
        for j in range(1, self.bsz + 1):
            self[0][j] = Trace(self[0][j - 1].cost + self.costs["I"](B[j - 1]),
                               {"I"})
        for i in range(len(A)):
            for j in range(len(B)):
                if A[i] == B[j]:
                    self[i + 1][j + 1] = Trace(self[i][j].cost, {"M"})
                else:
                    costD = self[i][j + 1].cost + self.costs["D"](A[i])
                    costI = self[i + 1][j].cost + self.costs["I"](B[j])
                    costS = self[i][j].cost + self.costs["S"](A[i], B[j])
                    min_val = min(costI, costD, costS)
                    trace = Trace(min_val, set())

                    if costD == min_val:
                        trace.ops.add("D")
                    if costI == min_val:
                        trace.ops.add("I")
                    if costS == min_val:
                        trace.ops.add("S")
                    self[i + 1][j + 1] = trace

        self.cost = self[-1][-1].cost

    def __repr__(self):
        return self.pprinter.pformat(self._table)

    def __iter__(self):
        for row in self._table:
            yield row

    def __getitem__(self, i):
        return self._table[i]


    def _stepback(self, i, j, trace, path_back):
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
                return
            else:
                raise ValueError("Unknown op {!r}".format(op))

    def alignments(self):

        queue = collections.deque(self._stepback(self.asz, self.bsz,
                                                 self[-1][-1], []))
        while queue:
            (i, j, trace, path_back) = queue.popleft()
            if trace.ops == {"O"}:
                yield path_back[::-1]
                continue
            queue.extend(self._stepback(i, j, trace, path_back))

    def IDS(self):

        npaths = 0
        opcounts = collections.Counter()
        for alignment in self.alignments():
            opcounts += collections.Counter(op for op in alignment if op != "M")
            npaths += 1
        return collections.Counter({o: c / npaths for (o, c) in
                                    opcounts.items()})

class Selector(object):

    def __init__(self, words):
        self.words = words
        self.bigram = {}
        self.trigram = {}
        self.tetragram = {}
        self.corrected = {}
        self.weights = [1, 1, 1, 1, 1]

    def storeBigram(self):
        with open('files/bigram_json.txt') as data_file:
            self.bigram = json.load(data_file)

    def storeTrigram(self):
        with open('files/trigram_json.txt') as data_file:
            self.trigram = json.load(data_file)

    def storeTetragram(self):
        with open('files/tetragram_json.txt') as data_file:
            self.tetragram = json.load(data_file)

    def choose(self):
        special_characters = [',','\n','\t', ';', '*', '/', '&', '"','=','$', '(', ')','|']
        prev_word = ''
        prev_prev_word = ''
        prev_prev_prev_word = ''
        for word, word_info in sorted(self.words.items(), key=lambda kv: kv[1]['index']):
            index = 0
            if(len(word) > 0):
                if(self.words[word]["status"] != 1):
                    score = 0
                    if(index == 0):
                        max_score = -1
                        for sug, scores in self.words[word]["suggestions"].iteritems():
                            levensthein_score = scores['Levensthein']
                            phonetic_score = scores['Phonetic']
                            score = self.calculateScore(levensthein_score, phonetic_score)
                            score += self.addBigram("<s>", sug.title())
                            if(score > max_score):
                                self.corrected[word] = sug
                                max_score = score
                    else:
                        max_score = -1
                        for sug, scores in self.words[word]["suggestions"].iteritems():
                            levensthein_score = scores['Levensthein']
                            phonetic_score = scores['Phonetic']
                            score = self.calculateScore(levensthein_score, phonetic_score, weights)
                            score += self.addBigram(prev_word, sug)
                            if(index > 1):
                                score += self.addTrigram(prev_prev_word, prev_word, sug)
                            if(index > 2):
                                score += self.addTetragram(prev_prev_prev_word, prev_prev_word, prev_word, sug)
                            if(score > max_score):
                                self.corrected[word] = sug
                                max_score = score
                else:
                    self.corrected[word] = self.words[word]["correct"]
            else:
                self.corrected[word] = word
            prev_word = word
            prev_prev_word = prev_word
            prev_prev_prev_word = prev_prev_word
            index = index + 1

    def calculateScore(self, lev, phon):
        return lev*self.weights[0] + phon*self.weights[1]

    def addBigram(self, first_word, second_word):
        if(self.bigram.has_key(first_word) and self.bigram[first_word].has_key(second_word)):
            return self.weights[2]*self.bigram[first_word][second_word]
        return 0

    def addTrigram(self, first_word, second_word, third_word):
        if(self.trigram.has_key(first_word) and self.trigram[first_word].has_key(second_word) and self.trigram[first_word][second_word].has_key(third_word)):
            return self.weights[3]*self.trigram[first_word][second_word][third_word]
        return 0

    def addTetragram(self, first_word, second_word, third_word, fourth_word):
        if(self.tetragram.has_key(first_word) and self.tetragram[first_word].has_key(second_word) and self.tetragram[first_word][second_word].has_key(third_word) and self.tetragram[first_word][second_word][third_word].has_key(fourth_word)):
            return self.weights[4]*self.tetragram[first_word][second_word][third_word][fourth_word]
        return 0

def correct_words(words, add_to_dict=[]):
    if add_to_dict:
        for w in add_to_dict:
            spellchecker.add(w)

    for word, status in words.iteritems():
        word_without_repetitions = re.sub(r'(.+?)\1+', r'\1', word)
        if len(word_without_repetitions) > 0 and word_without_repetitions[0] not in ["#", "@"] and status["status"] != 1:
            hunspell_ok = spellchecker.spell(word_without_repetitions)
            aspell_ok = aspell.check(word_without_repetitions)
            if not aspell_ok and not hunspell_ok:
                hunspell_suggestions = spellchecker.suggest(word_without_repetitions)
                aspell_suggestions = aspell.suggest(word_without_repetitions)
                suggestions = hunspell_suggestions + aspell_suggestions
                if suggestions:
                    for suggestion in suggestions:
                        words[word]["suggestions"][suggestion.replace('-','_')] = {"Levensthein": 0, "2gram": 0,"3gram": 0, "4gram": 0, "Phonetic": 0}
                else:
                    words[word]["status"] = 1
                    words[word]["correct"] = word_without_repetitions
            else:
                words[word]["status"] = 1
                words[word]["correct"] = word_without_repetitions
    return words

def to_dictionary(sentence):
    words = sentence.replace("?", " ").replace("!", " ").replace('"', " ").replace(".", " ").split(' ')
    special_characters = ['.', ',','\n','\t', ';', '*', '/', '&', '"','=','$', '(', ')','|', ':', "'"]
    info = {}
    index = 0
    for word in words:
        if(len(word) > 0):
            if(word[0] not in ["@", "#"]):
                info[word.translate(None, ''.join(special_characters))] = {"status": 0, "suggestions": {}, "correct": "", "index": index}
            else:
                info[word] = {"status": 1, "suggestions": {}, "correct": "", "index": index}
        index = index + 1
    return info

def find_capitals(words):
    with open('files/capitals.txt') as capitals:
        capitals_reader = capitals.readlines()

    for word, word_info in words.iteritems():
        for names in capitals_reader:
            names = names.replace('\n', '')
            names = names.split(' ')
            if word in names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word
                #print "Esta palabra existe en Neologismos: " + word
                break
            if word.lower() in names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.lower()
                #print "Esta palabra existe en Neologismos: " + word
                break
            if word.title() in names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.title()
                #print "Esta palabra existe en Neologismos: " + word
                break
    capitals.close()

def find_abreviaturas(words):

    for word, word_info in words.iteritems():
        with open('files/abreviaturas.csv', "r") as abreviaturas_file:
            abreviaturas_reader = csv.reader(abreviaturas_file)
            for abreviaturas_row in abreviaturas_reader:
                abreviatura = abreviaturas_row[0].replace('\n', '').split(' ')
                if word in abreviatura and word != '':
                    words[word]['status'] = 1
                    words[word]['correct'] = word
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.title() in abreviatura and word != '':
                    words[word]['status'] = 1
                    words[word]['correct'] = word.title()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.lower() in abreviatura and word != '':
                    words[word]['status'] = 1
                    words[word]['correct'] = word.lower()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
    abreviaturas_file.close()

def find_acronimos(words):

    for word, word_info in words.iteritems():
        with open('files/acronimos.csv', "r") as acronims_file:
            acronims_reader = csv.reader(acronims_file)
            for acronims_row in acronims_reader:
                acronim = acronims_row[0].replace('\n', '')
                if word == acronim and word != '':
                    words[word]['status'] = 1
                    words[word]['correct'] = word
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.lower() == acronim and word != '':
                    words[word]['status'] = 1
                    words[word]['correct'] = word.lower()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.upper() == acronim and word != '':
                    words[word]['status'] = 1
                    words[word]['correct'] = word.title()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
    acronims_file.close()

def find_forenames(words):
    with open('files/forenames.txt') as forenames:
        forenames_reader = forenames.readlines()

    for word, word_info in words.iteritems():
        for names in forenames_reader:
            names = names.replace('\n', '')
            names = names.split(' ')
            if word in names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word
                #print "Esta palabra existe en Neologismos: " + word
                break
            if word.lower() in names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.lower()
                #print "Esta palabra existe en Neologismos: " + word
                break
            if word.title() in names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.title()
                #print "Esta palabra existe en Neologismos: " + word
                break
    forenames.close()

def find_titles(words):

    with open('files/titles.txt') as titles:
        titles_reader = titles.readlines()

    for word, word_info in words.iteritems():
        for names in titles_reader:
            names = names.replace('\n', '')
            if word == names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word
                #print "Esta palabra existe en Neologismos: " + word
                break
            if word.lower() == names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.lower()
                #print "Esta palabra existe en Neologismos: " + word
                break
            if word.title() == names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.title()
                #print "Esta palabra existe en Neologismos: " + word
                break
    titles.close()

def find_person_names(words):

    with open('files/person-names.txt') as names_file:
        names_reader = names_file.readlines()

    for word, word_info in words.iteritems():
        for names in names_reader:
            names = names.replace('\n', '')
            if word == names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word
                #print "Esta palabra existe en Personas normal: " + word
                break
            if word.lower() == names.lower() and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.capitalize()
                #print "Esta palabra existe en Personas normal: " + word
                break
    names_file.close()

def find_gentilicis(words):

    with open('files/gentilicis.txt') as gentilicis:
        gentilicis_reader = gentilicis.readlines()

    for word, word_info in words.iteritems():
        for names in gentilicis_reader:
            names = names.replace('\n', '')
            names = names.split(' ')
            if word.lower() in names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.lower()
                #print "Esta palabra existe en Neologismos: " + word
                break
            if word.title() in names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.title()
                #print "Esta palabra existe en Neologismos: " + word
                break
            if word in names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word
                #print "Esta palabra existe en Neologismos: " + word
                break
    gentilicis.close()

def find_neologism(words):

    with open('files/neologism.txt') as neo_file:
        names_reader = neo_file.readlines()

    for word, word_info in words.iteritems():
        for names in names_reader:
            names = names.replace('\n', '')
            if word.lower() == names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.lower()
                #print "Esta palabra existe en Neologismos minusculas: " + word.lower()
                break
            if word.capitalize() == names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word.capitalize()
                #print "Esta palabra existe en Neologismos mayusculas: " + word.title()
                break
            if word == names and word != '':
                words[word]['status'] = 1
                words[word]['correct'] = word
                #print "Esta palabra existe en Neologismos normal: " + word
                break
    neo_file.close()

def add_levensthein_cost(words):
    for word, word_info in words.iteritems():
        for suggestion, scores in word_info["suggestions"].iteritems():
            words[word]["suggestions"][suggestion]["Levensthein"] = WagnerFischer(word, suggestion).cost

def make_transcription(words):
    for word, word_info in words.iteritems():
        perl_script_1 =  subprocess.Popen(["perl", "transcriptor.pl", word], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        transform_word = perl_script_1.communicate()[0]
        for suggestion, scores in word_info["suggestions"].iteritems():
            perl_script_2 =  subprocess.Popen(["perl", "transcriptor.pl",suggestion], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            words[word]["suggestions"][suggestion]['Phonetic'] = WagnerFischer(transform_word, perl_script_2.communicate()[0]).cost

def normalize_cost(words):
    for word, word_info in words.iteritems():
        max_phonetic = -1
        max_levensthein = -1
        for suggestion, scores in word_info["suggestions"].iteritems():
            if(max_phonetic < int(words[word]["suggestions"][suggestion]['Phonetic'])):
                max_phonetic = int(words[word]["suggestions"][suggestion]['Phonetic'])
            if(max_levensthein < int(words[word]["suggestions"][suggestion]['Levensthein'])):
                max_levensthein = int(words[word]["suggestions"][suggestion]['Levensthein'])

        for suggestion, scores in word_info["suggestions"].iteritems():
            phonetic = int(words[word]["suggestions"][suggestion]['Phonetic'])
            levensthein = int(words[word]["suggestions"][suggestion]['Levensthein'])
            if(max_phonetic != 0):
                words[word]["suggestions"][suggestion]['Phonetic'] = (max_phonetic - phonetic)/max_phonetic
            else:
                words[word]["suggestions"][suggestion]['Phonetic'] = phonetic

            if(max_levensthein != 0):
                words[word]["suggestions"][suggestion]['Levensthein'] = (max_levensthein - levensthein)/max_levensthein
            else:
                words[word]["suggestions"][suggestion]['Levensthein'] = levensthein

def main():
    sentence = 'Hola komo stan amigxs'
    words = to_dictionary(sentence)
    ordered_words = {}
    find_capitals(words)
    find_gentilicis(words)
    find_titles(words)
    find_forenames(words)
    find_acronimos(words)
    find_abreviaturas(words)
    find_person_names(words)
    find_neologism(words)
    words = correct_words(words)
    add_levensthein_cost(words)
    make_transcription(words)
    normalize_cost(words)

    selector = Selector(words)
    selector.storeBigram()
    selector.storeTrigram()
    selector.storeTetragram()

    #selector.choose()
    #for word, accurate in selector.corrected.iteritems():
     #   print "Palabra: " + word
     #   print "Corregido: " + accurate
main()
