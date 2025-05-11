import os
from dotenv import load_dotenv
import time
from langchain_community.retrievers import PineconeHybridSearchRetriever
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from pinecone_text.sparse import BM25Encoder
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pinecone_util import create_index
from langchain.prompts import ChatPromptTemplate

load_dotenv()

# Load environment variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")

# Constants
BM25_INDEX_DIR = "server/bm25_indexes"

# Initialize OpenAI LLM and embeddings
llm = init_chat_model("gpt-4.1-mini", 
                      model_provider="openai",
                      api_key=openai_api_key)
    
embeddings = OpenAIEmbeddings(api_key=openai_api_key, 
                              model="text-embedding-3-large")

def create_bm25_encoder():
    """
    Creates and returns a BM25Encoder by loading and merging all BM25 encoder files 
    from the bm25_indexes directory.
    
    Returns:
        BM25Encoder: The loaded or default BM25 encoder
    """
    # First try server/bm25_indexes, then fallback to bm25_indexes
    bm25_index_dir = BM25_INDEX_DIR
    if not os.path.exists(bm25_index_dir):
        bm25_index_dir = "bm25_indexes"
        
    try:
        if os.path.exists(bm25_index_dir):
            bm25_files = [os.path.join(bm25_index_dir, f) for f in os.listdir(bm25_index_dir) 
                          if f.endswith('.json')]
            
        if bm25_files:
            # Load the first encoder as base
            base_encoder = BM25Encoder().load(bm25_files[0])
            
            # Merge additional encoders if any
            if len(bm25_files) > 1:
                for file_path in bm25_files[1:]:
                    try:
                        encoder = BM25Encoder().load(file_path)
                        # Merge encoders by updating vocabulary and document frequencies
                        base_encoder.merge_encoder(encoder)
                    except Exception as e:
                        print(f"Error loading encoder from {file_path}: {e}")
            
            return base_encoder
        else:
            return BM25Encoder().default()
    except Exception as e:
        print(f"Error loading BM25 encoders: {e}")
        return BM25Encoder().default()

def create_hybrid_retriever():
    """
    Creates and returns a PineconeHybridSearchRetriever using all BM25 encoders in the directory.
    """
    try:
        index = create_index()
        bm25_encoder = create_bm25_encoder()
    
        # Create the retriever with the correct namespace
        retriever = PineconeHybridSearchRetriever(
            embeddings=embeddings, 
            sparse_encoder=bm25_encoder, 
            index=index,
            text_key="text",
            alpha=0.5,
            top_k=3,
            namespace="biz-to-bricks-namespace"
        )
            
        return retriever
        
    except Exception as e:
        print(f"Error creating retriever: {e}")
        raise

# Create the retriever (only once)
retriever = create_hybrid_retriever()

def format_docs(docs):
    """Format the documents into a string."""
    return "\n\n".join(doc.page_content for doc in docs)

# Prompt template
template = """Answer the question based only on the following context:
{context}

Question: {question}

"""

prompt = ChatPromptTemplate.from_template(template)

# Create the Langchain runnable pipeline
hybrid_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def execure_hybrid_chain(query):
    """Execute the hybrid chain."""
    return hybrid_chain.invoke(query)
