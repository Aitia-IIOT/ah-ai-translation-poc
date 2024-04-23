import nltk
import os
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords
from nltk.classify.util import accuracy as nltk_accuracy
from nltk.tokenize import word_tokenize

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Function to read files and assign labels based on file names
def read_files_in_directory(directory):
    data = []
    for label in os.listdir(directory):
        label_dir = os.path.join(directory, label)
        if os.path.isdir(label_dir):
            for file in os.listdir(label_dir):
                file_path = os.path.join(label_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    data.append((text, label))
    return data

# Extract features from text
def extract_features(text):
    words = word_tokenize(text)
    return {word: True for word in words if word not in stopwords.words('english')}

# Read dataset
data_directory = "Models"  # Update this to the path of your text files
data = read_files_in_directory(data_directory)

# Split data into training and testing sets (e.g., 80% train, 20% test)
train_size = int(len(data) * 0.8)
train_data = data[:train_size]
test_data = data[train_size:]

# Feature extraction
train_features = [(extract_features(text), label) for (text, label) in train_data]
test_features = [(extract_features(text), label) for (text, label) in test_data]

# Train the classifier
classifier = NaiveBayesClassifier.train(train_features)

# Evaluate the classifier
accuracy = nltk_accuracy(classifier, test_features)
print(f"Accuracy: {accuracy:.2f}")

# Classify a new text
#new_input = "{\"relay1state\" : false}"
#new_features = extract_features(new_input)
#print(f"Classification: {classifier.classify(new_features)}")


import json

#Open EC Example
with open('Models/Model_EC/SAE_EC_DataModel.xml_10', 'r') as file:
    json_string = file.read()

print(json_string)

new_features = extract_features(json_string)
print(f"Classification: {classifier.classify(new_features)}")

#Open PLM Example
with open('Models/Model_PLM/SAE_PLM_DataModel.xml_107', 'r') as file:
    json_string = file.read()

print(json_string)

new_features = extract_features(json_string)
print(f"Classification: {classifier.classify(new_features)}")

#Open Modified EC Example
with open('Test/SAE_EC_DataModel_10_modified.xml', 'r') as file:
    json_string = file.read()

print(json_string)

new_features = extract_features(json_string)
print(f"Classification: {classifier.classify(new_features)}")