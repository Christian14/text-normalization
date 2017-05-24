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

    def __init__(self, words, sentences):
        self.words = words
        self.sentences = sentences
        self.weights = []
        self.population = 1
        self.scores = []
        self.corrected = {}
        self.answers = {}

        self.generatePopulation()

        for i in range(2):
            self.addScores()
            self.calculateFitness()
            self.selectionReproduction()
            self.mutation()

    def selectionReproduction(self):
        for index, weights in enumerate(self.weights):
            if(index+1 < len(self.weights)):
                alpha = int(round(random.random()*5))
                if alpha >= 5:
                    alpha = 4
                beta = random.random()
                element_one = weights[alpha]
                element_two = self.weights[index+1][alpha]
                new_one = element_one - beta*[element_one - element_two]
                new_two = element_two + beta*[element_one - element_two]
                self.weights[index][alpha] = new_one
                self.weights[index+1][alpha] = new_two

    def mutation(self):
        for index, weights in enumerate(self.weights):
            alpha = int(round(random.random()*5))
            if alpha >= 5:
                alpha = 4
            self.weights[index][alpha] = random.random()

    def generatePopulation(self):
        for i in range(self.population):
            weights = []
            for i in range(5):
                weights.append(random.random())
            self.weights.append(weights)

    def addScores(self):
        special_characters = ['.', ',', '!', '?','\n','\t', ';', '*', '/', '&', '"','=','$', '(', ')','|', ':']
        for tweet_id, tweets_info in self.words.iteritems():
            #print "ID: " + tweet_id
            sentence = self.sentences[tweet_id]
            sentence = sentence.split(' ')
            sentence = [w.translate(None, ''.join(special_characters)) for w in sentence]
            for we_index, weights in enumerate(self.weights):
                self.corrected[we_index] = {"tweets": {}, "fitness": 0}
                self.corrected[we_index]["tweets"][tweet_id] = {}
                score = 0
                for index, word in enumerate(sentence):
                    first_word = []
                    second_word = []
                    third_word = []
                    fourth_word = []
                    if index < len(sentence):
                        first_value = sentence[index]
                    else:
                        first_value = ""
                    if index + 1 < len(sentence):
                        second_value = sentence[index+1]
                    else:
                        second_value = ""
                    if index + 2 < len(sentence):
                        third_value = sentence[index+2]
                    else:
                        third_value = ""
                    if index + 3 < len(sentence):
                        fourth_value = sentence[index+3]
                    else:
                        fourth_value = ""
                    if(len(first_value) > 0 and len(second_value) > 0 and first_value[0] != "@" and second_value[0] != "@" and first_value[0] != "#" and second_value[0] != "#"):
                    
                        if(len(first_value) > 0 and self.words[tweet_id][first_value]["suggestions"]):
                            if(len(self.words[tweet_id][first_value]["suggestions"]) < 1 ):
                                first_word.append = first_value
                            else:
                                for sug, scr in self.words[tweet_id][first_value]["suggestions"].iteritems():
                                    first_word.append(sug)
                        else:
                            first_word.append(first_value)

                        if(len(second_value) > 0 and self.words[tweet_id][second_value]["suggestions"]):
                            if(len(self.words[tweet_id][second_value]["suggestions"]) < 1 ):
                                second_word.append = second_value
                            else:
                                for sug, scr in self.words[tweet_id][second_value]["suggestions"].iteritems():
                                    second_word.append(sug)
                        else:
                            second_word.append(second_value)

                        if(len(third_value) > 0 and self.words[tweet_id][third_value]["suggestions"]):
                            if(len(self.words[tweet_id][third_value]["suggestions"]) < 1 ):
                                third_word.append = third_value
                            else:
                                for sug, scr in self.words[tweet_id][third_value]["suggestions"].iteritems():
                                    third_word.append(sug)
                        else:
                            third_word.append(third_value)

                        if(len(fourth_value) > 0 and self.words[tweet_id][fourth_value]["suggestions"]):
                            if(len(self.words[tweet_id][fourth_value]["suggestions"]) < 1 ):
                                fourth_word.append = fourth_value
                            else:
                                for sug, scr in self.words[tweet_id][fourth_value]["suggestions"].iteritems():
                                    fourth_word.append(sug)
                        else:
                            fourth_word.append(fourth_value)

                        #print "Palabra: " + str(first_value)
                        #print "Sugerencias: " + str(first_word)

                        score, best_fword = self.addBigram(first_word, second_word, weights, self.words[tweet_id][first_value]["suggestions"])
                        if len(best_fword) > 0:
                            first_word[0] = best_fword
                        else:
                            max_scr = -1
                            if(len(self.words[tweet_id][first_value]["suggestions"]) < 1 ):
                                best_fword = first_value
                            else:
                                for ind, fw_sug in enumerate(first_word):
                                    scr = 0
                                    calculated_word = self.words[tweet_id][first_value]["suggestions"][fw_sug]
                                    scr = self.calculateScore(calculated_word, weights)
                                    if(scr > max_scr):
                                        first_word = [fw_sug]
                                        best_fword = fw_sug

                        self.corrected[we_index]["tweets"][tweet_id][word] = best_fword

                        score, best_fword = self.addTrigram(first_word, second_word, third_word, weights[2], score)

                        if len(best_fword) > 0:
                            first_word[0] = best_fword
                        else:
                            first_word = [first_word[0]]

                        score, best_fword = self.addTetragram(first_word, second_word, third_word, fourth_word, weights[3], score)

    def calculateScore(self, scores, weights):
        return scores['Levensthein']*weights[0] + scores['Phonetic']*weights[4]

    def addBigram(self, fwords, swords, weights, word_scores):
        with open('files/2gram.txt', 'r') as lm_file:
            lm = lm_file.readlines()
        best_fword = ""
        max_score = -10000
        for f_word in fwords:
            for s_word in swords:
                for line in lm:
                    line = line.replace('\n', '').split(' ')
                    if (line[1] == f_word and line[2] == s_word):
                        score = weights[1]*pow(10, float(line[0])) + self.calculateScore(word_scores[f_word], weights)
                        if(score > max_score):
                            max_score = score
                            best_fword = f_word
        return max_score, best_fword

    def addTrigram(self, fwords, swords, twords, weight, current_score):
        with open('files/3gram.txt', 'r') as lm_file:
            lm = lm_file.readlines()
        best_fword = ""
        max_score = -10000
        for f_word in fwords:
            for s_word in swords:
                for t_word in twords:
                    for line in lm:
                        line = line.replace('\n', '').split(' ')
                        if (line[1] == f_word and line[2] == s_word and line[3] == t_word):
                            score = weight*pow(10, float(line[0])) + current_score
                            if(score > max_score):
                                max_score = score
                                best_fword = f_word
        return max_score, best_fword

    def addTetragram(self, fwords, swords, twords, fowords, weight, current_score):
        with open('files/4gram.txt', 'r') as lm_file:
            lm = lm_file.readlines()
        best_fword = ""
        max_score = -10000
        for f_word in fwords:
            for s_word in swords:
                for t_word in twords:
                    for fo_word in fowords:
                        for line in lm:
                            line = line.replace('\n', '').split(' ')
                            if (line[1] == f_word and line[2] == s_word and line[3] == t_word and line[4] == fo_word):
                                score = weight*pow(10, float(line[0])) + current_score
                                if(score > max_score):
                                    max_score = score
                                    best_fword = f_word
        return max_score, best_fword

    def calculateFitness(self):
        with open('files/tweet-norm-dev100_annotated.txt', 'r') as tweets_file:
            tweets_info = tweets_file.readlines()

        n_corrected = 0
        n_words = 0

        for ind_weight, weights in enumerate(self.weights):
            for index, line in enumerate(tweets_info):
                words = line.replace('\n', '').replace('\t', '').replace('\r','').split(' ')

                if(len(words) == 3):
                    print "Palabra Oracion Corregida:" + str(words[2])
                    print "Palabra Corregida Script:" + str(tweet[words[0]])
                    if(len(tweet) > 0 and tweet.get(words[0]) and tweet[words[0]].lower() == words[2].lower()):
                        n_corrected += 1 
                    n_words += 1
                else:
                    tweet = self.corrected[ind_weight]["tweets"][words[0]]
                    print "Tweet Corregido:" + str(tweet)
            self.corrected[ind_weight]["fitness"] = n_corrected/n_words

            print "Correctas: " + str(n_corrected)
            print "Palabras: " + str(n_words)

