import math
import itertools

NUM_CLUSTERS = 9
LIKELIHOOD_THRESHOLD = 20.0
K = 10
EPSILON = 0.00001


class EMAlgorithm:
    def __init__(self, articles, clusters_amount, vocabulary_size, topics, total_amount_of_words, lamda):
        self.total_amount_of_words = total_amount_of_words
        self.lamda = lamda
        self.vocabulary_size = vocabulary_size
        self.clusters_amount = clusters_amount
        self.articles = articles
        self.words = self.get_all_distinct_words(articles)
        self.wti = {}
        self.pik = {}
        self.pCi = [0 for i in xrange(clusters_amount)]
        self.topics = topics

    def dummy_split_articles_to_clusters(self):
        clusters = {}
        for i in xrange(len(self.articles)):
            if (i % self.clusters_amount not in clusters or clusters[i % self.clusters_amount] is None):
                clusters[i % self.clusters_amount] = []
            clusters[i % self.clusters_amount].append(self.articles[i])
        return clusters

    def get_all_distinct_words(self, articles):
        words = set()
        for article in articles:
            words.update(article.histogram.keys())
        return words

    def first_e_step(self):
        articles_by_clusters = self.dummy_split_articles_to_clusters()
        for article in self.articles:
            for cluster in xrange(self.clusters_amount):
                if (article in articles_by_clusters[cluster]):
                    self.wti[(article, cluster)] = 1.0
                else:
                    self.wti[(article, cluster)] = 0.0

    def calc_all_zi(self):
        '''
        This function calculates zi for each article and cluster.
        We calculate it by the formula form the doc.
        :return: dictionary (key - (cluster,article) , value - zi)
        '''
        all_zi = {}
        for cluster in xrange(self.clusters_amount):
            for article in self.articles:
                all_zi[(cluster, article)] = math.log(self.pCi[cluster]) + (sum(
                    math.log(self.pik[(word, cluster)]) * appearances for word, appearances in
                    article.histogram.iteritems()))

        return all_zi

    def calc_wti(self, article, cluster, all_zi, m_zi):
        '''
        Calculate the conditional probability of a cluster given some article. This method calculate the probability
        for each of the possible tuples of cluster and article. Also this method smooth each probability to zero to
        avoid underflow.
        :param article:
        :param cluster:
        :param all_zi:
        :param m_zi:
        :return:
        '''
        global K
        # If zi value of a cluster and article is smaller then max zi value for that article minus a given K value,
        # smooth it to zero. No calculation needed.
        if (all_zi[(cluster, article)] - m_zi < -1.0 * K):
            return 0.0
        # Wti is calculated by summing all zi values for the given article (by iterating throw all clusters)
        mechane = sum(
            [math.pow(math.e, all_zi[(subcluster, article)] - m_zi) for subcluster in xrange(self.clusters_amount) if
             all_zi[(subcluster, article)] - m_zi >= -1.0 * K])
        return math.pow(math.e, all_zi[(cluster, article)] - m_zi) / mechane

    def fix_pCi_probability(self):
        '''
        Reallocate distribution in order for the pCi values to add up to 1.
        :return: None
        '''
        pciSum = sum(self.pCi)
        for cluster in xrange(self.clusters_amount):
            self.pCi[cluster] /= pciSum

    def algorithm(self):
        last_likelihood = None
        all_zi, m_zi = None, None
        # Iterate from 1 to infinity until the break condition is met.
        for iteration in itertools.count(1):
            # E-Step
            if last_likelihood is None:
                self.first_e_step()
            else:
                self.e_step(all_zi, m_zi)
            # M-Step
            self.m_step()
            # ---- End of actual algorithm.
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
            # Break condition
            # If the new calculated likelihood isn't smaller from the last likelihood by at least the
            # given threshold, we're done.
            if (last_likelihood != None and likelihood - last_likelihood <= LIKELIHOOD_THRESHOLD):
                return confusion_matrix
            last_likelihood = likelihood

    def calc_perplexity(self, ln_likelihood):
        '''
        Calculate how well a probabilistic model predicts a sample (Perplexity).
        :param ln_likelihood:
        :return: The calculated perplexity.
        '''
        return math.pow(math.e, -1 * (ln_likelihood / float(self.total_amount_of_words)))

    def m_step(self):
        '''
        M-step's goal is to update the pci values and the pik values used by the E-step.
        :return: None
        '''
        self.update_pci()
        self.update_pik()

    def update_pik(self):
        '''
        Iterate through all wti values which exists for each article and cluster tuple and calculate the probability of
        each word to appear in any given cluster. The updated values are inserted to {self.wti}.
        :return: None
        '''
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
                (mona + self.lamda) / (wordMechaneDict[cluster] + (self.vocabulary_size * self.lamda)))

    def update_pci(self):
        '''
        In this function we calculate the PCI for each cluster.
        :return:
        '''
        global EPSILON
        for cluster in xrange(self.clusters_amount):
            self.pCi[cluster] = sum(
                probability for (doc, somecluster), probability in self.wti.iteritems() if somecluster == cluster)
            self.pCi[cluster] /= len(self.articles)
            # Avoid zero or really small values to pCi.
            if (self.pCi[cluster] < EPSILON):
                self.pCi[cluster] = EPSILON
        # After smoothing there is a need to reallocate distribution in order for the pCi values to add up to 1.
        self.fix_pCi_probability()

    def e_step(self, allzi, maxzi):
        '''
        This function represent the E step in the algorithm.
        We calculate Wti for each article and cluster
        :param allzi: zi as described in the Pdf document (for each article and cluster)
        :param maxzi: array of the maximum zi for each article
        :return:
        '''
        # Calculate wti through all articles and clusters.
        for article in self.articles:
            for cluster in xrange(self.clusters_amount):
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
        '''
        In this function we calculate the likelihood by iterating over maxzi and all_zi for
        each article and cluster.
        :param all_zi:
        :param m_zi:
        :return:
        '''
        global K
        total_by_article = {}
        # Initiate
        for article in self.articles:
            total_by_article[article] = 0.0
        # Calculate for each article its likelihood
        for article in self.articles:
            m = m_zi[article]
            exponent_sum = total_by_article[article]
            for cluster in xrange(self.clusters_amount):
                zi = all_zi[(cluster, article)]
                if zi - m >= -1 * K:
                    exponent_sum += math.pow(math.e, zi - m)
            total_by_article[article] = math.log(exponent_sum) + m
        # Sum all together
        return sum(total_by_article.itervalues())

    def articles_by_clusters(self):
        '''
        In this function we build a map from cluster to list of articles.
        The list of articles is the articles that has the maximum WTI with the cluster.
        For each article we take the maximum WTI and append the article to the maximum cluster.
        :return:
        '''
        clusters = {}
        for article in self.articles:
            max, index = 0.0, 0
            for cluster in xrange(self.clusters_amount):
                if self.wti[(article, cluster)] > max:
                    max = self.wti[(article, cluster)]
                    index = cluster
            if (index not in clusters or clusters[index] is None):
                clusters[index] = []
            clusters[index].append(article)
        return clusters

    def calc_confusion_matrix(self):
        '''
        This function calculates the confusion matrix, it iterates each article in the list of articles
        for each cluster and sums the number of topics.
        After that, we write to the matrix the new line which represent the sum of each article topics
        in the i-th cluster.
        :return:
        '''
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
        '''
        Calculate the accuracy by dividing the number of correct assignments made by your model by the total number of
        assignments made by your model.
        :param confusion_matrix:
        :return: The calculated accuracy.
        '''
        global NUM_CLUSTERS
        sum = 0.0
        for i in xrange(NUM_CLUSTERS):
            sum += max(confusion_matrix[i])
        return sum / len(self.articles)
