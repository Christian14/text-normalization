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

class GeneticAlgorithm(object):

    def __init__(self, words, sentences, not_available, available):
        self.words = words
        self.sentences = sentences
        self.weights = []
        self.population = 1000
        self.scores = []
        self.corrected = {}
        self.answers = {}
        self.not_available = not_available
        self.available = available
        self.bigram = {}
        self.trigram = {}
        self.tetragram = {}
        self.final_words = []
        self.final_corrects = []
        self.final_score = 0
        self.final_weights = []

    def storeBigram(self):
        with open('files/bigram.txt', 'r') as myfile:
            for line in myfile:
                line = line.replace('\n', '').replace('\t', ' ').split(' ')
                if(len(line[0]) > 0):
                    if(self.bigram.has_key(line[1])):
                        self.bigram[line[1].lower()][line[2].lower()] = pow(10, float(line[0]))
                    else:
                        self.bigram[line[1].lower()] = {}
                        self.bigram[line[1].lower()][line[2].lower()] = pow(10, float(line[0]))

        myfile.close()

    def storeTrigram(self):
        with open('files/trigram.txt', 'r') as lm_file:
            lm = lm_file.readlines()

        for line in lm:
            line = line.replace('\n', '').replace('\t', ' ').split(' ')
            if (len(line[0]) > 0):
                if(self.trigram.has_key(line[1].lower())):
                    if(self.trigram[line[1].lower()].has_key(line[2].lower())):
                        self.trigram[line[1].lower()][line[2].lower()][line[3].lower()] = pow(10, float(line[0]))
                    else:
                        self.trigram[line[1].lower()][line[2].lower()] = {}
                        self.trigram[line[1].lower()][line[2].lower()][line[3].lower()] = pow(10, float(line[0]))
                else:
                    self.trigram[line[1].lower()] = {}
                    self.trigram[line[1].lower()][line[2].lower()] = {}
                    self.trigram[line[1].lower()][line[2].lower()][line[3].lower()] = pow(10, float(line[0]))

        lm_file.close()

    def storeTetragram(self):
        with open('files/tetragram.txt', 'r') as lm_file:
            lm = lm_file.readlines()

        for line in lm:
            line = line.replace('\n', '').replace('\t', ' ').split(' ')
            if (len(line[0]) > 0):
                if(self.tetragram.has_key(line[1])):
                    if(self.tetragram[line[1]].has_key(line[2])):
                        if(self.tetragram[line[1]][line[2]].has_key(line[3])):
                            self.tetragram[line[1]][line[2]][line[3]][line[4]] = pow(10, float(line[0]))
                        else:
                            self.tetragram[line[1]][line[2]][line[3]] = {}
                            self.tetragram[line[1]][line[2]][line[3]][line[4]] = pow(10, float(line[0]))
                    else:
                        self.tetragram[line[1]][line[2]] = {}
                        self.tetragram[line[1]][line[2]][line[3]] = {}
                        self.tetragram[line[1]][line[2]][line[3]][line[4]] = pow(10, float(line[0]))
                else:
                    self.tetragram[line[1]] = {}
                    self.tetragram[line[1]][line[2]] = {}
                    self.tetragram[line[1]][line[2]][line[3]] = {}
                    self.tetragram[line[1]][line[2]][line[3]][line[4]] = pow(10, float(line[0]))

        lm_file.close()

    def selectionReproduction(self):
        new_weigths = []
        while len(new_weigths) != self.population:
            k1 = int((random.random()*self.population))
            if(k1 > self.population-1):
                k1 = self.population-1

            k2 = int((random.random()*self.population))
            if(k2 > self.population-1):
                k2 = self.population-1

            k3 = int((random.random()*self.population))
            if(k3 > self.population-1):
                k3 = self.population-1

            best1 = self.tournament(self.corrected[k1]["fitness"], self.corrected[k2]["fitness"], self.corrected[k3]["fitness"], k1, k2 ,k3) #select the best of two

            k1 = int((random.random()*self.population))
            if(k1 > self.population-1):
                k1 = self.population-1

            k2 = int((random.random()*self.population))
            if(k2 > self.population-1):
                k2 = self.population-1

            k3 = int((random.random()*self.population))
            if(k3 > self.population-1):
                k3 = self.population-1

            best2 = self.tournament(self.corrected[k1]["fitness"], self.corrected[k2]["fitness"], self.corrected[k3]["fitness"], k1, k2 ,k3)

            alpha = int(round(random.random()*4))
            if alpha > 4:
                alpha = 4
            beta = random.random()
            element_one = best1[alpha]
            element_two = best2[alpha]
            new_one = element_one - beta*(element_one - element_two)
            new_two = element_two + beta*(element_one - element_two)
            best1[alpha] = new_one
            best2[alpha] = new_two

            new_weigths.append(best1)
            new_weigths.append(best2)

        self.weights = new_weigths

    def tournament(self, first, second, third, k1, k2 ,k3):
        if(first > second):
            if(first > third):
                return self.weights[k1]
            else:
                return self.weights[k3]
        else:
            if(second > third):
                return self.weights[k2]
            else:
                return self.weights[k3]

    def mutation(self):
        for index, weights in enumerate(self.weights):
            alpha = int(round(random.random()*5))
            if alpha > 4:
                alpha = 4
            self.weights[index][alpha] = random.random()
            factor = 1/sum(self.weights[index])
            for i, weight in enumerate(self.weights[index]):
                self.weights[index][i] = factor*self.weights[index][i]

    def generatePopulation(self):
        for i in range(self.population):
            self.corrected[i] = {}
            new_weigths = []
            for w in range(5):
                new_weigths.append(random.random())
            factor = 1/sum(new_weigths)
            for i, w in enumerate(new_weigths):
                new_weigths[i] = new_weigths[i]*factor

            self.weights.append(new_weigths)

    def addScores(self):
        special_characters = [',','\n','\t', ';', '*', '/', '&', '"','=','$', '(', ')','|']
        for tweet_id, tweets_info in self.words.iteritems():
            #print "ID:" + tweet_id
            sentence = self.sentences[tweet_id]
            sentence = sentence.replace("?"," ").replace("!"," ").replace("."," ").replace(":"," ").replace('"'," ").split(' ')
            sentence = [w.translate(None, ''.join(special_characters)) for w in sentence]
            sentence = filter(None, sentence)
            #print str(self.words[tweet_id])
            for we_index, weights in enumerate(self.weights):
                #ssprint "Pesos: " + str(weights) + "\n"
                self.corrected[we_index]["fitness"] = 0
                self.corrected[we_index][tweet_id] = {}
                for index, word in enumerate(sentence):
                    current_word_suggestions = []
                    if(len(word) > 0 and word in self.words[tweet_id]):
                        if(self.words[tweet_id][word]["status"] != 1):
                            score = 0
                            #print "Palabra: " + word
                            if(index == 0):
                                max_score = -1
                                for sug, scores in self.words[tweet_id][word]["suggestions"].iteritems():
                                    levensthein_score = scores['Levensthein']
                                    phonetic_score = scores['Phonetic']
                                    score = self.calculateScore(levensthein_score, phonetic_score, weights)
                                    #print "Sugerencia: " + sug
                                    #print "Levensthein: " + str(levensthein_score)
                                    #print "Phonetic: " + str(phonetic_score)
                                    #print "Score LevenstheinC y Fonema: "+ str(score)
                                    score += self.addBigram("<s>", sug.title(), weights[2])
                                    #print "Score Bigram: "+ str(score) + "\n"
                                    if(score > max_score):
                                        self.corrected[we_index][tweet_id][word] = sug
                                        max_score = score
                            else:
                                max_score = -1
                                if(self.corrected[we_index][tweet_id].has_key(sentence[index-1])):
                                    prev_word = self.corrected[we_index][tweet_id][sentence[index-1]]
                                    for sug, scores in self.words[tweet_id][word]["suggestions"].iteritems():
                                        levensthein_score = scores['Levensthein']
                                        phonetic_score = scores['Phonetic']
                                        score = self.calculateScore(levensthein_score, phonetic_score, weights)
                                        #print "Sugerencia: " + sug
                                        #print "Levensthein: " + str(levensthein_score)
                                        #print "Phonetic: " + str(phonetic_score)
                                        #print "Score LevenstheinC y Fonema: "+ str(score)
                                        score += self.addBigram(prev_word, sug, weights[2])
                                        #print "Plus Bigram Score: "+ str(score) + "\n"
                                        if(index > 1):
                                            if(self.corrected[we_index][tweet_id].has_key(sentence[index-2])):
                                                prev_prev_word = self.corrected[we_index][tweet_id][sentence[index-2]]
                                                score += self.addTrigram(prev_prev_word, prev_word, sug, weights[3])
                                                #print "Plus Trigram Score: "+ str(score)
                                        if(index > 2):
                                            if(self.corrected[we_index][tweet_id].has_key(sentence[index-3])):
                                                prev_prev_prev_word = self.corrected[we_index][tweet_id][sentence[index-3]]
                                                score += self.addTetragram(prev_prev_prev_word, prev_prev_word, prev_word, sug, weights[4])
                                                #print "Plus Tetragram Score: "+ str(score)
                                        if(score > max_score):
                                            self.corrected[we_index][tweet_id][word] = sug
                                            max_score = score

                        else:
                            self.corrected[we_index][tweet_id][word] = self.words[tweet_id][word]["correct"]
                    else:
                        self.corrected[we_index][tweet_id][word] = word

    def calculateScore(self, lev, phon, weights):
        return lev*weights[0] + phon*weights[1]

    def addBigram(self, first_word, second_word, bigram_weight):
        if(self.bigram.has_key(first_word) and self.bigram[first_word].has_key(second_word)):
            return bigram_weight*self.bigram[first_word][second_word]
        return 0

    def addTrigram(self, first_word, second_word, third_word, trigram_weight):
        if(self.trigram.has_key(first_word) and self.trigram[first_word].has_key(second_word) and self.trigram[first_word][second_word].has_key(third_word)):
            return trigram_weight*self.trigram[first_word][second_word][third_word]
        return 0

    def addTetragram(self, first_word, second_word, third_word, fourth_word, tetragram_weight):
        if(self.tetragram.has_key(first_word) and self.tetragram[first_word].has_key(second_word) and self.tetragram[first_word][second_word].has_key(third_word) and self.tetragram[first_word][second_word][third_word].has_key(fourth_word)):
            return tetragram_weight*self.tetragram[first_word][second_word][third_word][fourth_word]
        return 0

    def calculateFitness(self):
        with open('files/tweet-norm-test_annotated.txt', 'r') as tweets_file:
            tweets_info = tweets_file.readlines()

        n_corrected = 0
        n_words = 0
        evaluate = False

        for ind_weight, weights in enumerate(self.weights):
            #print "Peso: " + str(weights)
            sentence_words = []
            corrected_words = []
            for index, line in enumerate(tweets_info):
                words = line.replace('\n', '').replace('\t', '').replace('\r','').split(' ')
                if(len(words) == 3 and evaluate):
                    if(tweet.has_key(words[0])):
                        sentence_words.append(words[0])
                        corrected_words.append(tweet[words[0]])
                        print ("Palabra de la oracion: " + words[0])
                        print ("Palabra correcta: " + words[2])
                        print ("Palabra corregida por script: " + tweet[words[0]])

                    if(len(tweet) > 0 and tweet.get(words[0]) and tweet[words[0]] == words[2] or (words[1] == 1 and (tweets[words[0]] == words[0]))):
                        n_corrected += 1

                    if(words[1] != 2):
                        n_words += 1
                else:
                    if(words[0] in self.not_available):
                        evaluate = False
                    if(words[0] in self.available):
                        tweet = self.corrected[ind_weight][words[0]]
                        evaluate = True
                        #print "Tweet ID: " + words[0]
                        #print "Tweet" + str(tweet)

            self.corrected[ind_weight]["fitness"] = n_corrected/n_words
            if(self.final_score < n_corrected/n_words):
                self.final_score = n_corrected/n_words
                self.final_words = sentence_words
                self.final_corrects = corrected_words
                self.final_weight = self.weights[ind_weight]

            #print ("Pesos: " + str(weights) + "- Fitness: " + str(self.corrected[ind_weight]["fitness"]*100))
            #print ("Correctos: " + str(n_corrected) + "- Palabras: " + str(n_words))
            n_corrected = 0
            n_words = 0