def correct_words(aspell, spellchecker, words, add_to_dict=[]):

    if add_to_dict:
        for w in add_to_dict:
            spellchecker.add(w)
    
    for tweet_id, tweet_info in words.iteritems():
        for word, status in tweet_info.iteritems():
            ok = spellchecker.spell(word)
            if not ok and status["status"] != 1:
                w_without_repetitions = "".join(OrderedDict.fromkeys(word))
                suggestions_with_repetitions = spellchecker.suggest(word)
                suggestion_without_repetitions = spellchecker.suggest(w_without_repetitions)
                aspell_suggestion = aspell.suggest(word)
                aspell_suggestion_without_repetitions = aspell.suggest(w_without_repetitions)

                suggestions = suggestions_with_repetitions + suggestion_without_repetitions + aspell_suggestion + aspell_suggestion_without_repetitions

                if suggestions:
                    for suggestion in suggestions:
                        words[tweet_id][word]["suggestions"][suggestion] = {"Levensthein": 0, "2gram": 0,"3gram": 0, "4gram": 0, "Phonetic": 0} 
                else:
                    words[tweet_id][word]["status"] = 2
            else:
                words[tweet_id][word]["status"] = 1

    return words

def to_dictionary(tweets):
    dictionary = {}
    for key, tweet in tweets.iteritems():
        words = tweet.split(' ')
        special_characters = ['.', ',', '!', '?','\n','\t', ';', '*', '/', '&', '"','=','$', '(', ')','|', ':']
        info = {}
        for word in words:
            if(word[0]) != "@":
                info[word.translate(None, ''.join(special_characters))] = {"status": 0, "suggestions": {}}
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
                    print "Esta palabra existe en forenames: " + word
                    break
    capitals.close()

