import json
import argparse
import traceback
import urllib.parse
from PIL import Image
from pathlib import Path
from loguru import logger
from transformers import AutoConfig
from ultrarag.common import BatchGather
from flask import Flask, request, Response, jsonify
from .models import model_mapping


def load_model(model_path: str, device: str):
    ''' when you load unknown embedding model, you can try this
    '''
    if Path(model_path).exists():
        config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        model_type = config.architectures[0]
        model_class = model_mapping.get(model_type)
        return model_class(url_or_path=model_path, device=device)
    else:
        raise ValueError(f"model path: {model_path} not exist!")


class EmbeddingServer:
    def __init__(self, model_path: str, device: str):
        if not Path(model_path).exists():
            raise ValueError(f"model path: {model_path} not exist!")
        
        # recognize model type and load its model class
        config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        model_type = config.architectures[0]
        self.model_type = config.architectures
        model_class = model_mapping.get(model_type)

        # load model
        if model_class is None:
            raise ValueError(f"Unsupported model type: {model_type}")
        self.emb = model_class(url_or_path=model_path, device=device)

        # query embedding
        self.query_executor = BatchGather(self.emb.query_encode, is_coroutine=True)
        self.query_executor.start()

        # document embedding
        self.document_executor = BatchGather(self.emb.document_encode, is_coroutine=True)
        self.document_executor.start()

        # start server
        self.app = Flask(__name__)
        self.app.add_url_rule('/embed', view_func=self.process, methods=['get', 'post'])
        self.app.add_url_rule('/infos', view_func=self.infos, methods=['get', 'post'])


    def process(self):
        data = json.loads(request.form.get("data", "{}"))
        type = request.form.get("type", "query")
        messages = data
        
        name2img = dict()
        for item in request.files.values():
            if not item: continue
            if "image" not in item.content_type: continue
            key = urllib.parse.unquote(item.filename)
            name2img[key] = Image.open(item).convert("RGB")
        logger.info(f"images files: {[n for n in name2img.keys()]}")

        if name2img:
            messages = [
                name2img.get(msg, msg)
                for msg in messages
            ]
        if None in messages:
            raise ValueError("Invalid image file")
        
        if type == "query":
            messages = self.emb.q_prefix(messages)
            ret_list = self.query_executor.put_task(messages).get_res()
        elif type == "document":
            messages = self.emb.d_prefix(messages)
            ret_list = self.document_executor.put_task(messages).get_res()
        else:
            raise ValueError(f"Unsupported type: {type}")
        
        return jsonify(ret_list)


    def infos(self):
        return jsonify(self.model_type)


    def run_server(self, host: str, port: int):
        try:
            self.app.run(host=host, port=port, use_reloader=False)
        except:
            print(traceback.format_exc())
