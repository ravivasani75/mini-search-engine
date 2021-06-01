import os
import json
import re
from collections import defaultdict

def tokenize(text):
    # Simple tokenization based on non-word characters
    tokens = re.findall(r'\b\w+\b', text.lower())
    return tokens

def build_index(data_directory):
    inverted_index = defaultdict(list)
    
    # Iterate over all JSON files in the data directory
    for filename in os.listdir(data_directory):
        if filename.endswith(".json"):
            filepath = os.path.join(data_directory, filename)
            with open(filepath, 'r') as file:
                document = json.load(file)
                url = document["url"]
                content = document["content"]
                tokens = tokenize(content)
                doc_length = len(tokens)
                token_counts = defaultdict(int)
                
                # Count the frequency of each token
                for token in tokens:
                    token_counts[token] += 1
                
                # Update the inverted index
                for token, count in token_counts.items():
                    inverted_index[token].append({
                        "url": url,
                        "frequency": count,
                        "doc_length": doc_length
                    })
    
    return inverted_index

def save_index(index, filepath):
    with open(filepath, 'w') as file:
        json.dump(index, file, indent=4)

if __name__ == "__main__":
    data_directory = "data"
    index = build_index(data_directory)
    save_index(index, "inverted_index.json")
    print(f"Inverted index saved to inverted_index.json")
