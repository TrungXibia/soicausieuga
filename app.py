import streamlit as st
import pandas as pd
import utils
from collections import Counter

# Page configuration
st.set_page_config(page_title="Siêu Gà 18+", layout="wide", page_icon="🐔")

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: 700; color: #FF4B4B;}
    .sub-header {font-size: 1.5rem; font-weight: 600;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🐔 Hệ thống Soi Cầu Siêu Gà 18+</div>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 KQXS Chi Tiết",
    "🤖 Cầu Tự Động",
    "📈 Tần Suất",
    "🔗 Cặp Lô Đi Cùng",
    "🔮 Soi Khác"
])

# ------------------- TAB 1: KQXS Chi Tiết -------------------
with tab1:
    # Select day, region, then station
    day_selected = st.selectbox("Chọn ngày", list(utils.DAY_STATIONS.keys()), index=0)
    day_stations = utils.DAY_STATIONS.get(day_selected, [])
    region_options = sorted({region for region, _ in day_stations})
    selected_region = st.selectbox("Chọn miền", region_options, index=0)
    station_options = [station for region, station in day_stations if region == selected_region]
    station_name = st.selectbox("Chọn đài", station_options, index=0)
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

# ------------------- TAB 2: Cầu Tự Động -------------------
with tab2:
    st.markdown('<div class="sub-header">Quét Cầu PASCAL / POSPAIR</div>', unsafe_allow_html=True)
    # Explanation expander
    with st.expander("📖 Giải thích phương pháp & Backtest"):
        st.markdown("""
        **1. POSPAIR (Position Pair):**
        - Lấy chữ số cuối cùng của 2 vị trí bất kỳ trong bảng kết quả.
        - Ghép lại thành cặp số. Ví dụ: Vị trí A là 123, Vị trí B là 456 -> Cặp 36, 63.

        **2. PASCAL:**
        - Lấy 2 số tại 2 vị trí, ghép lại thành chuỗi số.
        - Cộng dồn theo quy tắc tam giác Pascal (cộng 2 số liền kề, lấy hàng đơn vị) cho đến khi còn 2 số.
        - Ví dụ: 123 và 456 -> 123456 -> ... -> 89 -> Cặp 89, 98.

        **3. Win Rate (Tỷ lệ thắng):**
        - Là tỷ lệ số lần cầu này dự đoán đúng trong quá khứ (theo độ sâu quét).
        - Backtest được thực hiện tự động khi quét, hiển thị qua cột Win Rate.
        """)
    # Day & region selection for scanning
    day_selected = st.selectbox("Chọn ngày", list(utils.DAY_STATIONS.keys()), index=0, key="day_tab2")
    day_stations = utils.DAY_STATIONS.get(day_selected, [])
    region_options = sorted({region for region, _ in day_stations})
    selected_region = st.selectbox("Chọn miền", region_options, index=0, key="region_tab2")
    station_options = [station for region, station in day_stations if region == selected_region]
    s_cau = st.selectbox("Đài soi cầu", station_options, index=0)
    method = st.selectbox("Thuật toán", ["POSPAIR", "PASCAL"])
    min_str = st.number_input("Streak (chuỗi) tối thiểu", value=3, min_value=1)

    if st.button("🚀 Quét Cầu Ngay"):
        u = utils.ALL_STATIONS[s_cau]["url"]
        with st.spinner(f"Đang chạy thuật toán {method} trên đài {s_cau}..."):
            results = utils.scan_cau_dong(u, method=method, min_streak=min_str)
            if results:
                df_res = pd.DataFrame(results)
                st.success(f"Tìm thấy {len(results)} cầu!")
                st.dataframe(df_res.style.applymap(lambda x: 'font-weight: bold; color: blue', subset=['Dự đoán']), use_container_width=True)
            else:
                st.warning("Không tìm thấy cầu nào thỏa mãn điều kiện.")

# ------------------- TAB 3: Tần Suất -------------------
with tab3:
    st.markdown('<div class="sub-header">Kiểm tra tần suất dàn số</div>', unsafe_allow_html=True)
    user_input = st.text_area("Nhập các số (cách nhau bởi dấu cách hoặc phẩy)", "01 02 03 99")
    if user_input:
        nums = []
        for x in user_input.replace(",", " ").split():
            if x.strip().isdigit():
                nums.append(x.strip().zfill(2))
        if nums:
            counts = Counter(nums)
            df_freq = pd.DataFrame(list(counts.items()), columns=["Số", "Số lần xuất hiện"]).sort_values(by="Số lần xuất hiện", ascending=False)
            c_left, c_right = st.columns(2)
            with c_left:
                st.dataframe(df_freq, use_container_width=True)
            with c_right:
                st.bar_chart(df_freq.set_index("Số"))
        else:
            st.info("Hãy nhập số liệu để bắt đầu đếm.")

