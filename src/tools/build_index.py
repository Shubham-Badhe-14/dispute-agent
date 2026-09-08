import os
import re
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
POLICIES_DIR = os.path.join(BASE_DIR, 'data', 'policies')
CHROMA_DIR = os.path.join(BASE_DIR, 'data', 'chroma_db')

def parse_reason_code(text):
    match = re.search(r'Reason Code ([\d\.]+)', text)
    if match:
        return match.group(1)
    return None

def parse_mcc_code(text):
    match = re.search(r'MCC (\d{4})', text)
    if match:
        return match.group(1)
    return None

def build_index():
    print("Building RAG Index...")
    
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    all_chunks = []
    
    # 1. Process Reason Codes
    with open(os.path.join(POLICIES_DIR, 'chargeback_reason_codes.md'), 'r') as f:
        rc_docs = markdown_splitter.split_text(f.read())
        for doc in rc_docs:
            if "Header 2" in doc.metadata:
                code = parse_reason_code(doc.metadata["Header 2"])
                if code:
                    doc.metadata["reason_code"] = code
            all_chunks.append(doc)
            
    # 2. Process Merchant Rules
    with open(os.path.join(POLICIES_DIR, 'merchant_category_rules.md'), 'r') as f:
        mcc_docs = markdown_splitter.split_text(f.read())
        for doc in mcc_docs:
            if "Header 2" in doc.metadata:
                code = parse_mcc_code(doc.metadata["Header 2"])
                if code:
                    doc.metadata["mcc_code"] = code
            all_chunks.append(doc)
            
    # 3. Process Precedents
    with open(os.path.join(POLICIES_DIR, 'precedent_cases.md'), 'r') as f:
        prec_docs = markdown_splitter.split_text(f.read())
        all_chunks.extend(prec_docs)
        
    print(f"Generated {len(all_chunks)} chunks.")
    
    # Initialize Embeddings
    print("Initializing embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Persist to Chroma
    print("Persisting to ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name="policies"
    )
    
    print(f"Index built successfully at {CHROMA_DIR}")

if __name__ == "__main__":
    build_index()
