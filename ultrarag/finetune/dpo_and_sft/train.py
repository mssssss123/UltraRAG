import torch
from transformers import (AutoModelForCausalLM, AutoTokenizer,TrainingArguments)
from functools import partial
import logging
import os
from trl import DPOTrainer, DPOConfig, SFTTrainer, SFTConfig
import transformers
from dataclasses import dataclass, field
from typing import Optional
from datasets import load_dataset
import yaml
import argparse

logger = logging.getLogger(__name__)

MODEL_TARGET_MODULES = {
    "minicpm2": ['q_proj', 'v_proj'],
    "minicpm3": ['q_a_proj', 'q_b_proj', 'kv_a_proj_with_mqa', 'kv_b_proj', 'o_proj'],
    "llama_style": ['q_proj', 'k_proj', 'v_proj', 'o_proj']
}

@dataclass
class ModelArguments:
    # Arguments related to the model configuration
    model_name_or_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the pre-trained model or identifier from the HuggingFace model hub."},
    )
    model_type: str = field(
        default=None,
        metadata={
            "help": "Specify the model type. Options are 'minicpm2', 'minicpm3', and 'llama_style'."
        },
    )
    use_template: bool = field(
        default=True,
        metadata={"help": "Whether to use a predefined template for generating prompts."},
    )

@dataclass
class DataArguments:
    # Arguments related to the dataset
    train_data_path: str = field(
        default=None,
        metadata={"help": "Path to the training dataset in JSON format."},
    )
    eval_data_path: str = field(
        default=None,
        metadata={"help": "Path to the evaluation dataset in JSON format."},
    )
    max_length: int = field(
        default=1536,
        metadata={"help": "Maximum length of the sequences (prompt + completion) in the batch"},
    )
    max_prompt_length: int = field(
        default=1280,
        metadata={"help": "Maximum length of the prompt."},
    )
    max_passage_length: int = field(
        default=1024,
        metadata={"help": "Maximum length of the passage."},
    )
    max_seq_length: int = field(
        default=1280,
        metadata={"help": "Maximum sequence length for the ConstantLengthDataset and for automatically creating the dataset."},
    )
    top_n: int = field(
        default=5,
        metadata={"help": "Number of top passages to use for retrieval augmentation."},
    )

@dataclass
class TrainingArguments(transformers.TrainingArguments):
    # Custom Training Arguments for fine-tuning the model, inherited from transformers
    cache_dir: Optional[str] = field(
        default=None,
        metadata={"help": "Directory to store the cache files for the model and tokenizer."},
    )
    optim: str = field(
        default="adamw_torch",
        metadata={"help": "Optimizer to use during training. Options include 'adamw_torch', 'sgd', etc."},
    )
    output_dir: str = field(
        default=None,
        metadata={"help": "Directory to save the model checkpoints and training outputs."},
    )
    save_steps: int = field(
        default=10,
        metadata={"help": "Number of steps between saving model checkpoints."},
    )
    eval_steps: int = field(
        default=100,
        metadata={"help": "Number of steps between evaluation runs during training."},
    )
    per_device_train_batch_size: int = field(
        default=8,
        metadata={"help": "Batch size for training on each device."},
    )
    per_device_eval_batch_size: int = field(
        default=8, 
        metadata={"help": "Batch size per GPU/TPU/MPS/NPU core/CPU for evaluation."}
    )
    learning_rate: float = field(
        default=5e-5, 
        metadata={"help": "The initial learning rate for AdamW."}
    )
    eval_strategy: str = field(
        default='steps',
        metadata={"help": "Evaluation strategy to use during training. Options include 'steps' or 'epoch'."},
    )
    logging_steps: int = field(
        default=10,
        metadata={"help": "Number of steps between logging training metrics."},
    )
    logging_dir: str = field(
        default=None,
        metadata={"help": "Directory to save the training logs."},
    )
    bf16: bool = field(
        default=True,
        metadata={"help": "Whether to use bfloat16 (bf16) precision for training."},
    )

def load_yaml_config(config_path):
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
    
