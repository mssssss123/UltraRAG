import json
import argparse
import traceback
import urllib.parse
from PIL import Image
from pathlib import Path
from loguru import logger
from flask import Flask, request, Response, stream_with_context
from ultrarag.modules.llm.huggingface_like import HuggingFaceServer


class MicroServer:
    def __init__(self, model_path: str, device: str):
        if not Path(model_path).exists():
            raise ValueError(f"model path: {model_path} not exist!")
        self.llm = HuggingFaceServer(model_path=model_path, device=device)

        self.app = Flask(__name__)
        self.app.add_url_rule('/chat', view_func=self.process, methods=['get', 'post'])
        

    def process(self):
        try:
            data = json.loads(request.form.get("data", {}))
            messages = data.get('messages')
            stream = data.get('stream')
            
            name2img = dict()
            for item in request.files.values():
                if "image" not in item.content_type: continue
                key = urllib.parse.unquote(item.filename)
                name2img[key] = Image.open(item)
            logger.info(f"images files: {[n for n in name2img.keys()]}")
            
            if name2img:
                img_messages = []
                for msg in messages:
                    role, content = msg["role"], msg['content']
                    new_content = [name2img.get(item, item) for item in content]
                    img_messages.append(dict(role=role, content=new_content))
            else:
                img_messages = messages

            logger.info(f"messages: {img_messages}")
            resp = self.llm.run(messages=img_messages, stream=stream)
            if stream:
                return Response(stream_with_context(resp), mimetype='text/event-stream')
            else:
                return resp
        except Exception as e:
            err_msg = traceback.format_exc()
            return Response(err_msg, status=500)


    def run_server(self, host: str, port: int):
        try:
            self.app.run(host=host, port=port)
        except:
            print(traceback.format_exc())


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("-host", required=True, type=str, help="server host")
    args.add_argument("-port", required=True, type=int, help="server port")
    args.add_argument("-model_path", required=True, type=str, help="model file path")
    args.add_argument("-device", required=False, default="", type=str, help="model device")
    args = args.parse_args()

    server = MicroServer(model_path=args.model_path, device=args.device)
    server.run_server(host=args.host, port=args.port)