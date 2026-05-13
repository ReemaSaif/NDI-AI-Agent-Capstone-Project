import re
import os
import json
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

import pandas as pd
import easyocr
from pypdf import PdfReader
from docx import Document


class ComplianceAgent:
    def __init__(
        self,
        knowledge_dir="knowledge_base",
        use_llm=False
    ):
        self.reader = easyocr.Reader(["ar", "en"])
        self.knowledge_dir = Path(knowledge_dir)
        self.use_llm = use_llm

        self.classification_order = {
            "عام": 0,
            "مقيد": 1,
            "سري": 2,
            "سري للغاية": 3
        }

        self.allowed_classifications = [
            "عام",
            "مقيد",
            "سري",
            "سري للغاية"
        ]

        self.regex_rules = {
            "رقم الهوية الوطنية": {
                "pattern": r"\b1\d{9}\b",
                "domain": "PDP",
                "classification": "مقيد",
                "impact": "منخفض",
                "reason": "معرف شخصي مباشر."
            },
            "رقم الجوال": {
                "pattern": r"\b05\d{8}\b",
                "domain": "PDP",
                "classification": "مقيد",
                "impact": "منخفض",
                "reason": "رقم تواصل مرتبط بفرد."
            },
            "البريد الإلكتروني": {
                "pattern": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
                "domain": "PDP",
                "classification": "مقيد",
                "impact": "منخفض",
                "reason": "بريد إلكتروني يمكن ربطه بفرد أو جهة."
            },
            "رقم الآيبان": {
                "pattern": r"\bSA\d{22}\b",
                "domain": "PDP",
                "classification": "مقيد",
                "impact": "منخفض",
                "reason": "بيانات مالية أو رقم حساب."
            },
            "رقم الملف الطبي": {
                "pattern": r"\bMR-\d{4}-\d{4}\b",
                "domain": "PDP",
                "classification": "مقيد",
                "impact": "منخفض",
                "reason": "معلومات ملف صحي."
            }
        }

        self.keyword_rules = {
            "بيانات صحية": {
                "keywords": ["تقرير طبي", "تشخيص", "مريض", "ملف طبي", "وصفة طبية", "علاج"],
                "domain": "PDP",
                "classification": "مقيد",
                "impact": "منخفض",
                "reason": "يحتوي على بيانات صحية شخصية."
            },
            "بيانات مالية": {
                "keywords": ["راتب", "مكافأة", "تحويل بنكي", "حساب بنكي", "كشف حساب", "فاتورة"],
                "domain": "PDP",
                "classification": "مقيد",
                "impact": "منخفض",
                "reason": "يحتوي على بيانات مالية أو رواتب."
            },
            "بيانات مشاركة": {
                "keywords": ["مشاركة البيانات", "اتفاقية مشاركة", "مقدم الطلب", "الجهة الطالبة"],
                "domain": "DS",
                "classification": "مقيد",
                "impact": "منخفض",
                "reason": "يحتوي على مؤشرات مرتبطة بمشاركة البيانات."
            }
        }

        self.knowledge_chunks = self.load_knowledge_base()

    def load_knowledge_base(self):
        chunks = []

        if not self.knowledge_dir.exists():
            return chunks

        for file_path in self.knowledge_dir.glob("*.txt"):
            text = file_path.read_text(encoding="utf-8", errors="ignore")

            parts = [
                part.strip()
                for part in text.split("\n\n")
                if part.strip()
            ]

            for part in parts:
                chunks.append({
                    "source": file_path.name,
                    "content": part
                })

        return chunks

    def retrieve_policy_context(self, query, top_k=3):
        if not self.knowledge_chunks:
            return []

        scored_chunks = []

        for chunk in self.knowledge_chunks:
            score = SequenceMatcher(
                None,
                query[:1500],
                chunk["content"][:1500]
            ).ratio()

            keyword_overlap = 0
            for word in query.split():
                if len(word) > 3 and word in chunk["content"]:
                    keyword_overlap += 1

            final_score = score + (keyword_overlap * 0.05)

            scored_chunks.append({
                "score": final_score,
                "source": chunk["source"],
                "content": chunk["content"]
            })

        scored_chunks = sorted(
            scored_chunks,
            key=lambda x: x["score"],
            reverse=True
        )

        return scored_chunks[:top_k]

    def read_image(self, file_path):
        return " ".join(
            self.reader.readtext(str(file_path), detail=0)
        )

    def read_pdf(self, file_path):
        text = ""
        reader = PdfReader(str(file_path))

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text

    def read_txt(self, file_path):
        return Path(file_path).read_text(
            encoding="utf-8",
            errors="ignore"
        )

    def read_docx(self, file_path):
        doc = Document(str(file_path))
        return "\n".join([p.text for p in doc.paragraphs])

    def read_table(self, file_path):
        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(file_path)

        if suffix in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)

        return None

    def extract_text(self, file_path):
        suffix = file_path.suffix.lower()

        if suffix in [".png", ".jpg", ".jpeg"]:
            return self.read_image(file_path)

        if suffix == ".pdf":
            return self.read_pdf(file_path)

        if suffix == ".txt":
            return self.read_txt(file_path)

        if suffix == ".docx":
            return self.read_docx(file_path)

        if suffix in [".csv", ".xlsx", ".xls"]:
            df = self.read_table(file_path)
            return df.to_string(index=False)

        return ""

    def detect_regex(self, text):
        findings = []

        for label, rule in self.regex_rules.items():
            matches = re.findall(rule["pattern"], text)

            for match in matches:
                findings.append({
                    "نوع_الاكتشاف": "Regex",
                    "المجال": rule["domain"],
                    "العنصر_المكتشف": label,
                    "القيمة": match,
                    "مستوى_التصنيف": rule["classification"],
                    "درجة_الأثر": rule["impact"],
                    "مبرر_التصنيف": rule["reason"]
                })

        return findings

    def detect_keywords(self, text):
        findings = []

        for label, rule in self.keyword_rules.items():
            for keyword in rule["keywords"]:
                if keyword in text:
                    findings.append({
                        "نوع_الاكتشاف": "Keyword",
                        "المجال": rule["domain"],
                        "العنصر_المكتشف": label,
                        "القيمة": keyword,
                        "مستوى_التصنيف": rule["classification"],
                        "درجة_الأثر": rule["impact"],
                        "مبرر_التصنيف": rule["reason"]
                    })

        return findings

    def classify_with_retrieval(self, text, findings):
        retrieved_context = self.retrieve_policy_context(text)

        context_text = "\n".join(
            [
                item["content"]
                for item in retrieved_context
            ]
        )

        combined_text = text + "\n" + context_text

        classification = "عام"
        reason = "لم يتم اكتشاف مؤشرات واضحة تجعل البيانات أعلى من عام."

        top_secret_terms = [
            "سري للغاية",
            "مفاتيح التشفير",
            "تحركات القوات",
            "موقع عسكري",
            "قضية إرهابية",
            "البنية التحتية الوطنية",
            "أمن وطني"
        ]

        secret_terms = [
            "سري",
            "مخطط الشبكة",
            "جدار الحماية",
            "ضوابط الوصول",
            "ثغرة أمنية",
            "بيانات اعتماد",
            "كلمة مرور",
            "نظام داخلي"
        ]

        restricted_terms = [
            "مقيد",
            "بيانات شخصية",
            "رقم هوية",
            "رقم جوال",
            "بريد إلكتروني",
            "راتب",
            "آيبان",
            "معلومات مالية",
            "معلومات صحية"
        ]

        if any(term in combined_text for term in top_secret_terms):
            classification = "سري للغاية"
            reason = "تم اكتشاف مؤشرات عالية الحساسية مرتبطة بالأمن أو التشفير أو المصالح الوطنية."

        elif any(term in combined_text for term in secret_terms):
            classification = "سري"
            reason = "تم اكتشاف مؤشرات أمنية أو تقنية داخلية قد يسبب كشفها ضرراً متوسطاً أو عالياً."

        elif any(term in combined_text for term in restricted_terms):
            classification = "مقيد"
            reason = "تم اكتشاف بيانات شخصية أو مالية أو صحية أو محتوى غير مناسب للنشر العام."

        rule_based_classification = self.get_highest_classification(findings)

        if self.classification_order[rule_based_classification] > self.classification_order[classification]:
            classification = rule_based_classification
            reason = "تم رفع التصنيف بناءً على نتائج قواعد PDP أو المؤشرات المكتشفة."

        return {
            "classification": classification,
            "reason": reason,
            "retrieved_context": retrieved_context
        }

    def get_highest_classification(self, findings):
        if not findings:
            return "عام"

        highest = "عام"

        for item in findings:
            level = item["مستوى_التصنيف"]

            if self.classification_order[level] > self.classification_order[highest]:
                highest = level

        return highest

    def get_impact_level(self, classification):
        return {
            "عام": "لا يوجد أثر",
            "مقيد": "منخفض",
            "سري": "متوسط",
            "سري للغاية": "عالي"
        }[classification]

    def analyze_dq(self, file_path):
        suffix = file_path.suffix.lower()

        if suffix not in [".csv", ".xlsx", ".xls"]:
            return {
                "applies": False,
                "reason": "DQ ينطبق فقط على ملفات الجداول مثل CSV و Excel."
            }

        df = self.read_table(file_path)

        rows = int(df.shape[0])
        columns = int(df.shape[1])
        total_cells = rows * columns

        null_count = int(df.isna().sum().sum())

        null_percentage = 0
        if total_cells > 0:
            null_percentage = round(
                (null_count / total_cells) * 100,
                2
            )

        duplicate_rows = int(df.duplicated().sum())

        invalid_emails = 0

        email_columns = [
            col for col in df.columns
            if "email" in str(col).lower()
            or "بريد" in str(col).lower()
            or "ايميل" in str(col).lower()
        ]

        for col in email_columns:
            email_values = df[col].dropna().astype(str)

            invalid_email_count = (
                ~email_values.str.match(
                    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                )
            ).sum()

            invalid_emails += int(invalid_email_count)

        quality_score = 100
        quality_score -= min(null_percentage, 40)
        quality_score -= min(duplicate_rows * 2, 30)
        quality_score -= min(invalid_emails * 3, 30)

        quality_score = max(
            round(quality_score, 2),
            0
        )

        return {
            "applies": True,
            "rows": rows,
            "columns": columns,
            "null_count": null_count,
            "null_percentage": null_percentage,
            "duplicate_rows": duplicate_rows,
            "invalid_emails": invalid_emails,
            "quality_score": quality_score
        }

    def analyze_ds(self, final_classification, findings):
        sharing_keywords_found = any(
            item["المجال"] == "DS"
            for item in findings
        )

        if final_classification == "عام":
            return {
                "sharing_requires_review": False,
                "reason": "البيانات مصنفة كعامة ويمكن مشاركتها بضوابط أبسط."
            }

        if sharing_keywords_found:
            return {
                "sharing_requires_review": True,
                "reason": "تم اكتشاف سياق مشاركة بيانات، والبيانات ليست عامة؛ يجب تقييم الطلب وفق مبادئ مشاركة البيانات."
            }

        return {
            "sharing_requires_review": True,
            "reason": "البيانات مصنفة كمقيدة أو أعلى، لذلك تحتاج مراجعة قبل المشاركة."
        }

    def decide_next_action(self, final_classification, dq):
        if final_classification == "سري للغاية":
            return "تصعيد عاجل إلى RAG Policy Agent و Scoring Agent."

        if final_classification == "سري":
            return "إرسال إلى RAG Policy Agent لمراجعة الضوابط والسياسات."

        if final_classification == "مقيد":
            return "إرسال إلى Scoring Agent لحساب أثر الامتثال و RAG Agent للتوصية."

        if dq.get("applies") and dq.get("quality_score", 100) < 80:
            return "إرسال إلى Scoring Agent بسبب انخفاض جودة البيانات."

        return "حفظ الملف كبيانات عامة."

    def run(self, file_path):
        extracted_text = self.extract_text(file_path)

        regex_findings = self.detect_regex(extracted_text)
        keyword_findings = self.detect_keywords(extracted_text)

        findings = regex_findings + keyword_findings

        classification_result = self.classify_with_retrieval(
            extracted_text,
            findings
        )

        final_classification = classification_result["classification"]
        final_impact = self.get_impact_level(final_classification)

        dq = self.analyze_dq(file_path)

        ds = self.analyze_ds(
            final_classification,
            findings
        )

        pdp_findings = [
            f for f in findings
            if f["المجال"] == "PDP"
        ]

        dc_findings = [
            f for f in findings
            if f["المجال"] == "DC"
        ]

        ds_findings = [
            f for f in findings
            if f["المجال"] == "DS"
        ]

        output = {
            "agent_name": "NDI-Sentinel Compliance Agent",

            "agent_role": "تحليل الملفات العربية وفق PDP و DC و DQ و DS",

            "language_scope": "Arabic only",

            "file_name": file_path.name,

            "file_type": file_path.suffix,

            "timestamp": datetime.now().isoformat(),

            "domains_checked": [
                "PDP",
                "DC",
                "DQ",
                "DS"
            ],

            "extracted_text_preview": extracted_text[:1000],

            "pdp": {
                "has_personal_data": len(pdp_findings) > 0,
                "findings_count": len(pdp_findings),
                "findings": pdp_findings
            },

            "dc": {
                "classification_method": "Hybrid Rules + Arabic Retrieval",
                "final_classification": final_classification,
                "impact_level": final_impact,
                "classification_reason": classification_result["reason"],
                "retrieved_policy_context": classification_result["retrieved_context"],
                "findings_count": len(dc_findings),
                "findings": dc_findings
            },

            "dq": dq,

            "ds": {
                **ds,
                "findings_count": len(ds_findings),
                "findings": ds_findings
            },

            "all_findings_count": len(findings),

            "all_findings": findings,

            "next_action": self.decide_next_action(
                final_classification,
                dq
            )
        }

        return output


