import os
import re
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, 'data', 'chroma_db')
POLICIES_DIR = os.path.join(BASE_DIR, 'data', 'policies')

def ingest():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="policies"
    )
    
    texts = []
    metadatas = []
    
    # Process chargeback_reason_codes.md
    with open(os.path.join(POLICIES_DIR, 'chargeback_reason_codes.md'), 'r') as f:
        content = f.read()
        chunks = re.split(r'\n## ', content)
        for chunk in chunks[1:]: # skip title
            if chunk.startswith("Reason Code "):
                header_line = chunk.split('\n')[0]
                reason_code = re.search(r'Reason Code ([\d\.]+)', header_line)
                if reason_code:
                    texts.append("## " + chunk)
                    metadatas.append({"reason_code": reason_code.group(1)})
                    
    # Process merchant_category_rules.md
    with open(os.path.join(POLICIES_DIR, 'merchant_category_rules.md'), 'r') as f:
        content = f.read()
        chunks = re.split(r'\n## ', content)
        for chunk in chunks[1:]:
            if chunk.startswith("MCC "):
                header_line = chunk.split('\n')[0]
                mcc = re.search(r'MCC (\d+)', header_line)
                if mcc:
                    texts.append("## " + chunk)
                    metadatas.append({"mcc_code": mcc.group(1)})
                    
    # Process precedent_cases.md (Basic splitting)
    with open(os.path.join(POLICIES_DIR, 'precedent_cases.md'), 'r') as f:
        content = f.read()
        chunks = re.split(r'\n## ', content)
        for chunk in chunks[1:]:
            texts.append("## " + chunk)
            metadatas.append({"source": "precedent_cases"})
    
    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    print(f"Ingested {len(texts)} chunks into Chroma.")

if __name__ == "__main__":
    ingest()
