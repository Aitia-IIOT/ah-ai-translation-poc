from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import logging

# Enable logging for Gensim – useful to see training progress and other messages
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Path to your text file
text_file_path = 'preprocessed_inputText_TemperatureWikipedia.txt'

# Step 1: Prepare the data
# Assuming each line of your text file is a new sentence.
# The `LineSentence` class from Gensim can stream text lines from disk directly.
sentences = LineSentence(text_file_path)

# Step 2: Train the Word2Vec model
model = Word2Vec(sentences=sentences, vector_size=300, window=5, min_count=3, workers=4)

# Save the model to disk
model.save("word2vec_model.model")

# Step 3: Use the model for context recognition
# Loading the model from disk
model = Word2Vec.load("word2vec_model.model")

# Function to find similar words/context
def find_similar_words(word, model):
    try:
        similar_words = model.wv.most_similar(word)
        return similar_words
    except KeyError:
        return "The word is not in the vocabulary!"

# Example usage
word = 'k'
similar_words = find_similar_words(word, model)
print(f"Words similar to '{word}':")
for word, similarity in similar_words:
    print(f"{word}: {similarity}")

