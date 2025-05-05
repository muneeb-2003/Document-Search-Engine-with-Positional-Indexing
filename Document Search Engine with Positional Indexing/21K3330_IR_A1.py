import os
import tkinter as tk
from tkinter import scrolledtext
from nltk.stem import PorterStemmer

# Load stop words from a file
def load_stop_words(stop_words_file):
    with open(stop_words_file, "r") as f:
        return set(word.strip() for word in f.readlines())
#--------------------------------------------------------------------------------------------
# Process the index for a document
def process_index(tokens, doc_id, inverted_index, positional_index):
    positions = {}
    for i, token in enumerate(tokens):
        if token not in positions:
            positions[token] = {doc_id: [i]}
        elif doc_id not in positions[token]:
            positions[token][doc_id] = [i]
        else:
            positions[token][doc_id].append(i)
#--------------------------------------------------------------------------------------------
    # Update the inverted index and positional index with document positions
    for token, doc_positions in positions.items():
        update_index(token, doc_positions, inverted_index)
        update_index(token, doc_positions, positional_index)

#--------------------------------------------------------------------------------------------
# Update the inverted or positional index with document positions
def update_index(token, doc_positions, index):
    if token not in index:
        index[token] = doc_positions
    else:
        for existing_doc_id, existing_positions_list in doc_positions.items():
            if existing_doc_id not in index[token]:
                index[token][existing_doc_id] = existing_positions_list
            else:
                index[token][existing_doc_id].extend(existing_positions_list)
                

#--------------------------------------------------------------------------------------------
# Retrieve documents where two words are within a specified distance
def near_operator(word1, word2, k, positional_index):
    result = set()
    positions1 = positional_index.get(word1, {})
    positions2 = positional_index.get(word2, {})
    # Check for proximity of positions and add matching documents to the result set
    for doc_id, pos1 in positions1.items():
        pos2 = positions2.get(doc_id, [])
        for p1 in pos1:
            for p2 in pos2:
                if 0 < abs(p1 - p2) <= k:
                    result.add(doc_id)
                    break

    return result

#--------------------------------------------------------------------------------------------
# Process a document and update the inverted and positional index
def process_document(file_path, stop_words, inverted_index, doc_ids, positional_index):
    ps = PorterStemmer()
    with open(file_path, 'r', encoding='utf-8') as f:
        # Tokenize the document and filter out stop words
        tokens = [ps.stem(word.strip().lower()) for word in f.read().split() if word.strip().lower() not in stop_words]

        doc_id = len(doc_ids) + 1
        doc_ids[doc_id] = file_path

        # Process positional index
        process_index(tokens, doc_id, inverted_index, positional_index)

#--------------------------------------------------------------------------------------------
# Build the inverted index, document IDs, and positional index for a folder of documents
def build_index(folder_path, stop_words_file):
    stop_words = load_stop_words(stop_words_file)
    inverted_index = {}
    doc_ids = {}
    positional_index = {}

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            process_document(file_path, stop_words, inverted_index, doc_ids, positional_index)

    return inverted_index, doc_ids, positional_index

#--------------------------------------------------------------------------------------------
# Convert an infix expression to postfix notation
def infix_to_postfix(infix_tokens):
    precedence = {'NOT': 3, 'AND': 2, 'OR': 1, '(': 0, ')': 0, 'NEAR': 2, 'PHRASE': 2}
    output = []
    operator_stack = []

    # Convert infix expression to postfix notation
    for token in infix_tokens:
        if token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            operator_stack.pop()  # Pop '('
        elif token in precedence:
            while operator_stack and precedence[operator_stack[-1]] > precedence[token]:
                output.append(operator_stack.pop())
            operator_stack.append(token)
        else:
            output.append(token.lower())

    while operator_stack:
        output.append(operator_stack.pop())

    return output

#--------------------------------------------------------------------------------------------
# Perform AND operation on two sets
def and_operation(set1, set2):
    if set1 and set2:
        return set(set1).intersection(set2)
    else:
        return set()

