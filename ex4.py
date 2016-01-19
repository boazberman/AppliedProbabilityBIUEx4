import sys
import time
from EMAlgorithm import EMAlgorithm
from Article import Article
from collections import Counter

NUM_CLUSTERS = 9

def generateOutputFile(developmentSetFilename, topicsFileName):
    global NUM_CLUSTERS
    print "Started with: "
    print "\tDevelopment set filename: %s" % developmentSetFilename
    print "\tTopic filename: %s" % topicsFileName

    # file.write("#Students:\tSaar Arbel\tBoaz Berman\t315681775\t311504401\n")

    with open(developmentSetFilename, 'rb') as input_file:
        input_file_data = input_file.read()

    develop_word_count = Counter(parse_file_words(input_file_data))
    rare_words = set(filter(lambda word: develop_word_count[word]<=3,
                            develop_word_count.keys()))

    vocabulary = set(develop_word_count.keys()) - rare_words
    print 'Vocabulary Length: ', len(vocabulary)
    article_list = parse_articles(input_file_data,
                                  filter_word_set=rare_words)

    # articlesWithInfo = parse_file_data(input_file_data)
    #
    with open(topicsFileName, 'rb') as topic_file:
        topics_file_data = topic_file.read()
    topics = parse_topic_data(topics_file_data)
    # createConfusionMatrix(topics)
    #
    # typedArticles = [Article(article, info) for info, article in articlesWithInfo]
    #
    emAlgorithm = EMAlgorithm(article_list, NUM_CLUSTERS , len(vocabulary), topics, calcWordsLength(article_list))
    emAlgorithm.algorithm()

def calcWordsLength(article_list):
    sum = 0
    for article in article_list:
        sum += article.wordsLen
    return sum

# from uri
def parse_articles(file_data, filter_word_set=set()):
    '''
    parses the input file to a list of articles.
    @param file_data: the input file text
    @type file_data: string
    @param filter_word_set: words to be filtered from the articles
    @type filter_word_set: set (of strings)
    @return: list of articles.
    @rtype: list(em.article.Article)
    '''
    article_header_list = file_data.splitlines()[0::4]
    article_data_list = file_data.splitlines()[2::4]

    article_list = []
    for article_header, article_data in zip(article_header_list, article_data_list):
        # every header ends with a trailing '>'
        article_header = article_header[:-1]
        topics = article_header.split('\t')[2:]

        # every article ends with a trailing space
        article_data = article_data[:-1]
        word_list = article_data.split(' ')
        word_count = Counter(word_list)

        # filter the requested words
        for word in filter_word_set.intersection(word_count.keys()):
            del word_count[word]
        articleLen = sum(appearences for appearences in word_count.itervalues())
        article_list.append(Article(word_count,articleLen, topics))
    return article_list

# from uri
def parse_file_words(file_data):
    '''
    parses the input file to a sequence (list) of words
    @param file_data: the input file text
    @type file_data: string
    @return: a list of the files words
    @rtype: list(string)
    '''
    # starting from the 3rd line, every 4th line is an article
    article_lines = file_data.splitlines()[2::4]
    # every article ends with a trailing space,
    # so we get a string with all the words separated by one space
    words = ''.join(article_lines)
    # remove the last trailing space
    words = words[:-1]
    # create a list of all the words
    return words.split(' ')

def createConfusionMatrix(topics):
    global NUM_CLUSTERS
    # matrix = [[0 for i in xrange(len(topics+1))] for i in xrange(NUM_CLUSTERS)]
    matrix = []
    for i in xrange(NUM_CLUSTERS):
        new = []
        for j in xrange(len(topics)+1):
            new.append(0)
        matrix.append(new)

def parse_topic_data(topic_data):
    return topic_data.splitlines()[::2]

def parse_file_data(file_data):
    '''
    Parses the input file to a sequence (list) of articles
    @param file_data: the input file text
    @return: a list of articles
    '''
    # starting from the 3rd line, every 4th line is an article
    articles = file_data.splitlines()[2::4]
    articlesInfo = file_data.splitlines()[::4]
    articlesWithInfo = [(articlesInfo[i][1:-1].split('\t')[2:], articles[i][:-1]) for i in xrange(len(articles))]
    # # every article ends with a trailing space,
    # # so we get a string with all the words separated by one space
    # words = ''.join(file_lines)
    # remove the last trailing space of each article
    # articles = [article[:-1] for article in articles]
    # create a list of all the words
    return articlesWithInfo


def main():
    # if len(sys.argv) != 4:
    #   print "How to use: " + sys.argv[
    #     0] + " < development_set_filename > < test_set_filename > < INPUT WORD > < output_filename >"
    #  sys.exit(1)

    development_file_path = sys.argv[1]
    topic_file_path = sys.argv[2]

    generateOutputFile(development_file_path, topic_file_path)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print "--- %s seconds ---" % (time.time() - start_time)