def correct_words(aspell, spellchecker, words, add_to_dict=[]):

    if add_to_dict:
        for w in add_to_dict:
            spellchecker.add(w)

    for tweet_id, tweet_info in words.iteritems():
        for word, status in tweet_info.iteritems():
            word_without_repetitions = re.sub(r'(.+?)\1+', r'\1', word)
            if len(word_without_repetitions) > 0 and word_without_repetitions[0] not in ["#", "@"] and status["status"] != 1:
                #print "Palabra: " + str(word_without_repetitions) + " - status: " + str(status["status"])
                hunspell_ok = spellchecker.spell(word_without_repetitions)
                #print "Hunspell: " + str(hunspell_ok)
                aspell_ok = aspell.check(word_without_repetitions)
                #print "Aspell: " + str(aspell_ok)
                if not aspell_ok and not hunspell_ok:
                    hunspell_suggestions = spellchecker.suggest(word_without_repetitions)
                    #print "Hunspell sug: " + str(hunspell_suggestions)
                    aspell_suggestions = aspell.suggest(word_without_repetitions)
                    #print "Aspell sug: " + str(aspell_suggestions)
                    suggestions = hunspell_suggestions + aspell_suggestions
                    if suggestions:
                        for suggestion in suggestions:
                            words[tweet_id][word]["suggestions"][suggestion.replace('-','_')] = {"Levensthein": 0, "2gram": 0,"3gram": 0, "4gram": 0, "Phonetic": 0}
                    else:
                        words[tweet_id][word]["status"] = 1
                        words[tweet_id][word]["correct"] = word_without_repetitions
                else:
                    words[tweet_id][word]["status"] = 1
                    words[tweet_id][word]["correct"] = word_without_repetitions
    return words