def find_abreviaturas(words):

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            with open('files/abreviaturas.csv', "r") as abreviaturas_file:
                abreviaturas_reader = csv.reader(abreviaturas_file)
                for abreviaturas_row in abreviaturas_reader:
                    abreviatura = abreviaturas_row[0].replace('\n', '').lower().split(' ')
                    if word == abreviatura and word != '':
                        words[tweet_id][word]['status'] = 1
                        print "Esta palabra existe en abreviaturas: " + word
                        break
    abreviaturas_file.close()

def find_acronimos(words):

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            with open('files/acronimos.csv', "r") as acronims_file:
                acronims_reader = csv.reader(acronims_file)
                for acronims_row in acronims_reader:
                    acronim = acronims_row[0].replace('\n', '').lower()
                    if word == acronim and word != '':
                        words[tweet_id][word]['status'] = 1
                        print "Esta palabra existe en acronimos: " + word
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
                if word == names:
                    words[tweet_id][word]['status'] = 1
                    print "Esta palabra existe en forenames: " + word
                    break
    forenames.close()

def find_titles(words):

    with open('files/titles.txt') as titles:
        titles_reader = titles.readlines()

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            for names in titles_reader:
                names = names.replace('\n', '').lower()
                if word == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    print "Esta palabra existe en titulos: " + word
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
                    print "Esta palabra existe en Person names: " + word
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
                if word == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    print "Esta palabra existe en Gentilicios: " + word
                    break
    gentilicis.close()

def find_neologism(words):

    with open('files/neologism.txt') as neo_file:
        names_reader = neo_file.readlines()

    for tweet_id, tweets_info in words.iteritems():
        for word, word_info in tweets_info.iteritems():
            for names in names_reader:
                names = names.replace('\n', '')
                if word == names and word != '':
                    words[tweet_id][word]['status'] = 1
                    print "Esta palabra existe en Neologismos: " + word
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

def print_words(words):
    for tweet_id, tweets_info in words.iteritems():
        print "ID: " + tweet_id
        for word, word_info in tweets_info.iteritems():
            print "Word: " + word
            for status, suggestion in word_info.iteritems():
                print "Status: " + status
                print "Suggestion: " + str(suggestion)


if __name__ == "__main__":

    with open('files/tweets_dev100.txt', 'r') as tweets_file:
        tweets_info = tweets_file.readlines()

    tweets = {}
    sentences = {}

    for index,tweet in enumerate(tweets_info):
        info = tweet.split('\t')
        info[3] = info[3].replace("\n","")
        if(info[3] != "Not Available"):
            tweets[info[0]] = info[3]
            sentences[info[0]] = info[3]

    words = to_dictionary(tweets)

    #find_capitals(words)
    #find_gentilicis(words)
    #find_titles(words)
    #find_forenames(words)
    #find_acronimos(words)
    #find_abreviaturas(words)
    #find_person_names(words)

    correct_words(aspell, spellchecker, words)
    add_levensthein_cost(words)
    make_transcription(words)
    #print_words(words)
    
    #sudo ./ngram-count -text input.txt -order 4 -addsmooth 0 -lm 4gram.lm

    GeneticAlgorithm(words, sentences)