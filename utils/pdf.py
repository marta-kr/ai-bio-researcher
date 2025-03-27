import os
import requests
import tempfile

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents.base import Document


async def load_pdf_content(pdf_url: str) -> str:
    """
    Downloads a PDF from pdf_url, loads it as a single document using PyMuPDFLoader,
    and then chunks the text semantically.
    """
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(response.content)
            temp_pdf = tmp.name

        loader = PyMuPDFLoader(temp_pdf, mode="single")
        docs: list[Document] = loader.load()

        os.remove(temp_pdf)
        return docs[0].page_content

    except Exception as e:
        print(f"Error processing PDF from {pdf_url}: {e}")
        return ''
