import sys
import time
from EMAlgorithm import EMAlgorithm
from Article import Article

NUM_CLUSTERS = 9

def generateOutputFile(developmentSetFilename, topicsFileName):
    global NUM_CLUSTERS
    print "Started with: "
    print "\tDevelopment set filename: %s" % developmentSetFilename
    print "\tTopic filename: %s" % topicsFileName
    vocabularySize = 300000

    # file.write("#Students:\tSaar Arbel\tBoaz Berman\t315681775\t311504401\n")

    with open(developmentSetFilename, 'rb') as input_file:
        input_file_data = input_file.read()
    articles = parse_file_data(input_file_data)

    with open(topicsFileName, 'rb') as topic_file:
        topics_file_data = topic_file.read()
    topics = parse_topic_data(topics_file_data)
    createConfusionMatrix(topics)

    typedArticles = [Article(article) for article in articles]

    # emAlgorithm = EMAlgorithm(typedArticles, NUM_CLUSTERS , vocabularySize)
    # emAlgorithm.algorithm()

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
    # # every article ends with a trailing space,
    # # so we get a string with all the words separated by one space
    # words = ''.join(file_lines)
    # remove the last trailing space of each article
    articles = [article[:-1] for article in articles]
    # create a list of all the words
    return articles


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