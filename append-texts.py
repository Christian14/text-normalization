filenames = [
    'files/spanish_billion_words/spanish_billion_words_00', 
    'files/spanish_billion_words/spanish_billion_words_01',
    'files/spanish_billion_words/spanish_billion_words_02',
    'files/spanish_billion_words/spanish_billion_words_03',
    'files/spanish_billion_words/spanish_billion_words_04',
    'files/spanish_billion_words/spanish_billion_words_05',
    'files/spanish_billion_words/spanish_billion_words_06',
    'files/spanish_billion_words/spanish_billion_words_07',
    'files/spanish_billion_words/spanish_billion_words_08',
    'files/spanish_billion_words/spanish_billion_words_09',
]

for i in range(10, 100):
    filenames.append('files/spanish_billion_words/spanish_billion_words_'+str(i))

with open('corpus-billion.txt', 'w') as outfile:
    for fname in filenames:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)