def load_model_and_tokenizer(
    model_path: str,
    model_type: str,
    use_lora: bool = False,
    bf16: bool = False,
    fp16: bool = False,
):
    """
    Load the pre-trained model and tokenizer.

    Args:
        model_path (str): Path to the pre-trained model.
        model_type (str): Type of the model.
        use_lora (bool, optional): Whether to use LoRA (Low-Rank Adaptation) for the model. Defaults to False.
        bf16 (bool, optional): Whether to use bfloat16 precision. Defaults to False.
        fp16 (bool, optional): Whether to use float16 precision. Defaults to False.

    Returns:
        model: The loaded pre-trained model.
        tokenizer: The loaded tokenizer.
    """
    assert not (bf16 and fp16), "bf16 or fp16, not both"
    if bf16:
        dtype = torch.bfloat16
    elif fp16:
        dtype = torch.float16
    else:
        dtype = torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=dtype,
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    # If using LoRA, configure and apply LoRA
    if use_lora:
        from peft import LoraConfig, TaskType, get_peft_model 
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            target_modules = MODEL_TARGET_MODULES.get(model_type, []),
            r=8,
            lora_alpha=32,
            lora_dropout=0.1,
            inference_mode=False,
            )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
    return model, tokenizer

def truncated_passage(passage, tokenizer, truncate_size):
    encoded_passage = tokenizer.encode(passage, add_special_tokens=False)
    truncated_encoded_passage = encoded_passage[:truncate_size]
    decoded_passage = tokenizer.decode(truncated_encoded_passage)
    return decoded_passage

def preprocessing(example,args,tokenizer):
    """
    Preprocessing function to format input for the model.
    Args:
        example (dict): A dictionary containing the input example with keys 'query', 'retrieval_result', 'chosen', and 'rejected'.
        args (dict): A dictionary containing various arguments including 'Augment_template', 'QA_template', 'task_type', 'model_args', 'data_args', and 'passage_separator'.
        tokenizer (Tokenizer): A tokenizer object used to process the input text.
    Returns:
        dict: A dictionary containing the formatted input for the model. The keys are:
            - "prompt" (str or list): The formatted prompt for the model (for DPO task).
            - "chosen" (str): The chosen text from the example (for DPO task).
            - "rejected" (str): The rejected text from the example (for DPO task).
            - "input_text" (str or list): The formatted input text for the model (for SFT task).
    """
    one_item = {}
    query = example['query']
    retrieve_result = example['retrieval_result']

    # Template definitions
    Augment_template = args.get('Augment_template', "Background:\n{}\n\nQuestion: {}\nAnswer:")
    QA_template = args.get('QA_template', "Question: {}\nAnswer:")
    task_type = args.get('task_type', "DPO")
    model_args = ModelArguments(**args['model_args'])
    data_args = DataArguments(**args['data_args'])

    sep_token = args.get('passage_separator', "\n")
    passage = sep_token.join(retrieve_result)
    new_aug_psg = truncated_passage(passage, tokenizer, data_args.max_passage_length)

    if task_type == "DPO":
        # Format the prompt based on the model type
        if model_args.model_type == "minicpm2":
            aug_input = f"<User>{Augment_template.format(new_aug_psg, query)}<AI>"
            
        elif model_args.model_type == "minicpm3":
            input_data = Augment_template.format(new_aug_psg, query)
            aug_input = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": input_data},
            ]
            aug_input = tokenizer.apply_chat_template(aug_input, add_generation_prompt=True, tokenize=False)

        else:
            if model_args.use_template:
                aug_input = [{"role": "user", "content": Augment_template.format(new_aug_psg, query)}]
                aug_input = tokenizer.apply_chat_template(aug_input, add_generation_prompt=True, tokenize=False)
            else:
                aug_input = Augment_template.format(new_aug_psg, query)
                
        one_item["prompt"] = aug_input
        one_item["chosen"] = example["chosen"]["text"]
        one_item["rejected"] = example["rejected"]["text"]
    
    elif task_type == "SFT":
        # Format the prompt based on the model type
        if model_args.model_type == "minicpm2":
            aug_input = f'<User>{Augment_template.format(new_aug_psg, query)}<AI>{example["chosen"]["text"]}'
            
        elif model_args.model_type == "minicpm3":
            input_data = Augment_template.format(new_aug_psg, query)
            aug_input = [
                {"role": "system", "content": "You are a helpful assistant."}, 
                {"role": "user", "content": input_data}, 
                {"role": "assistant", "content": example["chosen"]['text']}
            ]
            aug_input = tokenizer.apply_chat_template(aug_input, add_generation_prompt=False, tokenize=False)

        else:
            if model_args.use_template:
                input_data = Augment_template.format(new_aug_psg, query)
                aug_input = [{"role": "user", "content": input_data}, {"role": "assistant", "content": example["chosen"]["text"]}]
                aug_input = tokenizer.apply_chat_template(aug_input, add_generation_prompt=False, tokenize=False)
            else:
                aug_input = Augment_template.format(new_aug_psg, query)
                aug_input = f'<user>{Augment_template.format(new_aug_psg, query)}<assistant>{example["chosen"]["text"]}'

        one_item["input_text"] = aug_input
    
    return one_item

