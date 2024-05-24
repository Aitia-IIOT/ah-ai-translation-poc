import nltk
import os
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords
from nltk.classify.util import accuracy as nltk_accuracy
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist, DictionaryProbDist
import json
import pickle

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

#Save the trained model
with open('nltk_model.pkl', 'wb') as file:
    pickle.dump(classifier, file)

# Classify a new text
#new_input = "{\"relay1state\" : false}"
#new_features = extract_features(new_input)
#print(f"Classification: {classifier.classify(new_features)}")

def testWithNLTK(filePath):
    #Open Modified EC Example
    with open(filePath, 'r') as file:
        json_string = file.read()
    new_features = extract_features(json_string)

    #print(json_string)
    print(f'\nTesting: {filePath}')

    # Get the probability distribution over labels
    prob_dist = classifier.prob_classify(new_features)
    # Get the predicted label
    predicted_label = classifier.classify(new_features)
    # Get the confidence of the predicted label
    confidence = prob_dist.prob(predicted_label)
    print(f'Predicted label: {predicted_label}')
    print(f'Confidence: {confidence}')


testWithNLTK('Test/IPC_2581A_test_orig.XML')
testWithNLTK('Test/IPC_2581A_test.XML')
testWithNLTK('Test/IPC_2581A_test2.XML')
testWithNLTK('Test/SAE_EC_DataModel_10_modified.xml')
testWithNLTK('Test/SAE_EC_DataModel_10_modified_2.xml')
testWithNLTK('Test/SAE_PLM_DataModel_107_modified.xml')
testWithNLTK('Test/TestInput_Json.input')
testWithNLTK('Test/Empty.input')