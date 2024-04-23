from gensim.models import Word2Vec
from sklearn.cluster import KMeans
import numpy as np

# Load your custom-trained Word2Vec model
model_path = 'word2vec_model.model'
word_vectors = Word2Vec.load(model_path).wv

# Words to cluster
words = ["energy", "c", "k", "celsius", "kelvin", "spectrum", "energy"]

# Transform words into vectors. Note: Only include words that are in the model's vocabulary.
word_vecs = np.array([word_vectors[word] for word in words if word in word_vectors])

# Apply K-means clustering
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(word_vecs)
labels = kmeans.labels_

# Output the cluster for each word
word_to_cluster = {word: label for word, label in zip(words, labels) if word in word_vectors}
for word, cluster in word_to_cluster.items():
    print(f"Word: '{word}' is in cluster #{cluster}")