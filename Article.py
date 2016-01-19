from collections import Counter

class Article:
    def __init__(self,histogram,len, clusters):
        # words = wholeArticle.split(' ')
        self.wordsLen = len
        self.histogram = histogram
        self.clusters = clusters
        self.requestedCluster = clusters[0]
