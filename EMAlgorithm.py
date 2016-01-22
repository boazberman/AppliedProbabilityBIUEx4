# Saar Arbel 315681775, Boaz Berman 311504401
import math
import itertools

NUM_CLUSTERS = 9
LIKELIHOOD_THRESHOLD = 20.0
K = 10


class EMAlgorithm:
    def __init__(self, articles, numClusters, ditinctWordLength, topics, wordsTotalLength):
        self.wordsTotalLength = wordsTotalLength
        self.epsilon = 0.00001
        self.lamda = 1.1
        self.ditinctWordLength = ditinctWordLength
        self.numClusters = numClusters
        self.articles = articles
        self.clusters = {}
        self.words = self.get_all_distinct_words()
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

    def get_all_distinct_words(self):
        words = set()
        for article in self.articles:
            words.update(article.histogram.keys())
        return words

    def first_e_step(self):
        for article in self.articles:
            for cluster in xrange(self.numClusters):
                if (article in self.clusters[cluster]):
                    self.wti[(article, cluster)] = 1.0
                else:
                    self.wti[(article, cluster)] = 0.0

    def calc_all_zi(self):
        allzi = {}
        for cluster in xrange(self.numClusters):
            for article in self.articles:
                allzi[(cluster, article)] = math.log(self.pCi[cluster]) + (sum(
                    math.log(self.pik[(word, cluster)]) * appearances for word, appearances in
                    article.histogram.iteritems()))

        return allzi

    def calc_wti(self, article, cluster, allzi, maxzi):
        global K
        if (allzi[(cluster, article)] - maxzi < -1.0 * K):
            return 0.0
        mechane = sum(
            [math.pow(math.e, allzi[(subcluster, article)] - maxzi) for subcluster in xrange(self.numClusters) if
             allzi[(subcluster, article)] - maxzi >= -1.0 * K])
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
        last_likelihood = None
        all_zi, m_zi = None, None
        # while True:
        for iteration in itertools.count(1):
            # E-Step
            if (last_likelihood != None):
                self.e_step(all_zi, m_zi)
            else:
                self.first_e_step()
            # M-Step
            self.m_step()
            # Statistics
            all_zi = self.calc_all_zi()
            m_zi = self.find_m_zi(all_zi)
            likelihood = self.likelihood(all_zi, m_zi)
            perplexity = self.calc_perplexity(likelihood)
            confusion_matrix = self.calc_confusion_matrix()
            accuracy = self.calc_accuracy(confusion_matrix)
            # Printers
            print "Iteration no. #" + str(iteration)
            print "\tLikelihood: " + str(likelihood)
            print "\tPerplexity: " + str(perplexity)
            print "\tAccuracy: " + str(accuracy) + '\n'
            # Condition
            # If the new calculated likelihood isn't smaller from the last likelihood by at least the
            # given threshold, we're done.
            if (last_likelihood != None and likelihood - last_likelihood <= LIKELIHOOD_THRESHOLD):
                return confusion_matrix
            last_likelihood = likelihood

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
            self.pik[(word, cluster)] = (
                (mona + self.lamda) / (wordMechaneDict[cluster] + (self.ditinctWordLength * self.lamda)))

    def calc_pci(self):
        for cluster in xrange(self.numClusters):
            self.pCi[cluster] = sum(
                probability for (doc, somecluster), probability in self.wti.iteritems() if somecluster == cluster)
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
                self.wti[(article, cluster)] = self.calc_wti(article, cluster, allzi, maxzi[article])

    def find_m_zi(self, all_zi):
        '''
        Iterate through all the clusters to find the maximum zi value for each article, for future use.
        :return: m_zi - dictionary of the maximum zi value for each article.
        '''
        m_zi = {}
        # Calculate max zi for each document through all clusters.
        for (cluster, article), zi in all_zi.iteritems():
            # m_zi is the max zi value available to the article.
            if article not in m_zi or m_zi[article] is None or m_zi[article] < zi:
                m_zi[article] = zi
        return m_zi

    def likelihood(self, all_zi, m_zi):
        global K
        totalByArticle = {}
        # Initiate
        for article in self.articles:
            totalByArticle[article] = 0.0
        # Calculate for each article its likelihood
        for article in self.articles:
            m = m_zi[article]
            exponent_sum = totalByArticle[article]
            for cluster in xrange(self.numClusters):
                zi = all_zi[(cluster, article)]
                if zi - m >= -1 * K:
                    exponent_sum += math.pow(math.e, zi - m)
            totalByArticle[article] = math.log(exponent_sum) + m
        # Sum all together
        return sum(totalByArticle.itervalues())

    # def accuracy(self):
    #     mona = 0.0
    #     for article in self.articles:
    #         max = 0.0
    #         max_cluster = None
    #         for cluster in xrange(self.numClusters):
    #             if self.wti[(article, cluster)] > max:
    #                 max, max_cluster = self.wti[(article, cluster)], cluster
    #         if self.topics[max_cluster] in article.clusters:
    #             mona += 1
    #
    #     return mona / float(len(self.articles))
    #     # return mona / sum(len(article.clusters) for article in self.articles))

    def articles_by_clusters(self):
        clusters = {}
        for article in self.articles:
            max, index = 0.0, 0
            for cluster in self.clusters.keys():
                if self.wti[(article, cluster)] > max:
                    max = self.wti[(article, cluster)]
                    index = cluster
            if (index not in clusters or clusters[index] is None):
                clusters[index] = []
            clusters[index].append(article)
        return clusters

    def calc_confusion_matrix(self):
        global NUM_CLUSTERS
        clusters = self.articles_by_clusters()
        matrix = []
        for i in xrange(NUM_CLUSTERS):
            new_line = []
            articles_by_topic = {}
            # Match each article to its corresponding topic
            for article in clusters[i]:
                if (article.requestedCluster not in articles_by_topic or articles_by_topic[article.requestedCluster] is None):
                    articles_by_topic[article.requestedCluster] = 0
                articles_by_topic[article.requestedCluster] += 1
            # Build line
            for j in xrange(len(self.topics)):
                if (self.topics[j] not in articles_by_topic or articles_by_topic[self.topics[j]] is None):
                    articles_by_topic[self.topics[j]] = 0
                new_line.append(articles_by_topic[self.topics[j]])
            # Add row to table
            matrix.append(new_line)
        return matrix

    def calc_accuracy(self, confusion_matrix):
        global NUM_CLUSTERS
        sum = 0.0
        for i in xrange(NUM_CLUSTERS):
            sum += max(confusion_matrix[i])
        return sum / len(self.articles)
