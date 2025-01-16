import os
from typing import List
import torch
import numpy as np


class BruteIndex(object):
    def __init__(self, device="cpu") -> None:
        self.device = device
        self.text, self.index = [], []

    def insert(self, text: List[str], embed: torch.Tensor): 
        if (isinstance(text, str)):
            text = [text]
        self.text.extend(text)
        if not isinstance(embed, torch.Tensor):
            embed = torch.tensor(embed)
        self.index.append(embed)
    
    @torch.no_grad()
    def search(self, embed: torch.Tensor, topn: int = 5, step: int = 256):
        if isinstance(self.index, torch.Tensor):
            self.index = self.index 
        else:
            self.index = torch.vstack(self.index)

        embed.to(self.device)
        self.index.to(self.device)
        assert self.index.shape[0] == len(self.text), "length not same"

        score_buff = []
        for idb in range(0, len(self.text), step):
            # cache = [step, dims]
            cache = self.index[idb: idb + step, :] 

            # step_score = [batch, step]
            step_score = embed @ cache.T
            score_buff.append(step_score)

        # batch_score = [batch, len(self.text)]
        batch_score = torch.hstack(score_buff)

        # batch_score = [batch, topn]
        values, indices = torch.topk(batch_score, topn, dim=-1)

        # content = [[self.text[row] for row in col] for col in indices.tolist()]
        # return values.tolist(), content
        
        # return indices directly
        return values.tolist(), indices.tolist()


    def load(self, file_path):
        if os.path.exists(file_path):
            raise ValueError("file exist and not empty!")
        text_file = os.path.join(file_path, "content.npy")
        index_file = os.path.join(file_path, 'index.bin')
        if os.path.exists(text_file) or os.path.exists(index_file):
            raise ValueError(f'file exist for {text_file} or {index_file}')
        
        np.save(text_file, self.text)
        torch.save(self.index, index_file)


    def dump(self, file_path):
        self.index = self.index if isinstance(self.index, torch.Tensor) else torch.vstack(self.index)
        text_file = os.path.join(file_path, 'content.npy')
        index_file = os.path.join(file_path, "index.bin")
        if not os.path.exists(text_file) or not os.path.exists(index_file):
            raise ValueError(f"please check path {text_file} and {index_file} existable")
        
        self.text = np.load(text_file).tolist()
        self.index = torch.load(index_file)