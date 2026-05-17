import os
import requests
import json
from query_agent import NDISentinelRetriever

class AdvisorAgent:
    def __init__(self, api_key: str):
        self.retriever = NDISentinelRetriever()
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.input_path = "outputs/detection_result.txt"
        self.output_path = "final_report.txt"

    def read_violation_finding(self) -> str:
        if not os.path.exists(self.input_path):
            return None
        with open(self.input_path, "r", encoding="utf-8") as file:
            return file.read().strip()

    def get_legal_context(self, violation: str):
        results = self.retriever.vector_db.similarity_search(violation, k=1)
        if not results:
            return None, None
        
        legal_text = results[0].page_content
        source_metadata = os.path.basename(results[0].metadata.get('source', 'SDAIA_Governance_Policy'))
        return legal_text, source_metadata

    def generate_strategic_recommendation(self):
        violation = self.read_violation_finding()
        if not violation:
            return "Error: System could not locate violation input."

        legal_text, source = self.get_legal_context(violation)
        if not legal_text:
            return "Error: Legal framework not found in vector database."

        prompt = (
            "Role: Senior Data Governance Expert\n"
            f"Context: {legal_text}\n"
            f"Violation: {violation}\n\n"
            "Task: Provide a professional advisory recommendation in Arabic. "
            "Focus on compliance with SDAIA regulations and provide immediate corrective actions."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://ndi-sentinel.sa",
            "X-Title": "NDI-Sentinel-Advisor"
        }
        
        payload = {
            "model": "google/gemini-2.0-flash-001", 
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                recommendation = result['choices'][0]['message']['content']
                with open(self.output_path, "w", encoding="utf-8") as file:
                    file.write(recommendation)
                return "Process Completed: Strategic report generated."
            else:
                return f"Execution Failure: API returned status {response.status_code}"
        except Exception as e:
            return f"Technical Error: {str(e)}"

if __name__ == "__main__":
    # Key configuration
    MY_KEY="xxxxxxxxxxxxxxxxx"
    advisor = AdvisorAgent(api_key=MY_KEY)
    execution_status = advisor.generate_strategic_recommendation()
    print(execution_status)