def to_dictionary(tweets):
    dictionary = {}
    for key, tweet in tweets.iteritems():
        words = tweet.replace("?", " ").replace("!", " ").replace('"', " ").replace(".", " ").split(' ')
        special_characters = ['.', ',','\n','\t', ';', '*', '/', '&', '"','=','$', '(', ')','|', ':', "'"]
        info = {}
        for word in words:
            if(len(word) > 0):
                if(word[0] not in ["@", "#"]):
                    info[word.translate(None, ''.join(special_characters))] = {"status": 0, "suggestions": {}, "correct": ""}
                else:
                    info[word] = {"status": 1, "suggestions": {}, "correct": ""}
        dictionary[key] = info

    return dictionary

def find_capitals(words):
    with open('files/capitals.txt') as capitals:
        capitals_reader = capitals.readlines()

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            for names in capitals_reader:
                names = names.replace('\n', '')
                names = names.split(' ')
                if word == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.lower() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.lower()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.title() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.title()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
    capitals.close()

def find_abreviaturas(words):

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            with open('files/abreviaturas.csv', "r") as abreviaturas_file:
                abreviaturas_reader = csv.reader(abreviaturas_file)
                for abreviaturas_row in abreviaturas_reader:
                    abreviatura = abreviaturas_row[0].replace('\n', '').split(' ')
                    if word == abreviatura and word != '':
                        words[tweet_id][word]['status'] = 1
                        words[tweet_id][word]['correct'] = word
                        #print "Esta palabra existe en Neologismos: " + word
                        break
                    if word.title() == abreviatura and word != '':
                        words[tweet_id][word]['status'] = 1
                        words[tweet_id][word]['correct'] = word.title()
                        #print "Esta palabra existe en Neologismos: " + word
                        break
                    if word.lower() == abreviatura and word != '':
                        words[tweet_id][word]['status'] = 1
                        words[tweet_id][word]['correct'] = word.lower()
                        #print "Esta palabra existe en Neologismos: " + word
                        break
    abreviaturas_file.close()

