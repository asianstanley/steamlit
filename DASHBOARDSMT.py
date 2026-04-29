import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from datetime import datetime
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import matplotlib
matplotlib.use('Agg')
import os
import json
import re
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="SMT Error Dashboard", layout="wide")

# ==================== INITIALIZE SESSION STATE ====================
for key, default in {
    'df': None,
    'selected_line': None,
    'loaded_files': [],
    'data_mode': None,
    'uploaded_files': [],
    'error_col': None,
    'lot_col': None,
    'data_loaded': False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ==================== CONFIGURATION ====================
LINE_CONFIG = {
    "Line 1": {
        "paths": [
            "//172.16.0.113/History_Log/Line1/YSM20-Y48740/Retry/",
            "//172.16.0.113/History_Log/Line1/YSM20-Y48998/Retry/"
        ],
        "file_pattern": "*RetryLog*.csv",
        "year": 2026
    },
    "Line 2": {
        "paths": ["//172.16.0.113/History_Log/Line2/YSM20_Y43897/Retry"],
        "file_pattern": "*.csv",
        "year": 2026
    },
    "Line 3": {
        "paths": ["//172.16.0.113/History_Log/Line3/YSM20R-Y56682/Retry"],
        "file_pattern": "*Retry*.csv",
        "year": 2026
    },
    "Line 4": {
        "paths": ["//172.16.0.114/History_log/Line4/YSM10_Y64131/Retry"],
        "file_pattern": "*Retry*.csv",
        "year": 2026
    },
    "Line 5": {
        "paths": ["//172.16.0.113/History_Log/Line5/YSM10_Y67426"],
        "file_pattern": "*Retry*.csv",
        "year": 2026
    },
    "Line 6": {
        "paths": [
            "//172.16.0.114/History_log/Line6/YSM20R_Y56073/Retry",
            "//172.16.0.114/History_log/Line6/YSM20R_Y66007/Retry",
            "//172.16.0.114/History_log/Line6/YSM20_Y37008/Retry"
        ],
        "file_pattern": "*RetryLog*.csv",
        "year": 2026
    },
    "Line 7": {
        "paths": ["//172.16.0.114/History_log/Line7/YSM10_Y64130/Retry"],
        "file_pattern": "*Retry*.csv",
        "year": 2026
    },
    "Line 8": {
        "paths": [
            "//172.16.0.195/YAMAHA_history/Line8_YRM/YRM20_1 (Y72929)/Retry",
            "//172.16.0.195/YAMAHA_history/Line8_YRM/YRM20_2 (Y72930)/Retry",
            "//172.16.0.195/YAMAHA_history/Line8_YRM/YRM20_3 (Y72927)/Retry"
        ],
        "file_pattern": "*RetryLog*.csv",
        "year": 2026
    },
    "Line 9": {
        "paths": [
            "//172.16.0.195/YAMAHA_history/Line9_YRM/YRM20_1 (Y72931)/Retry",
            "//172.16.0.195/YAMAHA_history/Line9_YRM/YRM20_2 (Y72932)/Retry",
            "//172.16.0.195/YAMAHA_history/Line9_YRM/YRM20_3 (Y72928)/Retry"
        ],
        "file_pattern": "*RetryLog*.csv",
        "year": 2026
    },
    "Line 10": {
        "paths": ["//172.16.0.114/History_log/Line7/YSM10_Y64130/Retry"],
        "file_pattern": "*Retry*.csv",
        "year": 2026
    },
    "Line 11": {
        "paths": ["//172.16.0.114/History_log/Line7/YSM10_Y64130/Retry"],
        "file_pattern": "*Retry*.csv",
        "year": 2026
    },
    "Line 12": {
        "paths": ["//172.16.0.111/History_log/Line12/YSM20R_Y56072/Retry"],
        "file_pattern": "*Retry*.csv",
        "year": 2026
    },
    "Line 13": {
        "paths": ["//172.16.0.111/History_log/Line13/YSM10_Y66005/Retry"],
        "file_pattern": "*Retry*.csv",
        "year": 2026
    },
    
"Line 14": {
    "paths": [
        "//172.16.0.112/History_log/Line14/YS24_Y27080/Retry",
        "//172.16.0.112/History_log/Line14/YS24_Y32890/Retry",
        "//172.16.0.112/History_log/Line14/YSM20_Y37011/Retry"
    ],
    "file_pattern": "*RetryLog*.csv",
    "year": 2026
},

"Line 15": {
    "paths": [
        "//172.16.0.112/History_log/Line15/YS24_Y31607/Retry",
        "//172.16.0.112/History_log/Line15/YS24_Y32889/Retry"
    ],
    "file_pattern": "*RetryLog*.csv",
    "year": 2026
},

"Line 16": {
    "paths": [
        "//172.16.0.111/History_log/Line16/YSM20_Y37007/Retry",
        "//172.16.0.111/History_log/Line16/YSM20_Y37010/Retry",
        "//172.16.0.111/History_log/Line16/YS88_Y27081/Retry"
    ],
    "file_pattern": "*RetryLog*.csv",
    "year": 2026
},

"Line 17": {
    "paths": [
        "//172.16.0.111/History_log/Line17/YSM20R_Y46695/Retry",
        "//172.16.0.111/History_log/Line17/YSM20_Y37004/Retry",
        "//172.16.0.111/History_log/Line17/YSM20_Y37005/Retry"
    ],
    "file_pattern": "*RetryLog*.csv",
    "year": 2026
},

"Line 18": {
    "paths": [
        "//172.16.0.113/History_Log/Line18/YSM10_Y67425/Retry",
        "//172.16.0.113/History_Log/Line18/YS88_Y33574/Retry"
    ],
    "file_pattern": "*RetryLog*.csv",
    "year": 2026
},

"Line 19": {
    "paths": [
        "//172.16.0.112/History_log/Line19/YS24_Y33570/Retry",
        "//172.16.0.112/History_log/Line19/YS24_Y33572/Retry",
        "//172.16.0.112/History_log/Line19/YS88_Y33573/Retry"
    ],
    "file_pattern": "*RetryLog*.csv",
    "year": 2026
},

"Line 20": {
    "paths": [
        "//172.16.0.112/History_log/Line19/YS24_Y33570/Retry",
        "//172.16.0.112/History_log/Line20/YS24_Y33571/Retry"
    ],
    "file_pattern": "*RetryLog*.csv",
    "year": 2026
},

"Line 21": {
    "paths": [
        "//172.16.0.112/History_log/Line21/YSM20R_Y58571/Retry",
        "//172.16.0.112/History_log/Line21/YSM20_Y37013/Retry"
    ],
    "file_pattern": "*RetryLog*.csv",
    "year": 2026
},

"Line 22": {
    "paths": ["//172.16.0.112/History_log/Line22/YSM20R_Y60462/Retry"],
    "file_pattern": "*Retry*.csv",
    "year": 2026
},

"Line 23": {
    "paths": [
        "//172.16.0.113/History_Log/Line23/YSM20R_Y62750/Retry",
        "//172.16.0.113/History_Log/Line23/YSM20R_Y62751/Retry",
        "//172.16.0.113/History_Log/Line23/YSM20R_Y62752/Retry"
    ],
    "file_pattern": "*RetryLog*.csv",
    "year": 2026
},

"Line 24": {
    "paths": ["//172.16.0.111/History_log/Line24/YSM20R_Y66006/Retry"],
    "file_pattern": "*Retry*.csv",
    "year": 2026
},
     
}

CONFIG_FILE = "line_config.json"


def normalize_path(path):
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
    text = str(text)
    for pattern in [r'(202[0-9])', r'ปี(202[0-9])', r'_(202[0-9])_', r'-(202[0-9])-']:
        years = re.findall(pattern, text)
        if years:
            return int(years[0])
    return None


def get_files_from_line(line_name, config):
    line_data = config[line_name]
    all_files = []
    for path in line_data['paths']:
        path = normalize_path(path)
        for file in glob(os.path.join(path, line_data.get('file_pattern', '*.csv'))):
            if extract_year_from_string(file) == line_data.get('year', 2026):
                all_files.append(file)
    return all_files


def read_single_file(args):
    """อ่านไฟล์เดี่ยว — ใช้กับ parallel"""
    file, line_name = args
    for enc in ['utf-8', 'latin1']:
        try:
            df = pd.read_csv(file, header=1, encoding=enc)
            df['source_file'] = os.path.basename(file)
            df['source_path'] = file
            df['line'] = line_name
            return df
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    return None


# ✅ cache_data: โหลดครั้งแรกเท่านั้น — ครั้งต่อไปใช้ผลเดิมทันที
@st.cache_data(show_spinner=False)
def load_data_from_line_cached(line_name, config_str):
    config = json.loads(config_str)
    files = get_files_from_line(line_name, config)
    if not files:
        return None, []
    # อ่านแบบ Parallel — ไฟล์ทุกตัวอ่านพร้อมกัน
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(read_single_file, [(f, line_name) for f in files]))
    all_dfs = [r for r in results if r is not None]
    return (pd.concat(all_dfs, ignore_index=True), files) if all_dfs else (None, [])


