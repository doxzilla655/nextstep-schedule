import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# โหลด session_state สำหรับจัดเก็บข้อมูล
if 'schedule' not in st.session_state:
    st.session_state.schedule = []

st.title("📺 ระบบจัดผังรายการ - NextStep TV")

# ======= INPUT FORM =======
with st.form("input_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("เลือกวันที่")
    with col2:
        time_slot = st.text_input("ช่วงเวลา (เช่น 08:00-09:00)")
    with col3:
        program_title = st.text_input("ชื่อรายการ")

    program_type = st.selectbox(
        "ประเภทรายการ",
        ["สำรวจโลก", "animal show", "mysci", "new explorer", "doxzilla", "อื่น ๆ"]
    )

    submitted = st.form_submit_button("➕ เพิ่มรายการ")
    if submitted:
        weekday_th = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์', 'อาทิตย์']
        day_name = weekday_th[date.weekday()]
        date_th = f"{day_name} {date.day} {date.strftime('%b')} {str(date.year+543)[-2:]}"
        st.session_state.schedule.append({
            "date": date_th,
            "time": time_slot,
            "program": program_title,
            "type": program_type
        })

# ======= FUNCTION =======
def parse_time_slot(time_str):
    try:
        start_str, end_str = time_str.split('-')
        start = datetime.strptime(start_str.strip(), '%H:%M')
        end = datetime.strptime(end_str.strip(), '%H:%M')
        return start, end
    except:
        return None, None

def check_overlap(df_day):
    df_day = df_day.sort_values(by='start')
    overlaps = []
    for i in range(1, len(df_day)):
        if df_day.iloc[i]['start'] < df_day.iloc[i-1]['end']:
            overlaps.append((df_day.iloc[i-1]['program'], df_day.iloc[i]['program']))
    return overlaps

def highlight_row(row):
    color = {
        'สำรวจโลก': '#d1e7dd',
        'animal show': '#cfe2ff',
        'mysci': '#fce5cd',
        'new explorer': '#fde2e2',
        'doxzilla': '#e2e2e2',
        'อื่น ๆ': '#f8f9fa'
    }.get(row['type'], '#ffffff')
    return [f'background-color: {color}'] * len(row)

# ======= DISPLAY TABLE =======
if st.session_state.schedule:
    df = pd.DataFrame(st.session_state.schedule)
    df[['start', 'end']] = df['time'].apply(lambda t: pd.Series(parse_time_slot(t)))

    df_sorted = df.sort_values(by=['date', 'start'])
    st.subheader("📋 ตารางผังรายการ (เรียงตามวันและเวลา)")
    st.dataframe(df_sorted.style.apply(highlight_row, axis=1), use_container_width=True)

    # ======= CHECK OVERLAP =======
    st.subheader("🚨 ตรวจสอบเวลาซ้อนกัน")
    warnings = []
    for date, group in df_sorted.groupby('date'):
        overlaps = check_overlap(group)
        for a, b in overlaps:
            warnings.append(f"📅 {date}: '{a}' ซ้อนกับ '{b}'")
    if warnings:
        for warn in warnings:
            st.error(warn)
    else:
        st.success("✅ ไม่พบรายการซ้อนเวลา")

    # ======= DOWNLOAD BUTTON =======
    to_export = df_sorted.drop(columns=['start', 'end'])
    
buffer = BytesIO()
import io

buffer = io.BytesIO()

df = pd.DataFrame(st.session_state.schedule)  # 👈 ดึงตารางรายการจาก session

to_export = df  # 👈 กำหนด DataFrame ที่จะ export

if not to_export.empty:
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        to_export.to_excel(writer, index=False, sheet_name="NextStep_Schedule")

    buffer.seek(0)

    st.download_button(
        label="📥 ดาวน์โหลดตาราง Excel",
        data=buffer,
        file_name="schedule_nextstep.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("กรุณาเพิ่มรายการเพื่อเริ่มต้นจัดผัง")
