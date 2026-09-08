import os
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, 'data', 'chroma_db')

# Initialize once to avoid overhead on every tool call
_embeddings = None
_vectorstore = None

def get_vectorstore():
    global _embeddings, _vectorstore
    if _vectorstore is None:
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        _vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=_embeddings,
            collection_name="policies"
        )
    return _vectorstore

@tool
def retrieve_policies(dispute_reason: str = None, mcc_code: str = None, query: str = None) -> str:
    """
    Retrieve relevant policies and rules for a given dispute reason or MCC code.
    Pass 'query' if a generic semantic search is needed.
    """
    vectorstore = get_vectorstore()
    retrieved_chunks = []
    
    # 1. Exact Match via Metadata filtering
    if dispute_reason:
        # Get chunks tagged with this reason code
        rc_results = vectorstore.get(where={"reason_code": dispute_reason})
        if rc_results and rc_results["documents"]:
            retrieved_chunks.extend(rc_results["documents"])
            
    if mcc_code:
        mcc_results = vectorstore.get(where={"mcc_code": mcc_code})
        if mcc_results and mcc_results["documents"]:
            retrieved_chunks.extend(mcc_results["documents"])
            
    # 2. Semantic Search Fallback / Supplement
    # If we didn't find exact matches, or the user passed a custom query, use semantic search
    semantic_query = query
    if not semantic_query and not retrieved_chunks:
        # Construct a query if none was provided and exact match failed
        parts = []
        if dispute_reason: parts.append(f"reason code {dispute_reason}")
        if mcc_code: parts.append(f"MCC {mcc_code}")
        if parts:
            semantic_query = "policy for " + " and ".join(parts)
            
    if semantic_query:
        # Use relevance scores (higher is better, typically 0 to 1)
        # Note: Depending on the distance metric, we might just use L2 distance.
        # Chroma default is L2. similarity_search_with_score returns lower=better for L2.
        results = vectorstore.similarity_search_with_score(semantic_query, k=2)
        
        # Threshold: For L2 distance on normalized embeddings, < 1.0 is generally good.
        # We will use a strict threshold so we don't return garbage.
        DISTANCE_THRESHOLD = 1.0 
        
        for doc, score in results:
            if score < DISTANCE_THRESHOLD:
                if doc.page_content not in retrieved_chunks:
                    retrieved_chunks.append(doc.page_content)

    if not retrieved_chunks:
        return "No relevant policy found."
        
    return "\n\n---\n\n".join(retrieved_chunks)
