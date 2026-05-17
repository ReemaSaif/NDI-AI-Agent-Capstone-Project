import os
import requests
import json
from query_agent import NDISentinelRetriever

import arabic_reshaper
from bidi.algorithm import get_display

class AdvisorAgent:
    def __init__(self, api_key: str):
        self.retriever = NDISentinelRetriever()
        self.api_key = api_key
        # الرابط الصحيح والمختبر
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.output_path = "outputs/detection_result.txt"

    def read_violation_finding(self) -> str:
        if not os.path.exists(self.output_path):
            return None
        with open(self.output_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def get_legal_context(self, violation: str):
        results = self.retriever.vector_db.similarity_search(violation, k=1)
        if not results:
            return None, None
        return results[0].page_content, os.path.basename(results[0].metadata.get('source', 'Unknown'))

    def generate_strategic_recommendation(self):
        violation = self.read_violation_finding()
        if not violation:
            return "Error: No detection results found in outputs/detection_result.txt"

        legal_text, source = self.get_legal_context(violation)
        if not legal_text:
            return "Error: No matching legal policies found."

        # تجهيز الطلب لـ GPT
        prompt = (
            f"أنت مستشار حوكمة بيانات خبير.\n"
            f"المخالفة: {violation}\n"
            f"السند القانوني من سدايا: {legal_text}\n"
            f"المصدر: {source}\n\n"
            f"صغ توصية استشارية قصيرة واحترافية بالعربية."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000", # متطلب لبعض موديلات OpenRouter
            "X-Title": "NDI-Sentinel"
        }
        
        payload = {

            "model": "google/gemini-2.0-flash-001", 

            "messages": [{"role": "user", "content": prompt}]

        }

        try:
            print(f"جاري الاتصال بـ المستشار الذكي لتحليل: {violation}...")
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"API Error {response.status_code}: {response.text}"
                
        except Exception as e:
            return f"Technical Error: {str(e)}"
    
if __name__ == "__main__":
    MY_KEY = "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" # مفتاحك هنا
    agent = AdvisorAgent(api_key=MY_KEY)
    
    # الحصول على التوصية
    recommendation = agent.generate_strategic_recommendation()
    
    # حفظ النتيجة في ملف نصي عشان تشوفينها بوضوح
    with open("final_report.txt", "w", encoding="utf-8") as f:
        f.write(recommendation)
        
    print("تم حفظ التوصية في ملف final_report.txt افتحيه الحين وشوفيه!")3