def parse_args():
    parser = argparse.ArgumentParser(description="Training")

    parser.add_argument('--model_name_or_path', type=str, required=True, help="Path to pre-trained model.")
    parser.add_argument('--task_type', type=str, required=True, help="The type of task (e.g., DPO/SFT)")
    parser.add_argument('--train_data_path', type=str, required=True, help="Path to the train data.")
    parser.add_argument('--eval_data_path', type=str, required=True, help="Path to the dev data.")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory to save the model.")
    parser.add_argument('--logging_dir', type=str, required=True, help="Directory for logs.")
    parser.add_argument('--use_lora', action="store_true", help="Use LoRA during training.")
    parser.add_argument('--deepspeed', type=str, required=True, help="Path to the DeepSpeed config file.")
    parser.add_argument('--config_file', type=str, required=True, help="Path to the YAML configuration file.")

    args, unknown = parser.parse_known_args()

    assert args.task_type in ["DPO", "SFT"], f"Invalid task_type: {args.task_type}. Must be 'DPO' or 'SFT'."

    return args

def main():
    args = parse_args()
    config = load_yaml_config(args.config_file)

    model_args = ModelArguments(**config['model_args'])
    data_args = DataArguments(**config['data_args'])
    training_args = TrainingArguments(**config['training_args'])

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO
    )
    logger.info("Training/evaluation parameters %s", training_args)
    logger.info("MODEL parameters %s", model_args)
    logger.info("DATA parameters %s", data_args)

    model, tokenizer = load_model_and_tokenizer(
        model_path=args.model_name_or_path,
        model_type = model_args.model_type,
        use_lora=args.use_lora,
        bf16=training_args.bf16,
        fp16=training_args.fp16,
    )
    config["task_type"] = args.task_type
    
    partial_preprocess = partial(preprocessing, args=config, tokenizer=tokenizer)

    if os.path.exists(args.eval_data_path):
        train_dataset = load_dataset("json", data_files=args.train_data_path, split="train")
        eval_dataset = load_dataset("json", data_files=args.eval_data_path, split="train")
        if args.task_type == "DPO":
            train_dataset = train_dataset.map(partial_preprocess)
            eval_dataset = eval_dataset.map(partial_preprocess)
    else:
        dataset = load_dataset("json", data_files=args.train_data_path, split="train")
        if args.task_type == "DPO":
            dataset = dataset.map(partial_preprocess)
        
        train_dataset = dataset.shuffle(seed=42).train_test_split(test_size=0.1, seed=42)["train"]
        eval_dataset = dataset.shuffle(seed=42).train_test_split(test_size=0.1, seed=42)["test"]

    if args.task_type == "DPO":
        dpo_training_args = DPOConfig(
            optim = training_args.optim,
            output_dir = args.output_dir,
            save_steps = training_args.save_steps,
            eval_steps = training_args.eval_steps,
            per_device_train_batch_size = training_args.per_device_train_batch_size,
            per_device_eval_batch_size = training_args.per_device_eval_batch_size,
            learning_rate = float(training_args.learning_rate),
            eval_strategy = training_args.eval_strategy,
            logging_steps = training_args.logging_steps,
            logging_dir = args.logging_dir,
            bf16 = training_args.bf16,
            num_train_epochs = training_args.num_train_epochs,
            max_length = data_args.max_length, 
            max_prompt_length = data_args.max_prompt_length
        )
        
        dpo_trainer = DPOTrainer(
            model,
            ref_model=None,
            args=dpo_training_args,
            train_dataset=train_dataset,
            eval_dataset =eval_dataset,
            tokenizer=tokenizer,
        )
        dpo_trainer.train()
        dpo_trainer.save_model()

    elif args.task_type == "SFT":
        sft_training_args = SFTConfig(
            optim = training_args.optim,
            output_dir = args.output_dir,
            save_steps = training_args.save_steps,
            eval_steps = training_args.eval_steps,
            per_device_train_batch_size = training_args.per_device_train_batch_size,
            per_device_eval_batch_size = training_args.per_device_eval_batch_size,
            learning_rate = float(training_args.learning_rate),
            eval_strategy = training_args.eval_strategy,
            logging_steps = training_args.logging_steps,
            logging_dir = args.logging_dir,
            bf16 = training_args.bf16,
            num_train_epochs = training_args.num_train_epochs,
            max_seq_length = data_args.max_seq_length, 
            dataset_text_field='input_text',
        )
        
        sft_trainer = SFTTrainer(
            model,
            args=sft_training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
        )
        sft_trainer.train()
        sft_trainer.save_model()

if __name__ == '__main__':
    main()



