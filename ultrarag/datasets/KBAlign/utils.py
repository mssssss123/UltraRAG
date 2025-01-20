import re
import json
import os

def iter_jsonl(fname, cnt=None):
    i = 0
    with open(fname, "r") as fin:
        for line in fin:
            if i == cnt:
                break
            yield json.loads(line)
            i += 1

def dump_jsonl(data, index, file_path,reference):
    """
    Appends a list of data entries to a JSON Lines file.
    Each entry in the JSON Lines file will contain the provided index, data, and golden reference.
    Args:
        data (list): A list of data entries to be written to the file.
        index (int): An index value to be included in each entry.
        file_path (str): The path to the JSON Lines file where data will be appended.
        reference (str): A reference value to be included as "golden_reference" in each entry.
    Returns:
        None
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf8") as f:
        for line in data:
            entry = {"index": index, "data": line,"golden_reference":reference}
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def read_and_concatenate_jsonl(chunk_files_path):
    """
    Reads all JSONL files listed in chunk_files_path, extracts arrays from each line, and concatenates them.
    
    :param chunk_files_path: A list of file paths pointing to JSONL files.
    :return: A single concatenated list containing all arrays from the files.
    """
    combined_array = [] 
    for file_path in chunk_files_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if isinstance(data, list):  
                        combined_array.extend(data)
                    else:
                        raise ValueError(f"Expected an array, but got: {type(data)}")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    
    return combined_array

def get_nested_arrays(jsonl_files):
    """
    Reads a list of JSONL (JSON Lines) files and returns a list of nested arrays.

    Args:
        jsonl_files (list of str): List of file paths to JSONL files.

    Returns:
        list: A list containing the parsed JSON objects from each line of the input files.
    """
    nested_arrays = []
    for file in jsonl_files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())  
                nested_arrays.append(data)
    return nested_arrays

def count_words(string):
    """
    Counts the number of Chinese characters and English words in a given string.

    Args:
        string (str): The input string to be analyzed.

    Returns:
        int: The total count of Chinese characters and English words in the string.
    """
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", string)
    num_chinese = len(chinese_chars)

    text_without_chinese = re.sub(r"[\u4e00-\u9fff]", "", string)
    words = text_without_chinese.split()
    num_english = len(words)

    return num_chinese + num_english