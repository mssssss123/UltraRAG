import argparse
from ultrarag.modules.embedding import EmbeddingServer


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("-host", required=True, type=str, help="server host")
    args.add_argument("-port", required=True, type=int, help="server port")
    args.add_argument("-model_path", required=True, type=str, help="model file path")
    args.add_argument("-device", required=False, default="", type=str, help="model device")
    args = args.parse_args()

    server = EmbeddingServer(model_path=args.model_path, device=args.device)
    server.run_server(host=args.host, port=args.port)