def detect_columns(df):
    cols = df.columns.tolist()
    time_col = next(
        (c for c in cols if any(k in str(c).lower() for k in ['time', 'date', 'วันที่', 'เวลา', 'timestamp'])),
        cols[0] if cols else None
    )
    error_col = next(
        (c for c in cols if 'error' in str(c).lower() and 'name' in str(c).lower()),
        next((c for c in cols if 'error' in str(c).lower()), cols[1] if len(cols) > 1 else None)
    )
    lot_col = next(
        (c for c in cols if 'lot' in str(c).lower()),
        cols[2] if len(cols) > 2 else None
    )
    return time_col, error_col, lot_col


# ✅ cache_data: process ครั้งแรกเท่านั้น
@st.cache_data(show_spinner=False)
def process_dataframe_cached(df):
    if df is None or len(df) == 0:
        return None, None, None, None
    time_col, error_col, lot_col = detect_columns(df)
    if time_col is None:
        return None, None, None, None
    try:
        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        df = df.dropna(subset=[time_col])
        df.rename(columns={time_col: 'Occurrence Time'}, inplace=True)
    except Exception:
        return None, None, None, None
    if len(df) == 0:
        return None, None, None, None
    return df, error_col, lot_col, time_col


def generate_pdf_report(df, filtered_df, error_col, lot_col, files_list, line_name=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    title_style  = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16,
                                  spaceAfter=30, textColor=colors.HexColor('#1f77b4'))
    heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=14,
                                   spaceAfter=12, textColor=colors.HexColor('#2c3e50'))
    normal_style  = ParagraphStyle('N', parent=styles['Normal'], fontSize=10, spaceAfter=6)

    story = []
    story.append(Paragraph(f"SMT Mounter Error Summary Report - {line_name or 'All Lines'}", title_style))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("1. Overview Summary", heading_style))

    if 'Occurrence Time' in filtered_df.columns and len(filtered_df) > 0:
        min_d = filtered_df['Occurrence Time'].min()
        max_d = filtered_df['Occurrence Time'].max()
        date_range_text = f"{min_d.strftime('%d/%m/%Y')} - {max_d.strftime('%d/%m/%Y')}"
        days_diff = (max_d - min_d).days + 1
    else:
        date_range_text = "No date data available"
        days_diff = 0

    summary_data = [
        ['Item', 'Value'],
        ['Number of Files Used', str(len(files_list))],
        ['Total Errors', f"{len(filtered_df):,}"],
        ['Number of Lots Found', f"{filtered_df[lot_col].nunique():,}"],
        ['Number of Error Types', f"{filtered_df[error_col].nunique():,}"],
        ['Date Range', date_range_text],
        ['Duration', f"{days_diff} Days"],
    ]
    t = Table(summary_data, colWidths=[120, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    for section_title, col, header_color, data_col in [
        ("2. Top 10 Most Frequent Errors", error_col,
         '#1f77b4', ['Rank', 'Error Name', 'Count', 'Percentage']),
        ("3. Top 10 Lots with Most Errors", lot_col,
         '#d62728', ['Rank', 'Lot Name', 'Error Count', 'Percentage']),
    ]:
        story.append(Paragraph(section_title, heading_style))
        counts = filtered_df[col].value_counts().head(10)
        rows = [data_col]
        for i, (name, cnt) in enumerate(counts.items(), 1):
            rows.append([str(i), str(name)[:50], f"{cnt:,}", f"{(cnt/len(filtered_df)*100):.1f}%"])
        tbl = Table(rows, colWidths=[40, 250, 60, 60])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 20))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ==================== SIDEBAR ====================