# ------------------- TAB 4: Cặp Lô Đi Cùng -------------------
with tab4:
    st.markdown('<div class="sub-header">🔗 Phân tích Cặp Lô Đi Cùng</div>', unsafe_allow_html=True)
    col_inp1, col_inp2, col_inp3 = st.columns(3)
    with col_inp1:
        target_lo = st.text_input("Nhập Lô mục tiêu (VD: 68)", max_chars=2)
    with col_inp2:
        region_opt = st.selectbox("Khu vực quét", ["MB (Miền Bắc)", "MN (Miền Nam)", "MT (Miền Trung)", "ALL (Tất cả)"])
        region_map = {"MB (Miền Bắc)": "MB", "MN (Miền Nam)": "MN", "MT (Miền Trung)": "MT", "ALL (Tất cả)": "ALL"}
        region_code = region_map[region_opt]
    with col_inp3:
        mode_opt = st.radio("Chế độ đếm", ["Theo ngày (Không trùng)", "Theo lần xuất hiện (Có trùng)"])
        mode_code = "day" if "ngày" in mode_opt else "hit"
    if st.button("🔍 Phân tích ngay", type="primary"):
        if not target_lo or not target_lo.isdigit() or len(target_lo) != 2:
            st.error("Vui lòng nhập đúng định dạng 2 chữ số (00-99).")
        else:
            my_bar = st.progress(0, text="Đang khởi tạo...")
            freq_list, logs = utils.scan_cap_lo_di_cung(
                target_lo,
                region_code,
                mode_code,
                progress_callback=lambda prog, msg: my_bar.progress(prog, text=msg)
            )
            my_bar.empty()
            if freq_list is None:
                st.error(logs)
            elif not freq_list:
                st.warning(f"Không tìm thấy số {target_lo} trong lịch sử 60 kỳ gần nhất của khu vực {region_code}.")
            else:
                st.success(f"Hoàn tất! Tìm thấy {target_lo} xuất hiện trong {len(logs)} kỳ quay.")
                res_c1, res_c2 = st.columns([1, 2])
                with res_c1:
                    st.write(f"**Top số hay về cùng {target_lo}:**")
                    df_freq = pd.DataFrame(freq_list)
                    st.dataframe(df_freq.style.background_gradient(cmap="Greens", subset=["Số lần/ngày gặp"]), use_container_width=True, height=400)
                with res_c2:
                    st.write("**Chi tiết các lần xuất hiện:**")
                    df_logs = pd.DataFrame(logs)
                    st.dataframe(df_logs, use_container_width=True, height=400)

# ------------------- TAB 5: SOI KHÁC (LÔ GAN & BẠC NHỚ) -------------------
with tab5:
    st.markdown('<div class="sub-header">🔮 Soi Lô Gan & Bạc Nhớ (Ngày Mai)</div>', unsafe_allow_html=True)
    t5_1, t5_2 = st.tabs(["🐢 Lô Gan (Lâu chưa về)", "📅 Bạc Nhớ (Dự đoán ngày mai)"])
    with t5_1:
        st.caption("Thống kê các số lâu chưa xuất hiện.")
        s_gan = st.selectbox("Chọn đài (Lô Gan)", list(utils.ALL_STATIONS.keys()), key="s_gan")
        limit_gan = st.slider("Xét trong bao nhiêu kỳ gần nhất?", 30, 100, 100, key="limit_gan")
        if st.button("Quét Lô Gan"):
            u_gan = utils.ALL_STATIONS[s_gan]["url"]
            with st.spinner("Đang quét lô gan..."):
                data_gan = utils.get_lo_gan(u_gan, limit=limit_gan)
                if data_gan:
                    st.dataframe(pd.DataFrame(data_gan), use_container_width=True)
                else:
                    st.error("Không có dữ liệu.")
    with t5_2:
        st.caption("Dựa vào số về hôm nay để dự đoán số về ngày mai (theo lịch sử).")
        c_bn1, c_bn2 = st.columns(2)
        with c_bn1:
            s_bn = st.selectbox("Chọn đài (Bạc Nhớ)", list(utils.ALL_STATIONS.keys()), key="s_bn")
        with c_bn2:
            target_bn = st.text_input("Nhập số vừa về (VD: 99)", max_chars=2, key="target_bn")
        if st.button("Soi Bạc Nhớ"):
            if not target_bn or not target_bn.isdigit():
                st.error("Vui lòng nhập số hợp lệ.")
            else:
                u_bn = utils.ALL_STATIONS[s_bn]["url"]
                with st.spinner("Đang phân tích bạc nhớ..."):
                    freq_bn, logs_bn = utils.get_bac_nho_next_day(u_bn, target_bn)
                    if freq_bn:
                        st.success(f"Khi {target_bn} về, ngày hôm sau thường về các số sau:")
                        df_bn = pd.DataFrame(freq_bn)
                        st.dataframe(df_bn.style.background_gradient(cmap="Reds"), use_container_width=True)
                        with st.expander("Xem chi tiết lịch sử"):
                            st.dataframe(pd.DataFrame(logs_bn), use_container_width=True)
                    else:
                        st.warning(f"Không tìm thấy dữ liệu lịch sử cho số {target_bn}.")