def find_acronimos(words):

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            with open('files/acronimos.csv', "r") as acronims_file:
                acronims_reader = csv.reader(acronims_file)
                for acronims_row in acronims_reader:
                    acronim = acronims_row[0].replace('\n', '')
                    if word == acronim and word != '':
                        words[tweet_id][word]['status'] = 1
                        words[tweet_id][word]['correct'] = word
                        #print "Esta palabra existe en Neologismos: " + word
                        break
                    if word.lower() == acronim and word != '':
                        words[tweet_id][word]['status'] = 1
                        words[tweet_id][word]['correct'] = word.lower()
                        #print "Esta palabra existe en Neologismos: " + word
                        break
                    if word.upper() == acronim and word != '':
                        words[tweet_id][word]['status'] = 1
                        words[tweet_id][word]['correct'] = word.title()
                        #print "Esta palabra existe en Neologismos: " + word
                        break
    acronims_file.close()

def find_forenames(words):
    with open('files/forenames.txt') as forenames:
        forenames_reader = forenames.readlines()

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            for names in forenames_reader:
                names = names.replace('\n', '')
                names = names.split(' ')
                if word == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.lower() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.lower()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.title() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.title()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
    forenames.close()

def find_titles(words):

    with open('files/titles.txt') as titles:
        titles_reader = titles.readlines()

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            for names in titles_reader:
                names = names.replace('\n', '')
                if word == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.lower() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.lower()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.title() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.title()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
    titles.close()