st.sidebar.header("🏭 เลือกไลน์การผลิต")
mode = st.sidebar.radio("เลือกโหมด", ["🌐 ดึงจาก Network ตามไลน์", "📁 อัปโหลดไฟล์เอง"])

if mode == "🌐 ดึงจาก Network ตามไลน์":
    config = load_line_config()
    selected_line = st.sidebar.selectbox("เลือกไลน์การผลิต", list(config.keys()))

    with st.sidebar.expander("🔌 สถานะการเชื่อมต่อ Network"):
        for i, path in enumerate(config[selected_line]['paths']):
            pn = normalize_path(path)
            if os.path.exists(pn):
                st.success(f"✅ Path {i+1}: เชื่อมต่อได้")
            else:
                st.error(f"❌ Path {i+1}: เชื่อมต่อไม่ได้")

    with st.sidebar.expander(f"📂 รายละเอียด {selected_line}"):
        info = config[selected_line]
        st.write(f"**จำนวน Path:** {len(info['paths'])}")
        for i, p in enumerate(info['paths']):
            st.write(f"- Path {i+1}: {p}")
        st.write(f"**ปีข้อมูล:** {info.get('year', 2026)}")
        st.write(f"**รูปแบบไฟล์:** {info.get('file_pattern', '*.csv')}")

    if st.sidebar.button(f"📥 โหลดข้อมูล {selected_line}", type="primary", use_container_width=True):
        with st.spinner(f"กำลังโหลดข้อมูลจาก {selected_line}... (ครั้งแรกอาจช้าหน่อย)"):
            config_str = json.dumps(config)
            raw_df, files = load_data_from_line_cached(selected_line, config_str)
            if raw_df is not None and len(raw_df) > 0:
                proc_df, ec, lc, _ = process_dataframe_cached(raw_df)
                if proc_df is not None and ec is not None and lc is not None:
                    st.session_state.update({
                        'df': proc_df, 'selected_line': selected_line,
                        'loaded_files': files, 'data_mode': 'network',
                        'error_col': ec, 'lot_col': lc, 'data_loaded': True
                    })
                    st.success(f"✅ โหลดสำเร็จ! {len(files)} ไฟล์, {len(proc_df):,} แถว")
                    st.rerun()
                else:
                    st.error("❌ ตรวจจับคอลัมน์ไม่สำเร็จ กรุณาตรวจสอบรูปแบบไฟล์")
            else:
                st.error(f"❌ ไม่พบข้อมูลใน {selected_line}")

    # ปุ่มล้าง cache — กดเมื่อต้องการดึงข้อมูลใหม่จาก network
    if st.sidebar.button("🔄 รีเฟรชข้อมูลใหม่จาก Network", use_container_width=True):
        load_data_from_line_cached.clear()
        process_dataframe_cached.clear()
        st.session_state['data_loaded'] = False
        st.session_state['df'] = None
        st.rerun()

