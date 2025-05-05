import re
from nltk.stem import PorterStemmer
from collections import defaultdict

# Stemming initialization
ps = PorterStemmer()

# Read stop words from a file
def read_stop_words(stop_words_file):
    with open(stop_words_file, 'r') as file:
        stop_words = set(file.read().split())
    return stop_words

# Create the inverted index
def build_inverted_index(stop_words):
    inverted_index = defaultdict(list)
    documents = {}

    for doc_no in range(56):  # Assuming there are 56 documents
        with open(f"C:/Users/Lenovo/OneDrive/Desktop/ir assignment 1/ResearchPapers/research_paper_{doc_no}.txt", 'r') as file:
            next(file)  # Skip the first line
            speech_text = file.read().replace('\n', ' ')

        # Cleaning documents
        speech_text = re.sub('  ', ' ', speech_text)
        speech_text = re.sub(r"[^\w\s]", ' ', speech_text)
        key = f'speech_{doc_no}'
        documents.setdefault(key, [])
        documents[key].append(speech_text)

        # Removing stopwords and lowercase
        speech_text = speech_text.lower()
        speech_text = [word if word not in stop_words else '' for word in speech_text.split()]
        stemmed = [ps.stem(word) for word in speech_text if word]

        # Creating inverted index
        for term in set(stemmed):
            inverted_index[term].append(doc_no)

    return inverted_index, documents

# def build_inverted_index(stop_words):
#     inverted_index = defaultdict(list)
#     documents = {}

    # for doc_no in range(23):
    #     with open(f"C:/Users/Lenovo/OneDrive/Desktop/ir assignment 1/ResearchPapers/research_paper_{doc_no}.txt", 'r') as file:
    #     # Rest of your code
        
    #     # # with open(f"Trump_Speeches/speech_{doc_no}.txt", 'r') as file:
    #     # with open(f"C:/Users/Lenovo/OneDrive/Desktop/ir assignment 1/ResearchPapers/research_paper.txt", 'r') as file:

    #         next(file)  # Skip the first line
    #         speech_text = file.read().replace('\n', ' ')

    #     # Cleaning documents
    #     speech_text = re.sub('  ', ' ', speech_text)
    #     speech_text = re.sub(r"[^\w\s]", ' ', speech_text)
    #     key = f'speech_{doc_no}'
    #     documents.setdefault(key, [])
    #     documents[key].append(speech_text)

    #     # Removing stopwords and lowercase
    #     speech_text = speech_text.lower()
    #     speech_text = [word if word not in stop_words else '' for word in speech_text.split()]
    #     stemmed = [ps.stem(word) for word in speech_text if word]

    #     # Creating inverted index
    #     for term in set(stemmed):
    #         inverted_index[term].append(doc_no)

    # return inverted_index, documents

# Infix to postfix query conversion
def postfix(infix_tokens):
    precedence = {'NOT': 3, 'AND': 2, 'OR': 1, '(': 0, ')': 0}
    output = []
    operator_stack = []

    for token in infix_tokens:
        if token == '(':
            operator_stack.append(token)
        elif token == ')':
            operator = operator_stack.pop()
            while operator != '(':
                output.append(operator)
                operator = operator_stack.pop()
        elif token in precedence:
            if operator_stack:
                current_operator = operator_stack[-1]
                while operator_stack and precedence[current_operator] > precedence[token]:
                    output.append(operator_stack.pop())
                    if operator_stack:
                        current_operator = operator_stack[-1]
            operator_stack.append(token)
        else:
            output.append(token.lower())

    while operator_stack:
        output.append(operator_stack.pop())

    return output

# AND operation for two posting lists
def AND_op(word1, word2):
    if word1 and word2:
        return set(word1).intersection(word2)
    else:
        return set()

# OR operation for two posting lists
def OR_op(word1, word2):
    return set(word1).union(word2)

# NOT operation for a posting list and document IDs
def NOT_op(a, doc_ids):
    return set(doc_ids).symmetric_difference(a)

