import streamlit as st
import pandas as pd
import utils
from collections import Counter
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Siêu Gà 18+", layout="wide", page_icon="🐔")

bg_color = st.sidebar.color_picker("Màu nền", "#f7f9fb")

# Get current day of week
def get_current_day_index():
    days_map = {
        0: "Thứ 2",
        1: "Thứ 3", 
        2: "Thứ 4",
        3: "Thứ 5",
        4: "Thứ 6",
        5: "Thứ 7",
        6: "Chủ nhật"
    }
    current_day = datetime.now().weekday()
    current_day_name = days_map[current_day]
    day_list = list(utils.DAY_STATIONS.keys())
    try:
        return day_list.index(current_day_name)
    except ValueError:
        return 0

# Custom CSS for styling
st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_color} !important;
        font-family: system-ui,-apple-system,"Segoe UI",Roboto,Ubuntu,"Helvetica Neue",Arial,"Noto Sans",sans-serif;
    }}
    .block-container {{
        padding: 2rem 2rem;
        max-width: 1200px;
    }}
    .main-header {{
        font-size: 2.2rem;
        font-weight: 700;
        color: #0ea5e9;
        letter-spacing: 0.2px;
    }}
    .sub-header {{
        font-size: 1.2rem;
        font-weight: 600;
        color: #334155;
        margin: 0.25rem 0 0.75rem 0;
    }}
    .stButton>button {{
        background-color: #0ea5e9;
        color: #ffffff;
        border: 0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        background-color: #38bdf8;
        color: #ffffff;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🐔 Hệ thống Soi Cầu Siêu Gà 18+</div>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab5, tab6 = st.tabs([
    "📊 KQXS Chi Tiết",
    "🤖 Cầu Tự Động",
    "🔮 Soi Khác",
    "📅 Quét Theo Ngày"
])

# ------------------- TAB 1: KQXS Chi Tiết -------------------
with tab1:
    day_selected = st.selectbox("Chọn ngày", list(utils.DAY_STATIONS.keys()), index=get_current_day_index())
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
    
    day_selected = st.selectbox("Chọn ngày", list(utils.DAY_STATIONS.keys()), index=get_current_day_index(), key="day_tab2")
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
    
    # Button Logic
    if st.button("🚀 Quét Cầu Ngay"):
        u = utils.ALL_STATIONS[s_cau]["url"]
        
        if method == "3 CÀNG":
            with st.spinner(f"Đang quét cầu 3 Càng trên đài {s_cau}..."):
                results = utils.scan_cau_3_cang(u, min_streak=min_str)
                if results:
                    # Process for Frequency Grouping (3 Càng)
                    all_preds = [r["Dự đoán"] for r in results if "Dự đoán" in r]
                    
                    if all_preds:
                        pred_counts = Counter(all_preds)
                        freq_groups = {}
                        for num, count in pred_counts.items():
                            if count not in freq_groups: freq_groups[count] = []
                            freq_groups[count].append(num)
                        
                        summary_rows = []
                        for count in sorted(freq_groups.keys(), reverse=True):
                            nums = sorted(freq_groups[count])
                            le_2d = [n[-2:] for n in nums]
                            summary_rows.append({
                                "Mức (Số cầu báo)": f"{count} cầu",
                                "Các số dự đoán": ", ".join(nums),
                                "Lê 2D": ", ".join(le_2d),
                                "Số lượng": len(nums)
                            })
                        
                        st.success(f"Tìm thấy {len(results)} cầu 3 càng!")
                        st.markdown("### 📊 Thống kê Mức Số (3 Càng)")
                        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

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


