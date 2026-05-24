import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & THEME SETUP
# ==========================================
st.set_page_config(
    page_title="TCP Inbound Delivery Management",
    page_icon="🥤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS เพื่อควบคุมสีปุ่มและ Title ให้เป็นเอกลักษณ์ของ TCP Group
st.markdown("""
    <style>
    :root {
        --tcp-blue: #0A2540;
        --tcp-red: #E30613;
    }
    .main-title {
        color: #0A2540;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 20px;
        border-bottom: 3px solid #E30613;
        padding-bottom: 10px;
    }
    .stButton>button {
        background-color: #0A2540;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #E30613;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOCK DATABASE INITIALIZATION (SHAREPOINT SIMULATION)
# ==========================================
if 'users_db' not in st.session_state:
    st.session_state.users_db = pd.DataFrame([
        {"email": "admin@tcp.com", "password": "admin", "role": "Admin", "name": "System Admin"},
        {"email": "supplier_a@email.com", "password": "123", "role": "Supplier", "name": "Thai Packaging Co., Ltd."},
        {"email": "supplier_b@email.com", "password": "123", "role": "Supplier", "name": "Agro Material Source"},
        {"email": "staff_bkk@tcp.com", "password": "123", "role": "Staff", "name": "พนักงานคลังสินค้า - บางบอน"},
        {"email": "staff_pro@tcp.com", "password": "123", "role": "Staff", "name": "พนักงานคลังสินค้า - ปราจีนบุรี"}
    ])

if 'delivery_db' not in st.session_state:
    st.session_state.delivery_db = pd.DataFrame([
        {
            "id": "TXT001",
            "type": "บรรจุภัณฑ์",
            "supplier_name": "Thai Packaging Co., Ltd.",
            "supplier_email": "supplier_a@email.com",
            "car_plate": "กข 1234 กทม",
            "delivery_date": "2026-05-25",
            "time_slot": "09:00 - 10:00",
            "location": "คลังสินค้า บางบอน",
            "invoice_file": "invoice_001.pdf",
            "other_file": "cert_001.pdf",
            "status": "Plan"
        }
    ])

if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def check_slot_availability(date_str, slot_str, location_str):
    df = pd.DataFrame(st.session_state.delivery_db)
    if df.empty:
        return True
    count = df[(df['delivery_date'] == str(date_str)) & 
               (df['time_slot'] == slot_str) & 
               (df['location'] == location_str)].shape[0]
    return count < 2

def send_mock_email(to_email, subject, body):
    st.toast(f"✉️ [Email Sent] ถึง: {to_email} | เรื่อง: {subject}", icon="📧")

# ==========================================
# 4. SIDEBAR - LOGIN SYSTEM
# ==========================================
with st.sidebar:
    st.image("https://www.tcp.com/images/logo.png", width=150)
    st.title("TCP Inbound")
    st.subheader("Delivery Management")
    st.write("---")
    
    if st.session_state.logged_in_user is None:
        st.subheader("🔑 กรุณาเข้าสู่ระบบ")
        login_email = st.text_input("อีเมล (E-mail)")
        login_password = st.text_input("รหัสผ่าน (Password)", type="password")
        
        if st.button("เข้าสู่ระบบ", use_container_width=True):
            users = st.session_state.users_db
            user_match = users[(users['email'] == login_email) & (users['password'] == login_password)]
            
            if not user_match.empty:
                st.session_state.logged_in_user = user_match.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("อีเมลหรือรหัสผ่านไม่ถูกต้อง")
    else:
        st.write(f"👋 สวัสดี, **{st.session_state.logged_in_user['name']}**")
        st.info(f"สิทธิ์ผู้ใช้งาน: **{st.session_state.logged_in_user['role']}**")
        if st.button("ออกจากระบบ", use_container_width=True):
            st.session_state.logged_in_user = None
            st.rerun()

# ==========================================
# 5. MAIN CONTENT AREA
# ==========================================
st.markdown('<div class="main-title">TCP Inbound Delivery Management</div>', unsafe_allow_html=True)

if st.session_state.logged_in_user is None:
    st.warning("🔒 กรุณาเข้าสู่ระบบที่แถบด้านซ้ายเพื่อเริ่มต้นใช้งานระบบ")
    
    st.subheader("📊 Real-time Delivery Dashboard")
    df_dashboard = pd.DataFrame(st.session_state.delivery_db)
    if not df_dashboard.empty:
        st.dataframe(
            df_dashboard[['id', 'type', 'supplier_name', 'car_plate', 'delivery_date', 'time_slot', 'location', 'status']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("ไม่มีข้อมูลการจัดส่งในขณะนี้")

else:
    role = st.session_state.logged_in_user['role']
    tabs = ["📊 สรุปสถานะ (Dashboard)"]
    if role == "Supplier": tabs.append("📝 กรอกแผนการจัดส่ง (Supplier)")
    if role == "Staff": tabs.append("📦 จัดการการรับสินค้า (Staff)")
    if role == "Admin": tabs.append("⚙️ ลงทะเบียนผู้ใช้ (Admin)")
    
    active_tab = st.radio("เลือกเมนูการใช้งาน:", tabs, horizontal=True)
    st.write("---")
    
    # --- DASHBOARD TAB ---
    if active_tab == "📊 สรุปสถานะ (Dashboard)":
        st.subheader("📋 สถานะการจัดส่งเรียลไทม์")
        df_all = pd.DataFrame(st.session_state.delivery_db)
        if not df_all.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("แผนการจัดส่ง (Plan)", df_all[df_all['status']=='Plan'].shape[0])
            c2.metric("ยืนยันแล้ว (Confirm)", df_all[df_all['status']=='Confirm'].shape[0])
            c3.metric("รถมาถึงแล้ว (Arrived)", df_all[df_all['status']=='Arrived'].shape[0])
            c4.metric("ลงของเสร็จสิ้น (Finished)", df_all[df_all['status']=='Finished'].shape[0])
        
        st.write("#### รายการจัดส่งทั้งหมด")
        st.dataframe(df_all, use_container_width=True, hide_index=True)

    # --- SUPPLIER TAB ---
    elif active_tab == "📝 กรอกแผนการจัดส่ง (Supplier)":
        st.subheader("📥 จองเวลาและกรอกข้อมูลแผนการจัดส่ง")
        with st.form("supplier_delivery_form"):
            col1, col2 = st.columns(2)
            with col1:
                delivery_type = st.selectbox("1. เลือกชนิดการจัดส่ง", ["วัตถุดิบ", "บรรจุภัณฑ์"])
                st.text_input("2. ชื่อ Supplier", value=st.session_state.logged_in_user['name'], disabled=True)
                car_plate = st.text_input("3. กรอกทะเบียนรถ", placeholder="ตัวอย่าง: กข 1234 กรุงเทพฯ")
                location = st.selectbox("5. เลือกสถานที่ส่ง", ["คลังสินค้า บางบอน", "โรงงาน ปราจีนบุรี"])
            with col2:
                delivery_date = st.date_input("4. เลือกวันจัดส่ง", min_value=datetime.today())
                time_slots = [f"{hour:02d}:00 - {hour+1:02d}:00" for hour in range(8, 17)]
                time_slot = st.selectbox("4.1 เลือก Slot เวลาจัดส่งรายชม.", time_slots)
                invoice_file = st.file_uploader("6. คลิกแนบเอกสาร Invoice", type=["pdf", "jpg", "png"])
                other_file = st.file_uploader("7. คลิกแนบเอกสารอื่นๆ", type=["pdf", "jpg", "png"])
                
            submit_btn = st.form_submit_button("8. กด Submit แผนการจัดส่ง")
            
            if submit_btn:
                if not car_plate or not invoice_file:
                    st.error("❌ กรุณากรอกทะเบียนรถและแนบเอกสาร Invoice ให้ครบถ้วน")
                else:
                    if check_slot_availability(delivery_date, time_slot, location):
                        new_id = f"TXT{len(st.session_state.delivery_db) + 1:03d}"
                        new_data = {
                            "id": new_id, "type": delivery_type, 
                            "supplier_name": st.session_state.logged_in_user['name'],
                            "supplier_email": st.session_state.logged_in_user['email'],
                            "car_plate": car_plate, "delivery_date": str(delivery_date),
                            "time_slot": time_slot, "location": location,
                            "invoice_file": invoice_file.name, 
                            "other_file": other_file.name if other_file else "None",
                            "status": "Plan"
                        }
                        st.session_state.delivery_db = pd.concat([st.session_state.delivery_db, pd.DataFrame([new_data])], ignore_index=True)
                        st.success(f"✔️ ส่งแผนสำเร็จ! รหัสรายการ: {new_id}")
                        send_mock_email("warehouse_staff@tcp.com", f"New Delivery Plan: {new_id}", "มีแผนการจัดส่งใหม่")
                        st.rerun()
                    else:
                        st.error("❌ ขออภัย! ช่วงเวลานี้ในสถานที่ดังกล่าวมีรถจองเต็ม 2 คันแล้ว")

    # --- STAFF TAB ---
    elif active_tab == "📦 จัดการการรับสินค้า (Staff)":
        st.subheader("🏭 รายการจัดการสำหรับพนักงาน")
        df_staff = pd.DataFrame(st.session_state.delivery_db)
        if df_staff.empty:
            st.info("ไม่มีรายการสินค้าในขณะนี้")
        else:
            for index, row in df_staff.iterrows():
                with st.container():
                    st.markdown(f"#### 🚚 ออเดอร์ {row['id']} - {row['supplier_name']} ({row['type']})")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.write(f"**ทะเบียนรถ:** {row['car_plate']}")
                    c2.write(f"**วัน/เวลา:** {row['delivery_date']} | {row['time_slot']}")
                    c3.write(f"**สถานที่:** {row['location']}")
                    c4.write(f"**สถานะ:** `{row['status']}`")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    if row['status'] == "Plan":
                        if col_btn1.button("✅ Confirm เวลา", key=f"conf_{row['id']}"):
                            st.session_state.delivery_db.at[index, 'status'] = "Confirm"
                            send_mock_email(row['supplier_email'], "Delivery Confirmed", "ยืนยันแผนการจัดส่งเรียบร้อย")
                            st.rerun()
                        new_slot = col_btn2.selectbox("เปลี่ยน Slot เวลา", [f"{h:02d}:00 - {h+1:02d}:00" for h in range(8, 17)], key=f"s_{row['id']}")
                        if col_btn2.button("⚠️ เลื่อนเวลาจัดส่ง", key=f"delay_{row['id']}"):
                            st.session_state.delivery_db.at[index, 'time_slot'] = new_slot
                            send_mock_email(row['supplier_email'], "Delivery Rescheduled", f"เลื่อนเวลาจัดส่งเป็น {new_slot}")
                            st.rerun()
                    elif row['status'] == "Confirm":
                        if col_btn1.button("🚛 รถมาถึงแล้ว (Arrived)", key=f"arr_{row['id']}"):
                            st.session_state.delivery_db.at[index, 'status'] = "Arrived"
                            st.rerun()
                    elif row['status'] == "Arrived":
                        if col_btn1.button("🏁 ลงของเสร็จสิ้น (Finished)", key=f"fin_{row['id']}"):
                            st.session_state.delivery_db.at[index, 'status'] = "Finished"
                            st.rerun()
                    st.write("---")

    # --- ADMIN TAB ---
    elif active_tab == "⚙️ ลงทะเบียนผู้ใช้ (Admin)":
        st.subheader("🧑‍💼 ระบบลงทะเบียนผู้ใช้งานระบบ")
        with st.form("admin_register_form"):
            new_user_email = st.text_input("ระบุ E-mail (สำหรับใช้ Login)")
            new_user_name = st.text_input("ชื่อ-นามสกุล หรือ ชื่อบริษัทคู่ค้า")
            new_user_pass = st.text_input("กำหนดรหัสผ่านเบื้องต้น", type="password")
            new_user_role = st.selectbox("เลือกประเภทผู้ใช้งาน (Role)", ["Supplier", "Staff", "Admin"])
            if st.form_submit_button("บันทึกและสร้างบัญชีผู้ใช้"):
                if not new_user_email or not new_user_name or not new_user_pass:
                    st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
                else:
                    new_user = {"email": new_user_email, "password": new_user_pass, "role": new_user_role, "name": new_user_name}
                    st.session_state.users_db = pd.concat([st.session_state.users_db, pd.DataFrame([new_user])], ignore_index=True)
                    st.success("✔️ ลงทะเบียนผู้ใช้เรียบร้อยแล้ว!")
        st.dataframe(st.session_state.users_db[['name', 'email', 'role']], use_container_width=True, hide_index=True)
