import os
from nltk.stem import PorterStemmer

def load_stop_words(stop_words_file):
    with open(stop_words_file, "r") as f:
        return set(word.strip() for word in f.readlines())

def process_positional_index(tokens, doc_id, inverted_index, positional_index):
    positions = {}
    for i, token in enumerate(tokens):
        if token not in positions:
            positions[token] = {doc_id: [i]}
        elif doc_id not in positions[token]:
            positions[token][doc_id] = [i]
        else:
            positions[token][doc_id].append(i)

    for token, doc_positions in positions.items():
        if token not in inverted_index:
            inverted_index[token] = doc_positions
        else:
            for existing_doc_id, existing_positions_list in doc_positions.items():
                if existing_doc_id not in inverted_index[token]:
                    inverted_index[token][existing_doc_id] = existing_positions_list
                else:
                    inverted_index[token][existing_doc_id].extend(existing_positions_list)

    for token, doc_positions in positions.items():
        if token not in positional_index:
            positional_index[token] = doc_positions
        else:
            for existing_doc_id, existing_positions_list in doc_positions.items():
                if existing_doc_id not in positional_index[token]:
                    positional_index[token][existing_doc_id] = existing_positions_list
                else:
                    positional_index[token][existing_doc_id].extend(existing_positions_list)

def near_operator(word1, word2, k, positional_index):
    result = set()
    positions1 = positional_index.get(word1, {})
    positions2 = positional_index.get(word2, {})

    for doc_id, pos1 in positions1.items():
        pos2 = positions2.get(doc_id, [])
        for p1 in pos1:
            for p2 in pos2:
                if 0 < abs(p1 - p2) <= k:
                    result.add(doc_id)
                    break

    return result

def process_document(file_path, stop_words, inverted_index, doc_ids, positional_index):
    ps = PorterStemmer()
    with open(file_path, 'r', encoding='utf-8') as f:
        tokens = [ps.stem(word.strip().lower()) for word in f.read().split() if word.strip().lower() not in stop_words]

        doc_id = len(doc_ids) + 1
        doc_ids[doc_id] = file_path

        # Process positional index
        process_positional_index(tokens, doc_id, inverted_index, positional_index)

def build_inverted_index(folder_path, stop_words_file):
    stop_words = load_stop_words(stop_words_file)
    inverted_index = {}
    doc_ids = {}
    positional_index = {}

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            process_document(file_path, stop_words, inverted_index, doc_ids, positional_index)

    return inverted_index, doc_ids, positional_index

def print_summary(inverted_index, doc_ids):
    print(f'Inverted Index:')
    for term, postings in inverted_index.items():
        print(f'{term}: {postings}')

    print(f'\nDocument IDs:')
    for doc_id, file_path in doc_ids.items():
        print(f'{doc_id}: {file_path}')

    print(f'\nTotal Unique Words: {len(inverted_index)}')

def infix_to_postfix(infix_tokens):
    precedence = {'NOT': 3, 'AND': 2, 'OR': 1, '(': 0, ')': 0, 'NEAR': 2, 'PHRASE': 2}
    output = []
    operator_stack = []

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

def AND_op(word1, word2):
    if word1 and word2:
        return set(word1).intersection(word2)
    else:
        return set()

def OR_op(word1, word2):
    return set(word1).union(word2)

def NOT_op(a, doc_ids):
    return set(doc_ids).difference(a)

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
            results_stack.append(AND_op(operand1, operand2))
        elif token == 'OR':
            operand1 = results_stack.pop()
            operand2 = results_stack.pop()
            results_stack.append(OR_op(operand1, operand2))
        elif token == 'NOT':
            operand = results_stack.pop()
            results_stack.append(NOT_op(operand, doc_ids))

    return results_stack.pop()

def main():
    folder_path = "ResearchPapers"  # Replace with the actual path of your folder
    stop_words_file = 'Stopword-List.txt'  # Replace with the actual path to your stop words file

    inverted_index, doc_ids, positional_index = build_inverted_index(folder_path, stop_words_file)
    print_summary(inverted_index, doc_ids)

    # Example queries
    queries = [
        'transformer AND model',
        'cancer AND learning',
        'transformer OR model ',
        'heart',
        'heart AND attack ',
        'NOT model ',
        'feature AND selection AND redundency',
        'feature AND selection AND classification ',
        'tubing ',
        'NOT classification  AND NOT feature ',
        'heart NEAR attack',
        'programming PHRASE language'
    ]

    for query in queries:
        result = process_query(query, inverted_index, doc_ids, positional_index)
        print(f"Query: {query}, Result: {result}")

if __name__ == "__main__":
    main()
