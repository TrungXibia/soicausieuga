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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 KQXS Chi Tiết",
    "🤖 Cầu Tự Động",
    "📈 Tần Suất",
    "🔗 Cặp Lô Đi Cùng",
    "🔮 Soi Khác",
    "📅 Quét Theo Ngày"
])

# ------------------- TAB 1: KQXS Chi Tiết -------------------
with tab1:
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
    st.markdown('<div class="sub-header">Quét Cầu PASCAL / POSPAIR / 3 CÀNG</div>', unsafe_allow_html=True)
    
    with st.expander("📖 Giải thích phương pháp & Backtest"):
        st.markdown("""
        **1. POSPAIR (Position Pair):**
        - Chọn 2 vị trí bất kỳ trong bảng kết quả xổ số.
        - Lấy chữ số tại vị trí đó (Cuối hoặc Sát cuối) để ghép cầu.
        - **Song thủ:** Ghép AB và BA. Trúng nếu về 1 trong 2.
        - **Bạch thủ:** Ghép AB. Trúng nếu về đúng AB.

        **2. 3 CÀNG (3 Số):**
        - Chọn 3 vị trí (A, B, C) từ các giải có từ 3 chữ số trở lên.
        - Ghép lại thành bộ 3 số ABC.
        - Soi kết quả dựa trên 3 số cuối của các giải (GĐB-G6 với MB, GĐB-G7 với MN/MT).

        **3. PASCAL:**
        - Lấy 2 số tại 2 vị trí bất kỳ, ghép lại thành chuỗi số.
        - Cộng dồn theo quy tắc tam giác Pascal (cộng 2 số liền kề, lấy hàng đơn vị) cho đến khi còn 2 số.
        """)
    
    day_selected = st.selectbox("Chọn ngày", list(utils.DAY_STATIONS.keys()), index=0, key="day_tab2")
    day_stations = utils.DAY_STATIONS.get(day_selected, [])
    region_options = sorted({region for region, _ in day_stations})
    selected_region = st.selectbox("Chọn miền", region_options, index=0, key="region_tab2")
    station_options = [station for region, station in day_stations if region == selected_region]
    s_cau = st.selectbox("Đài soi cầu", station_options, index=0)
    
    col1, col2 = st.columns(2)
    with col1:
        method = st.selectbox("Thuật toán", ["POSPAIR", "PASCAL", "3 CÀNG"])
    with col2:
        min_str = st.number_input("Streak (chuỗi) tối thiểu", value=3, min_value=1)
    
    # Options based on Method
    use_last = True
    use_near_last = False
    pred_code = "SONG_THU"
    selected_positions = None
    scan_mode = "Tự động (Quét tất cả vị trí)"

    if method == "POSPAIR":
        st.write("---")
        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            st.write("**Vị trí quét:**")
            use_last = st.checkbox("Số cuối giải (Hàng đơn vị)", value=True)
            use_near_last = st.checkbox("Số sát cuối giải (Hàng chục)", value=False)
        with c_opt2:
            st.write("**Loại cầu:**")
            pred_type = st.radio("Chế độ dự đoán", ["Song thủ (AB-BA)", "Bạch thủ (AB)"])
            pred_code = "SONG_THU" if "Song" in pred_type else "BACH_THU"
        
        scan_mode = st.radio("Chế độ quét", ["Tự động (Quét tất cả vị trí)", "Thủ công (Chọn vị trí cụ thể)"], horizontal=True)
        if scan_mode == "Thủ công (Chọn vị trí cụ thể)":
            st.info("💡 Nhập các cặp vị trí cần quét. Ví dụ: 0-1, 2-5, 7-9 (vị trí bắt đầu từ 0)")
            pos_input = st.text_input("Nhập các cặp vị trí (cách nhau bởi dấu phẩy)", "0-1, 0-2, 1-2")
            if pos_input:
                selected_positions = []
                for pair in pos_input.split(","):
                    pair = pair.strip()
                    if "-" in pair:
                        try:
                            a, b = pair.split("-")
                            selected_positions.append((int(a.strip()), int(b.strip())))
                        except:
                            pass

    elif method == "3 CÀNG":
        st.info("ℹ️ Chế độ 3 Càng sẽ tự động quét các tổ hợp 3 vị trí (A-B-C) từ các giải có độ dài >= 3.")
    
    if st.button("🚀 Quét Cầu Ngay"):
        u = utils.ALL_STATIONS[s_cau]["url"]
        
        if method == "3 CÀNG":
            with st.spinner(f"Đang quét cầu 3 Càng trên đài {s_cau}..."):
                results = utils.scan_cau_3_cang(u, min_streak=min_str)
                if results:
                    st.success(f"Tìm thấy {len(results)} cầu 3 càng!")
                    st.dataframe(pd.DataFrame(results).style.applymap(lambda x: 'font-weight: bold; color: purple', subset=['Dự đoán']), use_container_width=True)
                else:
                    st.warning("Không tìm thấy cầu 3 càng nào thỏa mãn.")
        else:
            # POSPAIR / PASCAL
            if method == "POSPAIR" and not use_last and not use_near_last:
                st.error("Vui lòng chọn ít nhất một loại vị trí quét.")
            else:
                with st.spinner(f"Đang chạy thuật toán {method} trên đài {s_cau}..."):
                    results = utils.scan_cau_dong(
                        u, 
                        method=method, 
                        min_streak=min_str, 
                        position_pairs=selected_positions,
                        use_last=use_last,
                        use_near_last=use_near_last,
                        prediction_type=pred_code
                    )
                    
                    if results:
                        # Summary Table Logic
                        all_preds = []
                        for r in results:
                            if "Raw_Pred" in r:
                                all_preds.extend(r["Raw_Pred"])
                        
                        if all_preds:
                            pred_counts = Counter(all_preds)
                            freq_groups = {}
                            for num, count in pred_counts.items():
                                if count not in freq_groups: freq_groups[count] = []
                                freq_groups[count].append(num)
                            
                            summary_rows = []
                            for count in sorted(freq_groups.keys(), reverse=True):
                                nums = sorted(freq_groups[count])
                                summary_rows.append({
                                    "Mức (Số cầu báo)": f"{count} cầu",
                                    "Các số dự đoán": ", ".join(nums),
                                    "Số lượng": len(nums)
                                })
                            
                            st.success(f"Tìm thấy {len(results)} cầu!")
                            st.markdown("### 📊 Thống kê Mức Số")
                            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)
                        
                        with st.expander("📋 Xem chi tiết từng cầu", expanded=True):
                            df_res = pd.DataFrame(results)
                            if "Raw_Pred" in df_res.columns:
                                df_res = df_res.drop(columns=["Raw_Pred"])
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

