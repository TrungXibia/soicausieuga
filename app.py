import streamlit as st
import pandas as pd
import utils
from collections import Counter

# Cấu hình trang (Full width)
st.set_page_config(page_title="Siêu Gà 18+", layout="wide", page_icon="🐔")

# CSS tùy chỉnh cho đẹp
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: 700; color: #FF4B4B;}
    .sub-header {font-size: 1.5rem; font-weight: 600;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🐔 Hệ thống Soi Cầu Siêu Gà 18+</div>', unsafe_allow_html=True)

# Tạo Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 KQXS Chi Tiết", "🤖 Cầu Tự Động", "📈 Tần Suất", "🔗 Cặp Lô Đi Cùng"])

# --- TAB 1: XEM KẾT QUẢ ---
with tab1:
    col1, col2 = st.columns([1, 3])
    with col1:
        # Lấy danh sách tên đài từ utils
        station_list = list(utils.ALL_STATIONS.keys())
        station_name = st.selectbox("Chọn đài", station_list)
        url = utils.ALL_STATIONS[station_name]["url"]
    
    if st.button("Tải dữ liệu KQXS", type="primary"):
        with st.spinner("Đang tải dữ liệu..."):
            data = utils.fetch_data(url)
            if data:
                rows = []
                for item in data:
                    raw = utils.parse_detail(item["detail"])
                    giai_db = raw[0] if raw else ""
                    los = [utils.get_last2(x) for x in raw if utils.get_last2(x)]
                    rows.append({
                        "Ngày": item["turnNum"],
                        "Đặc Biệt": giai_db,
                        "Lô (2 số)": ", ".join(sorted(set(los)))
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.error("Không tải được dữ liệu hoặc lỗi kết nối.")

# --- TAB 2: CẦU TỰ ĐỘNG ---
with tab2:
    st.markdown('<div class="sub-header">Quét Cầu PASCAL / POSPAIR</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        s_cau = st.selectbox("Đài soi cầu", list(utils.ALL_STATIONS.keys()), index=0)
    with c2:
        method = st.selectbox("Thuật toán", ["POSPAIR", "PASCAL"])
    with c3:
        min_str = st.number_input("Streak (chuỗi) tối thiểu", value=3, min_value=1)
    
    if st.button("🚀 Quét Cầu Ngay"):
        u = utils.ALL_STATIONS[s_cau]["url"]
        with st.spinner(f"Đang chạy thuật toán {method} trên đài {s_cau}..."):
            results = utils.scan_cau_dong(u, method=method, min_streak=min_str)
            if results:
                df_res = pd.DataFrame(results)
                st.success(f"Tìm thấy {len(results)} cầu!")
                # Highlight cột Dự đoán
                st.dataframe(df_res.style.applymap(lambda x: 'font-weight: bold; color: blue', subset=['Dự đoán']), use_container_width=True)
            else:
                st.warning("Không tìm thấy cầu nào thỏa mãn điều kiện.")

# --- TAB 3: TẦN SUẤT ---
with tab3:
    st.markdown('<div class="sub-header">Kiểm tra tần suất dàn số</div>', unsafe_allow_html=True)
    user_input = st.text_area("Nhập các số (cách nhau bởi dấu cách hoặc phẩy)", "01 02 03 99")
    
    if user_input:
        # Xử lý input
        nums = []
        for x in user_input.replace(",", " ").split():
            if x.strip().isdigit():
                nums.append(x.strip().zfill(2)) 
        
        if nums:
            counts = Counter(nums)
            df_freq = pd.DataFrame(list(counts.items()), columns=["Số", "Số lần xuất hiện"])
            df_freq = df_freq.sort_values(by="Số lần xuất hiện", ascending=False)
            
            c_left, c_right = st.columns(2)
            with c_left:
                st.dataframe(df_freq, use_container_width=True)
            with c_right:
                st.bar_chart(df_freq.set_index("Số"))
        else:
            st.info("Hãy nhập số liệu để bắt đầu đếm.")

# --- TAB 4: CẶP LÔ ĐI CÙNG (ĐÃ CẬP NHẬT) ---
with tab4:
    st.markdown('<div class="sub-header">🔗 Phân tích Cặp Lô Đi Cùng</div>', unsafe_allow_html=True)
    
    col_inp1, col_inp2, col_inp3 = st.columns(3)
    
    with col_inp1:
        target_lo = st.text_input("Nhập Lô mục tiêu (VD: 68)", max_chars=2)
    with col_inp2:
        region_opt = st.selectbox("Khu vực quét", ["MB (Miền Bắc)", "MN (Miền Nam)", "MT (Miền Trung)", "ALL (Tất cả)"])
        # Map selection to code
        region_map = {"MB (Miền Bắc)": "MB", "MN (Miền Nam)": "MN", "MT (Miền Trung)": "MT", "ALL (Tất cả)": "ALL"}
        region_code = region_map[region_opt]
    with col_inp3:
        mode_opt = st.radio("Chế độ đếm", ["Theo ngày (Không trùng)", "Theo lần xuất hiện (Có trùng)"])
        mode_code = "day" if "ngày" in mode_opt else "hit"

    if st.button("🔍 Phân tích ngay", type="primary"):
        if not target_lo or not target_lo.isdigit() or len(target_lo) != 2:
            st.error("Vui lòng nhập đúng định dạng 2 chữ số (00-99).")
        else:
            # Tạo thanh tiến trình
            my_bar = st.progress(0, text="Đang khởi tạo...")
            
            # Gọi hàm xử lý từ utils
            freq_list, logs = utils.scan_cap_lo_di_cung(
                target_lo, 
                region_code, 
                mode_code, 
                progress_callback=lambda prog, msg: my_bar.progress(prog, text=msg)
            )
            
            my_bar.empty() # Xóa thanh tiến trình khi xong

            if freq_list is None:
                st.error(logs) # Lỗi không có đài
            elif not freq_list:
                st.warning(f"Không tìm thấy số {target_lo} trong lịch sử 60 kỳ gần nhất của khu vực {region_code}.")
            else:
                st.success(f"Hoàn tất! Tìm thấy {target_lo} xuất hiện trong {len(logs)} kỳ quay.")
                
                # Chia 2 cột kết quả
                res_c1, res_c2 = st.columns([1, 2])
                
                with res_c1:
                    st.write(f"**Top số hay về cùng {target_lo}:**")
                    df_freq = pd.DataFrame(freq_list)
                    st.dataframe(
                        df_freq.style.background_gradient(cmap="Greens", subset=["Số lần/ngày gặp"]),
                        use_container_width=True,
                        height=400
                    )
                
                with res_c2:
                    st.write("**Chi tiết các lần xuất hiện:**")
                    df_logs = pd.DataFrame(logs)
                    st.dataframe(df_logs, use_container_width=True, height=400)