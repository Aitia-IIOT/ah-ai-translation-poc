#import nltk
#import os
#from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords
#from nltk.classify.util import accuracy as nltk_accuracy
from nltk.tokenize import word_tokenize
#from nltk.probability import FreqDist, DictionaryProbDist

import pickle

# Download necessary NLTK resources
#nltk.download('punkt')
#nltk.download('stopwords')

# Extract features from text
def extract_features(text):
    words = word_tokenize(text)
    return {word: True for word in words if word not in stopwords.words('english')}

def findLabelNLTK(classifier, filePath):
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

# Load the trained model
with open('NLTK/Model1/PretrainedModels/nltk_model.pkl', 'rb') as file:
    loaded_classifier = pickle.load(file)

findLabelNLTK(loaded_classifier, 'Test/IPC_2581A_test_orig.XML')
findLabelNLTK(loaded_classifier, 'Test/IPC_2581A_test.XML')
findLabelNLTK(loaded_classifier, 'Test/IPC_2581A_test2.XML')
findLabelNLTK(loaded_classifier, 'Test/SAE_EC_DataModel_10_modified.xml')
findLabelNLTK(loaded_classifier, 'Test/SAE_EC_DataModel_10_modified_2.xml')
findLabelNLTK(loaded_classifier, 'Test/SAE_PLM_DataModel_107_modified.xml')
findLabelNLTK(loaded_classifier, 'Test/TestInput_Json.input')
findLabelNLTK(loaded_classifier, 'Test/Empty.input')