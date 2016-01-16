
class EMAlgorithm:

    def __init__(self, articels, numClusters):
        self.numClusters = numClusters
        self.articels = articels
        self.clusters = {}
        self.documentToCategoryProbability = {}
        self.initClusters()

    def initClusters(self):
        for i in xrange(1,len(self.articels),1):
            if(i%self.numClusters not in self.clusters or self.clusters[i%self.numClusters] is None):
                self.clusters[i%self.numClusters] = []
            self.clusters[i%self.numClusters].append(self.articels[i])

    def initDocumentToCategoryProbability(self):
        for doc in self.articels:
            for i in xrange(1,self.numClusters,1):
                if(doc in self.clusters[i]):
                    self.documentToCategoryProbability[(doc,i)] = 1
                else:
                    self.documentToCategoryProbability[(doc,i)] = 0
