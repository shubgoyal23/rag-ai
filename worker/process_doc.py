
import os
from typing import Any, Dict
from helpers.llm import chat_completion, create_embedding
from helpers.milvus import insert_vector_data, search_similar_text
from helpers.redis import redis_list_add, redis_queue_data_change_status
from helpers.storage import delete_file_from_gcs, download_from_gcs
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    RecursiveUrlLoader
)
import re
from bs4 import BeautifulSoup

def process_doc_handler(job_id: str, job_data: Dict[str, Any]):
    try:
        file_obj, content_type, file_name = download_from_gcs(job_data["doc_id"])
        ext = os.path.splitext(file_name)[1].lower()
        
        # Save to a temporary file
        temp_path = f"/tmp/{file_name}"
        with open(temp_path, "wb") as f:
            f.write(file_obj.read())
            
        # Choose loader based on file extension
        if ext == ".pdf":
            loader = PyPDFLoader(temp_path)
        elif ext == ".txt":
            loader = TextLoader(temp_path)
        elif ext == ".docx":
            loader = UnstructuredWordDocumentLoader(temp_path)
        elif ext in [".xls", ".xlsx"]:
            loader = UnstructuredExcelLoader(temp_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        doc = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=400
        )
        split_docs = text_splitter.split_documents(documents=doc)
        os.remove(temp_path)
        if not delete_file_from_gcs(job_data["doc_id"]):
            redis_list_add("failed:delete_file", job_data["doc_id"])
            
        data = []
        
        for doc in split_docs:
            data.append({"job_id": job_id, "reference_id": f"page No: {doc.metadata.get("page_label")}", "content": doc.page_content, "metadata": doc.metadata})
            
        response = create_embedding([doc.page_content for doc in split_docs])
        for i in range(len(response)):
            data[i]["vector"] = response[i].embedding
        res = insert_vector_data(data)
        if not res:
            return "Document processing failed"
        return "Document processed successfully" 
    except Exception as e:
        redis_queue_data_change_status(job_id, "failed", "Document processing failed")
        print(e)
        return "Document processing failed"

def bs4_extractor(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    return re.sub(r"\n\n+", "\n\n", soup.get_text()).strip()

def process_links_handler(job_id: str, job_data: Dict[str, Any]):
    try:
        loader = RecursiveUrlLoader(
        job_data["doc_id"],
        max_depth=2,
        use_async=True,
        extractor=bs4_extractor,
        metadata_extractor=None,
        exclude_dirs=(),
        timeout=10,
        check_response_status=True,
        continue_on_failure=True,
        prevent_outside=True,
        base_url=None,
        )
        doc = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400
        )
        split_docs = text_splitter.split_documents(documents=doc)
        data = []
        
        for doc in split_docs:
            data.append({"job_id": job_id, "reference_id": f"page No: {doc.metadata.get("page_label")}", "content": doc.page_content, "metadata": doc.metadata})
            
        response = create_embedding([doc.page_content for doc in split_docs])
        for i in range(len(response)):
            data[i]["vector"] = response[i].embedding
        res = insert_vector_data(data)
        if not res:
            return "Document processing failed"
        return "Document processed successfully" 
    except Exception as e:
        redis_queue_data_change_status(job_id, "failed", "Document processing failed")
        print("process_links_handler", e)
        return "Document processing failed"

def process_message_handler(job_id: str, job_data: Dict[str, Any]):
    try:
        message = job_data["input"]
        reference_id = job_data["doc_id"]
        response = create_embedding([message])
        if reference_id:
            context = search_similar_text(response[0].embedding, expr=f"job_id == '{reference_id}'")
        else:
            context = "Context not available for this document use your general knowledge to answer the user query, but inform the user that context is not available for this document"
        SYSTEM_PROMPT = f"""
        You are a helpfull AI Assistant who asnweres user query based on the
        available context retrieved from a document along with page_contents and page number.

        You should only answer the user based on the context and navigate
        the user to open the right page number or link to read more or to download the document.

        Context:
        {context}
        """
        resp = chat_completion(message, SYSTEM_PROMPT)
        if resp:
            return resp
        return "Document processing failed" 
    except Exception as e:
        redis_queue_data_change_status(job_id, "failed", str(e))
        print(e)
        return "Document processing failed"

