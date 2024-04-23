import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Load stopwords
stop_words = set(stopwords.words('english'))

# Path to your input text file
input_file_path = 'inputText_TemperatureWikipedia.txt'
# Path for the preprocessed text file
output_file_path = 'preprocessed_inputText_TemperatureWikipedia.txt'

def preprocess_text(text):
    # Lowercase the text
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize text
    words = word_tokenize(text)
    # Remove stopwords
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)

# Read, preprocess, and write the text
with open(input_file_path, 'r', encoding='utf-8') as infile, \
     open(output_file_path, 'w', encoding='utf-8') as outfile:
    for line in infile:
        preprocessed_line = preprocess_text(line)
        outfile.write(preprocessed_line + '\n')

print("Preprocessing complete. Output saved to:", output_file_path)
