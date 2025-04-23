import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
from io import BytesIO

# ====== INITIALIZE SESSION ======
if 'schedule' not in st.session_state:
    st.session_state.schedule = []

st.title("ระบบจัดผังรายการ - NextStep TV")

# ====== FUNCTIONS ======
def parse_time_slot(time_str):
    try:
        start_str, end_str = time_str.split('-')
        start = datetime.strptime(start_str.strip(), '%H:%M')
        end = datetime.strptime(end_str.strip(), '%H:%M')
        return start, end
    except:
        return None, None

def is_locked_time_slot(date_obj, start_time, end_time):
    day = date_obj.strftime('%a').lower()
    locked_slots = {
        'mon': [(time(6,30), time(8,0)), (time(9,30), time(10,30)), (time(10,30), time(12,0)),
                (time(12,0), time(13,30)), (time(13,30), time(14,30)), (time(16,0), time(17,0)),
                (time(17,0), time(18,0)), (time(18,30), time(20,0)), (time(20,0), time(20,15)),
                (time(20,15), time(20,30)), (time(20,30), time(21,30)), (time(0,0), time(5,0))],
        'tue': [(time(6,30), time(8,0)), (time(8,0), time(8,30)), (time(9,30), time(10,30)),
                (time(10,30), time(12,0)), (time(12,0), time(13,30)), (time(13,30), time(14,30)),
                (time(15,0), time(16,0)), (time(17,0), time(18,0)), (time(18,30), time(20,0)),
                (time(20,0), time(20,15)), (time(20,15), time(20,30)), (time(20,30), time(21,30)),
                (time(0,0), time(5,0))],
        'wed': [(time(6,30), time(8,0)), (time(9,30), time(10,30)), (time(12,0), time(13,30)),
                (time(13,30), time(14,30)), (time(15,0), time(16,0)), (time(16,0), time(17,0)),
                (time(17,0), time(18,0)), (time(18,30), time(20,0)), (time(20,0), time(20,15)),
                (time(20,15), time(20,30)), (time(20,30), time(21,30)), (time(0,0), time(5,0))],
        'thu': [(time(6,30), time(8,0)), (time(9,30), time(10,30)), (time(12,0), time(13,30)),
                (time(13,30), time(14,30)), (time(15,0), time(16,0)), (time(17,0), time(18,0)),
                (time(18,30), time(20,0)), (time(20,0), time(20,15)), (time(20,15), time(20,30)),
                (time(20,30), time(21,30)), (time(0,0), time(5,0))],
        'fri': [(time(6,30), time(8,0)), (time(9,30), time(10,30)), (time(12,0), time(13,30)),
                (time(13,30), time(14,30)), (time(15,0), time(16,0)), (time(17,0), time(18,0)),
                (time(18,30), time(20,0)), (time(20,0), time(20,15)), (time(20,15), time(20,30)),
                (time(0,0), time(5,0))],
        'sat': [(time(11,30), time(12,0)), (time(12,0), time(13,0)), (time(17,0), time(18,0)),
                (time(18,30), time(19,30)), (time(19,30), time(20,30)), (time(20,30), time(21,0)),
                (time(0,0), time(5,0))],
        'sun': [(time(11,0), time(11,30)), (time(12,0), time(13,0)), (time(17,0), time(18,0)),
                (time(18,30), time(19,30)), (time(19,30), time(20,30)), (time(20,30), time(21,0)),
                (time(0,0), time(5,0))],
    }
    for locked_start, locked_end in locked_slots.get(day, []):
        if (start_time.time() < locked_end and end_time.time() > locked_start):
            return True
    return False

def is_duplicate_entry(date_obj, program_title):
    check_date = date_obj - timedelta(days=14)
    for entry in st.session_state.schedule:
        try:
            existing_date = datetime.strptime(entry['date'].split()[1] + ' ' + entry['date'].split()[2] + ' 25', '%d %b %y')
            if existing_date >= check_date and entry['program'] == program_title:
                return True
        except:
            continue
    return False

# ====== INPUT FORM ======
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

    program_link = st.text_input("ลิงก์รายการ (ถ้ามี)")

    submitted = st.form_submit_button("➕ เพิ่มรายการ")
    if submitted:
        start_dt, end_dt = parse_time_slot(time_slot)
        if not start_dt or not end_dt:
            st.warning("กรุณากรอกช่วงเวลาให้ถูกต้อง เช่น 08:00-09:00")
        elif is_locked_time_slot(date, start_dt, end_dt):
            st.warning("❌ เวลานี้เป็นช่วงรายการของสถานี กรุณาเลือกช่วงเวลาอื่น")
        elif is_duplicate_entry(date, program_title):
            st.warning("⚠️ รายการนี้เคยฉายภายใน 14 วันที่ผ่านมา กรุณาตรวจสอบ")
        else:
            weekday_th = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์', 'อาทิตย์']
            day_name = weekday_th[date.weekday()]
            date_th = f"{day_name} {date.day} {date.strftime('%b')} {str(date.year+543)[-2:]}"
            st.session_state.schedule.append({
                "date": date_th,
                "time": time_slot,
                "program": program_title,
                "type": program_type,
                "link": program_link
            })

# ====== DISPLAY AND DOWNLOAD ======
if st.session_state.schedule:
    df = pd.DataFrame(st.session_state.schedule)
    df[['start', 'end']] = df['time'].apply(lambda t: pd.Series(parse_time_slot(t)))
    df_sorted = df.sort_values(by=['date', 'start'])
    df_sorted['link'] = df_sorted['link'].apply(lambda url: f'=HYPERLINK("{url}", "เปิดลิงก์")' if pd.notna(url) and url != '' else '')
    to_export = df_sorted.drop(columns=['start', 'end'])
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        to_export.to_excel(writer, index=False, sheet_name="NextStep_Schedule")
    buffer.seek(0)
    st.download_button(
    label="ดาวน์โหลดตาราง Excel",        data=buffer,
        file_name="schedule_nextstep.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ====== DELETE ROWS ======
st.subheader("🗑️ ลบรายการ")
delete_index = st.selectbox(
    "เลือกรายการที่ต้องการลบ:",
    df_sorted.index,
    format_func=lambda i: f"{df_sorted.loc[i, 'date']} {df_sorted.loc[i, 'time']} - {df_sorted.loc[i, 'program']}"
)

if st.button("ลบรายการที่เลือก"):
    st.session_state.schedule.pop(delete_index)
    st.rerun()
