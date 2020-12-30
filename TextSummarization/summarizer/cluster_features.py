from typing import List, Dict

import numpy as np
from numpy import ndarray
from sklearn.cluster import KMeans
#from sklearn_extra.cluster import KMedoids


class ClusterFeatures(object):
    """
    Basic handling of clustering features.
    """

    def __init__(
        self,
        features: ndarray,
        algorithm: str = 'kmeans',
        random_state: int = 12345
    ):
        """
        :param features: the embedding matrix created by bert parent
        """

        self.features = features
        self.algorithm = algorithm
        self.random_state = random_state

    def __get_model(self, k: int):
        """
        Retrieve clustering model
        :param k: amount of clusters
        :return: Clustering model
        """
        # if self.algorithm == 'kmedoids':
        #     return KMedoids(n_clusters=k, random_state=self.random_state)
        return KMeans(n_clusters=k, random_state=self.random_state)

    def __get_centroids(self, model):
        """
        Retrieve centroids of model
        :param model: Clustering model
        :return: Centroids
        """
        return model.cluster_centers_

    def __find_closest_args(self, centroids: np.ndarray) -> Dict:
        """
        Find the closest arguments to centroid
        :param centroids: Centroids to find closest
        :return: Closest arguments
        """
        centroid_min = 1e10
        cur_arg = -1
        args = {}
        used_idx = []

        for j, centroid in enumerate(centroids):

            for i, feature in enumerate(self.features):
                value = np.linalg.norm(feature - centroid)

                if value < centroid_min and i not in used_idx:
                    cur_arg = i
                    centroid_min = value

            used_idx.append(cur_arg)
            args[j] = cur_arg
            centroid_min = 1e10
            cur_arg = -1

        return args

    def cluster(self, ratio: float = 0.1, num_sentences: int = None) -> List[int]:
        """
        Clusters sentences based on the ratio
        :param ratio: Ratio to use for clustering
        :param num_sentences: Number of sentences. Overrides ratio.
        :return: Sentences index that qualify for summary
        """
        if num_sentences is not None:
            if num_sentences == 0:
                return []

            k = min(num_sentences, len(self.features))
        else:
            k = max(int(len(self.features) * ratio), 1)

        model = self.__get_model(k).fit(self.features)

        centroids = self.__get_centroids(model)
        cluster_args = self.__find_closest_args(centroids)

        sorted_values = sorted(cluster_args.values())
        return sorted_values

    def __call__(self, ratio: float = 0.1, num_sentences: int = None) -> List[int]:
        return self.cluster(ratio)
