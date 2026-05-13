import streamlit as st
import json
import pandas as pd
from pathlib import Path


st.set_page_config(
    page_title="لوحة NDI-Sentinel",
    layout="wide"
)

st.title("لوحة NDI-Sentinel لحوكمة البيانات")
st.write("عرض نتائج اكتشاف البيانات الحساسة في المستندات العربية")

json_path = Path("outputs/vision_findings.json")

if not json_path.exists():
    st.warning("لا توجد نتائج تحليل حتى الآن. شغلي Vision Agent أولاً.")
else:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    st.subheader("معلومات الملف")

    col1, col2, col3 = st.columns(3)

    col1.metric("اسم الملف", data["اسم_الملف"])
    col2.metric("عدد النتائج", data["عدد_النتائج"])
    col3.metric(
        "تم اكتشاف بيانات حساسة",
        "نعم" if data["تم_اكتشاف_بيانات_حساسة"] else "لا"
    )

    st.subheader("النص المستخرج من الصورة")
    st.text_area(
        "OCR Output",
        data["النص_المستخرج"],
        height=160
    )

    st.subheader("البيانات الحساسة المكتشفة")

    findings = data["النتائج"]

    if findings:
        df = pd.DataFrame(findings)
        st.dataframe(df, use_container_width=True)

        high_count = sum(1 for item in findings if item["مستوى_الخطورة"] == "مرتفع")
        medium_count = sum(1 for item in findings if item["مستوى_الخطورة"] == "متوسط")

        col1, col2, col3 = st.columns(3)

        col1.metric("إجمالي البيانات الحساسة", len(findings))
        col2.metric("مخاطر مرتفعة", high_count)
        col3.metric("مخاطر متوسطة", medium_count)

        st.subheader("ملخص أولي للمخاطر")

        if high_count > 0:
            st.error("تم اكتشاف بيانات عالية الحساسية مثل رقم الهوية أو الآيبان.")
        elif medium_count > 0:
            st.warning("تم اكتشاف بيانات متوسطة الحساسية مثل رقم الجوال أو البريد الإلكتروني.")
    else:
        st.success("لم يتم اكتشاف بيانات حساسة في هذا الملف.")