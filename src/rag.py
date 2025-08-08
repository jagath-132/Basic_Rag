from langchain.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os 

document_loader = DirectoryLoader(
    path= "documents",
    glob= "**/*.docx",
    loader_cls= UnstructuredFileLoader
)
documents = document_loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size= 1500,
    chunk_overlap= 350
)
split_docs = text_splitter.split_documents(documents)

embedding = HuggingFaceBgeEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(
    documents= split_docs,
    embedding= embedding,
    persist_directory= "chroma-db",
    collection_name= "collections"
)
vectorstore.persist()

retriever = vectorstore.as_retriever(search_kwargs= {"k" : 4})

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model= "llama3-70b-8192",
    groq_api_key= groq_api_key,
    temperature= 0.7
)

rag_chain = RetrievalQA.from_chain_type(
    llm= llm,
    retriever= retriever,
    return_source_documents= True
)

while True:
    query = input("\n AI | Ask me anything based on documents | to quit ('exit' or 'quit') : ")
    if query.lower() in ("exit", "quit"):
        break
    response = rag_chain.invoke({'query' : query})
    print("\nAnswer:", response['result'])