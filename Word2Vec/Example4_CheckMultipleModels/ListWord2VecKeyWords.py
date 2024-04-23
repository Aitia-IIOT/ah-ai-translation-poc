from gensim.models import Word2Vec

# Load your Word2Vec model
model_path = 'word2vec_TemperatureWiki.model'  # Update this to the path of your model
model = Word2Vec.load(model_path)

# List all words in the model's vocabulary
words = list(model.wv.index_to_key)  # For gensim version 4.0.0 and above

# Print the words
for word in words:
    print(word)

# If you just want to see the number of words in the vocabulary
print(f"Total words in vocabulary: {len(words)}")