import sys
import os

from gensim.models import Word2Vec

model_path_hum = 'PretrainedModels/word2vec_HumidityWiki.model'
word_vectors_hum = Word2Vec.load(model_path_hum).wv

model_path_temp = 'PretrainedModels/word2vec_TemperatureWiki.model'
word_vectors_temp = Word2Vec.load(model_path_temp).wv

predefined_list = ["temperature", "humidity"]

labels = list()

def findLabelWord2Vec(word, preDefinedWord, word2vec, threshold):
    if(word in word2vec):
        if(preDefinedWord in word2vec):
            similarity = word2vec.similarity(word, preDefinedWord)
            #print("\n")
            #print(f"{word} vs {preDefinedWord} = {similarity}")
            if(similarity >= threshold):
                #print("\n")
                #print(f"[Label]: {word} vs {preDefinedWord} = {similarity}")
                labels.append(preDefinedWord)


def split_strings_with_angle_brackets(string_list):
    output_list = []

    for string in string_list:
        temp_list = [string]
        temp_list = [part for elem in temp_list for part in elem.split('>')]
        temp_list = [part for elem in temp_list for part in elem.split('<')]
        temp_list = [part for elem in temp_list for part in elem.split('{')]
        temp_list = [part for elem in temp_list for part in elem.split('}')]
        temp_list = [part for elem in temp_list for part in elem.split(':')]
        temp_list = [part for elem in temp_list for part in elem.split(',')]
        output_list.extend([part for part in temp_list if part])
    
    return output_list


def get_unique_strings(string_list):
    unique_list = []
    seen = set()
    for string in string_list:
        if string not in seen:
            seen.add(string)
            unique_list.append(string)
    
    return unique_list


def extract_unique_words(file_path):
    extractedWords = list()

    with open(file_path, 'r') as file:
        for line in file:
            words = line.split()
            output_list = split_strings_with_angle_brackets(words)
            modified_list = []
            for w in output_list:
                modified_string = w.replace('/', ' ')
                modified_string = w.replace('"', ' ')
                modified_string = modified_string.replace(' ', '')
                modified_list.append(modified_string)
            extractedWords += modified_list

    return get_unique_strings(extractedWords)


def findLabels(input_file, threshold):
    unique_words = extract_unique_words(input_file)
    #print(unique_words)

    for word in unique_words:
        findLabelWord2Vec(word, "temperature", word_vectors_temp, threshold)
        findLabelWord2Vec(word, "humidity", word_vectors_hum, threshold)

    uniqeLabels = get_unique_strings(labels)

    #print(uniqeLabels)
    return uniqeLabels

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
    
    output_file_path = input_file_path.replace('.input', '.output')
    
    try:
        with open(input_file_path, 'r') as input_file:
            uniqeLabels = findLabels(input_file_path, 0.1)
        
    except Exception as e:
        print(f"Could not open input file: {e}")
        sys.exit(1)

    try:
        with open(output_file_path, 'w') as output_file:
            if(len(uniqeLabels) == 0):
                output_file.write("{\n")
                output_file.write("\"Result\" : \"Error\",\n")
                output_file.write("\"Cause\" : \"Could not find label\"\n")
                output_file.write("}\n")
            else:
                output_file.write("{\n")
                output_file.write("\"Result\" : \"Success\",\n")
                output_file.write(f"\"ID\" : {input_id}\n")
                output_file.write(f"\"MinAccuracy\" : {accThreshold}\n")
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

if __name__ == "__main__":
    main()