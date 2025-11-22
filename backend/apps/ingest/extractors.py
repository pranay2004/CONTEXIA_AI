"""
Pure Python Text Extraction
Optimized for compatibility without binary dependencies.
"""
import io
import logging
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

class TextExtractor:
    
    @staticmethod
    def extract_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF using pure-python pypdf"""
        try:
            pdf_stream = io.BytesIO(file_content)
            reader = PdfReader(pdf_stream)
            text = []
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text.append(content)
            return "\n\n".join(text)
        except Exception as e:
            logger.error(f"PDF Error: {e}")
            return ""

    @staticmethod
    def extract_from_docx(file_content: bytes) -> str:
        """Extract from DOCX (Pure Python)"""
        try:
            doc = DocxDocument(io.BytesIO(file_content))
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            logger.error(f"DOCX Error: {e}")
            return ""

    @staticmethod
    def extract_from_pptx(file_content: bytes) -> str:
        """
        Extract text from PPTX by parsing XML directly.
        Does not require python-pptx library.
        """
        try:
            f = io.BytesIO(file_content)
            text_content = []
            
            with zipfile.ZipFile(f) as zf:
                # Find all slide XML files
                slide_files = [n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
                # Sort to maintain order (slide1, slide2, ...)
                slide_files.sort(key=lambda x: int(x.replace("ppt/slides/slide", "").replace(".xml", "")))

                # XML namespace for PowerPoint text
                ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

                for slide in slide_files:
                    xml_content = zf.read(slide)
                    root = ET.fromstring(xml_content)
                    
                    # Find all text bodies <a:t>
                    slide_text = []
                    for node in root.findall('.//a:t', ns):
                        if node.text:
                            slide_text.append(node.text)
                    
                    if slide_text:
                        text_content.append("\n".join(slide_text))
            
            return "\n\n--- SLIDE BREAK ---\n\n".join(text_content)

        except Exception as e:
            logger.error(f"PPTX Error: {e}")
            return ""

    @staticmethod
    def extract_from_url(url: str) -> str:
        """Extract from URL using BeautifulSoup (Pure Python parser)"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            
            # Use 'html.parser' instead of 'lxml' to avoid C++ errors
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            text = soup.get_text(separator='\n')
            
            # Clean whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return '\n'.join(chunk for chunk in chunks if chunk)
            
        except Exception as e:
            logger.error(f"URL Error: {e}")
            return ""

    @staticmethod
    def extract_from_txt(file_content: bytes) -> str:
        try:
            return file_content.decode('utf-8')
        except:
            return file_content.decode('latin-1', errors='ignore')

    @classmethod
    def extract_text(cls, file_content: bytes = None, url: str = None, file_type: str = None) -> str:
        if url: return cls.extract_from_url(url)
        if not file_content: return ""
        
        extractors = {
            'pdf': cls.extract_from_pdf,
            'docx': cls.extract_from_docx,
            'pptx': cls.extract_from_pptx,
            'txt': cls.extract_from_txt
        }
        return extractors.get(file_type, lambda x: "")(file_content)

def count_words(text: str) -> int:
    return len(text.split())