import sys
import json
import html
from pathlib import Path
from datetime import datetime
from typing import Any

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
UPLOADS_DIR = ROOT_DIR / "uploads"
OUTPUTS_DIR = ROOT_DIR / "outputs"
OUTPUT_DIR = ROOT_DIR / "output"
REPORTS_DIR = ROOT_DIR / "reports"
SCORING_DIR = ROOT_DIR / "scoring"
ADVISOR_DIR = ROOT_DIR / "Strategic Advisor"
ADVISOR_OUTPUTS_DIR = ADVISOR_DIR / "Outputs"
FINAL_PROJECT_DIR = ROOT_DIR / "final" / "project"
FINAL_VIOLATIONS_REPORT = FINAL_PROJECT_DIR / "NDI_Sentinel_Final_Report.pdf"
FINAL_RECOMMENDATIONS_TXT = FINAL_PROJECT_DIR / "strategic_advisory_output.txt"

for directory in [UPLOADS_DIR, OUTPUTS_DIR, OUTPUT_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

try:
    from compliance_agent import ComplianceAgent
except Exception as e:
    ComplianceAgent = None
    IMPORT_ERROR = str(e)

SUPPORTED_TYPES = ["png", "jpg", "jpeg", "pdf", "csv", "xlsx", "xls", "txt", "docx"]

st.set_page_config(
    page_title="NDI-Sentinel",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap');

    :root {
        --bg: #f3f7fb;
        --card: #ffffff;
        --text: #0f172a;
        --muted: #64748b;
        --line: #dbe4ef;
        --soft: #f8fafc;
        --primary: #0f766e;
        --primary-dark: #115e59;
        --primary-soft: #dff7ef;
        --navy: #10233f;
        --blue: #2563eb;
        --blue-soft: #e7efff;
        --amber: #d97706;
        --amber-soft: #fff1c2;
        --red: #dc2626;
        --red-soft: #fee2e2;
        --purple: #6d5dfc;
        --purple-soft: #eeeafd;
        --shadow: 0 14px 34px rgba(15, 23, 42, .075);
    }

    html, body, .stApp, [class*="css"] {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Tajawal', sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 9% 0%, rgba(37, 99, 235, .08), transparent 30%),
            radial-gradient(circle at 95% 7%, rgba(15, 118, 110, .10), transparent 32%),
            var(--bg);
    }

    .block-container {
        max-width: 1160px;
        padding: 24px 28px 34px;
    }

    section[data-testid="stSidebar"], div[data-testid="collapsedControl"], header[data-testid="stHeader"] {
        display: none !important;
    }

    .app-header {
        background: rgba(255,255,255,.95);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 17px 22px;
        box-shadow: var(--shadow);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 28px;
    }

    .brand { display: flex; align-items: center; gap: 13px; }
    .brand-icon {
        width: 50px; height: 50px; border-radius: 16px;
        background: linear-gradient(135deg, var(--primary-dark), #16a34a);
        color: white; display: flex; align-items: center; justify-content: center;
        font-size: 23px; font-weight: 900;
        box-shadow: 0 12px 26px rgba(15, 118, 110, .20);
    }
    .brand-title { color: var(--text); font-size: 25px; font-weight: 900; letter-spacing: -.3px; }
    .brand-subtitle { color: var(--muted); font-size: 13px; font-weight: 800; margin-top: 4px; }
    .top-menu { display: flex; gap: 8px; align-items: center; }
    .menu-item {
        color: #334155; font-weight: 900; font-size: 13px;
        padding: 10px 14px; border-radius: 12px; border: 1px solid transparent;
    }
    .menu-item.active { color: var(--primary-dark); background: #ecfdf5; border-color: #b7ead4; }

    .page-title {
        color: var(--text); font-size: 27px; font-weight: 900;
        margin: 0 0 6px; display: flex; align-items: center; gap: 9px;
    }
    .page-subtitle {
        color: var(--muted); font-size: 14.5px; line-height: 1.85;
        font-weight: 700; margin-bottom: 20px;
    }
    .section-title { color: var(--text); font-size: 20px; font-weight: 900; margin: 0 0 14px; }
    .section-title-sm { color: var(--text); font-size: 17px; font-weight: 900; margin: 0 0 14px; }

    .panel, .upload-panel, .file-card, .recommendation-card, .report-card, .visual-card {
        background: rgba(255,255,255,.96);
        border: 1px solid var(--line);
        border-radius: 20px;
        box-shadow: var(--shadow);
        padding: 20px;
        margin-bottom: 18px;
    }

    .metric-card {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 16px;
        min-height: 118px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, .055);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
    .metric-icon {
        width: 38px; height: 38px; border-radius: 13px;
        display: flex; align-items: center; justify-content: center;
        background: var(--icon-bg); color: var(--icon-color);
        font-size: 17px; font-weight: 900; flex: 0 0 auto;
    }
    .metric-label { color: #475569; font-size: 13px; font-weight: 900; line-height: 1.55; }
    .metric-value { color: var(--text); font-size: 30px; font-weight: 900; line-height: 1.05; margin-top: 12px; }
    .metric-note { color: var(--muted); font-size: 12px; font-weight: 800; margin-top: 5px; }

    .status {
        display: inline-flex; align-items: center; justify-content: center;
        padding: 6px 12px; border-radius: 999px;
        font-size: 12.5px; font-weight: 900; white-space: nowrap;
    }
    .status.green { background: var(--primary-soft); color: #047857; }
    .status.blue { background: var(--blue-soft); color: #1e40af; }
    .status.amber { background: var(--amber-soft); color: #92400e; }
    .status.red { background: var(--red-soft); color: #991b1b; }
    .status.purple { background: var(--purple-soft); color: #5b21b6; }

    .overview-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin: 20px 0; }
    .visual-card { min-height: 250px; }

    .classification-head { display: flex; justify-content: space-between; color: #334155; font-weight: 900; font-size: 13px; margin-top: 4px; }
    .progress-label { color: #334155; font-weight: 900; font-size: 13px; margin: 13px 0 5px; }

    div[data-testid="stProgress"] > div > div > div { background: linear-gradient(90deg, var(--primary-dark), #22c55e) !important; }
    div[data-testid="stProgress"] > div { background: #e8eef5 !important; }

    .gauge-box { margin-top: 24px; text-align: center; }
    .gauge-track { height: 16px; background: #e8eef5; border-radius: 999px; overflow: hidden; margin: 26px 12px 18px; }
    .gauge-fill { width: var(--w); height: 100%; background: linear-gradient(90deg, var(--primary-dark), #22c55e); border-radius: 999px; }
    .gauge-score { color: var(--text); font-size: 38px; font-weight: 900; line-height: 1; }
    .gauge-note { color: var(--muted); font-size: 13px; font-weight: 800; margin-top: 8px; }

    .maturity-badge {
        width: 108px; height: 108px; margin: 18px auto 12px; border-radius: 28px;
        background: linear-gradient(135deg, var(--primary-dark), #3ac779);
        color: white; display: flex; justify-content: center; align-items: center;
        font-size: 42px; font-weight: 900;
        box-shadow: 0 16px 32px rgba(15, 118, 110, .18);
    }
    .maturity-title { text-align: center; color: var(--text); font-size: 21px; font-weight: 900; margin-bottom: 8px; }
    .maturity-desc { color: var(--muted); text-align: center; font-size: 13px; font-weight: 800; line-height: 1.8; }

    .process-row { display: flex; gap: 12px; align-items: center; padding: 12px 0; border-bottom: 1px solid #edf2f7; }
    .process-row:last-child { border-bottom: 0; }
    .process-number {
        width: 32px; height: 32px; min-width: 32px; border-radius: 12px;
        background: var(--blue-soft); color: #1e40af; font-weight: 900;
        display: flex; align-items: center; justify-content: center;
    }
    .process-text { color: #334155; line-height: 1.8; font-weight: 800; }

    .file-head { display: flex; align-items: center; gap: 14px; border: 1px solid var(--line); border-radius: 16px; background: #fff; padding: 14px; margin-bottom: 14px; }
    .file-icon {
        width: 44px; height: 44px; min-width: 44px; border-radius: 14px;
        background: var(--primary-soft); color: var(--primary-dark);
        font-size: 20px; font-weight: 900; display: flex; align-items: center; justify-content: center;
    }
    .file-name { color: var(--text); font-size: 15px; font-weight: 900; word-break: break-word; }
    .file-type { color: var(--muted); font-size: 12.5px; font-weight: 800; margin-top: 3px; }

    .recommendation-box {
        background: linear-gradient(180deg, #f8fffd, #ffffff);
        border: 1px solid #bfe6dd; border-radius: 16px; padding: 18px;
        color: #1e293b; line-height: 2; font-weight: 750;
        white-space: pre-wrap; overflow-wrap: anywhere; max-height: 560px; overflow-y: auto;
    }
    .recommendation-source { color: var(--primary-dark); font-size: 12.5px; font-weight: 900; margin-top: 10px; }

    .empty-card, .success-card, .warning-card {
        border-radius: 16px; padding: 14px 16px; line-height: 1.9; font-weight: 850; margin-bottom: 14px;
    }
    .empty-card, .warning-card { background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; }
    .success-card { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }

    .table-wrap { width: 100%; overflow-x: auto; border: 1px solid var(--line); border-radius: 18px; background: white; margin-bottom: 16px; }
    table.clean-table { width: 100%; border-collapse: collapse; table-layout: auto; direction: rtl; }
    .clean-table th { background: #f8fafc; color: #64748b; font-size: 13px; font-weight: 900; padding: 13px 12px; border-bottom: 1px solid var(--line); white-space: nowrap; text-align: right; }
    .clean-table td { color: #1e293b; font-size: 13.5px; font-weight: 750; padding: 13px 12px; border-bottom: 1px solid #edf2f7; vertical-align: top; text-align: right; white-space: normal; overflow-wrap: anywhere; line-height: 1.75; min-width: 110px; }
    .clean-table tr:last-child td { border-bottom: 0; }
    .clean-table .wide { min-width: 260px; }

    .upload-intro { padding-bottom: 10px; }
    div[data-testid="stFileUploader"] { direction: rtl !important; text-align: right !important; border: 2px dashed #b9c8d8; border-radius: 18px; padding: 14px; background: #f8fafc; }
    div[data-testid="stFileUploader"] * { direction: rtl !important; text-align: right !important; font-family: 'Tajawal', sans-serif !important; }
    div[data-testid="stFileUploader"] button { min-width: 115px; }

    .stButton button, .stDownloadButton button {
        border-radius: 14px !important; min-height: 44px !important; font-weight: 900 !important;
        border: 1px solid #b7e4dc !important; color: var(--primary-dark) !important;
        background: white !important; box-shadow: none !important; direction: rtl !important;
        font-family: 'Tajawal', sans-serif !important;
    }
    .stButton button:hover, .stDownloadButton button:hover { background: #ecfdf5 !important; border-color: var(--primary-dark) !important; }

    input, textarea, select, .stSelectbox, .stTextArea, .stTextInput { direction: rtl !important; text-align: right !important; font-family: 'Tajawal', sans-serif !important; }
    textarea { border-radius: 16px !important; line-height: 1.9 !important; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl !important; gap: 4px; border-bottom: 1px solid var(--line); }
    .stTabs [data-baseweb="tab"] { font-weight: 900; color: #334155; direction: rtl !important; font-family: 'Tajawal', sans-serif !important; }
    .stTabs [aria-selected="true"] { color: var(--primary-dark) !important; border-bottom: 2px solid var(--primary-dark) !important; }

    .footer { text-align: center; color: #64748b; font-size: 12.5px; font-weight: 800; padding: 22px 0 4px; }



    /* FINAL UPLOAD + RTL FIXES */
    .upload-shell {
        background: rgba(255,255,255,.98);
        border: 1px solid var(--line);
        border-radius: 24px;
        box-shadow: var(--shadow);
        overflow: hidden;
        direction: rtl !important;
        text-align: right !important;
        margin-bottom: 18px;
    }
    .upload-shell-head {
        padding: 28px 30px 20px;
        border-bottom: 1px solid #edf2f7;
        direction: rtl !important;
        text-align: right !important;
    }
    .upload-shell-title {
        color: var(--text);
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 10px;
        direction: rtl !important;
        text-align: right !important;
    }
    .upload-shell-desc {
        color: var(--muted);
        font-size: 14px;
        font-weight: 800;
        line-height: 1.9;
        direction: rtl !important;
        text-align: right !important;
    }
    .upload-helper {
        color: var(--muted);
        font-size: 13px;
        font-weight: 800;
        text-align: center !important;
        margin: 0 0 24px;
        direction: rtl !important;
    }
    .process-card {
        background: rgba(255,255,255,.98);
        border: 1px solid var(--line);
        border-radius: 24px;
        box-shadow: var(--shadow);
        padding: 0;
        overflow: hidden;
        direction: rtl !important;
        text-align: right !important;
    }
    .process-title {
        padding: 24px 28px;
        border-bottom: 1px solid #edf2f7;
        font-size: 22px;
        font-weight: 900;
        color: var(--text);
        direction: rtl !important;
        text-align: right !important;
    }
    .process-row {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 14px !important;
        padding: 17px 26px !important;
        border-bottom: 1px solid #edf2f7 !important;
        direction: rtl !important;
        text-align: right !important;
    }
    .process-row:last-child { border-bottom: 0 !important; }
    .process-number {
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        border-radius: 14px !important;
        background: #ecfdf5 !important;
        color: var(--primary-dark) !important;
        font-weight: 900 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        order: 0 !important;
    }
    .process-text {
        flex: 1 !important;
        color: #1e293b !important;
        font-size: 15px !important;
        line-height: 1.8 !important;
        font-weight: 900 !important;
        direction: rtl !important;
        text-align: right !important;
        order: 1 !important;
    }

    div[data-testid="stFileUploader"] {
        direction: rtl !important;
        text-align: center !important;
        border: 0 !important;
        border-radius: 0 !important;
        padding: 26px 30px 18px !important;
        background: transparent !important;
        box-shadow: none !important;
        margin: 0 !important;
    }
    div[data-testid="stFileUploader"] * {
        font-family: 'Tajawal', sans-serif !important;
    }
    div[data-testid="stFileUploaderDropzone"] {
        min-height: 230px !important;
        border: 2px dashed #95d8c7 !important;
        border-radius: 22px !important;
        background: linear-gradient(180deg, #fbfffd, #f8fafc) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        direction: rtl !important;
        padding: 34px !important;
    }
    div[data-testid="stFileUploaderDropzone"] > div:first-child,
    div[data-testid="stFileUploaderDropzone"] small,
    div[data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"],
    div[data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"] * {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }
    div[data-testid="stFileUploaderDropzone"] button {
        align-self: center !important;
        margin: 0 auto !important;
        min-width: 220px !important;
        height: 56px !important;
        border-radius: 16px !important;
        background: linear-gradient(135deg, var(--primary-dark), #16a34a) !important;
        border: 0 !important;
        color: white !important;
        box-shadow: 0 14px 28px rgba(15, 118, 110, .20) !important;
        overflow: hidden !important;
        font-size: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stFileUploaderDropzone"] button::after {
        content: "اختر ملفًا من جهازك";
        font-size: 16px !important;
        font-weight: 900 !important;
        color: white !important;
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
        text-align: center !important;
    }
    div[data-testid="stFileUploaderDropzone"] button p,
    div[data-testid="stFileUploaderDropzone"] button span {
        display: none !important;
    }
    .footer {
        width: 100% !important;
        display: block !important;
        text-align: center !important;
        margin: 26px auto 0 !important;
        direction: ltr !important;
    }



    /* FINAL OVERRIDE: clean centered file uploader */
    .upload-shell {
        background: rgba(255,255,255,.98) !important;
        border: 1px solid var(--line) !important;
        border-radius: 26px !important;
        box-shadow: var(--shadow) !important;
        overflow: hidden !important;
        direction: rtl !important;
        text-align: right !important;
    }
    .upload-shell-head {
        padding: 30px 34px 20px !important;
        border-bottom: 1px solid #edf2f7 !important;
        direction: rtl !important;
        text-align: right !important;
    }
    .upload-shell-title {
        font-size: 25px !important;
        font-weight: 900 !important;
        color: var(--text) !important;
        margin-bottom: 12px !important;
        text-align: right !important;
        direction: rtl !important;
    }
    .upload-shell-desc {
        color: var(--muted) !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        line-height: 1.9 !important;
        text-align: right !important;
        direction: rtl !important;
    }
    [data-testid="stFileUploader"] {
        border: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 28px 34px 16px !important;
        margin: 0 !important;
        direction: rtl !important;
        text-align: center !important;
    }
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] [data-testid="stWidgetLabel"] {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        min-height: 245px !important;
        width: 100% !important;
        border: 2px dashed #92d9c6 !important;
        border-radius: 24px !important;
        background: linear-gradient(180deg, #fbfffd, #f8fafc) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 16px !important;
        padding: 36px !important;
        direction: rtl !important;
        text-align: center !important;
    }
    [data-testid="stFileUploaderDropzone"] > div:first-child,
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"],
    [data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stFileUploaderDropzone"] small {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        width: 240px !important;
        min-width: 240px !important;
        height: 58px !important;
        margin: 0 auto !important;
        border-radius: 17px !important;
        border: 0 !important;
        background: linear-gradient(135deg, var(--primary-dark), #16a34a) !important;
        box-shadow: 0 16px 30px rgba(15, 118, 110, .22) !important;
        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
        position: relative !important;
    }
    [data-testid="stFileUploaderDropzone"] button * {
        display: none !important;
        visibility: hidden !important;
        font-size: 0 !important;
        color: transparent !important;
    }
    [data-testid="stFileUploaderDropzone"] button::before {
        content: "اختر ملفًا من جهازك" !important;
        display: block !important;
        color: white !important;
        font-size: 16px !important;
        line-height: 1 !important;
        font-weight: 900 !important;
        font-family: 'Tajawal', sans-serif !important;
        text-align: center !important;
        direction: rtl !important;
    }
    [data-testid="stFileUploaderDropzone"] button:hover {
        background: linear-gradient(135deg, #115e59, #22c55e) !important;
        transform: translateY(-1px) !important;
    }
    .upload-helper {
        padding: 0 34px 30px !important;
        margin: 0 !important;
        color: #64748b !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        text-align: center !important;
        direction: rtl !important;
    }

    @media (max-width: 1000px) {
        .app-header, .top-menu { flex-direction: column; align-items: flex-start; }
        .overview-grid { grid-template-columns: 1fr; }
    }


    /* FINAL VISUAL POLISH: unified font, RTL text start, classification and recommendations */
    html, body, .stApp, [class*="css"], button, input, textarea, select {
        font-family: 'Tajawal', Arial, sans-serif !important;
    }
    .page-heading, .page-title, .page-subtitle {
        width: 100% !important;
        direction: rtl !important;
        text-align: right !important;
        margin-right: 0 !important;
        margin-left: auto !important;
    }
    .page-title {
        justify-content: flex-start !important;
        align-items: center !important;
    }
    .page-subtitle {
        display: block !important;
        max-width: 100% !important;
        color: #64748b !important;
        font-weight: 800 !important;
    }
    .metric-card, .visual-card, .file-card, .recommendation-card, .report-clean-section,
    .table-wrap, .process-card, .upload-shell {
        direction: rtl !important;
        text-align: right !important;
    }
    .classification-card {
        padding: 26px 28px !important;
        min-height: 285px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
    }
    .classification-list {
        display: flex !important;
        flex-direction: column !important;
        gap: 17px !important;
        margin-top: 20px !important;
    }
    .classification-row {
        direction: rtl !important;
        text-align: right !important;
    }
    .classification-meta {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 14px !important;
        margin-bottom: 8px !important;
        color: #0f172a !important;
        font-size: 14px !important;
        font-weight: 900 !important;
    }
    .classification-label {
        text-align: right !important;
        direction: rtl !important;
    }
    .classification-count {
        text-align: left !important;
        color: #334155 !important;
        min-width: 24px !important;
    }
    .classification-track {
        width: 100%;
        height: 10px;
        background: #e8eef5;
        border-radius: 999px;
        overflow: hidden;
}

    .classification-fill {
        height: 100%;
        border-radius: 999px;
        float: right;
}
    .recommendation-card {
        border-radius: 24px !important;
        padding: 24px !important;
    }
    .recommendation-box {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Tajawal', Arial, sans-serif !important;
        font-weight: 800 !important;
        line-height: 2.05 !important;
        color: #1e293b !important;
        background: linear-gradient(180deg, #fbfffd, #ffffff) !important;
        border: 1px solid #bfe6dd !important;
        border-radius: 18px !important;
        padding: 20px !important;
    }
    .recommendation-item {
        padding: 12px 0 !important;
        border-bottom: 1px solid #edf2f7 !important;
    }
    .recommendation-item:last-child {
        border-bottom: 0 !important;
    }
    .recommendation-source {
        direction: rtl !important;
        text-align: right !important;
        margin-top: 12px !important;
    }

    

    /* FINAL DELIVERY OVERRIDES */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap');
    html, body, .stApp, [class*="css"], button, input, textarea, select, p, div, span, label, table, th, td {
        font-family: 'Tajawal', sans-serif !important;
    }
    .page-heading, .page-title, .page-subtitle, .plain-section-title, .section-title, .section-title-sm {
        width: 100% !important;
        direction: rtl !important;
        text-align: right !important;
        justify-content: flex-start !important;
        margin-right: 0 !important;
        margin-left: auto !important;
    }
    .plain-section-title {
        color: var(--text) !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        margin: 34px 0 18px !important;
        display: block !important;
    }
    .classification-card {
        padding: 26px 28px !important;
        min-height: 285px !important;
    }
    .classification-list {
        display: flex !important;
        flex-direction: column !important;
        gap: 18px !important;
        margin-top: 22px !important;
    }
    .classification-row { direction: rtl !important; text-align: right !important; }
    .classification-meta {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 9px !important;
        color: #0f172a !important;
        font-size: 14px !important;
        font-weight: 900 !important;
    }
    .classification-label { text-align: right !important; direction: rtl !important; }
    .classification-count { color: #334155 !important; min-width: 24px !important; text-align: left !important; }
    .classification-track {
        width: 100% !important;
        height: 11px !important;
        background: #e8eef5 !important;
        border-radius: 999px !important;
        overflow: hidden !important;
        direction: rtl !important;
    }
    .classification-fill {
        height: 100% !important;
        min-width: 0 !important;
        border-radius: 999px !important;
        float: right !important;
        transition: width .25s ease !important;
    }
    .recommendation-source { display: none !important; }
    .recommendation-card, .recommendation-box, .recommendation-item {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Tajawal', sans-serif !important;
    }
    .report-card { background: transparent !important; border: 0 !important; box-shadow: none !important; padding: 0 !important; }
</style>
    """,
    unsafe_allow_html=True,
)


def safe_get(data: dict, paths: list[str], default: Any = None) -> Any:
    if not isinstance(data, dict):
        return default
    for path in paths:
        current = data
        ok = True
        for key in path.split("."):
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                ok = False
                break
        if ok and current not in [None, "", []]:
            return current
    return default


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return None
        return json.loads(text)
    except Exception:
        return None


def write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")


def save_uploaded_file(uploaded_file) -> Path:
    safe_name = uploaded_file.name.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = UPLOADS_DIR / f"{timestamp}_{safe_name}"
    path.write_bytes(uploaded_file.getbuffer())
    return path


def normalize_output(raw: Any) -> dict:
    if raw is None:
        return {"results": []}
    if isinstance(raw, dict) and isinstance(raw.get("results"), list):
        return raw
    if isinstance(raw, list):
        return {"system_name": "NDI-Sentinel", "results": raw}
    if isinstance(raw, dict):
        return {"system_name": "NDI-Sentinel", "results": [raw]}
    return {"results": []}


def existing_files(directory: Path, names: list[str]) -> list[Path]:
    if not directory.exists():
        return []
    files = [directory / name for name in names if (directory / name).exists()]
    files.extend(directory.glob("*.json"))
    return files


def all_json_files() -> list[Path]:
    names = [
        "scoring_engine_OE_report.json", "oe_report.json", "score_report.json", "scoring_output.json", "scores.json",
        "compliance_output.json", "latest_dashboard_output.json", "recommendations.json", "rag_output.json", "advisor_output.json",
    ]
    files = []
    for directory in [OUTPUTS_DIR, OUTPUT_DIR, SCORING_DIR, ADVISOR_OUTPUTS_DIR, ADVISOR_DIR, ROOT_DIR]:
        files.extend(existing_files(directory, names))
    unique = []
    seen = set()
    for path in sorted(files, key=lambda p: p.stat().st_mtime, reverse=True):
        resolved = path.resolve()
        if resolved not in seen:
            unique.append(path)
            seen.add(resolved)
    return unique


def all_text_reports() -> list[Path]:
    names = [
        "final_report.txt", "recommendation.txt", "recommendations.txt", "advisor_report.txt",
        "strategic_report.txt", "rag_output.txt", "advisor_output.txt", "rag_recommendations.txt",
        "policy_recommendations.txt", "final_recommendations.txt",
    ]
    files: list[Path] = []
    for directory in [FINAL_PROJECT_DIR, ADVISOR_OUTPUTS_DIR, ADVISOR_DIR, OUTPUTS_DIR, OUTPUT_DIR, REPORTS_DIR]:
        if directory.exists():
            files.extend([directory / name for name in names if (directory / name).exists()])
            for pattern in ["*recommend*.txt", "*recommend*.md", "*advisor*.txt", "*rag*.txt", "*policy*.txt", "*strategic*.txt"]:
                files.extend(directory.glob(pattern))
    blocked = {"requirements.txt", "packages.txt", "readme.txt", "detection_result.txt", "vision_findings.txt"}
    unique = []
    seen = set()
    for path in sorted(files, key=lambda p: p.stat().st_mtime, reverse=True):
        resolved = path.resolve()
        if path.name.lower() not in blocked and resolved not in seen:
            unique.append(path)
            seen.add(resolved)
    return unique


def latest_pdf_report() -> Path | None:
    if FINAL_VIOLATIONS_REPORT.exists():
        return FINAL_VIOLATIONS_REPORT
    files = []
    for directory in [FINAL_PROJECT_DIR, OUTPUTS_DIR, OUTPUT_DIR, REPORTS_DIR, SCORING_DIR, ROOT_DIR]:
        if directory.exists():
            files.extend(directory.glob("*.pdf"))
    files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def recommendations_txt_report() -> Path | None:
    if FINAL_RECOMMENDATIONS_TXT.exists():
        return FINAL_RECOMMENDATIONS_TXT
    for path in all_text_reports():
        if path.exists():
            return path
    return None


def latest_json_report() -> Path | None:
    for path in [OUTPUTS_DIR / "compliance_output.json", OUTPUTS_DIR / "latest_dashboard_output.json", OUTPUT_DIR / "compliance_output.json"]:
        if path.exists():
            return path
    files = all_json_files()
    return files[0] if files else None


def extract_score_from_json(data: dict) -> dict:
    if not isinstance(data, dict):
        return {}
    score = {}
    final_score = safe_get(data, ["final_score", "overall_score", "score.final_score", "scores.final_score", "scores.overall_score", "maturity_score", "ndi_maturity_score"])
    maturity_level = safe_get(data, ["maturity_level", "scores.maturity_level", "ndi_maturity_level"])
    maturity_label = safe_get(data, ["maturity_label", "scores.maturity_label", "ndi_maturity_label"])
    maturity_description = safe_get(data, ["maturity_description", "scores.maturity_description"])
    if final_score is not None:
        score["final_score"] = final_score
    if maturity_level is not None:
        score["maturity_level"] = maturity_level
    if maturity_label is not None:
        score["maturity_label"] = maturity_label
    if maturity_description is not None:
        score["maturity_description"] = maturity_description
    metrics = data.get("metrics")
    if isinstance(metrics, list):
        score["metrics"] = metrics
    return score


def find_scoring_result() -> tuple[dict, Path | None]:
    preferred = [ROOT_DIR / "scoring_engine_OE_report.json", SCORING_DIR / "scoring_engine_OE_report.json", OUTPUTS_DIR / "scoring_engine_OE_report.json"]
    for path in preferred + all_json_files():
        data = read_json(path)
        if not isinstance(data, dict):
            continue
        score = extract_score_from_json(data)
        if score:
            return score, path
    return {}, None


def extract_recommendations_from_json(data: dict) -> list[Any]:
    if not isinstance(data, dict):
        return []

    keys = {
        "rag_recommendations", "recommendations", "recommendation", "policy_recommendations",
        "advisor_recommendations", "final_recommendations", "strategic_recommendation",
        "strategic_report", "report", "answer", "content", "text", "output",
    }
    found: list[Any] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in keys:
                    if isinstance(child, list):
                        found.extend(child)
                    elif isinstance(child, (dict, str)):
                        found.append(child)
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(data)
    cleaned = []
    for rec in found:
        if isinstance(rec, str) and rec.strip():
            cleaned.append(rec.strip())
        elif isinstance(rec, dict) and rec:
            cleaned.append(rec)
    return cleaned


def find_recommendations() -> tuple[list[Any], Path | None, str]:
    if FINAL_RECOMMENDATIONS_TXT.exists():
        try:
            text = FINAL_RECOMMENDATIONS_TXT.read_text(encoding="utf-8").strip()
            if text and not any(bad in text for bad in ["Error:", "Execution Failure", "Traceback"]):
                return [text], FINAL_RECOMMENDATIONS_TXT, "txt"
        except Exception:
            pass

    for path in all_json_files():
        data = read_json(path)
        if isinstance(data, dict):
            recs = extract_recommendations_from_json(data)
            cleaned = []
            for rec in recs:
                text = rec if isinstance(rec, str) else json.dumps(rec, ensure_ascii=False)
                low = text.lower()
                if any(bad in low for bad in ["requirements", "easyocr", "opencv-python", "streamlit", "pandas"]):
                    continue
                if any(sig in low for sig in ["توص", "امتثال", "حوكمة", "معالجة", "سياسة", "مخالفة", "تحسين", "recommend", "compliance", "policy", "governance"]):
                    cleaned.append(rec)
            if cleaned:
                return cleaned, path, "json"

    signals = ["توص", "امتثال", "حوكمة", "معالجة", "سياسة", "مخالفة", "تحسين", "recommend", "compliance", "policy", "governance"]
    for path in all_text_reports():
        try:
            text = path.read_text(encoding="utf-8").strip()
            low = text.lower()
            if not text or any(bad in text for bad in ["Error:", "Execution Failure", "Traceback"]):
                continue
            if any(skip in low for skip in ["easyocr", "opencv-python", "streamlit", "pandas", "requirements"]):
                continue
            if any(signal in low for signal in signals):
                return [text], path, "txt"
        except Exception:
            pass
    return [], None, ""


def merge_team_outputs(output: dict) -> dict:
    output = normalize_output(output)
    results = output.get("results", [])
    scoring, scoring_path = find_scoring_result()
    recs, rec_path, _ = find_recommendations()
    for item in results:
        if scoring:
            item["scores"] = scoring
            item["scores_source"] = str(scoring_path) if scoring_path else ""
        if recs:
            item["recommendations"] = recs
            item["recommendations_source"] = str(rec_path) if rec_path else ""
    output["results"] = results
    if scoring:
        output["scores"] = scoring
        output["scores_source"] = str(scoring_path) if scoring_path else ""
    if recs:
        output["recommendations"] = recs
        output["recommendations_source"] = str(rec_path) if rec_path else ""
    return output


def build_single_file_output(result: dict) -> dict:
    classification = safe_get(result, ["dc.final_classification", "classification"], "غير محدد")
    return {
        "system_name": "NDI-Sentinel",
        "agent": "Dashboard Run",
        "total_files_scanned": 1,
        "summary": {
            "عام": 1 if classification == "عام" else 0,
            "مقيد": 1 if classification == "مقيد" else 0,
            "سري": 1 if classification == "سري" else 0,
            "سري للغاية": 1 if classification == "سري للغاية" else 0,
            "files_with_pdp": 1 if safe_get(result, ["pdp.has_personal_data"], False) else 0,
            "files_requiring_sharing_review": 1 if safe_get(result, ["ds.sharing_requires_review"], False) else 0,
        },
        "results": [result],
    }


def run_compliance_agent(file_path: Path) -> dict:
    if ComplianceAgent is None:
        raise RuntimeError(f"تعذر استيراد ComplianceAgent من src/compliance_agent.py\nسبب الخطأ: {IMPORT_ERROR}")
    agent = ComplianceAgent()
    result = agent.run(file_path)
    output = merge_team_outputs(build_single_file_output(result))
    write_json(output, OUTPUTS_DIR / "latest_dashboard_output.json")
    write_json(output, OUTPUTS_DIR / "compliance_output.json")
    return output


def load_default_output() -> dict:
    for path in [OUTPUTS_DIR / "latest_dashboard_output.json", OUTPUTS_DIR / "compliance_output.json", OUTPUT_DIR / "compliance_output.json"]:
        data = read_json(path)
        if data:
            return merge_team_outputs(data)
    return merge_team_outputs({"results": []})


def to_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace("%", "").strip())
        except Exception:
            return None
    return None


def format_value(value: Any, default: str = "غير متوفر") -> Any:
    if value in [None, "", []]:
        return default
    return value


def esc(value: Any) -> str:
    return html.escape(str(format_value(value, "")))


def status_html(text: str, color: str = "blue") -> str:
    return f'<span class="status {color}">{esc(text)}</span>'


def metric_card(label: str, value: Any, note: str = "", icon: str = "▣", color: str = "blue") -> None:
    colors = {
        "blue": ("var(--blue-soft)", "var(--blue)"),
        "green": ("var(--primary-soft)", "var(--primary)"),
        "amber": ("var(--amber-soft)", "var(--amber)"),
        "red": ("var(--red-soft)", "var(--red)"),
        "purple": ("var(--purple-soft)", "var(--purple)"),
    }
    icon_bg, icon_color = colors.get(color, colors["blue"])
    st.markdown(
        f"""
        <div class="metric-card" style="--icon-bg:{icon_bg}; --icon-color:{icon_color};">
            <div class="metric-top">
                <div class="metric-label">{esc(label)}</div>
                <div class="metric-icon">{esc(icon)}</div>
            </div>
            <div>
                <div class="metric-value">{esc(value)}</div>
                <div class="metric-note">{esc(note)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def arabic_maturity_description(description: Any, label: Any = None) -> str:
    mapping = {
        "Absence of Capabilities": "لا توجد ممارسات مؤسسية واضحة.",
        "Establishing": "تم تقديم ممارسات أساسية لكنها غير موحدة بالكامل.",
        "Defined": "ممارسات مطورة ومتسقة على مستوى الجهة.",
        "Activated": "عمليات مؤسسية وأدوات قابلة للتوسع.",
        "Managed": "حوكمة مركزية مدعومة بمؤشرات أداء وقياسات.",
        "Pioneer": "تحسين مستمر وابتكار في إدارة البيانات.",
        "Institutional processes and scalable tools": "عمليات مؤسسية وأدوات قابلة للتوسع.",
    }
    if label in mapping:
        return mapping[label]
    if description in mapping:
        return mapping[description]
    return str(description) if description not in [None, "", []] else "غير محسوب"


def render_header(active: str = "overview") -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <div class="brand">
                <div class="brand-icon">▣</div>
                <div>
                    <div class="brand-title">NDI-Sentinel</div>
                    <div class="brand-subtitle">منصة حوكمة البيانات والامتثال</div>
                </div>
            </div>
            <div class="top-menu">
                <span class="menu-item {'active' if active == 'overview' else ''}">نظرة عامة</span>
                <span class="menu-item {'active' if active == 'files' else ''}">الملفات</span>
                <span class="menu-item {'active' if active == 'reports' else ''}">التقارير</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_title(title: str, subtitle: str, icon: str = "▦") -> None:
    st.markdown(
        f"""<div class="page-heading"><div class="page-title">{esc(icon)} {esc(title)}</div><div class="page-subtitle">{esc(subtitle)}</div></div>""",
        unsafe_allow_html=True,
    )


def classification_counts(results: list[dict]) -> dict:
    counts = {"عام": 0, "مقيد": 0, "سري": 0, "سري للغاية": 0}
    for item in results:
        level = safe_get(item, ["dc.final_classification", "classification"], "غير محدد")
        if level in counts:
            counts[level] += 1
    return counts


def render_classification_summary(results: list[dict]) -> None:
    counts = classification_counts(results)
    total = max(sum(counts.values()), 1)

    color_map = {
    "عام": "#16a34a",
    "مقيد": "#16a34a",
    "سري": "#16a34a",
    "سري للغاية": "#16a34a",
    }

    bars_html = ""

    for label, value in counts.items():
        pct = int((value / total) * 100)
        color = color_map.get(label, "#0f766e")

        bars_html += f"""
        <div class="classification-item">
            <div class="classification-head">
                <span>{esc(label)}</span>
                <span>{value}</span>
            </div>
            <div class="classification-track">
                <div class="classification-fill" style="width:{pct}%; background:{color};"></div>
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div class="visual-card classification-card">
            <div class="section-title-sm">التصنيف العام للبيانات</div>
            {bars_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_score_gauge(score: Any) -> None:
    number = to_number(score)
    width = 0 if number is None else max(0, min(100, int((number / 5) * 100)))
    note = "من 5" if number is not None else "لا توجد نتيجة محسوبة"
    st.markdown(
        f"""
        <div class="visual-card">
            <div class="section-title-sm">ملخص الامتثال التشغيلي OE</div>
            <div class="gauge-box">
                <div class="gauge-score">{esc(score)}</div>
                <div class="gauge-track"><div class="gauge-fill" style="--w:{width}%;"></div></div>
                <div class="gauge-note">{esc(note)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_maturity_level(level: Any, description: str) -> None:
    st.markdown(
        f"""
        <div class="visual-card">
            <div class="section-title-sm">مستوى النضج</div>
            <div class="maturity-badge">{esc(level)}</div>
            <div class="maturity-title">مستوى {esc(level)}</div>
            <div class="maturity-desc">{esc(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_html_table(rows: list[dict], column_classes: dict[str, str] | None = None) -> None:
    if not rows:
        st.markdown('<div class="empty-card">لا توجد بيانات للعرض.</div>', unsafe_allow_html=True)
        return
    column_classes = column_classes or {}
    columns = list(rows[0].keys())
    thead = "".join([f"<th>{esc(col)}</th>" for col in columns])
    tbody = ""
    for row in rows:
        cells = ""
        for col in columns:
            css_class = column_classes.get(col, "")
            value = row.get(col, "")
            cells += f'<td class="{css_class}">{value}</td>'
        tbody += f"<tr>{cells}</tr>"
    st.markdown(f'<div class="table-wrap"><table class="clean-table"><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>', unsafe_allow_html=True)


def results_rows(results: list[dict]) -> list[dict]:
    rows = []
    for item in results:
        scores = item.get("scores", {})
        classification = safe_get(item, ["dc.final_classification", "classification"], "غير محدد")
        review = "نعم" if safe_get(item, ["ds.sharing_requires_review"], False) else "لا"
        pdp = "نعم" if safe_get(item, ["pdp.has_personal_data"], False) else "لا"
        rows.append({
            "اسم الملف": esc(item.get("file_name", item.get("اسم_الملف", ""))),
            "نوع الملف": esc(item.get("file_type", "")),
            "التصنيف": status_html(classification, "amber" if classification == "مقيد" else "green" if classification == "عام" else "red"),
            "درجة الأثر": esc(safe_get(item, ["dc.impact_level", "impact_level"], "غير محدد")),
            "بيانات شخصية": status_html(pdp, "blue" if pdp == "نعم" else "green"),
            "مراجعة مشاركة": status_html(review, "amber" if review == "نعم" else "green"),
            "جودة البيانات": esc(safe_get(item, ["dq.quality_score"], "لا ينطبق")),
            "درجة OE": esc(scores.get("final_score", "غير محسوب")),
            "مستوى النضج": esc(scores.get("maturity_level", "غير محسوب")),
        })
    return rows


def pdp_rows(item: dict) -> list[dict]:
    findings = safe_get(item, ["pdp.findings"], [])
    rows = []
    for finding in findings:
        rows.append({
            "القيمة": esc(finding.get("القيمة", finding.get("value", ""))),
            "المبرر": esc(finding.get("مبرر_التصنيف", finding.get("reason", finding.get("category", "")))),
        })
    return rows


def get_score_data(output: dict, results: list[dict]) -> dict:
    scoring = output.get("scores")
    if isinstance(scoring, dict) and scoring:
        return scoring
    for item in results:
        item_score = item.get("scores")
        if isinstance(item_score, dict) and item_score:
            return item_score
    return {}


def get_recommendations(output: dict, item: dict | None = None) -> tuple[list[Any], str]:
    recommendations = []
    source = ""
    if item:
        recommendations = item.get("recommendations", [])
        source = item.get("recommendations_source", "")
    if not recommendations:
        recommendations = output.get("recommendations", [])
        source = output.get("recommendations_source", "")
    return recommendations, source


def recommendation_text(rec: Any, fallback_source: str = "") -> tuple[str, str]:
    if isinstance(rec, dict):
        text = rec.get("recommendation") or rec.get("text") or rec.get("answer") or rec.get("content") or rec.get("report") or json.dumps(rec, ensure_ascii=False)
        source = rec.get("policy_reference") or rec.get("source") or rec.get("article") or rec.get("policy") or fallback_source
        return str(text), str(source) if source else "غير محدد"
    return str(rec), fallback_source or "مخرج وكيل التوصيات RAG"


def fallback_recommendations(item: dict | None = None) -> list[str]:
    if not item:
        return ["تشغيل وكيل التوصيات RAG وربط مخرجاته بملفات الامتثال قبل اعتماد التقرير النهائي."]
    recs: list[str] = []
    classification = safe_get(item, ["dc.final_classification", "classification"], "غير محدد")
    has_pdp = safe_get(item, ["pdp.has_personal_data"], False)
    requires_review = safe_get(item, ["ds.sharing_requires_review"], False)
    dq = item.get("dq", {}) if isinstance(item.get("dq", {}), dict) else {}
    if has_pdp:
        recs.append("تطبيق ضوابط حماية البيانات الشخصية قبل مشاركة الملف، مع إخفاء أو ترميز المعرفات المباشرة مثل الهوية ورقم الجوال والبيانات الصحية.")
    if classification in ["مقيد", "سري", "سري للغاية"]:
        recs.append(f"اعتماد تصنيف الملف كـ {classification} وتقييد الوصول حسب الصلاحيات المعتمدة وسياسات مشاركة البيانات.")
    if requires_review:
        recs.append("إجراء مراجعة حوكمة وموافقة مالك البيانات قبل أي مشاركة داخلية أو خارجية للملف.")
    if dq.get("applies"):
        recs.append("مراجعة مؤشرات جودة البيانات ومعالجة القيم المفقودة أو المكررة قبل استخدام الملف في التقارير الرسمية.")
    if not recs:
        recs.append("لا توجد ملاحظات حرجة ظاهرة، ويُنصح بحفظ نتيجة الفحص كدليل حوكمة ومراجعتها ضمن دورة الامتثال القادمة.")
    return recs


def render_recommendation_card(output: dict, item: dict | None = None) -> None:
    recommendations, source_path = get_recommendations(output, item)
    if not recommendations:
        recommendations = fallback_recommendations(item)

    blocks = []
    for rec in recommendations[:6]:
        text, _ = recommendation_text(rec, "")
        if text.strip():
            blocks.append(f'<div class="recommendation-item">{esc(text)}</div>')
    if not blocks:
        blocks = [f'<div class="recommendation-item">{esc(fallback_recommendations(item)[0])}</div>']

    st.markdown(
        f"""<div class="recommendation-card"><div class="section-title-sm">التوصيات الاستراتيجية </div><div class="recommendation-box">{''.join(blocks)}</div></div>""",
        unsafe_allow_html=True,
    )


def render_file_details(output: dict, item: dict) -> None:
    file_name = item.get("file_name", item.get("اسم_الملف", "ملف غير محدد"))
    file_type = item.get("file_type", "غير محدد")
    classification = safe_get(item, ["dc.final_classification", "classification"], "غير محدد")
    impact = safe_get(item, ["dc.impact_level", "impact_level"], "غير محدد")
    st.markdown(
        f"""
        <div class="file-card">
            <div class="section-title-sm">تفاصيل الملف</div>
            <div class="file-head">
                <div class="file-icon">▤</div>
                <div>
                    <div class="file-name">{esc(file_name)}</div>
                    <div class="file-type">نوع الملف: {esc(file_type)}</div>
                </div>
            </div>
            {status_html(classification, "amber" if classification == "مقيد" else "green" if classification == "عام" else "red")}
            {status_html(f"درجة الأثر: {impact}", "blue")}
        </div>
        """,
        unsafe_allow_html=True,
    )
    tab1, tab2, tab3, tab4 = st.tabs(["العناصر الشخصية PDP", "جودة البيانات DQ", "مشاركة البيانات DS", "النص المستخرج"])
    with tab1:
        rows = pdp_rows(item)
        if rows:
            render_html_table(rows, {"المبرر": "wide", "القيمة": "wide"})
        else:
            st.markdown('<div class="success-card">لم يتم اكتشاف عناصر شخصية واضحة في الملف.</div>', unsafe_allow_html=True)
    with tab2:
        dq = item.get("dq", {})
        if dq.get("applies"):
            q1, q2, q3, q4 = st.columns(4)
            with q1:
                metric_card("عدد الصفوف", dq.get("rows"), "صف", "▦", "blue")
            with q2:
                metric_card("القيم المفقودة", dq.get("null_percentage"), "نسبة مئوية", "◌", "amber")
            with q3:
                metric_card("الصفوف المكررة", dq.get("duplicate_rows"), "صف", "▧", "purple")
            with q4:
                metric_card("البريد غير الصحيح", dq.get("invalid_emails"), "عنصر", "✕", "red")
        else:
            st.markdown(f'<div class="empty-card">{esc(dq.get("reason", "لا ينطبق تحليل جودة البيانات على هذا الملف."))}</div>', unsafe_allow_html=True)
    with tab3:
        ds = item.get("ds", {})
        if ds.get("sharing_requires_review"):
            st.markdown(f'<div class="warning-card">{esc(ds.get("reason", "يحتاج الملف إلى مراجعة قبل المشاركة."))}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-card">{esc(ds.get("reason", "لا يحتاج الملف إلى مراجعة مشاركة عالية."))}</div>', unsafe_allow_html=True)
    with tab4:
        preview = item.get("extracted_text_preview", item.get("النص_المستخرج", ""))
        st.text_area("النص المستخرج", value=preview, height=220)


def render_reports_section() -> None:
    pdf = latest_pdf_report()
    txt = recommendations_txt_report()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = [
        {
            "نوع التقرير": "تقرير الانتهاكات PDF",
            "الحالة": status_html("متوفر", "green") if pdf else status_html("غير متوفر", "amber"),
            "آخر تحديث": esc(datetime.fromtimestamp(pdf.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if pdf else now),
            "الإجراء": "تحميل التقرير" if pdf else "غير متاح",
        },
        {
            "نوع التقرير": "ملف التوصيات TXT",
            "الحالة": status_html("متوفر", "green") if txt else status_html("غير متوفر", "amber"),
            "آخر تحديث": esc(datetime.fromtimestamp(txt.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if txt else now),
            "الإجراء": "تحميل التوصيات" if txt else "غير متاح",
        },
    ]
    st.markdown('<div class="plain-section-title">التقارير والمخرجات</div>', unsafe_allow_html=True)
    render_html_table(rows)

    col1, col2 = st.columns(2)
    with col1:
        if pdf:
            with open(pdf, "rb") as f:
                st.download_button("تحميل تقرير الانتهاكات PDF", data=f, file_name=pdf.name, mime="application/pdf", use_container_width=True)
    with col2:
        if txt:
            with open(txt, "rb") as f:
                st.download_button("تحميل ملف التوصيات TXT", data=f, file_name=txt.name, mime="text/plain", use_container_width=True)


def render_home() -> None:
    render_header("overview")
    render_page_title(
        "بدء فحص جديد",
        "ارفع ملفًا باللغة العربية لتحليل البيانات الشخصية وتصنيف مستوى الحساسية وقياس جودة البيانات وربط النتائج بالتوصيات والتقارير.",
        "▣",
    )
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.markdown(
            '<div class="upload-shell">\n                <div class="upload-shell-head">\n                    <div class="upload-shell-title">رفع ملف للتحليل</div>\n                    <div class="upload-shell-desc">الصيغ المدعومة: PNG, JPG, PDF, CSV, Excel, TXT, DOCX.</div>\n                </div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(" ", type=SUPPORTED_TYPES, label_visibility="collapsed")
        st.markdown('<div class="upload-helper">اسحب وأفلت الملف هنا أو استخدم زر الاختيار في المنتصف.</div></div>', unsafe_allow_html=True)
        if uploaded_file:
            if st.button("بدء التحليل وعرض لوحة التحكم", use_container_width=True):
                with st.spinner("جاري تحليل الملف وتشغيل النظام..."):
                    try:
                        path = save_uploaded_file(uploaded_file)
                        output = run_compliance_agent(path)
                        st.session_state["dashboard_output"] = output
                        st.session_state["page"] = "dashboard"
                        st.rerun()
                    except Exception as e:
                        st.error("حدث خطأ أثناء التحليل.")
                        st.exception(e)
    with right:
        st.markdown('<div class="process-card"><div class="process-title">مسار المعالجة</div>', unsafe_allow_html=True)
        steps = ["حفظ الملف داخل مجلد الرفع", "استخراج النص أو قراءة الجدول", "اكتشاف البيانات الشخصية وتصنيف البيانات", "تحليل جودة البيانات وقرار المشاركة", "دمج درجات النضج والتوصيات", "عرض التقرير النهائي"]
        for i, step in enumerate(steps, start=1):
            st.markdown(f'<div class="process-row"><div class="process-number">{i}</div><div class="process-text">{esc(step)}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("عرض آخر نتائج محفوظة", use_container_width=True):
            st.session_state["dashboard_output"] = load_default_output()
            st.session_state["page"] = "dashboard"
            st.rerun()
    st.markdown('<div class="footer">© 2026 NDI-Sentinel</div>', unsafe_allow_html=True)


def render_dashboard(output: dict) -> None:
    output = merge_team_outputs(output)
    results = output.get("results", [])
    render_header("overview")
    render_page_title("نظرة عامة على الامتثال", "عرض موحد لنتائج فحص الملفات ودرجات النضج والتوصيات والتقارير النهائية.", "▦")
    if not results:
        st.markdown('<div class="empty-card">لا توجد نتائج جاهزة للعرض. ارفع ملفًا جديدًا أو اعرض آخر نتائج محفوظة.</div>', unsafe_allow_html=True)
        if st.button("العودة إلى رفع الملفات", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()
        return
    scoring = get_score_data(output, results)
    final_score = scoring.get("final_score")
    maturity_level = scoring.get("maturity_level")
    maturity_label = scoring.get("maturity_label")
    maturity_description = arabic_maturity_description(scoring.get("maturity_description"), maturity_label)
    dq_score = safe_get(results[0], ["dq.quality_score"], None)
    total_files = len(results)
    pdp_count = sum(1 for r in results if safe_get(r, ["pdp.has_personal_data"], False))
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        metric_card("الملفات المفحوصة", total_files, "حسب نتائج التحليل", "▤", "purple")
    with m2:
        metric_card("بيانات شخصية", pdp_count, "ملفات تحتوي على PDP", "◎", "blue")
    with m3:
        metric_card("جودة البيانات", dq_score if dq_score is not None else "لا ينطبق", "نتيجة DQ الفعلية", "◒", "green")
    with m4:
        metric_card("مستوى النضج", maturity_level if maturity_level is not None else "غير محسوب", maturity_label if maturity_label else "غير محسوب", "◆", "amber")
    with m5:
        metric_card("درجة OE", final_score if final_score is not None else "غير محسوب", "من ملف scoring", "⬢", "green")
    st.markdown('<div class="overview-grid">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        render_classification_summary(results)
    with col2:
        render_score_gauge(final_score if final_score is not None else "غير محسوب")
    with col3:
        render_maturity_level(maturity_level if maturity_level is not None else "غير محسوب", maturity_description)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="plain-section-title">جدول الملفات</div>', unsafe_allow_html=True)
    render_html_table(results_rows(results), {"اسم الملف": "wide"})
    selected_item = results[0]
    if len(results) > 1:
        file_names = [r.get("file_name", r.get("اسم_الملف", f"file_{i}")) for i, r in enumerate(results)]
        selected_name = st.selectbox("اختيار ملف لعرض التفاصيل", file_names)
        selected_item = next(r for r in results if r.get("file_name", r.get("اسم_الملف", "")) == selected_name)
    left, right = st.columns([1, 1.2], gap="large")
    with left:
        render_file_details(output, selected_item)
    with right:
        render_recommendation_card(output, selected_item)
    render_reports_section()
    if st.button("رفع ملف جديد", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()
    st.markdown('<div class="footer">© 2026 NDI-Sentinel</div>', unsafe_allow_html=True)


def main() -> None:
    if "page" not in st.session_state:
        st.session_state["page"] = "home"
    if st.session_state["page"] == "home":
        render_home()
    elif st.session_state["page"] == "dashboard":
        output = st.session_state.get("dashboard_output") or load_default_output()
        render_dashboard(output)


if __name__ == "__main__":
    main()