# ------------------- TAB 5: SOI KHÁC (LÔ GAN & BẠC NHỚ) -------------------
with tab5:
    st.markdown('<div class="sub-header">🔮 Soi Lô Gan & Bạc Nhớ (Ngày Mai)</div>', unsafe_allow_html=True)
    
    # Hierarchical Selection (Same as Tab 2)
    day_selected = st.selectbox("Chọn ngày", list(utils.DAY_STATIONS.keys()), index=get_current_day_index(), key="day_tab5")
    day_stations = utils.DAY_STATIONS.get(day_selected, [])
    region_options = sorted({region for region, _ in day_stations})
    selected_region = st.selectbox("Chọn miền", region_options, index=0, key="region_tab5")
    station_options = [station for region, station in day_stations if region == selected_region]
    s_cau = st.selectbox("Đài soi cầu", station_options, index=0, key="station_tab5")

    t5_1, t5_2 = st.tabs(["🐢 Lô Gan (Lâu chưa về)", "📅 Bạc Nhớ (Dự đoán ngày mai)"])
    with t5_1:
        st.caption(f"Thống kê các số lâu chưa xuất hiện tại đài **{s_cau}**.")
        limit_gan = st.slider("Xét trong bao nhiêu kỳ gần nhất?", 30, 100, 100, key="limit_gan")
        if st.button("Quét Lô Gan"):
            u_gan = utils.ALL_STATIONS[s_cau]["url"]
            with st.spinner("Đang quét lô gan..."):
                data_gan = utils.get_lo_gan(u_gan, limit=limit_gan)
                if data_gan:
                    st.dataframe(pd.DataFrame(data_gan), use_container_width=True)
                else:
                    st.error("Không có dữ liệu.")
    with t5_2:
        st.caption(f"Dựa vào số về hôm nay để dự đoán số về ngày mai (theo lịch sử) tại đài **{s_cau}**.")
        target_bn = st.text_input("Nhập số vừa về (VD: 99)", max_chars=2, key="target_bn")
        if st.button("Soi Bạc Nhớ"):
            if not target_bn or not target_bn.isdigit():
                st.error("Vui lòng nhập số hợp lệ.")
            else:
                u_bn = utils.ALL_STATIONS[s_cau]["url"]
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
    st.markdown('<div class="sub-header">📅 Quét Theo Miền & Ngày với Phương Pháp Tự Động</div>', unsafe_allow_html=True)
    st.caption("Quét tất cả các đài của một miền trong ngày được chọn, áp dụng các phương pháp POSPAIR và PASCAL để tìm cầu.")
    
    col_t6_1, col_t6_2, col_t6_3 = st.columns(3)
    with col_t6_1:
        region_scan = st.selectbox(
            "Chọn miền", 
            ["MB (Miền Bắc)", "MN (Miền Nam)", "MT (Miền Trung)", "ALL (Tất cả)"],
            index=0,
            key="region_tab6"
        )
        region_map = {"MB (Miền Bắc)": "MB", "MN (Miền Nam)": "MN", "MT (Miền Trung)": "MT", "ALL (Tất cả)": "ALL"}
        region_code = region_map[region_scan]
    
    with col_t6_2:
        day_scan = st.selectbox("Chọn ngày", list(utils.DAY_STATIONS.keys()), index=get_current_day_index(), key="day_tab6")
    
    with col_t6_3:
        min_streak_t6 = st.slider("Streak tối thiểu", 2, 3, key="streak_tab6")
    
    # Method selection
    st.write("**Chọn phương pháp quét:**")
    col_method1, col_method2 = st.columns(2)
    with col_method1:
        use_pospair = st.checkbox("POSPAIR (Vị trí ghép)", value=True)
    with col_method2:
        use_pascal = st.checkbox("PASCAL (Tam giác Pascal)", value=True)
    
    st.write("**Loại cầu:**")
    pred_type_t6 = st.radio("Chế độ dự đoán", ["Song thủ (AB-BA)", "Bạch thủ (AB)"], key="pred_type_tab6", horizontal=True)
    pred_code_t6 = "SONG_THU" if "Song" in pred_type_t6 else "BACH_THU"
    
    if st.button("🔍 Quét Ngay", type="primary", key="scan_tab6"):
        if not use_pospair and not use_pascal:
            st.error("Vui lòng chọn ít nhất một phương pháp!")
        else:
            methods = []
            if use_pospair:
                methods.append("POSPAIR")
            if use_pascal:
                methods.append("PASCAL")
            
            my_bar = st.progress(0, text="Đang khởi tạo...")
            prediction_summary, station_details, total_stats = utils.scan_region_by_day_with_methods(
                region=region_code,
                day=day_scan,
                methods=methods,
                min_streak=min_streak_t6,
                depth=30,
                prediction_type=pred_code_t6,
                progress_callback=lambda prog, msg: my_bar.progress(prog, text=msg)
            )
            my_bar.empty()
            
            if total_stats["total_predictions"] > 0:
                st.success(f"✅ Hoàn tất! Quét {total_stats['total_stations']} đài, tìm thấy {total_stats['total_predictions']} cầu với {total_stats['unique_numbers']} số duy nhất.")
                
                # Display summary by frequency level
                st.markdown("### 📊 Thống Kê Mức Số (Nhiều Cầu Nhất)")
                if prediction_summary:
                    summary_rows = []
                    for level_count in sorted(prediction_summary.keys(), reverse=True):
                        info = prediction_summary[level_count]
                        summary_rows.append({
                            "Mức": info["level"],
                            "Các số dự đoán": ", ".join(info["numbers"]),
                            "Số lượng": info["total_numbers"]
                        })
                    
                    df_summary = pd.DataFrame(summary_rows)
                    st.dataframe(
                        df_summary.style.background_gradient(cmap="YlOrRd", subset=["Số lượng"]),
                        use_container_width=True
                    )
                
                # Display details by station
                with st.expander("📋 Xem chi tiết từng đài", expanded=False):
                    for station_info in station_details:
                        st.write(f"**{station_info['station']}** ({station_info['total_cau']} cầu)")
                        for method, method_info in station_info['methods'].items():
                            st.write(f"  - {method}: {method_info['count']} cầu → {', '.join(method_info['predictions'][:10])}{'...' if len(method_info['predictions']) > 10 else ''}")
            else:
                st.warning(f"Không tìm thấy cầu nào thỏa mãn điều kiện (streak >= {min_streak_t6}) cho {region_scan} vào {day_scan}.")

