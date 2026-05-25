import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from glob import glob
from datetime import datetime
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.fonts import addMapping
import matplotlib
import tempfile
import os
import json
import re
import matplotlib
matplotlib.use('Agg')


import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st

st.set_page_config(
    page_title="SMT Error Dashboard",
    layout="wide"
)

canvas.setFont("Helvetica", 12)

st.set_page_config(page_title="SMT Error Dashboard", layout="wide")

# ==================== INITIALIZE SESSION STATE ====================
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'selected_line' not in st.session_state:
    st.session_state['selected_line'] = None
if 'loaded_files' not in st.session_state:
    st.session_state['loaded_files'] = []
if 'data_mode' not in st.session_state:
    st.session_state['data_mode'] = None
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []
if 'error_col' not in st.session_state:
    st.session_state['error_col'] = None
if 'lot_col' not in st.session_state:
    st.session_state['lot_col'] = None
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False

# ==================== CONFIGURATION ====================
LINE_CONFIG = {
    "Line 1": {
        "paths": [
            "//172.16.0.113/History_Log/Line1/YSM20-Y48740/Retry/",
            "//172.16.0.113/History_Log/Line1/YSM20-Y48998/Retry/"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 2": {
        "paths": ["//172.16.0.113/History_Log/Line2/YSM20_Y43897/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 3": {
        "paths": ["//172.16.0.113/History_Log/Line3/YSM20R-Y56682/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 4": {
        "paths": ["//172.16.0.114/History_log/Line4/YSM10_Y64131/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 5": {
        "paths": ["//172.16.0.113/History_Log/Line5/YSM10_Y67426/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 6": {
        "paths": [
            "//172.16.0.114/History_log/Line6/YSM20R_Y56073/Retry",
            "//172.16.0.114/History_log/Line6/YSM20R_Y66007/Retry",
            "//172.16.0.114/History_log/Line6/YSM20_Y37008/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 7": {
        "paths": ["//172.16.0.114/History_log/Line7/YSM10_Y64130/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 8": {
        "paths": [
            "//172.16.0.195/YAMAHA_history/Line8_YRM/YRM20_1 (Y72929)/Retry",
            "//172.16.0.195/YAMAHA_history/Line8_YRM/YRM20_2 (Y72930)/Retry",
            "//172.16.0.195/YAMAHA_history/Line8_YRM/YRM20_3 (Y72927)/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 9": {
        "paths": [
            "//172.16.0.195/YAMAHA_history/Line9_YRM/YRM20_1 (Y72931)/Retry",
            "//172.16.0.195/YAMAHA_history/Line9_YRM/YRM20_2 (Y72932)/Retry",
            "//172.16.0.195/YAMAHA_history/Line9_YRM/YRM20_3 (Y72928)/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 10": {
        "paths": ["//172.16.0.195/YAMAHA_history/Line10-YRM/YRM20_Y72933/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 11": {
        "paths": ["//172.16.0.111/History_log/Line11/YSM20_Y37015/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 12": {
        "paths": ["//172.16.0.111/History_log/Line12/YSM20R_Y56072/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 13": {
        "paths": ["//172.16.0.111/History_log/Line13/YSM10_Y66005/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 14": {
        "paths": [
            "//172.16.0.112/History_log/Line14/YS24_Y27080/Retry",
            "//172.16.0.112/History_log/Line14/YS24_Y32890/Retry",
            "//172.16.0.112/History_log/Line14/YSM20_Y37011/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 15": {
        "paths": [
            "//172.16.0.112/History_log/Line15/YS24_Y31607/Retry",
            "//172.16.0.112/History_log/Line15/YS24_Y32889/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 16": {
        "paths": [
            "//172.16.0.111/History_log/Line16/YSM20_Y37007/Retry",
            "//172.16.0.111/History_log/Line16/YSM20_Y37010/Retry",
            "//172.16.0.111/History_log/Line16/YS88_Y27081/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 17": {
        "paths": [
            "//172.16.0.111/History_log/Line17/YSM20R_Y46695/Retry",
            "//172.16.0.111/History_log/Line17/YSM20_Y37004/Retry",
            "//172.16.0.111/History_log/Line17/YSM20_Y37005/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 18": {
        "paths": [
            "//172.16.0.113/History_Log/Line18/YSM10_Y67425/Retry",
            "//172.16.0.113/History_Log/Line18/YS88_Y33574/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 19": {
        "paths": [
            "//172.16.0.112/History_log/Line19/YS24_Y33570/Retry",
            "//172.16.0.112/History_log/Line19/YS24_Y33572/Retry",
            "//172.16.0.112/History_log/Line19/YS88_Y33573/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 20": {
        "paths": [
            "//172.16.0.112/History_log/Line19/YS24_Y33570/Retry",
            "//172.16.0.112/History_log/Line20/YS24_Y33571/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 21": {
        "paths": [
            "//172.16.0.112/History_log/Line21/YSM20R_Y58571/Retry",
            "//172.16.0.112/History_log/Line21/YSM20_Y37013/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 22": {
        "paths": ["//172.16.0.112/History_log/Line22/YSM20R_Y60462/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 23": {
        "paths": [
            "//172.16.0.113/History_Log/Line23/YSM20R_Y62750/Retry",
            "//172.16.0.113/History_Log/Line23/YSM20R_Y62751/Retry",
            "//172.16.0.113/History_Log/Line23/YSM20R_Y62752/Retry"
        ],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 24": {
        "paths": ["//172.16.0.111/History_log/Line24/YSM20R_Y66006/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    }
}

CONFIG_FILE = "line_config.json"

def normalize_path(path):
    """ปรับ Format Path ให้เหมาะสมกับ Windows"""
    if path.startswith('//'):
        path = path.replace('/', '\\')
    if not path.endswith('\\') and not path.endswith('/'):
        path = path + '\\'
    return path

def load_line_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return LINE_CONFIG

def extract_year_from_string(text):
    """ดึงปีจากข้อความ"""
    text = str(text)
    patterns = [r'(202[0-9])', r'ปี(202[0-9])', r'_(202[0-9])_', r'-(202[0-9])-']
    for pattern in patterns:
        years = re.findall(pattern, text)
        if years:
            return int(years[0])
    return None

def get_files_from_line(line_name, config, log_type):
    line_data = config[line_name]
    paths = line_data['paths']
    pattern = line_data.get('file_pattern', '*.csv')
    all_files = []

    for path in paths:
        if log_type == "Error Log":
            path = path.replace("Retry", "ErrorLog")

        path = normalize_path(path)
        search_pattern = os.path.join(path, pattern)
        files = glob(search_pattern)

        for file in files:
            all_files.append(file)

    return all_files

def load_data_from_line(line_name, config, log_type):

    files = get_files_from_line(line_name, config, log_type)

    if not files:
        return None, []

    all_dfs = []

    for file in files:

        try:
            df = pd.read_csv(file, header=1, encoding='utf-8')

            df['source_file'] = os.path.basename(file)
            df['source_path'] = file
            df['line'] = line_name
            df['log_type'] = log_type

            all_dfs.append(df)

        except UnicodeDecodeError:

            try:
                df = pd.read_csv(file, header=1, encoding='latin1')

                df['source_file'] = os.path.basename(file)
                df['source_path'] = file
                df['line'] = line_name
                df['log_type'] = log_type

                all_dfs.append(df)

            except Exception as e2:
                st.warning(f"อ่านไฟล์ {os.path.basename(file)} ไม่สำเร็จ: {str(e2)}")

        except Exception as e:
            st.warning(f"อ่านไฟล์ {os.path.basename(file)} ไม่สำเร็จ: {str(e)}")

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True), files

    return None, []

def detect_columns(df):
    """ตรวจจับคอลัมน์ที่จำเป็นอัตโนมัติ"""
    time_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['time', 'date', 'วันที่', 'เวลา', 'timestamp']):
            time_col = col
            break
    
    if time_col is None and len(df.columns) > 0:
        time_col = df.columns[0]
    
    error_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if 'error' in col_lower and 'name' in col_lower:
            error_col = col
            break
    
    if error_col is None:
        for col in df.columns:
            col_lower = str(col).lower()
            if 'error' in col_lower:
                error_col = col
                break
    
    if error_col is None and len(df.columns) > 1:
        error_col = df.columns[1]
    
    lot_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if 'lot' in col_lower:
            lot_col = col
            break
    
    if lot_col is None and len(df.columns) > 2:
        lot_col = df.columns[2]
    
    return time_col, error_col, lot_col

def process_dataframe(df):
    """ประมวลผล DataFrame ให้อยู่ในรูปแบบที่เหมาะสม"""
    if df is None or len(df) == 0:
        return None, None, None, None
    
    time_col, error_col, lot_col = detect_columns(df)
    
    if time_col is None:
        st.error("❌ ไม่พบคอลัมน์เวลาในข้อมูล")
        return None, None, None, None
    
    try:
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        df = df.dropna(subset=[time_col])
        df.rename(columns={time_col: 'Occurrence Time'}, inplace=True)
    except Exception as e:
        st.error(f"❌ ไม่สามารถแปลงคอลัมน์เวลาได้: {str(e)}")
        return None, None, None, None
    
    if len(df) == 0:
        st.error("❌ ไม่มีข้อมูลหลังจากแปลงเวลา")
        return None, None, None, None
    
    return df, error_col, lot_col, time_col

def generate_pdf_report(df, filtered_df, error_col, lot_col, uploaded_files, line_name=None):
    """สร้างรายงาน PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Tahoma-Bold',
        fontSize=22,
        leading=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1f77b4')
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName='Tahoma-Bold',
        fontSize=18,
        leading=20,
        spaceAfter=12,
        textColor=colors.HexColor('#2c3e50')
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Tahoma',
        fontSize=14,
        leading=16,
        spaceAfter=6
    )
    
    story = []
    
    title_text = f"รายงานสรุป Error SMT Mounter - {line_name if line_name else 'All Lines'}"
    story.append(Paragraph(title_text, title_style))
    story.append(Paragraph(f"วันที่สร้างรายงาน: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1. ข้อมูลสรุปภาพรวม", heading_style))
    
    if 'Occurrence Time' in filtered_df.columns and len(filtered_df) > 0:
        min_date = filtered_df['Occurrence Time'].min()
        max_date = filtered_df['Occurrence Time'].max()
        date_range_text = f"{min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')}"
        days_diff = (max_date - min_date).days + 1
    else:
        date_range_text = "ไม่พบข้อมูลวันที่"
        days_diff = 0
    
    summary_data = [
        ['รายการ', 'ค่า'],
        ['จำนวนไฟล์ที่ใช้', str(len(uploaded_files))],
        ['จำนวน Error ทั้งหมด', f"{len(filtered_df):,}"],
        ['จำนวน Lot ที่พบ', f"{filtered_df[lot_col].nunique():,}"],
        ['จำนวน Error Type', f"{filtered_df[error_col].nunique():,}"],
        ['ช่วงวันที่', date_range_text],
        ['ระยะเวลา', f"{days_diff} วัน"],
    ]
    
    summary_table = Table(summary_data, colWidths=[120, 300])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#d3d3d3')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Tahoma'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    if len(filtered_df) > 0:
        story.append(Paragraph("2. Error ที่พบบ่อยที่สุด 10 อันดับแรก", heading_style))
        error_counts = filtered_df[error_col].value_counts().head(10)
        error_table_data = [['ลำดับ', 'Error Name', 'จำนวนครั้ง', 'เปอร์เซ็นต์']]
        for i, (err_name, count) in enumerate(error_counts.items(), 1):
            percentage = (count / len(filtered_df)) * 100
            error_table_data.append([str(i), str(err_name)[:50], f"{count:,}", f'{percentage:.1f}%'])
        
        error_table = Table(error_table_data, colWidths=[40, 250, 60, 60])
        error_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(error_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("3. Lot ที่เกิด Error มากที่สุด 10 อันดับแรก", heading_style))
        lot_counts = filtered_df[lot_col].value_counts().head(10)
        lot_table_data = [['ลำดับ', 'Lot Name', 'จำนวน Error', 'เปอร์เซ็นต์']]
        for i, (lot_name, count) in enumerate(lot_counts.items(), 1):
            percentage = (count / len(filtered_df)) * 100
            lot_table_data.append([str(i), str(lot_name)[:50], f"{count:,}", f'{percentage:.1f}%'])
        
        lot_table = Table(lot_table_data, colWidths=[40, 250, 60, 60])
        lot_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(lot_table)
        
        
        # ==================== ADD CHARTS TO PDF ====================

        story.append(PageBreak())
        story.append(Paragraph("4. กราฟวิเคราะห์ข้อมูล", heading_style))

        # ---------- Chart 1: Top Error ----------
        error_counts = filtered_df[error_col].value_counts().head(10)

        fig1, ax1 = plt.subplots(figsize=(8, 4))
        error_counts.plot(kind='bar', color='skyblue', ax=ax1)

        ax1.set_title("Top 10 Error")
        ax1.set_xlabel("Error")
        ax1.set_ylabel("Count")

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        tmp1 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig1.savefig(tmp1.name, dpi=300, bbox_inches='tight')
        plt.close(fig1)

        story.append(Paragraph("4.1 Top 10 Error", heading_style))
        story.append(Image(tmp1.name, width=16*cm, height=8*cm))
        story.append(Spacer(1, 12))


        # ---------- Chart 2: Top Lot ----------
        lot_counts = filtered_df[lot_col].value_counts().head(10)

        fig2, ax2 = plt.subplots(figsize=(8, 4))
        lot_counts.plot(kind='bar', color='lightcoral', ax=ax2)

        ax2.set_title("Top 10 Lot")
        ax2.set_xlabel("Lot")
        ax2.set_ylabel("Count")

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        tmp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig2.savefig(tmp2.name, dpi=300, bbox_inches='tight')
        plt.close(fig2)

        story.append(Paragraph("4.2 Top 10 Lot", heading_style))
        story.append(Image(tmp2.name, width=16*cm, height=8*cm))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer



# ==================== MAIN UI ====================
st.title("🏭 SMT Machine Retry Error Dashboard")

st.sidebar.header("🏭 เลือกไลน์การผลิต")

log_type = st.sidebar.selectbox(
    "เลือกประเภท Log",
    ["Retry Log", "Error Log"]
)

mode = st.sidebar.radio(
    "เลือกโหมด",
    ["🌐 ดึงจาก Network ตามไลน์", "📁 อัปโหลดไฟล์เอง"],
    index=0
)

if mode == "🌐 ดึงจาก Network ตามไลน์":
    config = load_line_config()
    available_lines = list(config.keys())
    
    selected_line = st.sidebar.selectbox("เลือกไลน์การผลิต", available_lines)
    
    with st.sidebar.expander("🔌 สถานะการเชื่อมต่อ Network"):
        if selected_line and selected_line in config:
            line_info = config[selected_line]
            for i, path in enumerate(line_info['paths']):
                path_normalized = normalize_path(path)
                try:
                    if os.path.exists(path_normalized):
                        st.success(f"✅ Path {i+1}: เชื่อมต่อได้")
                    else:
                        st.error(f"❌ Path {i+1}: เชื่อมต่อไม่ได้")
                except:
                    st.error(f"❌ Path {i+1}: ไม่สามารถเข้าถึงได้")
    
    with st.sidebar.expander(f"📂 รายละเอียด {selected_line}"):
        with st.sidebar.expander("🐛 Debug Path"):
            if selected_line and selected_line in config:
                for path in config[selected_line]['paths']:
                    if log_type == "Error Log":
                        debug_path = path.replace("/Retry", "/ErrorLog").replace("\\Retry", "\\ErrorLog")  # ✅ แก้ตรงนี้ด้วย
                    else:
                        debug_path = path
                    debug_path = normalize_path(debug_path)
                    exists = os.path.exists(debug_path)
                    st.write(f"{'✅' if exists else '❌'} {debug_path}")
        if selected_line and selected_line in config:
            line_info = config[selected_line]
            st.write(f"**จำนวน Path:** {len(line_info['paths'])}")
            for i, path in enumerate(line_info['paths']):
                st.write(f"- Path {i+1}: {path}")
            st.write(f"**ปีข้อมูล:** {line_info.get('year', 2026)}")
            st.write(f"**รูปแบบไฟล์:** {line_info.get('file_pattern', '*.csv')}")
    
    if st.sidebar.button(f"📥 โหลดข้อมูล {selected_line}", type="primary", use_container_width=True):
        if selected_line and selected_line in config:
            with st.spinner(f"กำลังโหลดข้อมูลจาก {selected_line}..."):
                df, files = load_data_from_line(
                    selected_line,
                    config,
                    log_type
                )
                
                if df is not None and len(df) > 0:
                    processed_df, error_col, lot_col, _ = process_dataframe(df)
                    
                    if processed_df is not None and len(processed_df) > 0:
                        st.session_state['df'] = processed_df
                        st.session_state['selected_line'] = selected_line
                        st.session_state['loaded_files'] = files
                        st.session_state['data_mode'] = 'network'
                        st.session_state['error_col'] = error_col
                        st.session_state['lot_col'] = lot_col
                        st.session_state['data_loaded'] = True
                        st.success(f"✅ โหลดสำเร็จ! {len(files)} ไฟล์, {len(processed_df):,} แถว")
                        st.rerun()
                    else:
                        st.error(f"❌ ไม่สามารถประมวลผลข้อมูลจาก {selected_line}")
                else:
                    st.error(f"❌ ไม่พบข้อมูลใน {selected_line}")

else:
    uploaded_files = st.sidebar.file_uploader(f"📁 อัปโหลดไฟล์ {log_type} CSV", type=["csv"], accept_multiple_files=True)
    
    if st.sidebar.button("📥 โหลดข้อมูลจากไฟล์ที่อัปโหลด", type="primary", use_container_width=True):
        if uploaded_files:
            all_dfs = []
            for file in uploaded_files:
                try:
                    df_temp = pd.read_csv(file, header=1, encoding='utf-8')
                    df_temp['source_file'] = file.name
                    all_dfs.append(df_temp)
                except UnicodeDecodeError:
                    try:
                        df_temp = pd.read_csv(file, header=1, encoding='latin1')
                        df_temp['source_file'] = file.name
                        all_dfs.append(df_temp)
                    except Exception as e2:
                        st.warning(f"อ่านไฟล์ {file.name} ไม่สำเร็จ: {str(e2)}")
                except Exception as e:
                    st.warning(f"อ่านไฟล์ {file.name} ไม่สำเร็จ: {str(e)}")
            
            if all_dfs:
                df = pd.concat(all_dfs, ignore_index=True)
                processed_df, error_col, lot_col, _ = process_dataframe(df)
                
                if processed_df is not None and len(processed_df) > 0:
                    st.session_state['df'] = processed_df
                    st.session_state['uploaded_files'] = uploaded_files
                    st.session_state['data_mode'] = 'upload'
                    st.session_state['error_col'] = error_col
                    st.session_state['lot_col'] = lot_col
                    st.session_state['data_loaded'] = True
                    st.success(f"✅ โหลดสำเร็จ! {len(uploaded_files)} ไฟล์, {len(processed_df):,} แถว")
                    st.rerun()
                else:
                    st.error("❌ ไม่สามารถประมวลผลข้อมูลได้")
        else:
            st.warning("⚠️ กรุณาเลือกไฟล์ก่อน")

# ==================== CHECK DATA BEFORE DISPLAY ====================
# ตรวจสอบว่าโหลดข้อมูลแล้วหรือยัง
if not st.session_state.get('data_loaded', False):
    st.info("👈 กรุณาโหลดข้อมูลจากเมนูด้านซ้ายก่อน")
    st.stop()

# ตรวจสอบ df ว่าไม่ใช่ None
if st.session_state['df'] is None:
    st.error("❌ ไม่มีข้อมูล กรุณาโหลดข้อมูลใหม่")
    st.stop()

# ตรวจสอบว่า df เป็น DataFrame จริงๆ
if not isinstance(st.session_state['df'], pd.DataFrame):
    st.error("❌ ข้อมูลไม่ถูกต้อง กรุณาโหลดข้อมูลใหม่")
    st.stop()

# ตรวจสอบว่า df ไม่ว่าง
if len(st.session_state['df']) == 0:
    st.error("❌ ไม่มีข้อมูล (DataFrame ว่าง) กรุณาโหลดข้อมูลใหม่")
    st.stop()

# ดึงข้อมูลจาก session state
df = st.session_state['df']
error_col = st.session_state.get('error_col')
lot_col = st.session_state.get('lot_col')

# ตรวจสอบคอลัมน์อีกครั้ง (เพิ่มการตรวจสอบ df)
if df is not None:
    if error_col is None or lot_col is None:
        result = process_dataframe(df)
        if result[0] is None:
            st.error("❌ ไม่สามารถตรวจจับคอลัมน์ที่จำเป็นได้")
            st.stop()
        df, error_col, lot_col, _ = result
        st.session_state['df'] = df
        st.session_state['error_col'] = error_col
        st.session_state['lot_col'] = lot_col

# ตรวจสอบอีกครั้งว่า df มีข้อมูล (สำคัญมาก!)
if df is None:
    st.error("❌ DataFrame เป็น None กรุณาโหลดข้อมูลใหม่")
    st.stop()

if len(df) == 0:
    st.error("❌ DataFrame ไม่มีข้อมูล")
    st.stop()

# แสดงหัวข้อตามโหมด
if st.session_state.get('data_mode') == 'network':
    selected_line = st.session_state.get('selected_line', 'Unknown')
    st.title(f"🏭 SMT {log_type} Dashboard - {selected_line}")
    loaded_files = st.session_state.get('loaded_files', [])
    loaded_files_count = len(loaded_files) if loaded_files else 0
    st.caption(f"📅 ข้อมูลล่าสุด | 📁 {loaded_files_count} ไฟล์")
else:
    st.title(f"🏭 SMT {log_type} Dashboard - ข้อมูลที่อัปโหลด")
    uploaded_files = st.session_state.get('uploaded_files', [])
    uploaded_files_count = len(uploaded_files) if uploaded_files else 0
    st.caption(f"📁 {uploaded_files_count} ไฟล์ | {len(df):,} แถว")

# ==================== DISPLAY DATA PREVIEW ====================
st.subheader("📊 ตัวอย่างข้อมูล")
st.dataframe(df.head(10), use_container_width=True)

# ==================== FILTERS ====================
st.sidebar.markdown("---")
st.sidebar.header("🔍 ตัวกรองเพิ่มเติม")

error_options = ["ทั้งหมด"] + sorted(df[error_col].dropna().unique().tolist())
selected_error = st.sidebar.selectbox("เลือก Error Name", error_options)

lot_options = ["ทั้งหมด"] + sorted(df[lot_col].dropna().unique().tolist())
selected_lot = st.sidebar.selectbox("เลือก Lot Name", lot_options)

if 'Occurrence Time' in df.columns and len(df) > 0:
    min_date = df['Occurrence Time'].min().date()
    max_date = df['Occurrence Time'].max().date()
    date_range = st.sidebar.date_input("ช่วงวันที่", [min_date, max_date])
else:
    date_range = []
    st.sidebar.warning("ไม่พบข้อมูลวันที่")

filtered_df = df.copy()

if selected_error != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df[error_col] == selected_error]

if selected_lot != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df[lot_col] == selected_lot]

if len(date_range) == 2 and 'Occurrence Time' in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df['Occurrence Time'].dt.date >= date_range[0]) &
        (filtered_df['Occurrence Time'].dt.date <= date_range[1])
    ]

# 👇 เพิ่มตรงนี้
if len(filtered_df) > 0:
    min_date = filtered_df['Occurrence Time'].min()
    max_date = filtered_df['Occurrence Time'].max()

    st.info(
        f"📅 ช่วงข้อมูลที่แสดง: "
        f"{min_date.strftime('%d/%m/%Y %H:%M')} "
        f"ถึง "
        f"{max_date.strftime('%d/%m/%Y %H:%M')}"
    )

# ==================== PDF REPORT BUTTON ====================
st.markdown("---")
col_pdf1, col_pdf2, col_pdf3 = st.columns(3)

with col_pdf1:
    if st.button("📑 สร้างรายงาน PDF", use_container_width=True, type="primary"):
        with st.spinner("กำลังสร้างรายงาน PDF..."):
            try:
                if st.session_state.get('data_mode') == 'network':
                    line_name = st.session_state.get('selected_line')
                    files_list = st.session_state.get('loaded_files', [])
                else:
                    line_name = None
                    files_list = st.session_state.get('uploaded_files', [])
                
                pdf_buffer = generate_pdf_report(df, filtered_df, error_col, lot_col, files_list, line_name)
                
                st.download_button(
                    label="📥 ดาวน์โหลด PDF",
                    data=pdf_buffer,
                    file_name=f"SMT_Error_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="pdf_download"
                )
                st.success("✅ สร้าง PDF สำเร็จ!")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")

with col_pdf2:
    st.info(f"""
    **📊 สรุปข้อมูลปัจจุบัน:**
    - Error: {len(filtered_df):,} ครั้ง
    - Lot: {filtered_df[lot_col].nunique():,} Lots
    - Error Type: {filtered_df[error_col].nunique():,} ประเภท
    """)

with col_pdf3:
    if len(filtered_df) > 0:
        top_error = filtered_df[error_col].value_counts().index[0]
        top_error_count = filtered_df[error_col].value_counts().iloc[0]
        top_error_pct = (top_error_count / len(filtered_df)) * 100
        st.warning(f"""
        **⚠️ Error สูงสุด:**
        {str(top_error)[:30]}
        {top_error_count:,} ครั้ง ({top_error_pct:.1f}%)
        """)

st.markdown("---")

# ==================== KPIs ====================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📊 Error ทั้งหมด", f"{len(filtered_df):,}")

with col2:
    st.metric("🏷️ จำนวน Lot", f"{filtered_df[lot_col].nunique():,}")

with col3:
    st.metric("🔧 Error Type", f"{filtered_df[error_col].nunique():,}")

with col4:
    if 'Occurrence Time' in filtered_df.columns and len(filtered_df) > 0:
        days_count = (filtered_df['Occurrence Time'].max() - filtered_df['Occurrence Time'].min()).days + 1
        st.metric("📅 ระยะเวลา", f"{days_count} วัน")
    else:
        st.metric("📅 ระยะเวลา", "N/A")

with col5:
    if st.session_state.get('data_mode') == 'network':
        file_count = len(st.session_state.get('loaded_files', []))
    else:
        file_count = len(st.session_state.get('uploaded_files', []))
    st.metric("📁 จำนวนไฟล์", file_count)

st.markdown("---")

# ==================== CHARTS ====================
if len(filtered_df) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top 10 Error ที่พบบ่อย")
        error_counts = filtered_df[error_col].value_counts().head(10)
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        error_counts.plot(kind='bar', color='skyblue', ax=ax1)
        ax1.set_xlabel("Error Name", fontsize=12)
        ax1.set_ylabel("จำนวนครั้ง", fontsize=12)
        ax1.set_title("Top 10 Error ที่พบบ่อย", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        for i, v in enumerate(error_counts.values):
            ax1.text(i, v + 0.5, f"{v:,}", ha='center', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig1)
    
    with col2:
        st.subheader("📦 Top 10 Lot ที่เกิด Error มากสุด")
        lot_counts = filtered_df[lot_col].value_counts().head(10)
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        lot_counts.plot(kind='bar', color='lightcoral', ax=ax2)
        ax2.set_xlabel("Lot Name", fontsize=12)
        ax2.set_ylabel("จำนวน Error", fontsize=12)
        ax2.set_title("Top 10 Lot ที่เกิด Error มากสุด", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        for i, v in enumerate(lot_counts.values):
            ax2.text(i, v + 0.5, f"{v:,}", ha='center', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig2)
    
    if 'Occurrence Time' in filtered_df.columns:
        st.subheader("📅 แนวโน้ม Error รายวัน")
        filtered_df['Date'] = filtered_df['Occurrence Time'].dt.date
        daily_errors = filtered_df.groupby('Date').size()
        
        fig3, ax3 = plt.subplots(figsize=(14, 5))
        daily_errors.plot(kind='line', marker='o', color='green', linewidth=2, markersize=6, ax=ax3)
        ax3.set_xlabel("วันที่", fontsize=12)
        ax3.set_ylabel("จำนวน Error", fontsize=12)
        ax3.set_title("แนวโน้ม Error รายวัน", fontsize=14, fontweight='bold')
        ax3.fill_between(daily_errors.index, daily_errors.values, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig3)
        
        st.subheader("⏰ แนวโน้ม Error รายชั่วโมง")
        filtered_df['Hour'] = filtered_df['Occurrence Time'].dt.hour
        hourly_count = filtered_df.groupby('Hour').size()
        hourly_full = pd.DataFrame({'Hour': range(24)})
        hourly_full = hourly_full.merge(hourly_count.reset_index(name='Count'), on='Hour', how='left').fillna(0)
        
        fig5, ax5 = plt.subplots(figsize=(12, 5))
        ax5.plot(hourly_full['Hour'], hourly_full['Count'], marker='o', color='orange', linewidth=2, markersize=8)
        ax5.set_xlabel("ชั่วโมง (24 ชั่วโมง)", fontsize=12)
        ax5.set_ylabel("จำนวน Error", fontsize=12)
        ax5.set_title("แนวโน้ม Error รายชั่วโมง", fontsize=14, fontweight='bold')
        ax5.set_xticks(range(0, 24, 2))
        ax5.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig5)
        
        if len(filtered_df) >= 10:
            st.subheader("🔥 Heatmap: Error vs Lot")
            top_10_errors = filtered_df[error_col].value_counts().head(10).index.tolist()
            top_10_lots = filtered_df[lot_col].value_counts().head(10).index.tolist()
            
            heatmap_data = []
            for err in top_10_errors:
                row = [len(filtered_df[(filtered_df[error_col] == err) & (filtered_df[lot_col] == lot)]) for lot in top_10_lots]
                heatmap_data.append(row)
            
            fig6, ax6 = plt.subplots(figsize=(20, 12))
            im = ax6.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
            ax6.set_xticks(range(len(top_10_lots)))
            ax6.set_yticks(range(len(top_10_errors)))
            ax6.set_xticklabels([str(lot)[:20] for lot in top_10_lots], rotation=45, ha='right')
            ax6.set_yticklabels([str(err)[:30] for err in top_10_errors])
            
            for i in range(len(top_10_errors)):
                for j in range(len(top_10_lots)):
                    ax6.text(j, i, str(heatmap_data[i][j]), ha="center", va="center", color="black", fontweight='bold')
            
            ax6.set_xlabel("Lot Name", fontsize=12)
            ax6.set_ylabel("Error Name", fontsize=12)
            ax6.set_title("Heatmap ความสัมพันธ์ระหว่าง Error และ Lot", fontsize=14, fontweight='bold')
            plt.colorbar(im, ax=ax6, label='จำนวนครั้ง')
            plt.tight_layout()
            st.pyplot(fig6)

# ==================== DATA TABLE ====================
st.subheader("📋 รายละเอียด Error")
display_cols = ['Occurrence Time', lot_col, error_col]
display_cols = [col for col in display_cols if col in filtered_df.columns]

extra_cols = [col for col in filtered_df.columns if col not in display_cols and col not in ['Date', 'Hour']]
display_cols.extend(extra_cols[:3])

st.dataframe(filtered_df[display_cols].head(1000), use_container_width=True, height=400)

# ==================== DOWNLOAD BUTTONS ====================
st.markdown("---")
col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    csv_all = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลทั้งหมด",
        data=csv_all,
        file_name=f"all_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col_dl2:
    csv_filtered = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลที่กรองแล้ว",
        data=csv_filtered,
        file_name=f"filtered_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption(f"🔄 อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.sidebar.markdown("---")
st.sidebar.info("""
**📌 ข้อมูลระบบ:**
- รองรับไฟล์ CSV จาก SMT Machine
- แสดง Dashboard และรายงาน PDF
- สามารถกรองข้อมูลตาม Error, Lot และช่วงวันที่
""")

















