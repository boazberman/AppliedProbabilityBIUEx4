import math
from itertools import groupby

class EMAlgorithm:

    def __init__(self, articels, numClusters, vocabolarySize):
        self.k = 10
        self.epsilon = 0.000001
        self.lamda = 1
        self.vocabolarySize = vocabolarySize
        self.numClusters = numClusters
        self.articels = articels
        self.clusters = {}
        self.words = self.initWords()
        self.wti = {}
        self.pik = {}
        self.pCi = [0 for i in xrange(numClusters)]
        self.initClusters()

    def initClusters(self):
        for i in xrange(len(self.articels)):
            if(i%self.numClusters not in self.clusters or self.clusters[i%self.numClusters] is None):
                self.clusters[i%self.numClusters] = []
            self.clusters[i%self.numClusters].append(self.articels[i])

    def initWords(self):
        words = []
        for article in self.articels:
            words += article.histogram.keys()
        return set(words)

    def initWti(self):
        for article in self.articels:
            for i in xrange(self.numClusters):
                if(article in self.clusters[i]):
                    self.wti[(article, i)] = 1
                else:
                    self.wti[(article, i)] = 0

    def allzi(self):
        allzi = {}
        for cluster in self.clusters:
            for article in self.articels:
                allzi[(cluster, article)] = math.log(self.pCi[cluster]) + sum([math.log(self.pik[(word, cluster)]) * article.histogram[word] for word in article.histogram.keys()])

        return allzi


    def calcwti(self, article, cluster, allzi, maxzi):
        if(allzi[(cluster,article)] - maxzi < -1 * self.k):
            return 0
        mechane = sum([math.pow(math.e, allzi[(subcluster,article)] - maxzi) for subcluster in self.clusters if
                       allzi[subcluster,article] - maxzi >= -1 * self.k])
        return math.pow(math.e, allzi[(cluster,article)] - maxzi) / mechane


    def fixPCIprobability(self):
        pciSum = sum(self.pCi)
        for i in xrange(self.numClusters):
            self.pCi[i] /= pciSum

    def fixPIKProbability(self):
        pikSum = sum(self.pik.itervalues())
        for i in xrange(self.numClusters):
            for word in self.words:
                self.pik[(word,i)] /= pikSum


    def algorithm(self):
        lastlikelihood = None
        allzi, maxzi = None, None
        # while True:
        # E-Step
        # if(lastlikelihood != None):
        #     self.e_step(allzilist, maxzi)
        # else:
        self.initWti()
        self.first = False
        # M-Step
        self.m_step()
        allziDict, maxzi = self.calc_zi()
        # Likelihood
        likelihood = self.likelihood(allziDict, maxzi)
        # if(lastlikelihood != None and likelihood < lastlikelihood):
            #   break
        lastlikelihood = likelihood




    def m_step(self):
        for i in xrange(self.numClusters):
            # SPEED - groupby optimization
            self.pCi[i] = sum(probability for (doc, j), probability in self.wti.iteritems() if j == i)
            # self.pCi[i] = 0
            # for (doc,j),prob in self.wti.iteritems():
            #     if i==j:
            #         self.pCi[i] += prob
            self.pCi[i] /= len(self.articels)
            if (self.pCi[i] < self.epsilon):
                self.pCi[i] = self.epsilon
        if (sum(self.pCi) != 1):
            self.fixPCIprobability()
        for word in self.words:
            for cluster in self.clusters:
                mona, mechane = 0.0, 0.0
                for article in self.articels:
                    mona += article.histogram[word] * self.wti[(article, cluster)]
                    mechane += article.wordsLen * self.wti[(article, cluster)]
                    if (mona == 0):
                        mona += self.lamda
                        mechane += self.vocabolarySize * self.lamda
                    self.pik[(word, cluster)] = mona / mechane
        if (sum(self.pik.itervalues()) != 1):
            self.fixPIKProbability()

    def e_step(self, allzi, maxzi):
        # Calculate wti through all articles and clusters.
        for article in self.articels:
            for cluster in self.clusters:
                self.wti[(article, cluster)] = self.calcwti(article, cluster, allzi, maxzi[article])

    def calc_zi(self):
        allzi = self.allzi()
        # Calculate max zi for each document through all clusters.
        maxzi = {}
        iterable = sorted(allzi.iteritems(), key=lambda tup: tup[0][1])
        for article, values in groupby(iterable, key=lambda key: key[1]):
            maxzi[article] = max(zivalue for key, zivalue in values)
        return allzi, maxzi

    def likelihood(self, allzi, maxzi):
        total = 0.0

        for article in self.articels:
            total += maxzi[article] + math.log(sum(math.pow(math.e, zi - maxzi[article]) for zi in allzi.itervalues() if zi - maxzi[article] > -1 * self.k))

        return total