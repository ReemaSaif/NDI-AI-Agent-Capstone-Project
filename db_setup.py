import os
import logging
import sys
from typing import List

# Core AI Libraries
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# إعداد نظام التوثيق (Logging) لمراقبة أداء النظام
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class NDISentinelIngestor:
    """
    محرك معالجة البيانات (Ingestion Engine) لمشروع NDI-Sentinel.
    مسؤول عن تحويل ملفات الحوكمة الـ 9 إلى قاعدة بيانات متجهة ذكية.
    """
    
    def __init__(self, data_path: str = "data/", chroma_path: str = "chroma_db"):
        self.data_path = data_path
        self.chroma_path = chroma_path
        # اختيار نموذج يدعم العربية والإنجليزية (Multilingual)
        self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

    def load_documents(self) -> List:
        """تحميل ملفات الـ PDF مع التأكد من وجود المجلد والملفات."""
        if not os.path.exists(self.data_path):
            logger.error(f"المجلد {self.data_path} غير موجود!")
            return []

        pdf_files = [f for f in os.listdir(self.data_path) if f.endswith('.pdf')]
        if not pdf_files:
            logger.warning("لا توجد ملفات PDF في المجلد المحدد.")
            return []

        documents = []
        for file in pdf_files:
            file_path = os.path.join(self.data_path, file)
            try:
                logger.info(f"جاري تحميل ومعالجة: {file}")
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            except Exception as e:
                logger.error(f"خطأ أثناء قراءة الملف {file}: {e}")
        
        return documents

    def split_text(self, documents: List):
        """تقسيم النصوص إلى أجزاء ذكية مع مراعاة التداخل لضمان سياق المعنى."""
        # chunk_size=700 مناسب جداً للنصوص القانونية الطويلة في ملفات سدايا
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=120,
            length_function=len,
            add_start_index=True,
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"تم تقسيم الملفات إلى {len(chunks)} جزء نصي (Chunks).")
        return chunks

    def create_vector_store(self):
        """بناء قاعدة البيانات المتجهة ChromaDB."""
        # التأكد من عدم وجود قاعدة بيانات قديمة أو مسحها إذا أردتِ التحديث
        if os.path.exists(self.chroma_path):
            logger.info("تم العثور على قاعدة بيانات سابقة، سيتم التحديث/الإضافة عليها.")

        raw_docs = self.load_documents()
        if not raw_docs:
            return

        chunks = self.split_text(raw_docs)

        logger.info(f"بدء عملية بناء Vector Store باستخدام {self.model_name}...")
        
        try:
            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.chroma_path
            )
            logger.info(f"تم بناء 'العقل القانوني' بنجاح في المسار: {self.chroma_path}")
            return vector_db
        except Exception as e:
            logger.critical(f"فشل في إنشاء قاعدة البيانات: {e}")

if __name__ == "__main__":
    # تنفيذ العملية
    ingestor = NDISentinelIngestor()
    ingestor.create_vector_store()