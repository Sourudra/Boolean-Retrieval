import re
import streamlit as st
from collections import defaultdict

# Tokenization function
def tokenize(text):
    return set(re.findall(r'\b\w+\b', text.lower()))

# Function to build inverted index
def build_inverted_index(docs):
    index = defaultdict(set)
    for doc_id, text in docs.items():
        words = tokenize(text)
        for word in words:
            index[word].add(doc_id)
    return index

# Function to perform Boolean retrieval
def boolean_retrieval(index, query):
    query = query.lower().strip()
    result_docs = set(index.keys())  # Start with all documents
    
    if ' and ' in query:
        terms = query.split(' and ')
        result_docs = set(index.get(terms[0].strip(), set()))
        for term in terms[1:]:
            term = term.strip()
            result_docs = result_docs.intersection(index.get(term, set()))
    
    elif ' or ' in query:
        terms = query.split(' or ')
        result_docs = set()
        for term in terms:
            term = term.strip()
            result_docs = result_docs.union(index.get(term, set()))
    
    elif ' not ' in query:
        # Split query by ' not '
        split_query = query.split(' not ')
        if len(split_query) == 2:
            include_terms = split_query[0].strip()
            exclude_term = split_query[1].strip()
            
            # Handle terms before 'not'
            if ' and ' in include_terms:
                include_terms = include_terms.split(' and ')
                docs_to_include = set(index.get(include_terms[0].strip(), set()))
                for term in include_terms[1:]:
                    term = term.strip()
                    docs_to_include = docs_to_include.intersection(index.get(term, set()))
            elif ' or ' in include_terms:
                include_terms = include_terms.split(' or ')
                docs_to_include = set()
                for term in include_terms:
                    term = term.strip()
                    docs_to_include = docs_to_include.union(index.get(term, set()))
            else:
                docs_to_include = set(index.get(include_terms, set()))
            
            # Exclude documents containing the term after 'not'
            result_docs = docs_to_include.difference(index.get(exclude_term, set()))
        
        else:
            raise ValueError("Complex 'NOT' queries are not supported. Please use simple 'NOT' queries.")

    else:
        terms = re.findall(r'\b\w+\b', query)
        result_docs = set()
        for token in terms:
            result_docs = result_docs.union(index.get(token, set()))
    
    return result_docs

# Streamlit app
def main():
    st.title("Boolean Retrieval System")
    
    st.write("Upload documents to perform Boolean queries.")

    # Upload documents
    uploaded_files = st.file_uploader("Choose text files", accept_multiple_files=True, type=["txt"])

    if uploaded_files:
        # Read documents
        documents = {}
        for file in uploaded_files:
            documents[file.name] = file.read().decode('utf-8')
        
        # Show the count of uploaded documents
        doc_count = len(documents)
        st.success(f"Successfully uploaded {doc_count} document(s).")
        
        # Display uploaded documents with preview
        st.subheader("Uploaded Documents")
        for doc_id, content in documents.items():
            with st.expander(f"{doc_id}"):
                st.text_area("Document Content", value=content, height=300)

        # Build inverted index
        inverted_index = build_inverted_index(documents)

        # Query input and button
        query = st.text_input("Enter your Boolean query (supports AND, OR, NOT):")
        if st.button("Submit Query"):
            if query:
                try:
                    # Perform Boolean retrieval
                    results = boolean_retrieval(inverted_index, query)
                    result_count = len(results)
                    
                    # Display results count and results
                    if result_count > 0:
                        st.success(f"Query matched {result_count} document(s).")
                        st.subheader("Results")
                        for doc_id in results:
                            if doc_id in documents:
                                result_content = documents[doc_id]
                                st.info(f"**{doc_id}:**\n{result_content}")
                            else:
                                st.warning(f"Document ID {doc_id} not found in the uploaded documents.")
                    else:
                        st.error("No documents matched the query.")
                except ValueError as e:
                    st.error(str(e))

if __name__ == "__main__":
    main()
