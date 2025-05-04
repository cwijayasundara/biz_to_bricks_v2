from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone_text.sparse import BM25Encoder
from file_util import load_edited_file_or_parsed_file
from langchain_core.documents import Document
from pinecone_util import create_index

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")

INDEX_NAME = "biz-to-bricks-vector-store-hybrid"
BM25_INDEX_DIR = "bm25_indexes"

embeddings = OpenAIEmbeddings(api_key=openai_api_key, 
                              model="text-embedding-3-large")

def ingest_documents_to_pinecone_hybrid(file_name: str):
    """
    This function ingests documents to Pinecone.
    """
    try:
        text_content, metadata = load_edited_file_or_parsed_file(file_name)

        documents = [Document(page_content=text_content, metadata=metadata)]

        print("Creating/accessing Pinecone index...")
        create_index()

        print("Uploading documents to Pinecone...")
        
        vector_store = PineconeVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,
            index_name=INDEX_NAME,
            namespace="biz-to-bricks-namespace"
        )
        print("Successfully uploaded documents to Pinecone")
        return vector_store
    except Exception as e:
        print(f"Error while ingesting documents: {str(e)}")
        raise

def create_bm25_index(file_name: str):
    """
    This function creates a new BM25 index in Pinecone if it doesn't exist.
    """
    bm25_encoder = BM25Encoder().default()

    text_content, metadata = load_edited_file_or_parsed_file(file_name)

    bm25_encoder.fit([text_content])

    if not os.path.exists(BM25_INDEX_DIR):
        os.makedirs(BM25_INDEX_DIR)

    # remove the file extension
    file_name_without_extension = os.path.splitext(file_name)[0]

    bm25_encoder.dump(f"{BM25_INDEX_DIR}/{file_name_without_extension}.json")

    print(f"BM25 index created successfully for file: {file_name}")

# function to ingest documents to pinecone and bm25 index
def ingest_documents_to_pinecone_and_bm25(file_name: str):
    """
    This function ingests documents to Pinecone and BM25 index.
    """
    ingest_documents_to_pinecone_hybrid(file_name)
    create_bm25_index(file_name)

# test
# if __name__ == "__main__":
#     file_name = "Sample1.md"
#     ingest_documents_to_pinecone_and_bm25(file_name)