else:
    uploaded_files = st.sidebar.file_uploader(
        "📁 อัปโหลดไฟล์ RetryLog CSV", type=["csv"], accept_multiple_files=True)

    if st.sidebar.button("📥 โหลดข้อมูลจากไฟล์ที่อัปโหลด", type="primary", use_container_width=True):
        if uploaded_files:
            all_dfs = []
            for f in uploaded_files:
                for enc in ['utf-8', 'latin1']:
                    try:
                        tmp = pd.read_csv(f, header=1, encoding=enc)
                        tmp['source_file'] = f.name
                        all_dfs.append(tmp)
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        st.warning(f"อ่านไฟล์ {f.name} ไม่สำเร็จ: {e}")
                        break
            if all_dfs:
                raw_df = pd.concat(all_dfs, ignore_index=True)
                proc_df, ec, lc, _ = process_dataframe_cached(raw_df)
                if proc_df is not None and ec is not None and lc is not None:
                    st.session_state.update({
                        'df': proc_df, 'uploaded_files': uploaded_files,
                        'data_mode': 'upload', 'error_col': ec,
                        'lot_col': lc, 'data_loaded': True
                    })
                    st.success(f"✅ โหลดสำเร็จ! {len(uploaded_files)} ไฟล์, {len(proc_df):,} แถว")
                    st.rerun()
                else:
                    st.error("❌ ตรวจจับคอลัมน์ไม่สำเร็จ กรุณาตรวจสอบรูปแบบไฟล์")
        else:
            st.warning("⚠️ กรุณาเลือกไฟล์ก่อน")