if __name__ == "__main__":
    agent = ComplianceAgent(
        knowledge_dir="knowledge_base",
        use_llm=False
    )

    data_dir = Path("data")

    supported_files = []

    for ext in [
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.pdf",
        "*.csv",
        "*.xlsx",
        "*.xls",
        "*.txt",
        "*.docx"
    ]:
        supported_files.extend(data_dir.glob(ext))

    if not supported_files:
        print("لا توجد ملفات مدعومة داخل مجلد data")
        exit()

    results = []

    for file_path in supported_files:
        print(f"جاري تحليل الملف: {file_path.name}")
        results.append(agent.run(file_path))

    final_output = {
        "system_name": "NDI-Sentinel",

        "agent": "Compliance Agent",

        "approach": "Hybrid Arabic Rules + Retrieval-based Classification",

        "total_files_scanned": len(results),

        "summary": {
            "عام": sum(
                1 for r in results
                if r["dc"]["final_classification"] == "عام"
            ),

            "مقيد": sum(
                1 for r in results
                if r["dc"]["final_classification"] == "مقيد"
            ),

            "سري": sum(
                1 for r in results
                if r["dc"]["final_classification"] == "سري"
            ),

            "سري للغاية": sum(
                1 for r in results
                if r["dc"]["final_classification"] == "سري للغاية"
            ),

            "files_with_pdp": sum(
                1 for r in results
                if r["pdp"]["has_personal_data"]
            ),

            "files_requiring_sharing_review": sum(
                1 for r in results
                if r["ds"]["sharing_requires_review"]
            )
        },

        "results": results
    }

    output_path = Path("outputs/compliance_output.json")

    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            final_output,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("\nتم تحليل جميع الملفات بنجاح\n")

    print(
        json.dumps(
            final_output,
            ensure_ascii=False,
            indent=4
        )
    )