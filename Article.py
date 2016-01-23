# Saar Arbel 315681775, Boaz Berman 311504401
class Article:
    def __init__(self,histogram,len, clusters):
        self.wordsLen = len
        self.histogram = histogram
        self.clusters = clusters
        self.requestedCluster = clusters[0]
