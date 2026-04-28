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
matplotlib.use('Agg')
import tempfile
import os

st.set_page_config(page_title="SMT Error Dashboard", layout="wide")

st.title("🏭 SMT Machine Error Dashboard")
st.markdown("---")

def generate_pdf_report(df, filtered_df, error_col, lot_col, uploaded_files, stats_data):
    """สร้างรายงาน PDF ขนาด A4"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # สร้างสไตล์เพิ่มเติม
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30, textColor=colors.HexColor('#1f77b4'))
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#2c3e50'))
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    
    story = []
    
    # หัวข้อรายงาน
    story.append(Paragraph("รายงานสรุป Error SMT Mounter", title_style))
    story.append(Paragraph(f"วันที่สร้างรายงาน: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 12))
    
    # ข้อมูลสรุป
    story.append(Paragraph("1. ข้อมูลสรุปภาพรวม", heading_style))
    
    summary_data = [
        ['รายการ', 'ค่า'],
        ['จำนวนไฟล์ที่อัปโหลด', str(len(uploaded_files))],
        ['จำนวน Error ทั้งหมด', str(len(filtered_df))],
        ['จำนวน Lot ที่พบ', str(filtered_df[lot_col].nunique())],
        ['จำนวน Error Type', str(filtered_df[error_col].nunique())],
        ['ช่วงวันที่', f"{filtered_df['Occurrence Time'].min().strftime('%d/%m/%Y')} - {filtered_df['Occurrence Time'].max().strftime('%d/%m/%Y')}"],
        ['ระยะเวลา', f"{(filtered_df['Occurrence Time'].max() - filtered_df['Occurrence Time'].min()).days + 1} วัน"],
    ]
    
    summary_table = Table(summary_data, colWidths=[120, 300])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#d3d3d3')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Top Error
    story.append(Paragraph("2. Error ที่พบบ่อยที่สุด 10 อันดับแรก", heading_style))
    error_counts = filtered_df[error_col].value_counts().head(10)
    error_table_data = [['ลำดับ', 'Error Name', 'จำนวนครั้ง', 'เปอร์เซ็นต์']]
    for i, (err_name, count) in enumerate(error_counts.items(), 1):
        percentage = (count / len(filtered_df)) * 100
        error_table_data.append([str(i), err_name[:50], str(count), f'{percentage:.1f}%'])
    
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
    
    # Top Lot
    story.append(Paragraph("3. Lot ที่เกิด Error มากที่สุด 10 อันดับแรก", heading_style))
    lot_counts = filtered_df[lot_col].value_counts().head(10)
    lot_table_data = [['ลำดับ', 'Lot Name', 'จำนวน Error', 'เปอร์เซ็นต์']]
    for i, (lot_name, count) in enumerate(lot_counts.items(), 1):
        percentage = (count / len(filtered_df)) * 100
        lot_table_data.append([str(i), lot_name[:50], str(count), f'{percentage:.1f}%'])
    
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
    story.append(Spacer(1, 20))
    
    # สร้างกราฟและแทรกใน PDF (ถ้าสามารถสร้างได้)
    try:
        # สร้างกราฟ Top Error
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        error_counts.plot(kind='bar', color='skyblue', ax=ax1)
        ax1.set_xlabel("Error Name")
        ax1.set_ylabel("จำนวนครั้ง")
        ax1.set_title("Top 10 Error ที่พบบ่อย")
        plt.xticks(rotation=45, ha='right')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            plt.savefig(tmpfile.name, format='png', dpi=150, bbox_inches='tight')
            tmpfile_path = tmpfile.name
        
        story.append(Paragraph("4. กราฟแสดง Error ที่พบบ่อย", heading_style))
        story.append(Image(tmpfile_path, width=400, height=200))
        story.append(Spacer(1, 12))
        os.unlink(tmpfile_path)
        plt.close()
    except:
        pass
    
    # แนวโน้มรายวัน
    try:
        filtered_df['Date'] = filtered_df['Occurrence Time'].dt.date
        daily_errors = filtered_df.groupby('Date').size()
        
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        daily_errors.plot(kind='line', marker='o', color='green', linewidth=2, ax=ax2)
        ax2.set_xlabel("วันที่")
        ax2.set_ylabel("จำนวน Error")
        ax2.set_title("แนวโน้ม Error รายวัน")
        plt.xticks(rotation=45, ha='right')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            plt.savefig(tmpfile.name, format='png', dpi=150, bbox_inches='tight')
            tmpfile_path = tmpfile.name
        
        story.append(Paragraph("5. แนวโน้ม Error รายวัน", heading_style))
        story.append(Image(tmpfile_path, width=400, height=200))
        story.append(Spacer(1, 12))
        os.unlink(tmpfile_path)
        plt.close()
    except:
        pass
    
    # แนวโน้มรายชั่วโมง
    try:
        filtered_df['Hour'] = filtered_df['Occurrence Time'].dt.hour
        hourly_count = filtered_df.groupby('Hour').size()
        
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.plot(range(24), [hourly_count.get(h, 0) for h in range(24)], marker='o', color='orange', linewidth=2)
        ax3.set_xlabel("ชั่วโมง")
        ax3.set_ylabel("จำนวน Error")
        ax3.set_title("แนวโน้ม Error รายชั่วโมง")
        ax3.grid(True, alpha=0.3)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            plt.savefig(tmpfile.name, format='png', dpi=150, bbox_inches='tight')
            tmpfile_path = tmpfile.name
        
        story.append(Paragraph("6. แนวโน้ม Error รายชั่วโมง", heading_style))
        story.append(Image(tmpfile_path, width=400, height=200))
        story.append(Spacer(1, 12))
        os.unlink(tmpfile_path)
        plt.close()
    except:
        pass
    
    # ข้อเสนอแนะ
    story.append(PageBreak())
    story.append(Paragraph("7. ข้อเสนอแนะและแนวทางแก้ไข", heading_style))
    
    # วิเคราะห์และให้ข้อเสนอแนะอัตโนมัติ
    recommendations = []
    
    # ข้อเสนอแนะจาก Top Error
    top_error_name = error_counts.index[0] if len(error_counts) > 0 else ""
    top_error_pct = (error_counts.iloc[0] / len(filtered_df)) * 100 if len(error_counts) > 0 else 0
    
    recommendations.append(f"• Error ที่พบมากที่สุดคือ '{top_error_name}' คิดเป็น {top_error_pct:.1f}% ของ Error ทั้งหมด ควรตรวจสอบสาเหตุและแก้ไขเป็นลำดับแรก")
    
    if top_error_pct > 30:
        recommendations.append("• มี Error เพียงประเภทเดียวที่เกิดขึ้นมากกว่า 30% ควรวิเคราะห์สาเหตุหลักอย่างละเอียด")
    
    # ข้อเสนอแนะจากแนวโน้มชั่วโมง
    peak_hour = hourly_count.idxmax() if len(hourly_count) > 0 else 0
    peak_count = hourly_count.max() if len(hourly_count) > 0 else 0
    if peak_count > 0:
        recommendations.append(f"• ช่วงเวลาที่เกิด Error มากที่สุดคือเวลา {peak_hour}:00 น. ควรตรวจสอบการทำงานในช่วงเวลาดังกล่าว")
    
    # ข้อเสนอแนะจาก Lot
    top_lot = lot_counts.index[0] if len(lot_counts) > 0 else ""
    if top_lot:
        recommendations.append(f"• Lot '{top_lot}' มีปัญหาเกิด Error บ่อยที่สุด ควรตรวจสอบคุณภาพวัตถุดิบหรือกระบวนการผลิตของ Lot นี้")
    
    # ข้อเสนอแนะเพิ่มเติม
    if len(filtered_df) > 1000:
        recommendations.append("• จำนวน Error รวมสูงมาก ควรพิจารณาหยุดสายการผลิตเพื่อตรวจสอบและแก้ไขปัญหาเร่งด่วน")
    
    for rec in recommendations:
        story.append(Paragraph(rec, normal_style))
        story.append(Spacer(1, 6))
    
    # สร้าง PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# ===== ส่วนหลักของ Dashboard (เหมือนเดิม) =====

# อัปโหลดหลายไฟล์
uploaded_files = st.file_uploader(
    "📁 อัปโหลดไฟล์ RetryLog CSV (เลือกได้หลายไฟล์)", 
    type=["csv"],
    accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) > 0:
    
    # รวมข้อมูลจากทุกไฟล์
    all_dfs = []
    
    with st.spinner("กำลังอ่านและรวมข้อมูลจากทุกไฟล์..."):
        for file in uploaded_files:
            try:
                df = pd.read_csv(file, header=1)
                df['source_file'] = file.name
                all_dfs.append(df)
            except Exception as e:
                st.warning(f"อ่านไฟล์ {file.name} ไม่สำเร็จ: {str(e)}")
    
    if len(all_dfs) == 0:
        st.error("ไม่สามารถอ่านไฟล์ใดได้เลย กรุณาตรวจสอบรูปแบบไฟล์")
        st.stop()
    
    df = pd.concat(all_dfs, ignore_index=True)
    
    st.success(f"✅ รวมข้อมูลสำเร็จ! {len(uploaded_files)} ไฟล์, รวม {len(df)} แถว")
    
    with st.expander("📄 รายการไฟล์ที่อัปโหลด"):
        for file in uploaded_files:
            st.write(f"- {file.name}")
    
    with st.expander("🔧 ดูชื่อคอลัมน์ที่มีในไฟล์"):
        st.write(df.columns.tolist())
    
    # หาคอลัมน์ที่จำเป็น
    time_col = None
    for col in df.columns:
        if 'Time' in str(col) or 'เวลา' in str(col):
            time_col = col
            break
    
    if time_col is None:
        st.error("❌ ไม่พบคอลัมน์เวลา")
        st.stop()
    
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col])
    df.rename(columns={time_col: 'Occurrence Time'}, inplace=True)
    
    error_col = None
    for col in df.columns:
        if 'Error' in str(col) and 'Name' in str(col):
            error_col = col
            break
    if error_col is None:
        error_col = df.columns[4] if len(df.columns) > 4 else df.columns[0]
    
    lot_col = None
    for col in df.columns:
        if 'Lot' in str(col):
            lot_col = col
            break
    if lot_col is None:
        lot_col = df.columns[2] if len(df.columns) > 2 else df.columns[0]
    
    # SIDEBAR ตัวกรอง
    st.sidebar.header("🔍 ตัวกรอง")
    
    error_options = ["ทั้งหมด"] + sorted(df[error_col].dropna().unique().tolist())
    selected_error = st.sidebar.selectbox("เลือก Error Name", error_options)
    
    lot_options = ["ทั้งหมด"] + sorted(df[lot_col].dropna().unique().tolist())
    selected_lot = st.sidebar.selectbox("เลือก Lot Name", lot_options)
    
    min_date = df['Occurrence Time'].min().date()
    max_date = df['Occurrence Time'].max().date()
    date_range = st.sidebar.date_input("ช่วงวันที่", [min_date, max_date])
    
    # FILTER
    filtered_df = df.copy()
    
    if selected_error != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df[error_col] == selected_error]
    
    if selected_lot != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df[lot_col] == selected_lot]
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Occurrence Time'].dt.date >= date_range[0]) &
            (filtered_df['Occurrence Time'].dt.date <= date_range[1])
        ]
    
    if len(filtered_df) == 0:
        st.warning("⚠️ ไม่มีข้อมูลในช่วงที่กรอง กรุณาเปลี่ยนเงื่อนไข")
        st.stop()
    
    # ===== เพิ่มปุ่มดาวน์โหลดรายงาน PDF ขนาด A4 =====
    st.markdown("---")
    st.subheader("📄 สรุปรายงาน")
    
    col_pdf1, col_pdf2, col_pdf3 = st.columns(3)
    
    with col_pdf1:
        if st.button("📑 สร้างรายงาน PDF (A4)", use_container_width=True, type="primary"):
            with st.spinner("กำลังสร้างรายงาน PDF กรุณารอสักครู่..."):
                try:
                    stats_data = {
                        'total_errors': len(filtered_df),
                        'total_lots': filtered_df[lot_col].nunique(),
                        'total_error_types': filtered_df[error_col].nunique(),
                    }
                    pdf_buffer = generate_pdf_report(df, filtered_df, error_col, lot_col, uploaded_files, stats_data)
                    
                    st.download_button(
                        label="📥 ดาวน์โหลดรายงาน PDF",
                        data=pdf_buffer,
                        file_name=f"SMT_Error_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        key="pdf_download"
                    )
                    st.success("✅ รายงาน PDF สร้างสำเร็จ! คลิกปุ่มด้านบนเพื่อดาวน์โหลด")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการสร้าง PDF: {str(e)}")
                    st.info("⚠️ อาจต้องติดตั้งไลบรารี reportlab: pip install reportlab")
    
    # แสดงข้อมูลสรุปแบบย่อใน Dashboard
    with col_pdf2:
        st.info(f"""
        **สรุปข้อมูลปัจจุบัน:**
        - จำนวน Error: {len(filtered_df):,} ครั้ง
        - จำนวน Lot: {filtered_df[lot_col].nunique()} Lots
        - Error Type: {filtered_df[error_col].nunique()} ประเภท
        """)
    
    with col_pdf3:
        if len(filtered_df) > 0:
            top_error = filtered_df[error_col].value_counts().index[0]
            top_error_count = filtered_df[error_col].value_counts().iloc[0]
            top_error_pct = (top_error_count / len(filtered_df)) * 100
            st.warning(f"""
            **⚠️ Error ที่พบมากสุด:**
            {top_error}
            จำนวน: {top_error_count} ครั้ง ({top_error_pct:.1f}%)
            """)
    
    st.markdown("---")
    
    # ===== ส่วนที่เหลือของ Dashboard (KPI, กราฟต่างๆ เหมือนเดิม) =====
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📊 จำนวน Error ทั้งหมด", len(filtered_df))
    with col2:
        st.metric("🏷️ จำนวน Lot", filtered_df[lot_col].nunique())
    with col3:
        st.metric("🔧 จำนวน Error Type", filtered_df[error_col].nunique())
    with col4:
        days_count = (filtered_df['Occurrence Time'].max() - filtered_df['Occurrence Time'].min()).days + 1
        st.metric("📅 ระยะเวลา", f"{days_count} วัน")
    with col5:
        st.metric("📁 จำนวนไฟล์", len(uploaded_files))
    
    st.markdown("---")
    
    # แถวที่ 1: Top Error + Top Lot
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top 10 Error ที่พบบ่อย")
        error_counts = filtered_df[error_col].value_counts().head(10)
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        error_counts.plot(kind='bar', color='skyblue', ax=ax1)
        ax1.set_xlabel("Error Name")
        ax1.set_ylabel("จำนวนครั้ง")
        plt.xticks(rotation=45, ha='right')
        
        for i, v in enumerate(error_counts.values):
            ax1.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        
        st.pyplot(fig1)
    
    with col2:
        st.subheader("📦 Top 10 Lot ที่เกิด Error มากสุด")
        lot_counts = filtered_df[lot_col].value_counts().head(10)
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        lot_counts.plot(kind='bar', color='lightcoral', ax=ax2)
        ax2.set_xlabel("Lot Name")
        ax2.set_ylabel("จำนวน Error")
        plt.xticks(rotation=45, ha='right')
        
        for i, v in enumerate(lot_counts.values):
            ax2.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        
        st.pyplot(fig2)
    
    # แถวที่ 2: Error รายวัน + Pie Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 จำนวน Error แยกตามวัน")
        filtered_df['Date'] = filtered_df['Occurrence Time'].dt.date
        daily_errors = filtered_df.groupby('Date').size()
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        daily_errors.plot(kind='bar', color='lightgreen', ax=ax3)
        ax3.set_xlabel("วันที่")
        ax3.set_ylabel("จำนวน Error")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig3)
    
    with col2:
        st.subheader("📊 สัดส่วน Error (เปอร์เซ็นต์)")
        error_pct = filtered_df[error_col].value_counts(normalize=True) * 100
        error_pct_df = error_pct.head(10).reset_index()
        error_pct_df.columns = [error_col, 'Percentage (%)']
        
        st.dataframe(error_pct_df, use_container_width=True)
        
        fig_pct, ax_pct = plt.subplots(figsize=(10, 6))
        bars = ax_pct.barh(error_pct_df[error_col], error_pct_df['Percentage (%)'], color='skyblue')
        ax_pct.set_xlabel("Percentage (%)")
        ax_pct.set_title("Top Error by Percentage")
        
        for bar, pct in zip(bars, error_pct_df['Percentage (%)']):
            ax_pct.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                        f'{pct:.1f}%', va='center')
        
        st.pyplot(fig_pct)
    
    # แนวโน้มรายชั่วโมง
    st.subheader("⏰ แนวโน้ม Error ตามช่วงเวลา (รายชั่วโมง)")
    
    filtered_df['Hour'] = filtered_df['Occurrence Time'].dt.hour
    hourly_data = pd.DataFrame({'Hour': list(range(24))})
    hourly_count = filtered_df.groupby('Hour').size().reset_index(name='Error_Count')
    hourly_result = pd.merge(hourly_data, hourly_count, on='Hour', how='left')
    hourly_result['Error_Count'] = hourly_result['Error_Count'].fillna(0)
    
    fig5, ax5 = plt.subplots(figsize=(12, 5))
    ax5.plot(hourly_result['Hour'], hourly_result['Error_Count'], marker='o', color='green', linewidth=2, markersize=8)
    ax5.set_xlabel("ชั่วโมง (24 ชั่วโมง)")
    ax5.set_ylabel("จำนวน Error")
    ax5.set_xticks(range(0, 24, 2))
    ax5.grid(True, alpha=0.3)
    st.pyplot(fig5)
    
    # Heatmap
    st.subheader("🔥 Heatmap: Error vs Lot (Top 5 x Top 5)")
    
    top_5_errors_list = filtered_df[error_col].value_counts().head(5).index.tolist()
    top_5_lots_list = filtered_df[lot_col].value_counts().head(5).index.tolist()
    
    heatmap_data = []
    for err in top_5_errors_list:
        row = []
        for lot in top_5_lots_list:
            count = len(filtered_df[(filtered_df[error_col] == err) & (filtered_df[lot_col] == lot)])
            row.append(count)
        heatmap_data.append(row)
    
    fig6, ax6 = plt.subplots(figsize=(10, 6))
    im = ax6.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
    
    ax6.set_xticks(range(len(top_5_lots_list)))
    ax6.set_yticks(range(len(top_5_errors_list)))
    ax6.set_xticklabels(top_5_lots_list, rotation=45, ha='right')
    ax6.set_yticklabels(top_5_errors_list)
    
    for i in range(len(top_5_errors_list)):
        for j in range(len(top_5_lots_list)):
            text = ax6.text(j, i, heatmap_data[i][j], ha="center", va="center", color="black", fontweight='bold')
    
    ax6.set_xlabel("Lot Name")
    ax6.set_ylabel("Error Name")
    plt.colorbar(im, ax=ax6, label='จำนวนครั้ง')
    st.pyplot(fig6)
    
    # ตารางข้อมูล
    st.subheader("📋 รายละเอียด Error (ทั้งหมด)")
    
    default_cols = ['Occurrence Time', lot_col, error_col]
    available_cols = [col for col in default_cols if col in filtered_df.columns]
    other_cols = [col for col in ['Lane', 'Table', 'Parts No.', 'Head No.', 'Feeder No.', 'source_file'] if col in filtered_df.columns]
    
    display_cols = available_cols + other_cols
    st.dataframe(filtered_df[display_cols], use_container_width=True, height=400)
    
    # ดาวน์โหลด CSV
    st.markdown("---")
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        csv_all = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลทั้งหมด (ทุกไฟล์)",
            data=csv_all,
            file_name="all_errors_combined.csv",
            mime="text/csv"
        )
    
    with col_dl2:
        csv_filtered = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลที่กรองแล้ว",
            data=csv_filtered,
            file_name="filtered_errors.csv",
            mime="text/csv"
        )
    
    # แนวโน้มและวิเคราะห์หลายไฟล์
    st.subheader("📈 แนวโน้มและวิเคราะห์หลายไฟล์")
    st.markdown("---")
    
    if len(uploaded_files) > 1:
        # แนวโน้ม Error รวมตามวัน
        st.subheader("📅 แนวโน้ม Error รายวัน (รวมทุกไฟล์)")
        
        df_daily = filtered_df.copy()
        df_daily['Date'] = df_daily['Occurrence Time'].dt.date
        daily_trend = df_daily.groupby('Date').size().reset_index(name='Error Count')
        
        fig_trend1, ax_trend1 = plt.subplots(figsize=(14, 5))
        ax_trend1.plot(daily_trend['Date'], daily_trend['Error Count'], marker='o', linewidth=2, markersize=8, color='blue')
        ax_trend1.fill_between(daily_trend['Date'], daily_trend['Error Count'], alpha=0.3, color='blue')
        ax_trend1.set_xlabel("วันที่")
        ax_trend1.set_ylabel("จำนวน Error")
        ax_trend1.set_title("แนวโน้ม Error รายวัน", fontsize=14, fontweight='bold')
        ax_trend1.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig_trend1)
        
        avg_errors = daily_trend['Error Count'].mean()
        max_errors = daily_trend['Error Count'].max()
        max_date = daily_trend.loc[daily_trend['Error Count'].idxmax(), 'Date']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 ค่าเฉลี่ย Error ต่อวัน", f"{avg_errors:.1f}")
        with col2:
            st.metric("📈 Error สูงสุดในวันเดียว", max_errors)
        with col3:
            st.metric("📅 วันที่ Error สูงสุด", max_date)
        
        st.markdown("---")
        
        # แนวโน้ม Error Type
        st.subheader("📊 แนวโน้มของ Error แต่ละประเภท (ยอดนิยม Top 5)")
        
        top5_errors = filtered_df[error_col].value_counts().head(5).index.tolist()
        error_trend = filtered_df[filtered_df[error_col].isin(top5_errors)].copy()
        error_trend['Date'] = error_trend['Occurrence Time'].dt.date
        error_pivot = error_trend.groupby(['Date', error_col]).size().unstack(fill_value=0)
        
        fig_trend3, ax_trend3 = plt.subplots(figsize=(14, 6))
        error_pivot.plot(kind='line', marker='o', linewidth=2, ax=ax_trend3)
        ax_trend3.set_xlabel("วันที่")
        ax_trend3.set_ylabel("จำนวน Error")
        ax_trend3.set_title("แนวโน้ม Error แต่ละประเภท", fontsize=14, fontweight='bold')
        ax_trend3.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax_trend3.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig_trend3)
        
        st.markdown("---")
        
        # ยอด Error สะสม
        st.subheader("📈 ยอด Error สะสม (Cumulative Error Trend)")
        
        filtered_df_sorted = filtered_df.sort_values('Occurrence Time')
        filtered_df_sorted['Cumulative Error'] = range(1, len(filtered_df_sorted) + 1)
        
        fig_trend5, ax_trend5 = plt.subplots(figsize=(14, 5))
        ax_trend5.plot(filtered_df_sorted['Occurrence Time'], 
                       filtered_df_sorted['Cumulative Error'], 
                       linewidth=2, color='purple')
        ax_trend5.set_xlabel("เวลา")
        ax_trend5.set_ylabel("จำนวน Error สะสม")
        ax_trend5.set_title("ยอด Error สะสมตามเวลา", fontsize=14, fontweight='bold')
        ax_trend5.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig_trend5)
        
        if len(filtered_df_sorted) > 1:
            time_diff = (filtered_df_sorted['Occurrence Time'].max() - filtered_df_sorted['Occurrence Time'].min()).total_seconds() / 3600
            error_rate = len(filtered_df_sorted) / time_diff if time_diff > 0 else 0
            st.metric("⚡ อัตราการเกิด Error (errors/hour)", f"{error_rate:.2f}")
    
    else:
        st.info("📌 อัปโหลดหลายไฟล์เพื่อดูแนวโน้มและการเปรียบเทียบ")

else:
    st.info("👈 กรุณาอัปโหลดไฟล์ RetryLog CSV อย่างน้อย 1 ไฟล์")
    st.markdown("""
    ### ✨ HELLO BRO!!!!!!!!!!!##""")
    
    