# ==================== GUARD ====================
if not st.session_state['data_loaded'] or st.session_state['df'] is None:
    st.title("🏭 SMT Machine Error Dashboard")
    st.info("👈 กรุณาโหลดข้อมูลจากเมนูด้านซ้ายก่อน")
    st.stop()

df        = st.session_state['df']
error_col = st.session_state['error_col']
lot_col   = st.session_state['lot_col']
data_mode = st.session_state['data_mode']

if error_col is None or lot_col is None:
    df, error_col, lot_col, _ = process_dataframe_cached(df)
    if df is None or error_col is None or lot_col is None:
        st.error("❌ ไม่สามารถตรวจจับคอลัมน์ที่จำเป็น กรุณาโหลดข้อมูลใหม่")
        st.stop()
    st.session_state.update({'df': df, 'error_col': error_col, 'lot_col': lot_col})

# ==================== HEADER ====================
if data_mode == 'network':
    line_label = st.session_state.get('selected_line', 'Unknown')
    file_count = len(st.session_state.get('loaded_files', []))
    st.title(f"🏭 SMT Error Dashboard - {line_label}")
    st.caption(f"📅 ข้อมูลล่าสุด | 📁 {file_count} ไฟล์ | {len(df):,} แถว")
else:
    file_count = len(st.session_state.get('uploaded_files', []))
    st.title("🏭 SMT Error Dashboard - ข้อมูลที่อัปโหลด")
    st.caption(f"📁 {file_count} ไฟล์ | {len(df):,} แถว")

# ==================== DATA PREVIEW ====================
st.subheader("📊 ตัวอย่างข้อมูล")
st.dataframe(df.head(10), use_container_width=True)

# ==================== SIDEBAR FILTERS ====================
st.sidebar.markdown("---")
st.sidebar.header("🔍 ตัวกรองเพิ่มเติม")

error_options = ["ทั้งหมด"] + sorted(df[error_col].dropna().unique().tolist())
selected_error = st.sidebar.selectbox("เลือก Error Name", error_options)

lot_options = ["ทั้งหมด"] + sorted(df[lot_col].dropna().unique().tolist())
selected_lot = st.sidebar.selectbox("เลือก Lot Name", lot_options)

# Filter แยกตาม Machine
if 'source_file' in df.columns:
    machine_options = ["ทั้งหมด"] + sorted(df['source_file'].dropna().unique().tolist())
    selected_machine = st.sidebar.selectbox("🤖 เลือก Machine", machine_options)
else:
    selected_machine = "ทั้งหมด"

if 'Occurrence Time' in df.columns:
    min_date = df['Occurrence Time'].min().date()
    max_date = df['Occurrence Time'].max().date()
    date_range = st.sidebar.date_input("ช่วงวันที่", [min_date, max_date])
else:
    date_range = []
    st.sidebar.warning("ไม่พบข้อมูลวันที่")

# ==================== APPLY FILTERS ====================
filtered_df = df.copy()

if selected_error != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df[error_col] == selected_error]
if selected_lot != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df[lot_col] == selected_lot]
if selected_machine != "ทั้งหมด" and 'source_file' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['source_file'] == selected_machine]
if len(date_range) == 2 and 'Occurrence Time' in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df['Occurrence Time'].dt.date >= date_range[0]) &
        (filtered_df['Occurrence Time'].dt.date <= date_range[1])
    ]

if len(filtered_df) == 0:
    st.warning("⚠️ ไม่มีข้อมูลในช่วงที่กรอง")
    st.stop()