#--------------------------------------------------------------------------------------------
# Perform OR operation on two sets
def or_operation(set1, set2):
    return set(set1).union(set2)

#--------------------------------------------------------------------------------------------
# Perform NOT operation on a set of document IDs
def not_operation(a, doc_ids):
    return set(doc_ids).difference(a)

#--------------------------------------------------------------------------------------------
# Process a query and return the resulting set of document IDs
def process_query(query, inverted_index, doc_ids, positional_index):
    ps = PorterStemmer()
    query = query.replace('(', '( ')
    query = query.replace(')', ' )')
    query_tokens = query.split()
    query_tokens = [ps.stem(token) for token in query_tokens]

    for i in range(len(query_tokens)):
        if query_tokens[i] in {'and', 'or', 'not', 'near', 'phrase'}:
            query_tokens[i] = query_tokens[i].upper()

    results_stack = []
    postfix_query = infix_to_postfix(query_tokens)

    # Process the query using the postfix notation
    for token in postfix_query:
        if token not in {'AND', 'OR', 'NOT', 'NEAR', 'PHRASE'}:
            token = token.replace('(', ' ')
            token = token.replace(')', ' ')
            token = token.lower()
            if token == 'phrase':
                operand = results_stack.pop()
                distance = int(results_stack.pop())
                results_stack.append(phrase_query(operand, positional_index, inverted_index))
            elif token == 'near':
                distance = int(results_stack.pop())
                operand2 = results_stack.pop()
                operand1 = results_stack.pop()
                results_stack.append(near_operator(operand1, operand2, distance, positional_index))
            else:
                token_info = inverted_index.get(token)
                results_stack.append(token_info)
        elif token == 'AND':
            operand1 = results_stack.pop()
            operand2 = results_stack.pop()
            results_stack.append(and_operation(operand1, operand2))
        elif token == 'OR':
            operand1 = results_stack.pop()
            operand2 = results_stack.pop()
            results_stack.append(or_operation(operand1, operand2))
        elif token == 'NOT':
            operand = results_stack.pop()
            results_stack.append(not_operation(operand, doc_ids))

    return results_stack.pop()

def main():
    folder_path = "ResearchPapers" 
    stop_words_file = 'Stopword-List.txt'  

    inverted_index, doc_ids, positional_index = build_index(folder_path, stop_words_file)
    print_summary_console(inverted_index, doc_ids)

    root = tk.Tk()
    root.title("Document Search Engine")

#--------------------------------------------------------------------------------------------
    # Run the GUI
    run_gui(root, inverted_index, doc_ids, positional_index)

def run_gui(root, inverted_index, doc_ids, positional_index):
    def search_query():
        query = query_entry.get()
        result = process_query(query, inverted_index, doc_ids, positional_index)
        result_text.config(state=tk.NORMAL)
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, f"Query: {query}\nResult: {result}")
        result_text.config(state=tk.DISABLED)
    query_frame = tk.Frame(root)
    query_frame.pack(pady=10)

    query_label = tk.Label(query_frame, text="Enter your query (eg: R1 AND R2 OR R3):")
    query_label.grid(row=0, column=0, padx=5)
    query_entry = tk.Entry(query_frame, width=50)
    query_entry.grid(row=0, column=1, padx=5)
    search_button = tk.Button(query_frame, text="Search", command=search_query)
    search_button.grid(row=0, column=2, padx=5)
    result_text = scrolledtext.ScrolledText(root, width=80, height=10, wrap=tk.WORD, state=tk.DISABLED)
    result_text.pack(pady=10)
    root.mainloop()

#--------------------------------------------------------------------------------------------
def print_summary_console(inverted_index, doc_ids):
    print(f'\nInverted Index:')
    for term, postings in inverted_index.items():
        print(f'{term}: {postings}')

    print(f'\nDocument IDs:')
    for doc_id, file_path in doc_ids.items():
        print(f'{doc_id}: {file_path}')

    print(f'\nTotal Unique Words: {len(inverted_index)}')

#--------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
