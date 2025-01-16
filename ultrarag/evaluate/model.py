import torch
from transformers import AutoTokenizer, BertModel
from typing import List
from tqdm import tqdm


class ModelEmbed(object):
    ''' 使用模型将文本表征为向量
    '''
    def __init__(self, path, device='cuda', batch_size = 256) -> None:
        self.token = AutoTokenizer.from_pretrained(path)
        self.model = BertModel.from_pretrained(path, device_map=device) 
        self.model = self.model.half()
        self.device = self.model.device
        self.batch_size = batch_size

    def embed(self, text: List[str], max_length: int = 512) -> torch.Tensor :
        if isinstance(text, str): text = [text]
        
        vector_buff = []
        # 当batch size 过大的时候分批计算
        for pos in range(0, len(text), self.batch_size):
            prein = self.token.batch_encode_plus(
                text[pos: pos + self.batch_size], 
                padding="longest", 
                truncation=True, 
                max_length=max_length, 
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                model_output = self.model(**prein)
                attention_mask = prein['attention_mask']
                last_hidden = model_output.last_hidden_state.masked_fill(~attention_mask[..., None].bool(), 0.0)
                vectors = last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
                vectors = torch.nn.functional.normalize(vectors, 2.0, dim=1)
            vector_buff.append(vectors.to('cpu'))
        vectors = torch.vstack(vector_buff)
        return vectors.to('cuda')