import sys
import time


def generateOutputFile(developmentSetFilename, testSetFilename, outputFilename):
    print "Started with: "
    print "\tDevelopment set filename: %s" % developmentSetFilename
    print "\tTest set filename: %s" % testSetFilename
    print "\tOutput filename: %s" % outputFilename
    vocabularySize = 300000

    file = open(outputFilename, "w+")
    # file.write("#Students:\tSaar Arbel\tBoaz Berman\t315681775\t311504401\n")
    # file.write("Output1: " + developmentSetFilename + "\n")
    # file.write("Output2: " + testSetFilename + "\n")
    # file.write("Output3: " + firstInputWord + " " + secondInputWord + "\n")
    # file.write("Output4: " + outputFilename + "\n")
    # file.write("Output5: " + str(vocabularySize) + "\n")

    with open(developmentSetFilename, 'rb') as input_file:
        input_file_data = input_file.read()
    articles = parse_file_data(input_file_data)


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
    test_file_path = sys.argv[2]
    # first_input_word = sys.argv[3]
    # second_input_word = sys.argv[4]
    output_file_path = sys.argv[3]

    generateOutputFile(development_file_path, test_file_path, output_file_path)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print "--- %s seconds ---" % (time.time() - start_time)