import json
import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

# 1. الاستيرادات
from RAG.Retrieval.query_agent import NDISentinelRetriever
from Strategic_Advisor.advisor_agent import AdvisorAgent 
from scoring.scoring_engine import evaluate_oe
from reporting.pdf_builder import OEReportBuilder
from reporting.layouts import OESummary, MetricItem
from reporting.font import register_fonts

# 2. تعريف الحالة (State)
class AgentState(TypedDict):
    compliance_report: dict
    violation_type: str
    legal_context: str
    final_advice: str
    scoring_results: list
    maturity_score: float
    maturity_label: str
    report_path: str

# 3. بناء العُقد (Nodes)

def advisor_node(state: AgentState):
    # الـ API Key الخاص بكِ لـ OpenRouter
    MY_KEY = "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"
    advisor = AdvisorAgent(api_key=MY_KEY)
    
    first_result = state['compliance_report']['results'][0]
    violation = first_result['all_findings'][0]['العنصر_المكتشف']
    
    legal_text, source = advisor.get_legal_context(violation)
    advisor.generate_strategic_recommendation()
    
    # التعديل هنا: نقرأ من الملف الفعلي اللي ينتجه كودك بالتسمية الصحيحة والمسافات الموزونة
    with open("strategic_advisory_output.txt", "r", encoding="utf-8") as f:
        advice = f.read()
    
    return {"violation_type": violation, "legal_context": legal_text, "final_advice": advice}

def scoring_node(state: AgentState):
    sample_data = {
        "DSI.OE.01": {"apis": [{"certified": 80, "total_attributes": 100, "classified": True}]},
        "DSI.OE.02": {"systems": [{"implemented": True, "method_followed": True, "updated": True}]},
        "DO.OE.03": {"percentage": 85}, "DQ.OE.02": {"percentage": 70}, "DO.OE.02": {"percentage": 90},
        "RMD.OE.01": {"published": 20, "required": 25}, "OD.OE.01": {"published": 100, "required": 120},
        "OD.OE.05": {"requests": [{"category": "Easy", "duration": 5}]}, "MCM.OE.01": {"done": 30, "required": 40},
        "MCM.OE.02": {"done": 15, "required": 20}, "MCM.OE.03": {"done": 50, "required": 60},
        "DSI.OE.05": {"done": 45, "required": 50}, "DQ.OE.03": {"done": 35, "required": 40}
    }
    result = evaluate_oe("وزارة الصحة", "الدورة الثالثة", sample_data)
    metrics_list = [{"metric_id": m.metric_id, "percentage": m.percentage} for m in result.metrics]
    return {"scoring_results": metrics_list, "maturity_score": result.final_score, "maturity_label": result.maturity_label}

def reporting_node(state: AgentState):
    print("... جاري إنشاء ملف الـ PDF النهائي ...")
    register_fonts()
    
    # تحويل النتائج لتناسب كود الـ PDF
    metrics = [MetricItem(metric_id=m['metric_id'], percentage=m['percentage'], scale=0, weight=0, weighted_score=0) for m in state['scoring_results']]
    
    # صياغة النص الصافي الموجه مباشرة للجدول بدون كتابة العناوين الثابتة عشان تطلع جنب العبارة بالضبط
  #  description = (
      #  "تم اكتشاف انتهاكات في البيانات الشخصية (كشف بيانات الهوية الوطنية وتسريب سجلات الرواتب). "
        
   # )

    summary = OESummary(
        entity_name="وزارة الصحة",
        cycle_name="نتائج نظام NDI-Sentinel",
        final_score=state['maturity_score'],
        maturity_level=int(state['maturity_score']),
        maturity_label=state['maturity_label'],
        maturity_description="تم اكتشاف انتهاكات في البيانات الشخصية (كشف بيانات الهوية الوطنية وتسريب سجلات الرواتب). ",
        metrics=metrics
    )
    
    # تحديد مكان الحفظ بوضوح في المجلد الرئيسي
    output_pdf = "NDI_Sentinel_Final_Report.pdf"
    builder = OEReportBuilder(output_file=output_pdf)
    builder.build(summary)
    
    print(f"تم حفظ الملف بنجاح في: {os.path.abspath(output_pdf)}")
    return {"report_path": output_pdf}

# 4. رسم مسار العمل للـ LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("advisor", advisor_node)
workflow.add_node("scoring", scoring_node)
workflow.add_node("reporting", reporting_node)
workflow.set_entry_point("advisor")
workflow.add_edge("advisor", "scoring")
workflow.add_edge("scoring", "reporting")
workflow.add_edge("reporting", END)
app = workflow.compile()

# 5. التنفيذ
if __name__ == "__main__":
    try:
        with open("outputs/compliance_output.json", "r", encoding="utf-8") as f:
            initial_json = json.load(f)
        
        print("جاري تشغيل نظام NDI Sentinel الموحد...")
        app.invoke({"compliance_report": initial_json})
        print("اكتملت العملية بنجاح كامل!")
    except Exception as e:
        print(f"حدث خطأ: {e}")
