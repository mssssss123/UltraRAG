import argparse
import sys
from pathlib import Path
home_path = Path().resolve()
sys.path.append(home_path.as_posix())
parser = argparse.ArgumentParser(description="")



parser.add_argument('--pipeline_type', type=str)
args, unknown=parser.parse_known_args()

if args.pipeline_type == "kbalign":
   from ultrarag.datasets.KBAlign.kbalign import KBAlignClass
   kbalign_class = KBAlignClass(parser)
   kbalign_class.main()
   
if args.pipeline_type == "merge":
   from ultrarag.datasets.others.others import OthersClass
   OthersClass.merge(parser)

if args.pipeline_type == "embedding_training_data":
   from ultrarag.datasets.embedding.retriever_finetune import RetrieverFinetune
   syntheiser = RetrieverFinetune()
   syntheiser.main(parser)

if args.pipeline_type == "ddr":
   from ultrarag.datasets.DDR.workflow import GenerationFlow
   ddr_flow = GenerationFlow(parser)
   ddr_flow.execute()

print("finish")