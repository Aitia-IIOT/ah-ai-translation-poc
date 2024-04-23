from gensim.models import Word2Vec

# Load your custom-trained Word2Vec model
model_path_hum = 'word2vec_HumidityWiki.model'
word_vectors_hum = Word2Vec.load(model_path_hum).wv

model_path_temp = 'word2vec_TemperatureWiki.model'
word_vectors_temp = Word2Vec.load(model_path_temp).wv

# Predefined list of words to compare similarities
predefined_list = ["temperature", "humidity", "fahrenheit"]

# Function to find the best match from the predefined list for a given word
def find_best_match(word, word_vectors_hum, word_vectors_temp, predefined_list):
    best_match = None
    highest_similarity = -1  # Initialize with -1, since similarity ranges from -1 to 1

    for predefined_word in predefined_list:
        if (word in word_vectors_temp): 
            if predefined_word in word_vectors_temp:
                similarity_temp = word_vectors_temp.similarity(word, predefined_word)
                print(f"[TEMP]: {word} vs {predefined_word} = {similarity_temp}")
                if similarity_temp > highest_similarity:
                    highest_similarity = similarity_temp
                    best_match = "temperature"
            else:
                print(f"[TEMP]: {word} is not in the word_vectors_temp model's vocabulary.")
        else:
            print(f"[TEMP]: {word} is not in the word_vectors_temp model's vocabulary.")
        
        if (word in word_vectors_hum):   
            if predefined_word in word_vectors_hum:
                similarity_hum = word_vectors_hum.similarity(word, predefined_word)
                print(f"[HUMI]: {word} vs {predefined_word} = {similarity_hum}")
                if similarity_hum > highest_similarity:
                    highest_similarity = similarity_hum
                    best_match = "humidity"  
            else:
                print(f"[HUMI]: {word} is not in the word_vectors_hum model's vocabulary.")
        else:
            print(f"[HUMI]: {word} is not in the word_vectors_hum model's vocabulary.")
        print("")
    return best_match

# Example inputs to find their best matches
input_words = ["temperature", "c", "k", "celsius", "kelvin", "energy", "water", "vapor"]

# Find and print the best match for each input word
for word in input_words:
    print("---------------------------------------------")
    best_match = find_best_match(word, word_vectors_hum, word_vectors_temp, predefined_list)
    print(f"Best match for '{word}': {best_match}")
    print("---------------------------------------------")