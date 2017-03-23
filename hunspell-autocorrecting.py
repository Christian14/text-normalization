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

# /usr/share/hunspell/es_PE.aff
# /usr/share/hunspell/es_PE.dic
spellchecker = hunspell.HunSpell('/usr/share/hunspell/es_PE.dic',
                                 '/usr/share/hunspell/es_PE.aff')

def correct_words(spellchecker, words, add_to_dict=[]):

    if add_to_dict:
        for w in add_to_dict:
            spellchecker.add(w)
    
    for word, value in words.iteritems():
        if(words[word]['status'] == 0):
            ok = spellchecker.spell(word)
            if not ok:
                w_without_repetions = "".join(OrderedDict.fromkeys(word))
                suggestions_with_repetions = spellchecker.suggest(word)
                suggestion_without_repetions = spellchecker.suggest(w_without_repetions)

                if (len(suggestions_with_repetions) > len(suggestion_without_repetions)):
                    suggestions = suggestions_with_repetions
                else: 
                    suggestions = suggestion_without_repetions

                if suggestions:
                    for suggestion in suggestions:
                        words[word][suggestion] = {"Levensthein": 0, "2-gram": 0,"3-gram": 0, "4-gram": 0, "Phonetic": 0} 
                else:
                    words[word]['status'] = 2 #No especifica
            else:
                words[word]['status'] = 1 #Palabra corregida

    return words

def hunspell_correction(words):

    return correct_words(spellchecker, words)

def to_dictionary(tweet):
    dictionary = {}
    words = tweet.split(' ')
    special_characters = ['.', ',', '!', '?','\n','\t']

    for word in words:
        dictionary[word.translate(None, ''.join(special_characters))] = {"status": 0}

    return dictionary

def find_capitals(words):
    with open('capitals.txt') as capitals:
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
        with open('abreviaturas.csv', "r") as abreviaturas_file:
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
        with open('acronimos.csv', "r") as acronims_file:
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
    with open('forenames.txt') as forenames:
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

    with open('titles.txt') as titles:
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

    with open('person-names.txt') as names_file:
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

    with open('gentilicis.txt') as gentilicis:
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

if __name__ == "__main__":

    correct_sentence = "@anngeleescastro gracias grandullona...... Ja claro q te invito.. Y tu pagas vale?? Ja te quiero gracias!!".encode("utf-8")

    with open('tweets_dev100.txt', 'r') as tweets_file:
        tweets_info = tweets_file.readlines()

    tweets = [tweet.split('\t')[3] for tweet in tweets_info]

    words = to_dictionary(tweets[57])

    words = find_capitals(words)
    words = find_gentilicis(words)
    words = find_titles(words)
    words = find_forenames(words)
    words = find_acronimos(words)
    words = find_abreviaturas(words)
    words = find_person_names(words)

    words = hunspell_correction(words)

    print json.dumps(words, indent=4, sort_keys=True)






