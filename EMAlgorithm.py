import math


class EMAlgorithm:
    def __init__(self, articels, numClusters, ditinctWordLength, topics, wordsTotalLength):
        self.k = 10
        self.wordsTotalLength = wordsTotalLength
        self.epsilon = 0.00001
        self.lamda = 0.1
        self.ditinctWordLength = ditinctWordLength
        self.numClusters = numClusters
        self.articles = articels
        self.clusters = {}
        self.words = self.initWords()
        self.wti = {}
        self.pik = {}
        self.pCi = [0 for i in xrange(numClusters)]
        self.initClusters()
        self.topics = topics

    def initClusters(self):
        for i in xrange(len(self.articles)):
            if (i % self.numClusters not in self.clusters or self.clusters[i % self.numClusters] is None):
                self.clusters[i % self.numClusters] = []
            self.clusters[i % self.numClusters].append(self.articles[i])

    def initWords(self):
        words = set()
        for article in self.articles:
            words.update(article.histogram.keys())
        return words

    def initWti(self):
        for article in self.articles:
            for cluster in xrange(self.numClusters):
                if (article in self.clusters[cluster]):
                    self.wti[(article, cluster)] = 1.0
                else:
                    self.wti[(article, cluster)] = 0.0

    def allzi(self):
        allzi = {}
        for cluster in xrange(self.numClusters):
            for article in self.articles:
                allzi[(cluster, article)] = math.log(self.pCi[cluster]) + (sum(
                    math.log(self.pik[(word, cluster)]) * appearances for word, appearances in
                    article.histogram.iteritems()))

        return allzi

    def calcwti(self, article, cluster, allzi, maxzi):
        if (allzi[(cluster, article)] - maxzi < -1.0 * self.k):
            return 0.0
        mechane = sum([math.pow(math.e, allzi[(subcluster, article)] - maxzi) for subcluster in xrange(self.numClusters) if
                       allzi[(subcluster, article)] - maxzi >= -1.0 * self.k])
        return math.pow(math.e, allzi[(cluster, article)] - maxzi) / mechane

    def fixPCIprobability(self):
        pciSum = sum(self.pCi)
        for cluster in xrange(self.numClusters):
            self.pCi[cluster] /= pciSum

    def fixPIKProbability(self):
        pikSum = sum(self.pik.itervalues())
        for cluster in xrange(self.numClusters):
            for word in self.words:
                self.pik[(word, cluster)] /= pikSum

    def algorithm(self):
        lastlikelihood = None
        allziDict, maxzi = None, None
        # while True:
        for i in xrange(30):
            print str(i) + '\n'
            # E-Step
            if (lastlikelihood != None):
                self.e_step(allziDict, maxzi)
            else:
                self.initWti()
                self.first = False
            # M-Step
            self.m_step()
            allziDict, maxzi = self.calc_zi()
            # Likelihood
            likelihood = self.likelihood(allziDict, maxzi)
            print str(likelihood) + '\n'
            if (lastlikelihood != None and likelihood <= lastlikelihood):
                break
            lastlikelihood = likelihood
            perplexity = self.calc_perplexity(lastlikelihood)
            print str(perplexity) + '\n'
            print str(self.accuracy()) + '\n'


    def calc_perplexity(self, lnlikelihood):
        perplexity_extension = -1 * (lnlikelihood / float(self.wordsTotalLength))
        return math.pow(math.e, perplexity_extension)

    def m_step(self):
        self.calc_pci()

        wordMechaneDict = {}
        wordMonaDict = {}
        for (article, cluster), prob in self.wti.iteritems():
            for word in article.histogram.iterkeys():
                if (word, cluster) not in wordMonaDict or wordMonaDict[(word, cluster)] is None:
                    wordMonaDict[(word, cluster)] = 0.0
                wordMonaDict[(word, cluster)] += article.histogram[word] * prob
            if cluster not in wordMechaneDict or wordMechaneDict[cluster] is None:
                wordMechaneDict[cluster] = 0.0
            wordMechaneDict[cluster] += article.wordsLen * prob
        for (word, cluster), mona in wordMonaDict.iteritems():
            self.pik[(word, cluster)] = ((mona + self.lamda) / (wordMechaneDict[cluster] + (self.ditinctWordLength * self.lamda)))


    def calc_pci(self):
        for cluster in xrange(self.numClusters):
            self.pCi[cluster] = sum(probability for (doc, somecluster), probability in self.wti.iteritems() if somecluster == cluster)
            self.pCi[cluster] /= len(self.articles)
            if (self.pCi[cluster] < self.epsilon):
                self.pCi[cluster] = self.epsilon
                # print sum(self.pCi)
                # if (not (sum(self.pCi) == 1)):
                #     self.fixPCIprobability()

    def e_step(self, allzi, maxzi):
        # Calculate wti through all articles and clusters.
        for article in self.articles:
            for cluster in xrange(self.numClusters):
                self.wti[(article, cluster)] = self.calcwti(article, cluster, allzi, maxzi[article])

    def calc_zi(self):
        allzi = self.allzi()
        # Calculate max zi for each document through all clusters.
        maxzi = {}
        for (cluster, article), zivalue in allzi.iteritems():
            if article not in maxzi or maxzi[article] is None or maxzi[article] < zivalue:
                maxzi[article] = zivalue
        return allzi, maxzi

    def likelihood(self, allzi, maxzi):
        totalByArticle = {}
        for article in self.articles:
            totalByArticle[article] = 0.0
        # for (cluster, article), zi in allzi.iteritems():
        #     if zi - maxzi[article] >= -1 * self.k:
        #         totalByArticle[article] += math.pow(math.e, zi - maxzi[article])
        # for article in self.articles:
        #     totalByArticle[article] = maxzi[article] + math.log(totalByArticle[article])

        for article in self.articles:
            m = maxzi[article]
            exponent_sum = totalByArticle[article]
            for cluster in xrange(self.numClusters):
                zi = allzi[(cluster, article)]
                if zi - m >= -1 * self.k:
                    exponent_sum += math.pow(math.e, zi - m)
            totalByArticle[article] = math.log(exponent_sum) + m

        total = sum(totalByArticle.itervalues())

        return total


    def accuracy(self):
        mona = 0.0
        for article in self.articles:
            max = 0.0
            max_cluster = None
            for cluster in xrange(self.numClusters):
                if self.wti[(article, cluster)] > max:
                    max, max_cluster = self.wti[(article, cluster)], cluster
            if self.topics[max_cluster] in article.clusters:
                mona += 1

        return mona / float(len(self.articles))
        # return mona / sum(len(article.clusters) for article in self.articles))