# ==================== PDF REPORT ====================
st.markdown("---")
col_pdf1, col_pdf2, col_pdf3 = st.columns(3)

with col_pdf1:
    if st.button("📑 สร้างรายงาน PDF", use_container_width=True, type="primary"):
        with st.spinner("กำลังสร้างรายงาน PDF..."):
            try:
                files_list = (st.session_state.get('loaded_files', [])
                              if data_mode == 'network'
                              else st.session_state.get('uploaded_files', []))
                line_name = st.session_state.get('selected_line') if data_mode == 'network' else None
                pdf_buf = generate_pdf_report(df, filtered_df, error_col, lot_col, files_list, line_name)
                st.download_button("📥 ดาวน์โหลด PDF", data=pdf_buf,
                                   file_name=f"SMT_Error_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                   mime="application/pdf", key="pdf_download")
                st.success("✅ สร้าง PDF สำเร็จ!")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

with col_pdf2:
    st.info(f"""
**📊 สรุปข้อมูลปัจจุบัน:**
- Error: {len(filtered_df):,} ครั้ง
- Lot: {filtered_df[lot_col].nunique():,} Lots
- Error Type: {filtered_df[error_col].nunique():,} ประเภท
""")

with col_pdf3:
    top_err  = filtered_df[error_col].value_counts()
    top_name = top_err.index[0]
    top_cnt  = top_err.iloc[0]
    st.warning(f"""
**⚠️ Error สูงสุด:**
{str(top_name)[:30]}
{top_cnt:,} ครั้ง ({top_cnt/len(filtered_df)*100:.1f}%)
""")

st.markdown("---")
# ==================== KPIs ====================
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📊 Total Errors", f"{len(filtered_df):,}")
c2.metric("🏷️ Total Lots", f"{filtered_df[lot_col].nunique():,}")
c3.metric("🔧 Error Types", f"{filtered_df[error_col].nunique():,}")
if 'Occurrence Time' in filtered_df.columns:
    days = (filtered_df['Occurrence Time'].max() - filtered_df['Occurrence Time'].min()).days + 1
    c4.metric("📅 Time Span", f"{days} days")
else:
    c4.metric("📅 Time Span", "N/A")
c5.metric("📁 File Count", file_count)

st.markdown("---")

# ==================== CHARTS ====================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Top 10 Most Frequent Errors")
    ec_counts = filtered_df[error_col].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    ec_counts.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_xlabel("Error Name"); ax.set_ylabel("Count")
    ax.set_title("Top 10 Most Frequent Errors", fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(ec_counts.values):
        ax.text(i, v + 0.5, f"{v:,}", ha='center', fontweight='bold')
    plt.tight_layout(); st.pyplot(fig); plt.close(fig)

with col2:
    st.subheader("📦 Top 10 Lots with Most Errors")
    lc_counts = filtered_df[lot_col].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    lc_counts.plot(kind='bar', color='lightcoral', ax=ax)
    ax.set_xlabel("Lot Name"); ax.set_ylabel("Error Count")
    ax.set_title("Top 10 Lots with Most Errors", fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(lc_counts.values):
        ax.text(i, v + 0.5, f"{v:,}", ha='center', fontweight='bold')
    plt.tight_layout(); st.pyplot(fig); plt.close(fig)

if 'Occurrence Time' in filtered_df.columns:
    filtered_df = filtered_df.copy()
    filtered_df['Date'] = filtered_df['Occurrence Time'].dt.date

    st.subheader("📅 Daily Error Trend")
    daily = filtered_df.groupby('Date').size()
    fig, ax = plt.subplots(figsize=(14, 5))
    daily.plot(kind='line', marker='o', color='green', linewidth=2, markersize=6, ax=ax)
    ax.fill_between(daily.index, daily.values, alpha=0.3)
    ax.set_xlabel("Date"); ax.set_ylabel("Error Count")
    ax.set_title("Daily Error Trend", fontweight='bold')
    plt.xticks(rotation=45, ha='right'); plt.grid(True, alpha=0.3)
    plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    ca, cb, cc = st.columns(3)
    ca.metric("📊 Avg Errors per Day", f"{daily.mean():.1f}")
    cb.metric("📈 Max Errors in a Day", f"{daily.max():,}")
    cc.metric("📅 Peak Error Date", str(daily.idxmax()))

    st.subheader("⏰ Hourly Error Trend")
    filtered_df['Hour'] = filtered_df['Occurrence Time'].dt.hour
    hourly = filtered_df.groupby('Hour').size().reindex(range(24), fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(hourly.index, hourly.values, marker='o', color='orange', linewidth=2, markersize=8)
    ax.set_xlabel("Hour"); ax.set_ylabel("Error Count")
    ax.set_title("Hourly Error Trend", fontweight='bold')
    ax.set_xticks(range(0, 24, 2)); plt.grid(True, alpha=0.3)
    plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    st.subheader("📈 Cumulative Errors")
    sorted_df = filtered_df.sort_values('Occurrence Time')
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(sorted_df['Occurrence Time'], range(1, len(sorted_df)+1),
            linewidth=2, color='purple')
    ax.set_xlabel("Time"); ax.set_ylabel("Cumulative Errors")
    ax.set_title("Cumulative Errors Over Time", fontweight='bold')
    plt.grid(True, alpha=0.3); plt.xticks(rotation=45)
    plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    if len(sorted_df) > 1:
        time_diff = (sorted_df['Occurrence Time'].max() - sorted_df['Occurrence Time'].min()).total_seconds() / 3600
        rate = len(sorted_df) / time_diff if time_diff > 0 else 0
        st.metric("⚡ Error Rate (errors/hour)", f"{rate:.2f}")

    if len(filtered_df) >= 5:
        st.subheader("🔥 Heatmap: Error vs Lot")
        top5e = filtered_df[error_col].value_counts().head(5).index.tolist()
        top5l = filtered_df[lot_col].value_counts().head(5).index.tolist()
        hmap = [[len(filtered_df[(filtered_df[error_col]==e) & (filtered_df[lot_col]==l)])
                 for l in top5l] for e in top5e]
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(hmap, cmap='YlOrRd', aspect='auto')
        ax.set_xticks(range(len(top5l))); ax.set_yticks(range(len(top5e)))
        ax.set_xticklabels([str(l)[:20] for l in top5l], rotation=45, ha='right')
        ax.set_yticklabels([str(e)[:30] for e in top5e])
        for i in range(len(top5e)):
            for j in range(len(top5l)):
                ax.text(j, i, str(hmap[i][j]), ha="center", va="center", fontweight='bold')
        ax.set_xlabel("Lot Name"); ax.set_ylabel("Error Name")
        ax.set_title("Heatmap: Error vs Lot Relationship", fontweight='bold')
        plt.colorbar(im, ax=ax, label='Count')
        plt.tight_layout(); st.pyplot(fig); plt.close(fig)

# ==================== DATA TABLE ====================
st.subheader("📋 รายละเอียด Error")
display_cols = [c for c in ['Occurrence Time', lot_col, error_col] if c in filtered_df.columns]
extra = [c for c in filtered_df.columns if c not in display_cols and c not in ['Date', 'Hour']]
display_cols.extend(extra[:3])
st.dataframe(filtered_df[display_cols].head(1000), use_container_width=True, height=400)

# ==================== DOWNLOAD ====================
st.markdown("---")
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button("📥 ดาวน์โหลดข้อมูลทั้งหมด",
                       data=df.to_csv(index=False).encode('utf-8'),
                       file_name=f"all_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                       mime="text/csv")
with col_dl2:
    st.download_button("📥 ดาวน์โหลดข้อมูลที่กรองแล้ว",
                       data=filtered_df.to_csv(index=False).encode('utf-8'),
                       file_name=f"filtered_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                       mime="text/csv")

st.markdown("---")
st.caption(f"🔄 อัปเดตล่าสุด: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.sidebar.markdown("---")
st.sidebar.info("""
**📌 ข้อมูลระบบ:**
- รองรับไฟล์ CSV จาก SMT Machine
- แสดง Dashboard และรายงาน PDF
- กรองตาม Error / Lot / Machine / วันที่
- กด 🔄 รีเฟรช เมื่อต้องการดึงข้อมูลใหม่จาก Network
""")
