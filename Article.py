from collections import Counter

class Article:
    def __init__(self,words):
        self.wordsLen = len(words)
        self.histogram = Counter(words)

    # def initHistogram(self):
    #     return Counter(self.words)
        # counter = Counter(self.words)
        # wordsLen = len(self.words)
        # histogram = {}
        # for word,amount in counter:
        #     histogram[word] = amount / wordsLen
        # return histogram

    def debug(self):
        sum = sum(self.histogram.itervalues())
        if(sum==1):
            print 'OK!'
        else:
            print 'Boaz is gay'