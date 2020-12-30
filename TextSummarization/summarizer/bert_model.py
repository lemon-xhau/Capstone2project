from typing import List

import numpy as np
import torch
from numpy import ndarray
from transformers import *
from transformers import PhobertTokenizer

class BertModel(object):

    MODELS = {
        'bert-base-multilingual-uncased': (BertModel, BertTokenizer),
        'vinai/phobert-base': (AutoModel, PhobertTokenizer)
    }

    def __init__(
        self,
        model: str,
        custom_model: PreTrainedModel=None,
        custom_tokenizer: PreTrainedTokenizer=None
    ):
        base_model, base_tokenizer = self.MODELS.get(model, (None, None))

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if custom_model:
            self.model = custom_model.to(self.device)
        else:
            self.model = base_model.from_pretrained(model, output_hidden_states=True).to(self.device)

        if custom_tokenizer:
            self.tokenizer = custom_tokenizer
        else:
            self.tokenizer = base_tokenizer.from_pretrained(model)

        self.model.eval()

    def tokenize_input(self, text: str) -> torch.tensor:
        """
        Tokenizes the text input.
        :return: Returns a torch tensor
        """
        tokenized_text = self.tokenizer.tokenize(text)
        indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokenized_text)
        return torch.tensor([indexed_tokens]).to(self.device)

    def extract_embeddings(
        self,
        text: str,
        hidden: int=-2,
        reduce_option: str ='mean'
    ) -> torch.Tensor:

        """
        Extracts the embeddings for the given text
        :return: A numpy array.
        """
        tokens_tensor = self.tokenize_input(text)
        pooled, hidden_states = self.model(tokens_tensor)[-2:]

        if -1 > hidden > -12:

            if reduce_option == 'max':
                #pooled = hidden_states[hidden].max(dim=1)[0]
                pooled = hidden_states[hidden].max(dim=1)[0].squeeze()

            elif reduce_option == 'median':
                #pooled = hidden_states[hidden].median(dim=1)[0]
                pooled = hidden_states[hidden].median(dim=1)[0].squeeze()

            elif reduce_option == 'concat_last_4':
                last_4 = [hidden_states[i] for i in (-1, -2, -3, -4)]
                cat_hidden_states = torch.cat(tuple(last_4), dim=-1)
                pooled = torch.mean(cat_hidden_states, dim=1).squeeze()

            elif reduce_option == 'reduce_last_4':
                last_4 = [hidden_states[i] for i in (-1, -2, -3, -4)]
                pooled = torch.cat(tuple(last_4), dim=1).mean(axis=1).squeeze()

            else:
                pooled = hidden_states[hidden].mean(dim=1).squeeze()
                #pooled = hidden_states[hidden].mean(dim=1)

        return pooled

    def create_matrix(
        self,
        content: List[str],
        hidden: int=-2,
        reduce_option: str = 'mean'
    ) -> ndarray:
        """
        Create matrix from the embeddings
        """
        return np.asarray([
            np.squeeze(self.extract_embeddings(t, hidden=hidden, reduce_option=reduce_option).data.cpu().numpy())
            for t in content
        ])

    def __call__(
        self,
        content: List[str],
        hidden: int= -2,
        reduce_option: str = 'mean'
    ) -> ndarray:
        return self.create_matrix(content, hidden, reduce_option)
