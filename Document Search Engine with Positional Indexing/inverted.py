import os
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import nltk
import re
import string

nltk.download('punkt')

# Define the directory containing your files
directory = r'C:\Users\Lenovo\OneDrive\Desktop\ir assignment 1\ResearchPapers'
tokens = {}
No_stop_word_tokens = {}  # Dictionary to store processed tokens from all files
index = {}  # Inverted index to store tokens and corresponding documents

def remove_urls(tokens):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    # Iterate through the tokens and filter out URLs
    tokens_without_urls = [token for token in tokens if not url_pattern.match(token)]
    return tokens_without_urls

def remove_special_characters(tokens):
    # Define the pattern to match special characters
    special_char_pattern = re.compile(r'[^\w\s]')  # Matches any character that is not a word character or whitespace

    # Iterate through the tokens and remove special characters
    tokens_without_special_chars = [special_char_pattern.sub('', token) for token in tokens]

    # Remove empty tokens after removing special characters
    tokens_without_special_chars = [token for token in tokens_without_special_chars if token]

    return tokens_without_special_chars

def remove_numbers(tokens):
    # Define the pattern to match numbers
    number_pattern = re.compile(r'\b\d+\b')

    # Iterate through the tokens and remove tokens containing numbers
    tokens_without_numbers = [token for token in tokens if not number_pattern.match(token)]

    return tokens_without_numbers

document_data = {}
n = 0
# Loop through each file in the directory
for filename in os.listdir(directory):
    # Construct the full path to the file
    file_path = os.path.join(directory, filename)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        # Read the content of the file
        file_content = file.read()

        # Tokenize the content
        tokens = word_tokenize(file_content)

        # Stemming and other processing
        ps = PorterStemmer()
        token_case_fold = [ps.stem(word) for word in tokens]

        custom_stop_words = set([
            'a', 'is', 'the', 'of', 'all', 'and', 'to', 'can', 'be', 'as',
            'once', 'for', 'at', 'am', 'are', 'has', 'have', 'had', 'up',
            'his', 'her', 'in', 'on', 'no', 'we', 'do'
        ])

        punctuation = set(string.punctuation)

        # Remove punctuation and stop words
        No_punctuation_tokens = [word for word in token_case_fold if word not in punctuation]
        No_stop_word_tokens = [word for word in No_punctuation_tokens if word.lower() not in custom_stop_words]

        No_url_tokens= remove_urls(No_stop_word_tokens)

        No_special_char_tokens = remove_special_characters(No_url_tokens)

        No_number_tokens = remove_numbers(No_special_char_tokens)

        # Store document data
        document_data[filename] = {
            'tokens': No_stop_word_tokens,  # Store processed tokens
             'term_count': len(set(No_number_tokens))
        }

# for filename, data in document_data.items():
#     print(f"Document: {filename}")
#     print("Processed Tokens:", data['tokens'])
#     print()

grand_total = sum(data['term_count'] for data in document_data.values())
print("Grand Total of Terms:", grand_total)

for filename, data in document_data.items():
  if  'cancer'  in data['tokens'] and 'learn' in data['tokens'] :
      print(filename)

class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def __str__(self):
        result = []
        current = self.head
        while current:
            result.append(str(current.data))
            current = current.next
        return ' -> '.join(result)


# Implement inverted index
inverted_index = {}
document_frequency = {}

for filename, data in document_data.items():
    tokens = data['tokens']
    unique_tokens_in_doc = set(tokens)
    for token in unique_tokens_in_doc:
        if token not in inverted_index:
            inverted_index[token] = LinkedList()
            document_frequency[token] = 1
        else:
            document_frequency[token] += 1
        inverted_index[token].append(filename)

# Example of how to print inverted index
# for term, posting_list in inverted_index.items():
#     print(f"Term: {term}, Posting List: {posting_list}, Document Frequency: {document_frequency[term]}")

# Example: Search for documents containing specific terms
search_terms = ['transformer', 'model']
documents_containing_terms = None

for term in search_terms:
    if term in inverted_index:
        posting_list = inverted_index[term]
        current = posting_list.head
        documents_containing_this_term = set()

        # Add documents containing the current term to a temporary set
        while current:
            documents_containing_this_term.add(current.data)
            current = current.next

        if documents_containing_terms is None:
            # Initialize with the first set of documents
            documents_containing_terms = documents_containing_this_term
        else:
            # Intersect with subsequent sets of documents
            documents_containing_terms.intersection_update(documents_containing_this_term)

print("Documents containing 'transformer' and 'model':", documents_containing_terms)

c = 1
for i in documents_containing_terms:
  print(f"{c} -- {i}")
  c+=1