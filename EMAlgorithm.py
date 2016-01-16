
class EMAlgorithm:

    def __init__(self, articels, numClusters):
        self.numClusters = numClusters
        self.articels = articels
        self.clusters = {}
        self.words = self.initWords()
        self.documentToCategoryProbability = {}
        self.wordInClusterProbability = {}
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
            words.append(article.words)
        return set(words)

    def initDocumentToCategoryProbability(self):
        for article in self.articels:
            for i in xrange(1,self.numClusters,1):
                if(article in self.clusters[i]):
                    self.documentToCategoryProbability[(article,i)] = 1
                else:
                    self.documentToCategoryProbability[(article,i)] = 0

    def algorithm(self):
        #E-Step
        for article in self.articels:
            for cluster in self.clusters:
                mona,mechane = 0,0


        #M-Step
        for i in xrange(1,self.numClusters,1):
            self.pCi[i] = sum([probability for (doc,j),probability in self.documentToCategoryProbability.iteritems() if j==i])
            self.pCi[i] /= len(self.articels)

        for word in self.words:
            for cluster in self.clusters:
                mona,mechane = 0,0
                for article in self.articels:
                    mona += article.histogram[word] * self.documentToCategoryProbability[(article,cluster)]
                    mechane += article.wordsLen * self.documentToCategoryProbability[(article,cluster)]
                self.wordInClusterProbability[word,cluster] = mona/mechane