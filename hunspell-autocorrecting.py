from __future__ import division
from collections import OrderedDict
from unidecode import unidecode
import hunspell
import json
import csv

# /usr/share/hunspell/es_PE.aff
# /usr/share/hunspell/es_PE.dic
spellchecker = hunspell.HunSpell('/usr/share/hunspell/es_PE.dic',
                                 '/usr/share/hunspell/es_PE.aff')

def correct_words(spellchecker, words, data, add_to_dict=[]):
    #enc = spellchecker.get_dic_encoding()
    
    #add custom words to the dictionary
    if add_to_dict:
        for w in add_to_dict:
            spellchecker.add(w)
    
    corrected = []
    for w in words:
        if(data[w]['status'] == 0):
            ok = spellchecker.spell(w)
            if not ok:
                w_without_repetions = "".join(OrderedDict.fromkeys(w))
                suggestions_with_repetions = spellchecker.suggest(w)
                suggestion_without_repetions = spellchecker.suggest(w_without_repetions)

                #print str(suggestions_with_repetions) + " - " + str(suggestion_without_repetions)
                if (len(suggestions_with_repetions) > len(suggestion_without_repetions)):
                    suggestions = suggestions_with_repetions
                else: 
                    suggestions = suggestion_without_repetions
                if suggestions:
                    best = suggestions[0].decode("utf-8")
                    data[w]['status'] == 1
                    data[w]['correct'] = best
                    corrected.append(best)
                else:
                    corrected.append(w)
            else:
                corrected.append(w)

    return corrected, data

def hunspell_correction(words, data):
    #words = ['hoi', 'todos', 'eztamz', 'juntas', 'en', 'family']
    answers = []

    with open('answer_dev100.txt', 'r') as ans_file:
        lines = ans_file.readlines()

    for line in lines:
        word = line.replace('\r\n', '')
        answers.append(word.decode("utf-8"))

    new_data = {}
    for key, value in data.items():
        if(value['status'] == 0):
            new_data[key.lower()] = value
        else:
            new_data[key] = value

    #print json.dumps(new_data, indent=4, sort_keys=True)

    correct, answer_data = correct_words(spellchecker, words, new_data)

    n_correct_words = 0
    for index, word in enumerate(correct):
        if (word == answers[index]):
            n_correct_words += 1

    #print correct
    #print answers

    dev_file.close()
    ans_file.close()

    return n_correct_words/len(words), answer_data

def find_titles(words, output_f, json_words):

    with open('titles.txt') as titles:
        titles_reader = titles.readlines()

    for word in words:
        for names in titles_reader:
            names = names.replace('\n', '').lower()
            if word == names:
                json_words[word]['status'] = 1
                json_words[word]['correct'] = word
                output_f.write(word + " 1 " + word + "\n")
                print "Esta palabra existe en titulos: " + word
                break
    titles.close()

    return json_words

def find_person_names(words, output_f, json_words):

    with open('person-names.txt') as names_file:
        names_reader = names_file.readlines()

    for word in words:
        for names in names_reader:
            names = names.replace('\n', '')
            if word == names:
                json_words[word]['status'] = 1
                json_words[word]['correct'] = word
                output_f.write(word + " 1 " + word + "\n")
                print "Esta palabra existe en Person names: " + word
                break
    names_file.close()

    return json_words

def find_gentilicis(words, output_f, json_words):

    with open('gentilicis.txt') as gentilicis:
        gentilicis_reader = gentilicis.readlines()

    for word in words:
        for names in gentilicis_reader:
            names = names.replace('\n', '')
            names = names.split(' ')
            if word in names:
                json_words[word]['status'] = 1
                json_words[word]['correct'] = word
                output_f.write(word + " 1 " + word + "\n")
                print "Esta palabra existe en Gentilicios: " + word
                break
    gentilicis.close()

    return json_words

def find_forenames(words, output_f, json_words):
    with open('forenames.txt') as forenames:
        forenames_reader = forenames.readlines()

    for word in words:
        for names in forenames_reader:
            names = names.replace('\n', '')
            names = names.split(' ')
            if word in names:
                json_words[word]['status'] = 1
                json_words[word]['correct'] = word
                output_f.write(word + " 1 " + word + "\n")
                print "Esta palabra existe en forenames: " + word
                break
    forenames.close()

    return json_words

def find_capitals(words, output_f, json_words):
    with open('capitals.txt') as capitals:
        capitals_reader = capitals.readlines()

    for word in words:
        for names in capitals_reader:
            names = names.replace('\n', '')
            names = names.split(' ')
            if word in names:
                json_words[word]['status'] = 1
                json_words[word]['correct'] = word
                output_f.write(word + " 1 " + word + "\n")
                print "Esta palabra existe en forenames: " + word
                break
    capitals.close()

    return json_words

def find_acronimos(words, output_f, json_words):

    for word in words:
        with open('acronimos.csv', "r") as acronims_file:
            acronims_reader = csv.reader(acronims_file)
            for acronims_row in acronims_reader:
                acronim = acronims_row[0].replace('\n', '').lower()
                if word in acronim and word != '':
                    json_words[word]['status'] = 1
                    json_words[word]['correct'] = word
                    output_f.write(word + " 1 " + word + "\n")
                    print "Esta palabra existe en acronimos: " + word
                    break

    acronims_file.close()

    return json_words

def find_abreviaturas(words, output_f, json_words):

    for word in words:
        with open('abreviaturas.csv', "r") as abreviaturas_file:
            abreviaturas_reader = csv.reader(abreviaturas_file)
            for abreviaturas_row in abreviaturas_reader:
                abreviatura = abreviaturas_row[0].replace('\n', '').lower().split(' ')
                if word in abreviatura and word != '':
                    json_words[word]['status'] = 1
                    json_words[word]['correct'] = word
                    output_f.write(word + " 1 " + word + "\n")
                    print "Esta palabra existe en abreviaturas: " + word
                    break
    abreviaturas_file.close()

    return json_words

if __name__ == "__main__":

    words = []
    data = {}
    with open('dev100.txt', 'r') as dev_file:
        lines = dev_file.readlines()

    with open('JSONData.json', 'w') as f:
        for line in lines:
            word = line.replace('\r\n', '')
            words.append(word)
            data[word] = {"status": 0, "correct": ''}
            json.dump(json.dumps(data), f)

    output_f = open('output.txt', 'w')

    jsonwords = find_capitals(words, output_f, data)
    jsonwords = find_titles(words, output_f, data)
    jsonwords = find_person_names(words, output_f, data)
    jsonwords = find_forenames(words, output_f, data)
    jsonwords = find_gentilicis(words, output_f, data)
    jsonwords = find_acronimos(words, output_f, data)
    jsonwords = find_abreviaturas(words, output_f, data)

    output_f.close()
    dev_file.close()

    print_data = data

    #print json.dumps(print_data, indent=4, sort_keys=True)

    words = [w.lower() for w in words]
    precision, new_data = hunspell_correction(words, data)

    print "Using only hunspell:\nPrecision: %.2f" % (precision*100) +"%"

    print json.dumps(new_data, indent=4)
