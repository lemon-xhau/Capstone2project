from typing import List, Optional, Tuple

import numpy as np
from transformers import *

from summarizer.bert_model import BertModel
from summarizer.cluster_features import ClusterFeatures
from summarizer.sentence_handler import SentenceHandler


class ModelProcessor(object):

    aggregate_map = {
        'mean': np.mean,
        'min': np.min,
        'median': np.median,
        'max': np.max
    }

    def __init__(
        self,
        model: str = 'vinai/phobert-base',
        custom_model: PreTrainedModel = None,
        custom_tokenizer: PreTrainedTokenizer = None,
        hidden: int = -2,
        reduce_option: str = 'mean',
        sentence_handler: SentenceHandler = SentenceHandler(),
        random_state: int = 2020
    ):
       
        np.random.seed(random_state)
        self.model = BertModel(model, custom_model, custom_tokenizer)
        self.hidden = hidden
        self.reduce_option = reduce_option
        self.sentence_handler = sentence_handler
        self.random_state = random_state

    def process_content_sentences(self, body: str, min_length: int = 10, max_length: int = 200) -> List[str]:
        """
        Processes the content sentences with neural coreference.
        """
        doc = self.nlp(doc)
        return [c.string.strip() for c in doc.sents if max_length > len(c.string.strip()) > min_length]

    def cluster_runner(
        self,
        content: List[str],
        ratio: float = 0.2,
        algorithm: str = 'kmeans',
        use_first: bool = False,
        num_sentences: int = None
    ) -> Tuple[List[str], np.ndarray]:
        """
        Runs the cluster algorithm based on the hidden state. Returns both the embeddings and sentences.
        """

        if num_sentences is not None:
            num_sentences = num_sentences if use_first else num_sentences

        hidden = self.model(content, self.hidden, self.reduce_option)
        hidden_args = ClusterFeatures(hidden, algorithm, random_state=self.random_state).cluster(ratio, num_sentences)

        if use_first:

            if not hidden_args:
                hidden_args.append(0)

            elif hidden_args[0] != 0:
                hidden_args.insert(0, 0)

        sentences = [content[j] for j in hidden_args]
        embeddings = np.asarray([hidden[j] for j in hidden_args])

        return sentences, embeddings

    def __run_clusters(
        self,
        content: List[str],
        ratio: float = 0.2,
        algorithm: str = 'kmeans',
        use_first: bool = False,
        num_sentences: int = None
    ) -> List[str]:
        """
        Runs clusters and returns sentences.
        :return: summarized sentences
        """
        sentences, _ = self.cluster_runner(content, ratio, algorithm, use_first, num_sentences)
        return sentences

    def __retrieve_summarized_embeddings(
            self, content: List[str], ratio: float=0.2, algorithm: str='kmeans', use_first: bool = True, num_sentences: int = None
    ) -> np.ndarray:
        """
        Retrieves embeddings of the summarized sentences.
        :return: Summarized embeddings
        """
        _, embeddings = self.cluster_runner(content, ratio, algorithm, use_first, num_sentences)
        return embeddings

    def run_embeddings(
        self,
        body: str,
        ratio: float = 0.2,
        min_length: int = 20,
        max_length: int = 400,
        use_first: bool = False,
        algorithm: str = 'kmeans',
        num_sentences: int = None,
        aggregate: str = None
    ) -> Optional[np.ndarray]:
        """
        Preprocesses the sentences, runs the clusters to find the centroids, then combines the embeddings.

        :param body: The raw string body to process
        :param ratio: Ratio of sentences to use
        :param min_length: Minimum length of sentence candidates to utilize for the summary.
        :param max_length: Maximum length of sentence candidates to utilize for the summary
        :param use_first: Whether or not to use the first sentence
        :param algorithm: Which clustering algorithm to use. (kmeans, kmedois)
        :param num_sentences: Number of sentences to use. Overrides ratio.
        :param aggregate: One of mean, median, max, min. Applied on zero axis
        :return: A summary embedding
        """

        sentences = self.sentence_handler(body, min_length, max_length)

        if sentences:
            embeddings = self.__retrieve_summarized_embeddings(sentences, ratio, algorithm, use_first, num_sentences)

            if aggregate is not None:

                assert aggregate in ['mean', 'median', 'max', 'min'], "aggregate must be mean, min, max, or median"
                embeddings = self.aggregate_map[aggregate](embeddings, axis=0)

            return embeddings

        return None

    def run(
        self,
        body: str,
        ratio: float = 0.2,
        min_length: int = 20,
        max_length: int = 400,
        use_first: bool = False,
        algorithm: str = 'kmeans',
        num_sentences: int = None
    ) -> str:
        """
        Preprocesses the sentences, runs the clusters to find the centroids, then combines the sentences.

        :param body: The raw string body to process
        :param ratio: Ratio of sentences to use
        :param min_length: Minimum length of sentence candidates to utilize for the summary.
        :param max_length: Maximum length of sentence candidates to utilize for the summary
        :param use_first: Whether or not to use the first sentence
        :param algorithm: Which clustering algorithm to use. (kmeans, kmedois)
        :param num_sentences: Number of sentences to use (overrides ratio).
        :return: A summary sentence
        """

        sentences = self.sentence_handler(body, min_length, max_length)

        if sentences:
            sentences = self.__run_clusters(sentences, ratio, algorithm, use_first, num_sentences)

        return ' '.join(sentences)

    def __call__(
        self,
        body: str,
        ratio: float = 0.2,
        min_length: int = 20,
        max_length: int = 400,
        use_first: bool = False,
        algorithm: str = 'kmeans',
        num_sentences: int = None
    ) -> str:
        """
        (utility that wraps around the run function)

        Preprocesses the sentences, runs the clusters to find the centroids, then combines the sentences.

        :param body: The raw string body to process
        :param ratio: Ratio of sentences to use
        :param min_length: Minimum length of sentence candidates to utilize for the summary.
        :param max_length: Maximum length of sentence candidates to utilize for the summary
        :param use_first: Whether or not to use the first sentence
        :param algorithm: Which clustering algorithm to use. (kmeans, kmedois)
        :param Number of sentences to use (overrides ratio).
        :return: A summary sentence
        """

        return self.run(
            body, ratio, min_length, max_length, algorithm=algorithm, use_first=use_first, num_sentences=num_sentences
        )


class Summarizer(ModelProcessor):

    def __init__(
        self,
        model: str = 'vinai/phobert-base',
        custom_model: PreTrainedModel = None,
        custom_tokenizer: PreTrainedTokenizer = None,
        hidden: int = -2,
        reduce_option: str = 'reduce_last_4',
        sentence_handler: SentenceHandler = SentenceHandler(),
        random_state: int = 123456
    ):
        """
        This is the main phoBert Summarizer class.

        :param model: This parameter is associated with the inherit string parameters from the transformers library.
        :param custom_model: If you have a pre-trained model, you can add the model class here.
        :param custom_tokenizer: If you have a custom tokenizer, you can add the tokenizer here.
        :param hidden: This signifies which layer of the phoBERT model you would like to use as embeddings.
        :param reduce_option: Given the output of the bert model, this param determines how you want to reduce results.
        :param random_state: The random state to reproduce summarizations.
        """
        super(Summarizer, self).__init__(
            model, custom_model, custom_tokenizer, hidden, reduce_option, sentence_handler, random_state
        )
