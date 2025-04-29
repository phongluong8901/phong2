import streamlit as st
import pandas as pd
import datetime
import io
import random
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
# Ẩn menu và footer
from utils.default_style import default_style
default_style()
#check authen

import streamlit as st
import requests
import random

def auth_check(page_id: str) -> str:
    """
    Hàm dùng chung để xác thực người dùng trước khi render page.
    
    1) Đọc query param: siteid, orgid, token
    2) Giải mã token bằng RSA PRIVATE KEY
    3) POST /VerifyStreamlit với headers: Authorization = <token tu parameter>
       và body: {"orgid": <orgid>, "pageid": page_id}
    4) Nếu message != "" => hiển thị lỗi và st.stop()
       Nếu = "" => cho phép chạy tiếp
    """
    # 1) Lấy query params
    query_params = st.query_params
    siteid = int(query_params["siteid"])
    orgid = query_params["orgid"]
    token = query_params["token"]

    # Kiểm tra tối thiểu
    if not token:
        st.error("Data không hợp lệ.")
        st.stop()
    if not orgid:
        st.error("Org không hợp lệ.")
        st.stop()

   

    # 2) Tìm URL theo siteid
    if siteid == 0:
        arr_base_url = [
           "https://dms.mobiwork.vn:3016",
           "https://dms.mobiwork.vn:3018",
           "https://dms.mobiwork.vn:3012",
           "https://dms.mobiwork.vn:3020",
           "https://api.mobiwork.vn:3016",
           "https://api.mobiwork.vn:3018",
           "https://api.mobiwork.vn:3012",
           "https://api.mobiwork.vn:3020"
        ]
    elif siteid == 1:
        arr_base_url = [
           "https://dev.mobiwork.vn:3016",
           "https://dev.mobiwork.vn:4034"
        ]
    elif siteid == 2:
        arr_base_url = [
           "http://dms.hungcuongcompany.com:3051",
           "http://dms.hungcuongcompany.com:3052",
           "http://dmshc2.mobiwork.vn:5053",
           "http://dmshc2.mobiwork.vn:5054",
           "http://dmshc2.mobiwork.vn:5055",
           "http://dmshc2.mobiwork.vn:5056",
           "http://dmshc2.mobiwork.vn:5057",
           "http://dmshc2.mobiwork.vn:5058"
        ]
    else:
        st.error("Siteid không hợp lệ.")
        st.stop()
    base_url = random.choice(arr_base_url)
    verify_url = f"{base_url}/VerifyStreamlit"

    # Gửi request
    headers = {
        "Authorization": "Basic " + token
    }
    payload = {
        "orgid": orgid,
        "pageid": page_id
    }

    try:
        resp = requests.post(verify_url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as ex:
        st.error(f"Lỗi gọi API VerifyStreamlit: {ex}")
        st.stop()

    data_json = resp.json()
    msg = data_json.get("message", "")

    # 4) Kiểm tra message
    if msg != "":
        msg = msg +  " : " + data_json.get("debug", "")
        st.error(f"{msg}")
        st.stop()

    # Nếu ok => return True, cho page chạy tiếp
    return base_url
base_url  = auth_check("sl_report_003")
# Danh sách tỉnh/thành (64 tỉnh Việt Nam)
LIST_PROVINCES = [
    "An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn",
    "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước",
    "Bình Thuận", "Cà Mau", "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk",
    "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai",
    "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương", "Hải Phòng",
    "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang",
    "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An",
    "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ",
    "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh",
    "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình",
    "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang",
    "TP Hồ Chí Minh", "Trà Vinh", "Tuyên Quang", "Vĩnh Long",
    "Vĩnh Phúc", "Yên Bái"
]

def generate_demo_data(num_rows=200000):
    """
    Sinh dữ liệu demo cỡ 200k dòng, có cột 'Khu vực' (tỉnh/thành) 
    và một số cột ví dụ khác (STT, Mã nhân viên...).
    """
    data = {
        "STT": list(range(1, num_rows+1)),
        "Mã nhân viên": [f"NV{random.randint(1000,9999)}" for _ in range(num_rows)],
        "Tên nhân viên": [f"Nhân viên {i}" for i in range(num_rows)],
        "Khu vực": [random.choice(LIST_PROVINCES) for _ in range(num_rows)],
        "Số lượng đặt": [random.randint(1, 100) for _ in range(num_rows)],
        "Đơn giá": [random.randint(10000, 200000) for _ in range(num_rows)],
    }
    df = pd.DataFrame(data)
    # Thêm cột Thành tiền
    df["Thành tiền"] = df["Số lượng đặt"] * df["Đơn giá"]
    return df

def to_excel(df):
    """
    Chuyển DataFrame -> binary Excel (dạng BytesIO) để download.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()

def main():
    #st.title("Trang Excel Page - 200k dòng, lọc Khu vực, Xuất Excel")

    # 1) Sinh (hoặc lưu) DataFrame 200k dòng trong session_state
    if "data_df" not in st.session_state:
        st.session_state["data_df"] = generate_demo_data(num_rows=200000)
    df = st.session_state["data_df"]

    # 2) Bộ lọc Khu vực (nhiều lựa chọn)
    st.subheader("Bộ lọc Khu vực - Anh Phong Test")
    selected_provinces = st.multiselect("Chọn Khu vực", LIST_PROVINCES)

    # Lọc DataFrame theo Khu vực
    if selected_provinces:
        df_filtered = df[df["Khu vực"].isin(selected_provinces)]
    else:
        df_filtered = df

    st.write(f"Dữ liệu sau khi lọc: {len(df_filtered)} dòng")

    # 3) Nút Xuất Excel
    #    - Khi bấm, tạo file Excel từ df_filtered
    #    - Hiển thị nút download
    if st.button("Xuất Excel"):
        excel_data = to_excel(df_filtered)
        st.download_button(
            label="Tải xuống Excel",
            data=excel_data,
            file_name="filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
