import argparse
import torch
from peft import PeftConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

class LoRAModelMerger:
    def __init__(self, model_name_or_path, lora_name_or_path, save_path):
        self.model_name_or_path = model_name_or_path
        self.lora_name_or_path = lora_name_or_path
        self.save_path = save_path

        # Initialize the base model and tokenizer
        self.base_tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )

    def merge_lora(self):
        """Merge the LoRA model with the base model."""
        print(f"Loading LoRA checkpoint from {self.lora_name_or_path}...")
        # Load the LoRA config and model
        config = PeftConfig.from_pretrained(self.lora_name_or_path)
        self.model = PeftModel.from_pretrained(self.model, self.lora_name_or_path)
        
        self.model = self.model.merge_and_unload()

    def save_model(self):
        """Save the merged model and tokenizer."""
        print(f"Saving merged model and tokenizer to {self.save_path}...")
        self.model.save_pretrained(self.save_path)
        self.base_tokenizer.save_pretrained(self.save_path)
        print("LoRA merge completed and model saved successfully.")

    def merge_and_save(self):
        """Merge LoRA and save the model."""
        self.merge_lora()
        self.save_model()

def main():
    parser = argparse.ArgumentParser(description="Merge LoRA model with base model.")
    parser.add_argument("--model_name_or_path", type=str, required=True, help="Path to the base model or model name.")
    parser.add_argument("--lora_name_or_path", type=str, required=True, help="Path to the LoRA checkpoint.")
    parser.add_argument("--save_path", type=str, required=True, help="Path to save the merged model.")

    args = parser.parse_args()

    lora_merger = LoRAModelMerger(args.model_name_or_path, args.lora_name_or_path, args.save_path)
    lora_merger.merge_and_save()

if __name__ == "__main__":
    main()