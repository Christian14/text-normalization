def to_dictionary(tweets):
    dictionary = {}
    for key, tweet in tweets.iteritems():
        words = tweet.split(' ')
        special_characters = ['.', ',', '!', '?','\n','\t', ';', '*', '/', '&', '"','=','$', '(', ')','|']
        info = {}
        for word in words:
        	if(word[0]) != "@":
        		info[word.translate(None, ''.join(special_characters))] = {"status": 0}
        dictionary[key] = info
        print key
        print info

    return dictionary

if __name__ == "__main__":

    with open('files/tweets_dev100.txt', 'r') as tweets_file:
        tweets_info = tweets_file.readlines()

    tweets = {}

    for tweet in tweets_info:
        info = tweet.split('\t')
        info[3] = info[3].replace("\n","")
        if(info[3] != "Not Available"):
            tweets[info[0]] = info[3]

    words = to_dictionary(tweets)