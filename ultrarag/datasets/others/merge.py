import argparse
import json
import random
import os
from typing import List

def load_file(file_path: str) -> List[dict]:
    """
    Load data from a JSON or JSONL file and return it as a list of dictionaries.

    Args:
        file_path (str): The path to the JSON or JSONL file.

    Returns:
        List[dict]: A list of dictionaries containing the data from the file.

    Raises:
        ValueError: If the file format is not supported (i.e., not '.json' or '.jsonl').

    Example:
        >>> data = load_file('data.json')
        >>> data = load_file('data.jsonl')
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.endswith('.jsonl'):
            return [json.loads(line) for line in f]
        elif file_path.endswith('.json'):
            return json.load(f)
        else:
            raise ValueError(f"Unsupported file format for {file_path}. Use '.json' or '.jsonl'.")


def load_files(file_list: List[str]) -> List[List[dict]]:
    """
    Load data from a list of JSON or JSONL files and return as a list of lists.
    Args:
        file_list (List[str]): A list of file paths to JSON or JSONL files.
    Returns:
        List[List[dict]]: A list of lists containing the data from each file.
    Raises:
        FileNotFoundError: If any file in the list does not exist.
        ValueError: If any file in the list has an unsupported file format.
    """
    all_data = []
    for file_path in file_list:
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} does not exist.")
            
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if ext == '.jsonl':
                    all_data.append([json.loads(line) for line in f])
                elif ext == '.json':
                    all_data.append(json.load(f))
                else:
                    raise ValueError(f"Unsupported file format for {file_path}. Use '.json' or '.jsonl'.")
        except:
            pass
    return all_data

def split_data(all_data: List[List[dict]], ratios: List[int]) -> List[int]:
    """
    Calculate the quantity of each subset based on the given proportions.

    Args:
        all_data (List[List[dict]]): A list of datasets, where each dataset is a list of dictionaries.
        ratios (List[int]): A list of integers representing the proportions for splitting the data.

    Returns:
        List[int]: A list of integers representing the quantity of each subset based on the given proportions.
    """
    total = sum(ratios)
    all_data_len = sum([len(dataset) for dataset in all_data])
    counts = [int(all_data_len * (r / total)) for dataset, r in zip(all_data, ratios)]
    return counts

def merge_data(all_data: List[List[dict]], counts: List[int], fixed_steps: int = None, random_merge: bool = False) -> List[dict]:
    """
    Merge data based on counts, fixed steps, or randomly.

    Args:
        all_data (List[List[dict]]): A list of datasets, where each dataset is a list of dictionaries.
        counts (List[int]): A list of integers representing the number of items to merge from each dataset.
        fixed_steps (int, optional): If provided, merge data at fixed intervals. Defaults to None.
        random_merge (bool, optional): If True, shuffle the datasets before merging. Defaults to False.

    Returns:
        List[dict]: A list of merged dictionaries from the datasets.
    """
    merged_data = []
    if random_merge or not fixed_steps:
        for dataset, count in zip(all_data, counts):
            random.shuffle(dataset)
            merged_data.extend(dataset[:count])
    else:
        for dataset, count in zip(all_data, counts):
            data = dataset[:count]
            merged_data.extend(data[::fixed_steps])

    return merged_data

def write_output(data: List[dict], output_file: str, output_format: str):
    """
    Write merged data to an output file in JSON or JSONL format.

    Args:
        data (List[dict]): The data to be written to the output file.
        output_file (str): The path to the output file.
        output_format (str): The format of the output file. Must be either 'json' or 'jsonl'.

    Raises:
        ValueError: If the output_format is not 'json' or 'jsonl'.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        if output_format == 'jsonl':
            for entry in data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        elif output_format == 'json':
            json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            raise ValueError("Unsupported output format. Use 'json' or 'jsonl'.")
        
def add_output(data: List[dict], output_file: str, output_format: str):
    """
    Add merged data to an output file in JSON or JSONL format.

    Args:
        data (List[dict]): A list of dictionaries containing the data to be written to the output file.
        output_file (str): The path to the output file where the data will be written.
        output_format (str): The format in which to write the data. Must be either 'json' or 'jsonl'.

    Raises:
        ValueError: If the specified output format is not 'json' or 'jsonl'.
    """
    with open(output_file, 'a', encoding='utf-8') as f:
        if output_format == 'jsonl':
            for entry in data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        elif output_format == 'json':
            json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            raise ValueError("Unsupported output format. Use 'json' or 'jsonl'.")

def merge_main(parser):
    # parser = argparse.ArgumentParser(description="Merge JSON or JSONL files with specified proportions and options.")
    parser.add_argument("--file_list", nargs='+', required=True, help="List of JSON or JSONL files to merge.")
    parser.add_argument("--ratios", nargs='+', type=int, required=True, help="Proportions for each file in format 1:2:3.")
    parser.add_argument("--fixed_steps", type=int, default=None, help="Number of fixed steps for merging.")
    parser.add_argument("--random_merge", action='store_true', help="Whether to shuffle data before merging.")
    parser.add_argument("--output_file", required=True, help="Output file for merged data.")
    parser.add_argument("--output_format", required=True, choices=['json', 'jsonl'], help="Output format: 'json' or 'jsonl'.")

    args, unknown=parser.parse_known_args()

    all_data = load_files(args.file_list)

    counts = split_data(all_data, args.ratios)

    merged_data = merge_data(all_data, counts, fixed_steps=args.fixed_steps, random_merge=args.random_merge)

    write_output(merged_data, args.output_file, args.output_format)
