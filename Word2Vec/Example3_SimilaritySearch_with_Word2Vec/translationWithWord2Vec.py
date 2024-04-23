import json
from gensim.models import Word2Vec

# Load your custom-trained Word2Vec model
model_path = 'word2vec_model.model'
word_vectors = Word2Vec.load(model_path).wv

# Function to find the best match in the model's vocabulary for a given key
def find_best_match_for_key(key, word_vectors, predefined_list):
    best_match = None
    highest_similarity = -1  # Initialize with -1, since similarity ranges from -1 to 1
    
    # Ensure the key is in lowercase to match the model's format
    key = key.lower()
    
    if key not in word_vectors:
        return key  # Return the original key if not found in model's vocabulary

    for predefined_word in predefined_list:
        if predefined_word in word_vectors:
            similarity = word_vectors.similarity(key, predefined_word)
            print(f"key: {key} category: {predefined_word} similarity: {similarity}.")
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = predefined_word
        else:
            print(f"Warning: {predefined_word} is not in the model's vocabulary.")

    return best_match if best_match else key  # Return the original key if no match found

# Predefined list of words
predefined_list = ["temperature", "energy", "sound"]

# Read JSON object from file
input_file_path = 'input.json'
with open(input_file_path, 'r') as file:
    json_object = json.load(file)

# Create a new JSON object with keys replaced by their best matches
new_json_object = {}
for key, value in json_object.items():
    new_key = find_best_match_for_key(key, word_vectors, predefined_list)
    
    # Check if the new_key already exists in new_json_object and append a number to make it unique
    original_new_key = new_key
    counter = 1
    while new_key in new_json_object:
        new_key = f"{original_new_key}_{counter}"
        counter += 1
    
    new_json_object[new_key] = value

# Write the new JSON object to an output file
output_file_path = 'output.json'
with open(output_file_path, 'w') as file:
    json.dump(new_json_object, file, indent=4)

print(f"Output JSON with updated keys has been saved to {output_file_path}")