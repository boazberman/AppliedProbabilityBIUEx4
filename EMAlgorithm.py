import math

class EMAlgorithm:

    def __init__(self, articels, numClusters):
        self.k = 10
        self.first = True
        self.numClusters = numClusters
        self.articels = articels
        self.clusters = {}
        self.words = self.initWords()
        self.wti = {}
        self.pik = {}
        self.pCi = []
        self.initClusters()

    def initClusters(self):
        for i in xrange(1,len(self.articels),1):
            if(i%self.numClusters not in self.clusters or self.clusters[i%self.numClusters] is None):
                self.clusters[i%self.numClusters] = []
            self.clusters[i%self.numClusters].append(self.articels[i])

    def initWords(self):
        words = []
        for article in self.articels:
            words += article.histogram.keys()
        return set(words)

    def initDocumentToCategoryProbability(self):
        for article in self.articels:
            for i in xrange(1,self.numClusters,1):
                if(article in self.clusters[i]):
                    self.wti[(article, i)] = 1
                else:
                    self.wti[(article, i)] = 0

    def allzi(self):
        allzi = {}
        for cluster in self.clusters:
            allzi[cluster] = math.log(self.pCi[cluster]) + sum([math.log(self.pik[(word, cluster)]) * article.histogram[word] for word in article.histogram.keys() for article in self.articels])

        return allzi;


    def calcwti(self, article, cluster, allzi, maxzi):
        if(allzi[cluster] - maxzi < -1 * self.k):
            return 0
        mechane = sum([math.pow(math.e, allzi[subcluster] - maxzi) for subcluster in self.clusters if
                    allzi[subcluster] - maxzi >= -1 * self.k])
        return math.pow(math.e, allzi[cluster] - maxzi) / mechane


    def algorithm(self):
        #E-Step
        if(not self.first):
            self.e_step()
        else:
            self.first = False
        #M-Step
        for i in xrange(1,self.numClusters,1):
            self.pCi[i] = sum([probability for (doc, j), probability in self.wti.iteritems() if j == i])
            self.pCi[i] /= len(self.articels)

        for word in self.words:
            for cluster in self.clusters:
                mona, mechane = 0.0, 0.0
                for article in self.articels:
                    mona += article.histogram[word] * self.wti[(article, cluster)]
                    mechane += article.wordsLen * self.wti[(article, cluster)]
                self.pik[(word, cluster)] = mona / mechane

    def e_step(self):
        allzi = self.allzi()
        maxzi = max(allzi)
        for article in self.articels:
            for cluster in self.clusters:
                self.wti[(article, cluster)] = self.calcwti(article, cluster, allzi, maxzi)