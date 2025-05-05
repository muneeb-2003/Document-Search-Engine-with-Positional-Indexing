# Document Search Engine with Positional Indexing

This project is a Python-based document search engine that builds an inverted index with positional information to enable advanced querying functionalities. The search engine supports complex queries such as `AND`, `OR`, `NOT`, `NEAR`, and `PHRASE` operations, which are executed on the indexed documents. The search results are displayed in a graphical user interface (GUI) built with Tkinter, providing a user-friendly experience for querying document collections.

## Features:
- **Inverted Indexing**: Efficient indexing of documents based on term frequency and positions within the document.
- **Positional Index**: Stores the positions of words within documents to support proximity queries.
- **Advanced Querying**: Supports Boolean operations (`AND`, `OR`, `NOT`), proximity search (`NEAR`), and phrase search (`PHRASE`).
- **GUI Interface**: Built with Tkinter to allow users to input queries and view results interactively.
- **Stop Word Removal**: Filters out common stop words to enhance the search accuracy.
- **Stemming**: Uses the Porter Stemmer to reduce words to their root form for better matching.

## Requirements:
- Python 3.x
- Tkinter
- NLTK library