def find_person_names(words):

    with open('files/person-names.txt') as names_file:
        names_reader = names_file.readlines()

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            for names in names_reader:
                names = names.replace('\n', '')
                if word == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word
                    #print "Esta palabra existe en Personas normal: " + word
                    break
    names_file.close()

def find_gentilicis(words):

    with open('files/gentilicis.txt') as gentilicis:
        gentilicis_reader = gentilicis.readlines()

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            for names in gentilicis_reader:
                names = names.replace('\n', '')
                names = names.split(' ')
                if word.lower() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.lower()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word.title() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.title()
                    #print "Esta palabra existe en Neologismos: " + word
                    break
                if word == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word
                    #print "Esta palabra existe en Neologismos: " + word
                    break
    gentilicis.close()

def find_neologism(words):

    with open('files/neologism.txt') as neo_file:
        names_reader = neo_file.readlines()

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            for names in names_reader:
                names = names.replace('\n', '')
                if word.lower() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.lower()
                    #print "Esta palabra existe en Neologismos minusculas: " + word.lower()
                    break
                if word.title() == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word.title()
                    #print "Esta palabra existe en Neologismos mayusculas: " + word.title()
                    break
                if word == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    words[tweet_id][word]['correct'] = word
                    #print "Esta palabra existe en Neologismos normal: " + word
                    break
    neo_file.close()

def add_levensthein_cost(words):
    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            for suggestion, scores in word_info["suggestions"].iteritems():
                words[tweet_id][word]["suggestions"][suggestion]["Levensthein"] = WagnerFischer(word, suggestion).cost

