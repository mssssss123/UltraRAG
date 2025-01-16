from flask import Flask, request, jsonify, Response
from ultrarag.common import BatchGather
import argparse
import traceback

from ultrarag.modules.reranker import BaseRerank, all_reranker


class MicroServer:
    def __init__(self, model_name, model_path):
        if model_name not in all_reranker:
            raise ValueError(f"not found module name {model_name}, \
                    must be one of {[item for item in all_reranker.keys()]}")
        reranker: BaseRerank = all_reranker[model_name]
        self.reranker = reranker(model_path)
        self.executor = BatchGather(self.reranker.run_batch)
        self.executor.start()

        self.app = Flask(__name__)
        self.app.add_url_rule('/rerank', view_func=self.process, methods=['get', 'post'])
        

    def process(self):
        try:
            query = request.json['query']
            texts = request.json['texts']
            text_pairs = [(query, text) for text in texts]
            ret_list = self.executor.put_task(text_pairs).get_res()
            return jsonify(ret_list)
        except Exception as e:
            err_msg = traceback.format_exc()
            return Response(err_msg, status=500)


    def run_server(self, host: str, port: int):
        try:
            self.app.run(host=host, port=port)
        finally:
            self.executor.stop()


if __name__ == "__main__":
    choices = [item for item in all_reranker.keys()]
    args = argparse.ArgumentParser()
    args.add_argument("-host", required=True, type=str, help="server host")
    args.add_argument("-port", required=True, type=int, help="server port")
    args.add_argument("-model_path", required=True, type=str, help="model file path")
    args.add_argument("-model_type", required=True, choices=choices, help="your reranker model type")
    args = args.parse_args()

    server = MicroServer(model_name=args.model_type, model_path=args.model_path)
    server.run_server(host=args.host, port=args.port)