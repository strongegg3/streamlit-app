from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
base_url=os.getenv("OPENAI_API_BASE")
model="gpt-3.5-turbo"



def build_vectorstore(text, db_path):
    # 文本切分
    splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=100)
    docs = splitter.create_documents([text])

    # 嵌入与存储
    embeddings = OpenAIEmbeddings( model = "text-embedding-ada-002",
                                   openai_api_key = OPENAI_API_KEY,
                                   base_url=base_url)
    vectorstore = Chroma.from_documents(documents=docs,
                                        embedding=embeddings,
                                        persist_directory=db_path)  #指定本地向量数据库文件夹的路径
    vectorstore.persist()
    #这里是保险措施，强制向量库内容存到路径下，怕有的不会存
    return vectorstore

def load_vectorstore(db_path):
    embeddings = OpenAIEmbeddings()
    return Chroma(persist_directory=db_path, embedding_function=embeddings)

def create_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_type="mmr", k=8)
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.3,base_url=base_url,model=model)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever,chain_type="map_reduce")
    return qa_chain