def make_transcription(words):

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            perl_script_1 =  subprocess.Popen(["perl", "transcriptor.pl", word], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            transform_word = perl_script_1.communicate()[0]
            for suggestion, scores in word_info["suggestions"].iteritems():
                perl_script_2 =  subprocess.Popen(["perl", "transcriptor.pl",suggestion], stdin=PIPE, stdout=PIPE, stderr=PIPE)
                words[tweet_id][word]["suggestions"][suggestion]['Phonetic'] = WagnerFischer(transform_word, perl_script_2.communicate()[0]).cost

def normalize_cost(words):
    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            max_phonetic = -1
            max_levensthein = -1
            #print "Palabra: " + word
            for suggestion, scores in word_info["suggestions"].iteritems():
                if(max_phonetic < int(words[tweet_id][word]["suggestions"][suggestion]['Phonetic'])):
                    max_phonetic = int(words[tweet_id][word]["suggestions"][suggestion]['Phonetic'])
                if(max_levensthein < int(words[tweet_id][word]["suggestions"][suggestion]['Levensthein'])):
                    max_levensthein = int(words[tweet_id][word]["suggestions"][suggestion]['Levensthein'])
            #print "Max levensthein: " + str(max_levensthein)
            #print "Max phonetic: " + str(max_phonetic)

            for suggestion, scores in word_info["suggestions"].iteritems():
                phonetic = int(words[tweet_id][word]["suggestions"][suggestion]['Phonetic'])
                levensthein = int(words[tweet_id][word]["suggestions"][suggestion]['Levensthein'])
                #print "Sugerencia: " + suggestion + " - Phonetic: " + str(phonetic) + " - Levensthein: " + str(levensthein)
                if(max_phonetic != 0):
                    words[tweet_id][word]["suggestions"][suggestion]['Phonetic'] = (max_phonetic - phonetic)/max_phonetic
                else:
                    words[tweet_id][word]["suggestions"][suggestion]['Phonetic'] = phonetic

                if(max_levensthein != 0):
                    words[tweet_id][word]["suggestions"][suggestion]['Levensthein'] = (max_levensthein - levensthein)/max_levensthein
                else:
                    words[tweet_id][word]["suggestions"][suggestion]['Levensthein'] = levensthein

def main():
    with open('files/tweets_test.txt', 'r') as tweets_file:
        tweets_info = tweets_file.readlines()

    tweets = {}
    sentences = {}
    not_available = []
    available = []

    for index,tweet in enumerate(tweets_info):
        info = tweet.split('\t')
        info[3] = info[3].replace("\n","")
        if(info[3] != "Not Available"):
            tweets[info[0]] = info[3]
            sentences[info[0]] = info[3]
            available.append(info[0])
        else:
            not_available.append(info[0])

    words = to_dictionary(tweets)
    find_capitals(words)
    find_gentilicis(words)
    find_titles(words)
    find_forenames(words)
    find_acronimos(words)
    find_abreviaturas(words)
    find_person_names(words)
    find_neologism(words)

    words = correct_words(aspell, spellchecker, words)
    add_levensthein_cost(words)
    make_transcription(words)
    normalize_cost(words)

    # for tweet_id, tweet_info in words.iteritems():
    #     for word, words_info in tweet_info.iteritems():
    #         print "Palabra: " + word + " - Estado: " + str(words_info["status"])
    #         print "Palabra Corregida: " + str(words_info["correct"])
    #         print "Sugerencias: "
    #         for sug, scr in words_info["suggestions"].iteritems():
    #             print sug
    #             print "Levensthein: " + str(scr['Levensthein'])
    #             print "Phonetic: " + str(scr['Phonetic'])

    #SRILM sudo ./ngram-count -text corpus-billion.txt -order 4 -addsmooth 0 -lm billion.lm

    GA = GeneticAlgorithm(words, sentences, not_available, available)

    GA.generatePopulation()
    GA.storeBigram()
    GA.storeTrigram()
    GA.storeTetragram()

    for i in range(0, 100):
        GA.addScores()
        GA.calculateFitness()
        GA.selectionReproduction()
        GA.mutation()

    print str(GA.final_weight)
    print str(GA.final_score)

    #for index, word in enumerate(self.final_words):
        #print word + " - " + self.final_corrects[index]

main()