# ------------------- TAB 6: QUÉT THEO NGÀY -------------------
with tab6:
    st.markdown('<div class="sub-header">📅 Quét Tất Cả Đài Theo Ngày</div>', unsafe_allow_html=True)
    st.caption("Quét tất cả các đài của một ngày trong tuần và tổng hợp theo tần suất xuất hiện.")
    
    col_t6_1, col_t6_2 = st.columns(2)
    with col_t6_1:
        day_scan = st.selectbox("Chọn ngày quét", list(utils.DAY_STATIONS.keys()), index=0, key="day_tab6")
    with col_t6_2:
        limit_scan = st.slider("Số kỳ quét gần nhất", 10, 100, 30, key="limit_tab6")
    
    if st.button("🔍 Quét Ngay", type="primary"):
        my_bar = st.progress(0, text="Đang khởi tạo...")
        freq_data, detail_logs = utils.scan_day_stations(
            day_scan,
            limit=limit_scan,
            progress_callback=lambda prog, msg: my_bar.progress(prog, text=msg)
        )
        my_bar.empty()
        
        if freq_data:
            st.success(f"Hoàn tất! Đã quét {len(utils.get_stations_by_day(day_scan))} đài của {day_scan}.")
            
            res_t6_1, res_t6_2 = st.columns([2, 1])
            with res_t6_1:
                st.write("**Bảng tần suất xuất hiện (Top 50):**")
                df_freq = pd.DataFrame(freq_data[:50])
                st.dataframe(
                    df_freq.style.background_gradient(cmap="Blues", subset=["Số lần xuất hiện"]),
                    use_container_width=True,
                    height=500
                )
            with res_t6_2:
                st.write("**Biểu đồ Top 20:**")
                df_top20 = pd.DataFrame(freq_data[:20])
                st.bar_chart(df_top20.set_index("Số")["Số lần xuất hiện"])
            
            with st.expander("📋 Xem chi tiết kết quả từng đài"):
                df_detail = pd.DataFrame(detail_logs)
                st.dataframe(df_detail, use_container_width=True, height=400)
        else:
            st.warning("Không có dữ liệu để hiển thị.")
