#import nltk
import os
import sys
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


def findLabelNLTK(classifier, inputFile, threshold):
    json_string = inputFile.read()
    new_features = extract_features(json_string)

    # Get the probability distribution over labels
    prob_dist = classifier.prob_classify(new_features)
    # Get the predicted label
    predicted_label = classifier.classify(new_features)
    # Get the confidence of the predicted label
    confidence = prob_dist.prob(predicted_label)
    
    unique_list = []
    if(confidence >= float(threshold)):
        #print(f'Predicted label: {predicted_label}')
        #print(f'Confidence: {confidence}')
        unique_list.append(predicted_label)
        
    return unique_list

def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <file path> <ID> <AccuracyThreshold>")
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    input_id = sys.argv[2]
    accThreshold = sys.argv[3]
    
    base_name = os.path.basename(input_file_path)
    if not base_name.endswith('.input'):
        print("Error: Wrong input file name format (Expected: name.input)")
        sys.exit(1)
    
    output_file_path_tmp = input_file_path.replace('.input', '.output_tmp')
    
    try:
        # Load the trained model
        with open('NLTK/Model1/PretrainedModels/nltk_model.pkl', 'rb') as file:
            loaded_classifier = pickle.load(file)

    except Exception as e:
        print(f"Could not open model: {e}")
        sys.exit(1)

    try:
        with open(input_file_path, 'r') as input_file:
            uniqeLabels = findLabelNLTK(loaded_classifier, input_file, accThreshold)
        
    except Exception as e:
        print(f"Could not open input file: {e}")
        sys.exit(1)

    try:
        with open(output_file_path_tmp, 'w') as output_file:
            if(len(uniqeLabels) == 0):
                output_file.write("{\n")
                output_file.write("\"$Result\" : \"Error\",\n")
                output_file.write("\"$Cause\" : \"Could not find label\"\n")
                output_file.write("}\n")
            else:
                output_file.write("{\n")
                output_file.write("\"$Result\" : \"Success\",\n")
                output_file.write(f"\"$ID\" : \"{input_id}\",\n")
                output_file.write(f"\"$MinAccuracy\" : {accThreshold},\n")
                output_file.write("\"Labels\" : [\n")
                for w in uniqeLabels:
                    if( uniqeLabels.index(w) == len(uniqeLabels) - 1):
                        output_file.write(f"\t\"{w}\"\n")
                    else:
                        output_file.write(f"\t\"{w}\",\n")
                output_file.write("\t]\n")
                output_file.write("}\n")
    except Exception as e:
        print(f"Could not open output file: {e}")
        sys.exit(1)
        
    try:
        output_file_path = output_file_path_tmp.replace('.output_tmp', '.output')
        os.rename(output_file_path_tmp, output_file_path)
    except Exception as e:
        print(f"Could not rename tmp file: {e}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()