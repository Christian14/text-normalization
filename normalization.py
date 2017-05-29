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
        self.population = 100
        self.scores = []
        self.corrected = {}
        self.answers = {}
        self.not_available = not_available
        self.available = available
        self.bigram = {}
        self.trigram = {}
        self.tetragram = {}

        self.generatePopulation()
        self.storeBigram()
        self.storeTrigram()
        self.storeTetragram()

        for i in range(2):
            self.addScores()
            self.calculateFitness()
            self.selectionReproduction()
            self.mutation()


    def storeBigram(self):
        with open('files/2gram.txt', 'r') as lm_file:
            lm = lm_file.readlines()

        for line in lm:
            line = line.replace('\n', '').replace('\t', ' ').split(' ')
            if(len(line[0]) > 0):
                if(self.bigram.has_key(line[1])):
                    self.bigram[line[1]][line[2]] = pow(10, float(line[0]))
                else:
                    self.bigram[line[1]] = {}
                    self.bigram[line[1]][line[2]] = pow(10, float(line[0]))

    def storeTrigram(self):
        with open('files/3gram.txt', 'r') as lm_file:
            lm = lm_file.readlines()

        for line in lm:
            line = line.replace('\n', '').replace('\t', ' ').split(' ')
            if (len(line[0]) > 0):
                if(self.trigram.has_key(line[1])):
                    if(self.trigram[line[1]].has_key(line[2])):
                        self.trigram[line[1]][line[2]][line[3]] = pow(10, float(line[0]))
                    else:
                        self.trigram[line[1]][line[2]] = {}
                        self.trigram[line[1]][line[2]][line[3]] = pow(10, float(line[0]))
                else:
                    self.trigram[line[1]] = {}
                    self.trigram[line[1]][line[2]] = {}
                    self.trigram[line[1]][line[2]][line[3]] = pow(10, float(line[0]))


    def storeTetragram(self):
        with open('files/4gram.txt', 'r') as lm_file:
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

    def selectionReproduction(self):
        fitness_scores = {}
        for we_index, weights in enumerate(self.weights):
            fitness_scores[we_index] = self.corrected[we_index]["fitness"]
        
        for key, value in sorted(fitness_scores.iteritems(), key=lambda (k,v): (v,k), reverse=True):
            alpha = int(round(random.random()*5))
            if alpha >= 5:
                alpha = 4
            if(key + 1 >= len(self.weights)):
                break
            beta = random.random()
            element_one = self.weights[key][alpha]
            element_two = self.weights[key+1][alpha]
            new_one = element_one - beta*(element_one - element_two)
            new_two = element_two + beta*(element_one - element_two)
            self.weights[key][alpha] = new_one
            self.weights[key+1][alpha] = new_two

    def mutation(self):
        for index, weights in enumerate(self.weights):
            alpha = int(round(random.random()*5))
            if alpha >= 5:
                alpha = 4
            self.weights[index][alpha] = random.random()

    def generatePopulation(self):
        for i in range(self.population):
            weights = []
            self.corrected[i] = {}
            for i in range(5):
                weights.append(random.random())
            self.weights.append(weights)

    def addScores(self):
        special_characters = [',','\n','\t', ';', '*', '/', '&', '"','=','$', '(', ')','|']
        for tweet_id, tweets_info in self.words.iteritems():
            print "ID:" + tweet_id
            sentence = self.sentences[tweet_id]
            sentence = sentence.replace("?"," ").replace("!"," ").replace("."," ").replace(":"," ").replace('"'," ").split(' ')
            sentence = [w.translate(None, ''.join(special_characters)) for w in sentence]
            sentence = filter(None, sentence)
            #print str(self.words[tweet_id])
            for we_index, weights in enumerate(self.weights):
                #print "Pesos: " + str(weights)
                self.corrected[we_index]["fitness"] = 0
                self.corrected[we_index][tweet_id] = {}
                for index, word in enumerate(sentence):
                    current_word_suggestions = []
                    if(len(word) > 0 and word in self.words[tweet_id]):
                        if(self.words[tweet_id][word]["status"] != 1):
                            score = 0
                            print "Palabra: " + word
                            if(index == 0):
                                max_score = -1
                                for sug, scores in self.words[tweet_id][word]["suggestions"].iteritems():
                                    score = self.calculateScore(scores, weights)
                                    print "Sugerencia: " + sug
                                    print "Score LevenstheinC y Fonema: "+ str(score) + "\n"
                                    if(score > max_score):
                                        self.corrected[we_index][tweet_id][word] = sug
                                        max_score = score
                            else:
                                max_score = -1
                                prev_word = self.corrected[we_index][tweet_id][sentence[index-1]]
                                for sug, scores in self.words[tweet_id][word]["suggestions"].iteritems():
                                    score = self.calculateScore(scores, weights)
                                    print "Sugerencia: " + sug
                                    print "Score LevenstheinC y Fonema: "+ str(score) 
                                    score += self.addBigram(prev_word, sug, weights[1])
                                    print "Plus Bigram Score: "+ str(score)
                                    if(index > 1):
                                        prev_prev_word = self.corrected[we_index][tweet_id][sentence[index-2]]
                                        score += self.addTrigram(prev_prev_word, prev_word, sug, weights[2])
                                        print "Plus Trigram Score: "+ str(score)
                                    if(index > 2):
                                        prev_prev_prev_word = self.corrected[we_index][tweet_id][sentence[index-3]]
                                        score += self.addTetragram(prev_prev_prev_word, prev_prev_word, prev_word, sug, weights[3])
                                        print "Plus Tetragram Score: "+ str(score)
                                    if(score > max_score):
                                        self.corrected[we_index][tweet_id][word] = sug
                                        max_score = score
                                    print "\n"
                        else:
                            self.corrected[we_index][tweet_id][word] = word
                    else:
                        self.corrected[we_index][tweet_id][word] = word

    def calculateScore(self, scores, weights):
        return scores['Levensthein']*weights[0] + scores['Phonetic']*weights[4]

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
        with open('files/tweet-norm-dev100_annotated.txt', 'r') as tweets_file:
            tweets_info = tweets_file.readlines()

        n_corrected = 0
        n_words = 0

        print "*****************************************************************************"
        for ind_weight, weights in enumerate(self.weights):
            for index, line in enumerate(tweets_info):
                words = line.replace('\n', '').replace('\t', '').replace('\r','').split(' ')
                if(len(words) == 3 and evaluate):
                    print "Palabra corregida: " + words[2]
                    print "Palabra de la oracion: " + words[0]
                    print "Palabra corregida por script: " + tweet[words[0]]

                    if(len(tweet) > 0 and tweet.get(words[0]) and tweet[words[0]] == words[2] or (words[1] == 1 and tweets[words[0]] == words[0])):
                        n_corrected += 1
                    n_words += 1
                else:
                    if(words[0] in self.not_available):
                        evaluate = False
                    if(words[0] in self.available):
                        tweet = self.corrected[ind_weight][words[0]]
                        print "Tweet ID: " + words[0]
                        print "Tweet" + str(tweet)
                        evaluate = True

            self.corrected[ind_weight]["fitness"] = n_corrected/n_words
            print "Pesos: " + str(weights) + "- Fitness: " + str(self.corrected[ind_weight]["fitness"]*100)
            print "Correctos: " + str(n_corrected) + "- Palabras: " + str(n_words)
            print "*****************************************************************************"
            n_corrected = 0
            n_words = 0

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
        words = tweet.replace("?", " ").replace("!", " ").replace('"', " ").split(' ')
        special_characters = ['.', ',','\n','\t', ';', '*', '/', '&', '"','=','$', '(', ')','|', ':']
        info = {}
        for word in words:
            if(len(word) > 0):
                if(word[0]) != "@" and word[0] != "#":
                    info[word.translate(None, ''.join(special_characters))] = {"status": 0, "suggestions": {}}
                else:
                    info[word] = {"status": 1, "suggestions": {}}
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
                    #print "Esta palabra existe en forenames: " + word
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
                        #print "Esta palabra existe en abreviaturas: " + word
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
                        #print "Esta palabra existe en acronimos: " + word
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
                    #print "Esta palabra existe en forenames: " + word
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
                    #print "Esta palabra existe en titulos: " + word
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
                    #print "Esta palabra existe en Person names: " + word
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
                    #print "Esta palabra existe en Gentilicios: " + word
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
                    #print "Esta palabra existe en Neologismos: " + word
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

if __name__ == "__main__":

    with open('files/tweets_dev100.txt', 'r') as tweets_file:
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

    words = correct_words(aspell, spellchecker, words)
    add_levensthein_cost(words)
    make_transcription(words)
    

    # for tweet_id, tweet_info in words.iteritems():
    #     for word, words_info in tweet_info.iteritems():
    #         print "Palabra: " + word + " - Estado: " + str(words_info["status"])
    #         print "Sugerencias: "
    #         for sug, scr in words_info["suggestions"].iteritems():
    #             print sug

    #SRILM sudo ./ngram-count -text input.txt -order 4 -addsmooth 0 -lm 4gram.lm

    GeneticAlgorithm(words, sentences, not_available, available)