# Boolean query processing
def process_query(q, inverted_index, doc_ids):
    q = q.replace('(', '( ')
    q = q.replace(')', ' )')
    q = q.split(' ')
    query = []

    for i in q:
        query.append(ps.stem(i))
    for i in range(len(query)):
        if query[i] in {'and', 'or', 'not'}:
            query[i] = query[i].upper()

    results_stack = []
    postfix_queue = postfix(query)

    for i in postfix_queue:
        if i not in {'AND', 'OR', 'NOT'}:
            i = i.replace('(', ' ')
            i = i.replace(')', ' ')
            i = i.lower()
            i = inverted_index.get(i)
            results_stack.append(i)
        elif i == 'AND':
            a = results_stack.pop()
            b = results_stack.pop()
            results_stack.append(AND_op(a, b))
        elif i == 'OR':
            a = results_stack.pop()
            b = results_stack.pop()
            results_stack.append(OR_op(a, b))
        elif i == 'NOT':
            a = results_stack.pop()
            results_stack.append(NOT_op(a, doc_ids))

    return results_stack.pop()

# Positonal query processing
def positional_query(q, dictionary_positional):
    q = re.sub(r"AND", "", q)
    q = re.sub(r"  ", " ", q)
    q = q.split(' ')
    query = []

    for i in q:
        query.append(ps.stem(i))

    word1 = dictionary_positional.get(query[0])
    word2 = dictionary_positional.get(query[1])
    anding = set(word1).intersection(word2)

    q[2] = re.sub(r"/", "", q[2])
    answer = []
    skip = int(q[2]) + 1

    for i in anding:
        pp1 = dictionary_positional.get(query[0])[i]
        pp2 = dictionary_positional.get(query[1])[i]
        plen1 = len(pp1)
        plen2 = len(pp2)
        ii = jj = 0

        while ii != plen1:
            while jj != plen2:
                if abs(pp1[ii] - pp2[jj]) == skip:
                    answer.append(i)
                elif pp2[jj] > pp1[ii]:
                    break
                jj += 1
            ii += 1

    answer = list(dict.fromkeys(answer))
    return answer

# Checking whether word is present within position
def doc_check(ii, jj, plen1, plen2, skip, pp1, pp2):
    while ii != plen1:
        while jj != plen2:
            if abs(pp1[ii] - pp2[jj]) == skip:
                return 1
            elif pp2[jj] > pp1[ii]:
                break
            jj += 1
        ii += 1

    return 0

# Phrase query processing
def phrase_query(q, dictionary_positional, inverted_index):
    q = q.replace('"', '')
    q = q.split()

    query = []
    for i in q:
        query.append(ps.stem(i))
        query.append('AND')
    query.pop()
    query = " ".join(query)
    anding = process_query(query, inverted_index, doc_ids)
    answer = []
    query = query.replace('AND', '')
    query = query.split()

    for i in anding:
        pp1 = dictionary_positional.get(query[0].lower())[i]
        flag = []
        skip = 1

        for x in range(1, len(query)):
            pp2 = dictionary_positional.get(query[x].lower())[i]
            plen1 = len(pp1)
            plen2 = len(pp2)
            ii = jj = 0
            flag.append(doc_check(ii, jj, plen1, plen2, skip, pp1, pp2))
            skip = skip + 1

        if 0 not in flag:
            answer.append(i)

    answer = list(dict.fromkeys(answer))
    return answer

# Example usage
stop_words_file = 'Stopword-List.txt'  # Replace with the actual path to your stop words file
stop_words = read_stop_words(stop_words_file)

inverted_index, documents = build_inverted_index(stop_words)

# Example query processing:
doc_ids = list(range(56))  # Assuming there are 56 documents
boolean_query_result = process_query('(word1 AND word2) OR NOT word3', inverted_index, doc_ids)
positional_query_result = positional_query('word1 AND word2 /2', dictionary_positional)
phrase_query_result = phrase_query('"word1" AND "word2"', dictionary_positional, inverted_index)
