import json
from datetime import datetime
from psycopg2.extras import execute_batch
from connection import get_connection

# SIMPLE LOGGER
def log(msg):
    print(f"[LOG {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# DATABASE CONNECTION
try:
    conn = get_connection()
    cur = conn.cursor()
    log("Connected to PostgreSQL using connection.py")
except Exception as e:
    print(f"[FATAL] Database connection failed: {e}")
    raise

# LOAD JSON
try:
    with open("../output/compliance_output.json", "r", encoding="utf-8") as f:
        compliance_json = json.load(f)

    results = compliance_json.get("results", [])
    log(f"Loaded {len(results)} compliance records.")
except Exception as e:
    print(f"[FATAL] Failed to load JSON file: {e}")
    raise

# STATIC DATA
government_entities = [
    ("وزارة الصحة", "حكومي", "الرياض", 1950),
    ("وزارة الداخلية", "حكومي", "الرياض", 1951),
    ("وزارة التعليم", "حكومي", "الرياض", 1954),
    ("وزارة المالية", "حكومي", "الرياض", 1952),
    ("وزارة العدل", "حكومي", "الرياض", 1970),
    ("وزارة الاتصالات وتقنية المعلومات", "حكومي", "الرياض", 2003),
    ("سدايا", "هيئة", "الرياض", 2019),
    ("الهيئة العامة للإحصاء", "هيئة", "الرياض", 1960),
    ("المركز الوطني للتخصيص", "هيئة", "الرياض", 2017),
    ("أمانة منطقة الرياض", "بلدية", "الرياض", 1937),
    ("وزارة الإعلام", "حكومي", "الرياض", 1962),
    ("هيئة الزكاة والضريبة والجمارك", "هيئة", "الرياض", 2021)
]

ndi_components = [
    ("قياس نضج تطبيق الممارسات في إدارة البيانات", "قياس تطبيق أفضل ممارسات إدارة البيانات وتحسين مستوى النضج."),
    ("قياس الامتثال", "قياس الالتزام بضوابط ومعايير إدارة وحوكمة البيانات الوطنية."),
    ("قياس التميز التشغيلي", "قياس تقدم العمليات التشغيلية لإدارة البيانات عبر المنصات الوطنية.")
]

maturity_levels = [
    (0, "غياب القدرات", 0.0),
    (1, "البناء", 1.0),
    (2, "التعريف", 2.0),
    (3, "التفعيل", 3.0),
    (4, "التمكين", 4.0),
    (5, "الريادة", 5.0),
]

compliance_status = [
    ("متوافق",),
    ("متوافق جزئيًا",),
    ("غير متوافق",),
]

policy_docs = [
    ("NDMO PDP Policy", "1.0", "NDMO", "policies/pdp.pdf"),
    ("NDMO Data Classification Policy", "1.0", "NDMO", "policies/dc.pdf"),
    ("NDMO Data Sharing Policy", "1.0", "NDMO", "policies/ds.pdf"),
    ("NDMO Data Quality Policy", "1.0", "NDMO", "policies/dq.pdf"),
    ("NDMO Data Governance Framework", "1.0", "NDMO", "policies/dg.pdf"),
]

# INSERT STATIC TABLES
try:
    execute_batch(cur, """
        INSERT INTO government_entities
        (entity_name, sector, city, established_year)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (entity_name) DO NOTHING
    """, government_entities)

    execute_batch(cur, """
        INSERT INTO ndi_components
        (component_name, description)
        VALUES (%s, %s)
        ON CONFLICT (component_name) DO NOTHING
    """, ndi_components)

    execute_batch(cur, """
        INSERT INTO maturity_levels
        (level_number, level_name, score_value)
        VALUES (%s, %s, %s)
        ON CONFLICT (level_number) DO NOTHING
    """, maturity_levels)

    execute_batch(cur, """
        INSERT INTO compliance_status
        (status_name)
        VALUES (%s)
        ON CONFLICT (status_name) DO NOTHING
    """, compliance_status)

    execute_batch(cur, """
        INSERT INTO policy_documents
        (policy_name, version, source_authority, file_path)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (policy_name) DO NOTHING
    """, policy_docs)

    log("Inserted static tables.")
except Exception as e:
    conn.rollback()
    print(f"[ERROR] Static data insertion failed: {e}")
    raise

# FETCH IDS
cur.execute("SELECT component_id, component_name FROM ndi_components")
comp_map = {name: cid for cid, name in cur.fetchall()}

# INSERT DATA DOMAINS
data_domains = [
    ("DG", "حوكمة البيانات", "إدارة البيانات", comp_map["قياس نضج تطبيق الممارسات في إدارة البيانات"]),
    ("DQ", "جودة البيانات", "تحسين الجودة", comp_map["قياس نضج تطبيق الممارسات في إدارة البيانات"]),
    ("DC", "تصنيف البيانات", "سياسات التصنيف", comp_map["قياس الامتثال"]),
    ("PDP", "حماية البيانات الشخصية", "سياسات الحماية", comp_map["قياس الامتثال"]),
]

execute_batch(cur, """
    INSERT INTO data_domains
    (domain_code, domain_name, description, component_id)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (domain_code) DO NOTHING
""", data_domains)

log("Inserted data domains.")

# FETCH POLICY + RULE IDS
cur.execute("SELECT policy_id, policy_name FROM policy_documents")
policy_map = {name: pid for pid, name in cur.fetchall()}

rules = [
    (policy_map["NDMO PDP Policy"], "PDP-01", "حماية البيانات الشخصية", "High"),
    (policy_map["NDMO PDP Policy"], "PDP-02", "تخزين البيانات", "Medium"),
    (policy_map["NDMO Data Classification Policy"], "DC-01", "تصنيف البيانات", "Medium"),
    (policy_map["NDMO Data Quality Policy"], "DQ-01", "جودة البيانات", "Low"),
    (policy_map["NDMO Data Sharing Policy"], "DS-01", "مشاركة البيانات", "High"),
]

execute_batch(cur, """
    INSERT INTO compliance_rules
    (policy_id, rule_code, description, severity)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (rule_code) DO NOTHING
""", rules)

log("Inserted compliance rules.")

cur.execute("SELECT rule_id, rule_code FROM compliance_rules")
rule_map = {code: rid for rid, code in cur.fetchall()}

cur.execute("SELECT compliance_id, status_name FROM compliance_status")
comp_status_map = {name: cid for cid, name in cur.fetchall()}

# PROCESS DOCUMENTS
required_keys = ["file_name", "file_type", "dc", "pdp"]

for item in results:

    if not all(k in item for k in required_keys):
        log(f"[SKIP] Missing keys in JSON record: {item}")
        continue

    try:
        uploaded_at = datetime.now()

        # DOCUMENT
        cur.execute("""
            INSERT INTO documents
            (file_name, file_type, file_path, uploaded_by, uploaded_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING document_id
        """, (
            item["file_name"],
            item["file_type"],
            f"uploads/{item['file_name']}",
            item.get("agent_name", "Compliance Agent"),
            uploaded_at
        ))

        document_id = cur.fetchone()[0]

        # CLASSIFICATION
        final_class = item["dc"]["final_classification"]
        classification_descriptions = {
            "عام": "بيانات لا يترتب على الإفصاح عنها أي ضرر.",
            "مقيد": "بيانات قد يسبب الإفصاح عنها ضررًا محدودًا.",
            "سري": "بيانات قد يسبب الإفصاح عنها ضررًا جسيمًا.",
            "سري للغاية": "بيانات قد يسبب الإفصاح عنها ضرر جسيم واستثنائي لا يمكن تداركه."
        }

        description = classification_descriptions.get(final_class)

        cur.execute("""
            INSERT INTO data_classifications (classification_name, description)
            VALUES (%s, %s)
            ON CONFLICT (classification_name)
            DO UPDATE SET description = EXCLUDED.description
            RETURNING classification_id
        """, (final_class, description))

        result = cur.fetchone()

        if result is None:
            # Row already exists = fetch ID
            cur.execute("""
                SELECT classification_id
                FROM data_classifications
                WHERE classification_name = %s
            """, (final_class,))
            classification_id = cur.fetchone()[0]
        else:
            classification_id = result[0]

        findings_count = item.get("all_findings_count", 0)
        confidence_score = min(70 + findings_count * 5, 99)

        cur.execute("""
            INSERT INTO document_classifications
            (document_id, classification_id, confidence_score)
            VALUES (%s, %s, %s)
        """, (
            document_id,
            classification_id,
            confidence_score
        ))

        # SENSITIVE DATA FINDINGS
        seen_findings = set()
        finding_rows = []

        for finding in item.get("pdp", {}).get("findings", []):
            unique_key = (
                finding.get("العنصر_المكتشف"),
                finding.get("القيمة")
            )

            if unique_key in seen_findings:
                continue

            seen_findings.add(unique_key)

            finding_rows.append((
                document_id,
                finding.get("العنصر_المكتشف"),
                finding.get("القيمة"),
                finding.get("مستوى_التصنيف"),
                finding.get("درجة_الأثر"),
                finding.get("مبرر_التصنيف")
            ))

        if finding_rows:
            execute_batch(cur, """
                INSERT INTO sensitive_data_findings
                (document_id, data_type, detected_value, classification_level, impact_level, justification)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, finding_rows)

        # COMPLIANCE SCAN
        overall_score = max(100 - findings_count * 5, 50)

        cur.execute("""
            INSERT INTO compliance_scans
            (document_id, compliance_id, overall_score, json_output_path, scan_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING scan_id
        """, (
            document_id,
            comp_status_map["متوافق جزئيًا"],
            overall_score,
            "output/compliance_output.json",
            uploaded_at
        ))

        scan_id = cur.fetchone()[0]

        # VIOLATIONS
        violation_rows = []

        for violation in item.get("all_findings", []):
            violation_rows.append((
                scan_id,
                rule_map["PDP-01"],
                violation.get("العنصر_المكتشف"),
                violation.get("درجة_الأثر")
            ))

        if violation_rows:
            execute_batch(cur, """
                INSERT INTO compliance_violations
                (scan_id, rule_id, violation_text, severity)
                VALUES (%s, %s, %s, %s)
            """, violation_rows)

        log(f"[OK] Processed file: {item['file_name']}")

    except Exception as e:
        conn.rollback()
        log(f"[ERROR] Failed processing {item.get('file_name')}: {e}")
        continue

# ENTITY ASSESSMENTS
cur.execute("SELECT entity_id FROM government_entities")
entities = [row[0] for row in cur.fetchall()]

cur.execute("SELECT domain_id FROM data_domains")
domains = [row[0] for row in cur.fetchall()]

cur.execute("SELECT level_id FROM maturity_levels WHERE level_number = 3")
defined_level = cur.fetchone()[0]

cur.execute("""
    SELECT compliance_id
    FROM compliance_status
    WHERE status_name = 'متوافق'
""")

compliant_status = cur.fetchone()[0]

assessment_rows = []

for entity_id in entities:
    for domain_id in domains:
        assessment_rows.append((
            entity_id,
            domain_id,
            defined_level,
            compliant_status,
            "Auto-generated assessment",
            datetime.now()
        ))

execute_batch(cur, """
    INSERT INTO entity_assessments
    (entity_id, domain_id, level_id, compliance_id, notes, assessment_date)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (entity_id, domain_id) DO NOTHING
""", assessment_rows)

log("Inserted entity assessments.")

# FINALIZE
try:
    conn.commit()
    log("Mock data inserted successfully!")
except Exception as e:
    conn.rollback()
    print(f"[ERROR] Commit failed: {e}")
finally:
    cur.close()
    conn.close()
    log("Database connection closed.")

