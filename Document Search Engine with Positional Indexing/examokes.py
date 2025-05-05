import os
from nltk.stem import PorterStemmer, WordNetLemmatizer
import nltk

class Tokenizer:
    def __init__(self, stop_words_file):
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = self.load_stop_words(stop_words_file)
        self.doc_count = 0
        self.total_tokens_before = 0
        self.total_tokens_after = 0
        self.tokens = set()
        self.token_counts = {}
        self.posting_lists = {}
        self.inverted_index = {}

    def load_stop_words(self, stop_words_file):
        with open(stop_words_file, "r") as f:
            return set(word.strip() for word in f.readlines())

    def process_document(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            tokens = [word.strip().lower() for word in f.read().split()]

            self.total_tokens_before += len(tokens)

            tokens = [self.lemmatizer.lemmatize(self.stemmer.stem(token)) for token in tokens if token not in self.stop_words]

            self.total_tokens_after += len(tokens)

            self.tokens.update(tokens)

            for token in set(tokens):
                self.token_counts[token] = self.token_counts.get(token, 0) + 1

                if token not in self.posting_lists:
                    self.posting_lists[token] = [file_path]
                else:
                    self.posting_lists[token].append(file_path)

                if token not in self.inverted_index:
                    self.inverted_index[token] = {file_path}
                else:
                    self.inverted_index[token].add(file_path)

    def process_folder(self, folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.endswith('.txt'):
                self.process_document(file_path)
                self.doc_count += 1

    def print_summary(self):
        print(f'Total Documents: {self.doc_count}')
        print(f'Total Tokens (Before): {self.total_tokens_before}')
        print(f'Total Tokens (After removing stop words): {self.total_tokens_after}')
        print(f'Token Counts: {len(self.token_counts)}')

    def print_tokens_sorted(self):
        sorted_tokens = sorted(self.tokens)
        for token in sorted_tokens:
            print(f'{token}: {", ".join(self.posting_lists.get(token, []))}')

    def handle_query(self, query):
        stack = []
        operators = {'AND', 'OR', 'NOT'}

        for term in query:
            if term not in operators:
                term_ids = self.inverted_index.get(term, set())
                stack.append(term_ids)
            else:
                if term == 'NOT':
                    operand = stack.pop()
                    result = set(self.inverted_index.keys()) - operand
                else:
                    operand2 = stack.pop()
                    operand1 = stack.pop()
                    if term == 'AND':
                        result = operand1.intersection(operand2)
                    elif term == 'OR':
                        result = operand1.union(operand2)

                stack.append(result)

        if stack:
            return stack[0]
        else:
            return set()

    def normal_query(self, query):
        currentIndex = 0
        result_docs = set()
        universal_set = set(range(1, 51))
        error = False

        while currentIndex < len(query):
            current_term = self.stemmer.stem(query[currentIndex])

            if current_term == "not":
                if currentIndex + 1 < len(query):
                    result_for_word = set(self.inverted_index[self.stemmer.stem(query[currentIndex + 1])])
                    taking_not = universal_set - result_for_word
                    result_docs = result_docs.intersection(taking_not)
                    currentIndex += 2
                else:
                    print("Invalid Query, 'NOT' operator should be followed by a term.")
                    error = True
                    break
            else:
                result_docs = result_docs.union(set(self.inverted_index[current_term]))
                currentIndex += 1

            if currentIndex < len(query):
                if query[currentIndex] == "and":
                    currentIndex += 1
                elif query[currentIndex] == "or":
                    currentIndex += 1
                else:
                    print("Invalid Query, operators should be 'AND' or 'OR' between terms.")
                    error = True
                    break

        if not error:
            print(result_docs)
            return result_docs
        else:
            return set()

# Example usage:
queries = [
    ['transformer', 'AND', 'model'],
    ['deep', 'AND', 'learning', 'OR', 'neural', 'AND', 'network'],
    ['natural', 'AND', 'language', 'NOT', 'processing']
]

def main():
    nltk.download('wordnet')

    folder_path = "ResearchPapers"  # Change this to the actual path of your folder
    stop_words_file = 'Stopword-List.txt'  # Replace with the actual path to your stop words file

    tokenizer = Tokenizer(stop_words_file)
    tokenizer.process_folder(folder_path)
    tokenizer.print_summary()
    tokenizer.print_tokens_sorted()

    for query in queries:
        result = tokenizer.normal_query(query)
        print(f"Query: {query}, Result: {result}")

if __name__ == "__main__":
    main()
