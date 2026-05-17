import os
import logging
from typing import List, Optional

# المكتبات الأساسية
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# مكتبات تصحيح اللغة العربية
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد نظام التوثيق (Logging) لمراقبة أداء النظام
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NDISentinelRetriever:
    """
    فئة احترافية لإدارة استرجاع البيانات من نظام حوكمة البيانات الوطني.
    تعتمد على تقنية RAG (Retrieval-Augmented Generation).
    """
    
    def __init__(self, db_path: str = "chroma_db", model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.db_path = db_path
        self.model_name = model_name
        self.embeddings = self._load_embeddings()
        self.vector_db = self._load_vector_db()

    def _load_embeddings(self) -> HuggingFaceEmbeddings:
        """تحميل محرك الفهم اللغوي."""
        try:
            logger.info(f"جاري تحميل نموذج الـ Embeddings: {self.model_name}")
            return HuggingFaceEmbeddings(model_name=self.model_name)
        except Exception as e:
            logger.error(f"فشل في تحميل النموذج: {e}")
            raise

    def _load_vector_db(self) -> Chroma:
        """الاتصال بقاعدة البيانات المتجهة."""
        if not os.path.exists(self.db_path):
            logger.error(f"قاعدة البيانات غير موجودة في المسار: {self.db_path}")
            raise FileNotFoundError("ChromaDB path not found.")
        
        return Chroma(persist_directory=self.db_path, embedding_function=self.embeddings)

    @staticmethod
    def _fix_arabic_text(text: str) -> str:
        """تصحيح عرض اللغة العربية لضمان قراءة احترافية."""
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)

    def query(self, user_query: str, top_k: int = 3) -> List[Document]:
        """البحث عن المعلومات الأكثر صلة."""
        logger.info(f"جاري معالجة الاستعلام: {user_query}")
        
        # البحث مع الحصول على نتائج الدقة
        results = self.vector_db.similarity_search_with_relevance_scores(user_query, k=top_k)
        
        if not results:
            logger.warning("لم يتم العثور على نتائج مطابقة.")
            return []

        print(f"\n" + "="*70)
        print(self._fix_arabic_text(f"نتائج البحث عن: '{user_query}'"))
        print("="*70 + "\n")

        for i, (doc, score) in enumerate(results, 1):
            source = os.path.basename(doc.metadata.get('source', 'Unknown'))
            page = doc.metadata.get('page', 'N/A')
            
            # معالجة النص المستخرج
            clean_content = doc.page_content.strip().replace('\n', ' ')
            fixed_content = self._fix_arabic_text(clean_content[:500])

            # طباعة المصدر والصفحة مصححة
            print(f"[{i}] " + self._fix_arabic_text(f"المصدر: {source} (صفحة: {page})"))
            
            # تصحيح العناوين الثابتة لتظهر بشكل سليم في الـ Terminal
            label_score = self._fix_arabic_text("درجة الموثوقية: ")
            label_content = self._fix_arabic_text("النص المستخرج: ")
            
            print(f"{label_score}{abs(score):.4f}")
            print(f"{label_content}{fixed_content}...")
            print("-" * 50)

        return [doc for doc, score in results]

if __name__ == "__main__":
    # تشغيل النظام كـ Object
    try:
        agent = NDISentinelRetriever()
        
        # تجربة استعلام احترافي
        test_question = "ما هي مستويات تصنيف البيانات المعتمدة؟"
        agent.query(test_question)
        
    except Exception as e:
        logger.critical(f"حدث خطأ غير متوقع في النظام: {e}")