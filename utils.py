import requests
import json
import pandas as pd
from collections import Counter
import datetime
from itertools import permutations

# ==== 1. DANH SÁCH API ĐẦY ĐỦ (MB, MN, MT) ====
ALL_STATIONS = {
    # -- Miền Bắc --
    "Miền Bắc": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=100&gameCode=miba", "region": "MB"},
    
    # -- Miền Nam --
    "Hồ Chí Minh": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=tphc", "region": "MN"},
    "Đồng Tháp": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=doth", "region": "MN"},
    "Cà Mau": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=cama", "region": "MN"},
    "Bến Tre": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=betr", "region": "MN"},
    "Vũng Tàu": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=vuta", "region": "MN"},
    "Bạc Liêu": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=bali", "region": "MN"},
    "Đồng Nai": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=dona", "region": "MN"},
    "Cần Thơ": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=cath", "region": "MN"},
    "Sóc Trăng": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=sotr", "region": "MN"},
    "Tây Ninh": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=tani", "region": "MN"},
    "An Giang": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=angi", "region": "MN"},
    "Bình Thuận": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=bith", "region": "MN"},
    "Vĩnh Long": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=vilo", "region": "MN"},
    "Bình Dương": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=bidu", "region": "MN"},
    "Trà Vinh": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=trvi", "region": "MN"},
    "Long An": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=loan", "region": "MN"},
    "Bình Phước": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=biph", "region": "MN"},
    "Hậu Giang": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=hagi", "region": "MN"},
    "Tiền Giang": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=tigi", "region": "MN"},
    "Kiên Giang": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=kigi", "region": "MN"},
    "Đà Lạt": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=dalat", "region": "MN"},

    # -- Miền Trung --
    "Đà Nẵng": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=dana", "region": "MT"},
    "Khánh Hòa": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=khho", "region": "MT"},
    "Đắk Lắk": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=dalak", "region": "MT"},
    "Quảng Nam": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=quna", "region": "MT"},
    "Bình Định": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=bidi", "region": "MT"},
    "Quảng Trị": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=qutr", "region": "MT"},
    "Quảng Bình": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=qubi", "region": "MT"},
    "Gia Lai": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=gila", "region": "MT"},
    "Ninh Thuận": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=nith", "region": "MT"},
    "Quảng Ngãi": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=qung", "region": "MT"},
    "Đắk Nông": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=dano", "region": "MT"},
    "Kon Tum": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=kotu", "region": "MT"},
    "Thừa Thiên Huế": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=thth", "region": "MT"},
    "Phú Yên": {"url": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=30&gameCode=phye", "region": "MT"},
}

# ==== 2. CÁC HÀM XỬ LÝ DATA ====

def fetch_data(url):
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        return res.json().get("t", {}).get("issueList", [])
    except:
        return []

def parse_detail(detail_str):
    try:
        data = json.loads(detail_str)
        numbers = []
        for field in data:
            for x in field.split(","):
                x = x.strip().replace('"', '').replace("'", "")
                if x:
                    numbers.append(x)
        return numbers
    except:
        return []

def get_last2(s):
    s = str(s).strip()
    if len(s) >= 2 and s.isdigit():
        return s[-2:]
    return None

def get_last3(s):
    s = str(s).strip()
    if len(s) >= 3 and s.isdigit():
        return s[-3:]
    return None

# ==== 3. THUẬT TOÁN CẦU ====

def algo_pascal(s_a, s_b):
    base = (s_a or "") + (s_b or "")
    base = "".join([c for c in base if c.isdigit()])
    if len(base) < 2: return (None, None)
    arr = [int(ch) for ch in base]
    while len(arr) > 2:
        nxt = [(arr[i] + arr[i+1]) % 10 for i in range(len(arr)-1)]
        arr = nxt
    return (f"{arr[0]}{arr[1]}", f"{arr[1]}{arr[0]}")

def scan_cau_3_cang(url, depth=30, min_streak=2):
    issues = fetch_data(url)
    if not issues: return []
    issues = issues[:depth][::-1] 
    days = []
    for it in issues:
        raw = parse_detail(it.get("detail", "[]"))
        # Filter for 3-cang targets: only prizes with len >= 3
        los = set([get_last3(s) for s in raw if get_last3(s)])
        days.append({"date": it.get("turnNum"), "raw": raw, "los": los})
    if len(days) < 2: return []

    # Determine available nodes based on the LAST day's structure
    # Only pick nodes from prizes with len >= 3 (MB: GĐB-G6, MN/MT: GĐB-G7)
    last_raw = days[-1]["raw"]
    nodes = []
    for idx, val in enumerate(last_raw):
        if len(val) >= 3:
            # Default to Last Digit (-1) for 3-cang to save performance
            nodes.append((idx, -1, f"Pos {idx}"))
            
    limit_nodes = len(nodes)
    results = []
    
    # Generate permutations of 3 nodes
    # P(N, 3)
    perms = list(permutations(range(limit_nodes), 3))
    
    for p in perms:
        node_a = nodes[p[0]]
        node_b = nodes[p[1]]
        node_c = nodes[p[2]]
        
        hits = []
        for k in range(len(days)-1):
            curr_raw = days[k]["raw"]
            next_los = days[k+1]["los"]
            
            # Helper to get digit
            def get_digit(n, raw_data):
                p_idx, c_idx, _ = n
                val_str = raw_data[p_idx] if p_idx < len(raw_data) else ""
                if val_str and len(val_str) >= abs(c_idx) and val_str[c_idx].isdigit():
                    return val_str[c_idx]
                return None

            da = get_digit(node_a, curr_raw)
            db = get_digit(node_b, curr_raw)
            dc = get_digit(node_c, curr_raw)
            
            pred_abc = None
            if da and db and dc:
                pred_abc = da + db + dc
            
            if pred_abc:
                hits.append(pred_abc in next_los)
            else:
                hits.append(False)
                
        streak = 0
        for h in reversed(hits):
            if h: streak += 1
            else: break
            
        if streak >= min_streak:
            # Calculate prediction for tomorrow
            last_raw = days[-1]["raw"]
            
            def get_digit_last(n, raw_data):
                p_idx, c_idx, lbl = n
                val_str = raw_data[p_idx] if p_idx < len(raw_data) else ""
                if val_str and len(val_str) >= abs(c_idx) and val_str[c_idx].isdigit():
                    return val_str[c_idx]
                return ""

            da = get_digit_last(node_a, last_raw)
            db = get_digit_last(node_b, last_raw)
            dc = get_digit_last(node_c, last_raw)
            
            p_abc = None
            if da and db and dc:
                p_abc = da + db + dc
            
            if p_abc:
                win_count = sum(hits)
                total_runs = len(hits)
                win_rate = (win_count / total_runs * 100) if total_runs > 0 else 0
                
                results.append({
                    "Vị trí": f"{node_a[2]} - {node_b[2]} - {node_c[2]}",
                    "Kiểu": "3 Càng",
                    "Streak": streak,
                    "Win Rate": f"{win_rate:.1f}% ({win_count}/{total_runs})",
                    "Dự đoán": p_abc
                })
                
    results.sort(key=lambda x: x["Streak"], reverse=True)
    return results

def scan_cau_dong(url, method="POSPAIR", depth=30, min_streak=2, position_pairs=None, 
                  use_last=True, use_near_last=False, prediction_type="SONG_THU"):
    issues = fetch_data(url)
    if not issues: return []
    issues = issues[:depth][::-1] 
    days = []
    for it in issues:
        raw = parse_detail(it.get("detail", "[]"))
        los = set([get_last2(s) for s in raw if get_last2(s)])
        days.append({"date": it.get("turnNum"), "raw": raw, "los": los})
    if len(days) < 2: return []

    # Determine available nodes based on the LAST day's structure
    # Node format: (prize_index, char_index, label)
    last_raw = days[-1]["raw"]
    nodes = []
    for idx, val in enumerate(last_raw):
        if use_last:
            nodes.append((idx, -1, f"Pos {idx} (Cuối)"))
        if use_near_last and len(val) >= 2:
            nodes.append((idx, -2, f"Pos {idx} (Sát)"))
            
    limit_nodes = len(nodes)
    results = []
    
    # Determine pairs to scan
    pairs_to_scan = []
    if position_pairs:
        # Manual mode: assume user meant Last digit of prize i and prize j
        for (i, j) in position_pairs:
            node_i = next((k for k, n in enumerate(nodes) if n[0] == i and n[1] == -1), None)
            node_j = next((k for k, n in enumerate(nodes) if n[0] == j and n[1] == -1), None)
            if node_i is not None and node_j is not None:
                pairs_to_scan.append((node_i, node_j))
    else:
        # Auto mode: scan all pairs of nodes
        pairs_to_scan = [(i, j) for i in range(limit_nodes) for j in range(i+1, limit_nodes)]
    
    for i, j in pairs_to_scan:
        node_a = nodes[i]
        node_b = nodes[j]
        
        hits = []
        for k in range(len(days)-1):
            curr_raw = days[k]["raw"]
            next_los = days[k+1]["los"]
            
            p_idx_a, c_idx_a, _ = node_a
            val_a_str = curr_raw[p_idx_a] if p_idx_a < len(curr_raw) else ""
            digit_a = val_a_str[c_idx_a] if val_a_str and len(val_a_str) >= abs(c_idx_a) and val_a_str[c_idx_a].isdigit() else None
            
            p_idx_b, c_idx_b, _ = node_b
            val_b_str = curr_raw[p_idx_b] if p_idx_b < len(curr_raw) else ""
            digit_b = val_b_str[c_idx_b] if val_b_str and len(val_b_str) >= abs(c_idx_b) and val_b_str[c_idx_b].isdigit() else None
            
            pred_ab, pred_ba = (None, None)
            
            if method == "PASCAL":
                v_a = val_a_str
                v_b = val_b_str
                pred_ab, pred_ba = algo_pascal(v_a, v_b)
            else:
                if digit_a and digit_b:
                    pred_ab = digit_a + digit_b
                    pred_ba = digit_b + digit_a
            
            if pred_ab:
                if prediction_type == "BACH_THU":
                    hits.append(pred_ab in next_los)
                else: 
                    hits.append((pred_ab in next_los) or (pred_ba in next_los))
            else:
                hits.append(False)
                
        streak = 0
        for h in reversed(hits):
            if h: streak += 1
            else: break
            
        if streak >= min_streak:
            last_raw = days[-1]["raw"]
            
            p_idx_a, c_idx_a, lbl_a = node_a
            val_a_str = last_raw[p_idx_a] if p_idx_a < len(last_raw) else ""
            digit_a = val_a_str[c_idx_a] if val_a_str and len(val_a_str) >= abs(c_idx_a) and val_a_str[c_idx_a].isdigit() else ""
            
            p_idx_b, c_idx_b, lbl_b = node_b
            val_b_str = last_raw[p_idx_b] if p_idx_b < len(last_raw) else ""
            digit_b = val_b_str[c_idx_b] if val_b_str and len(val_b_str) >= abs(c_idx_b) and val_b_str[c_idx_b].isdigit() else ""
            
            p_ab, p_ba = (None, None)
            
            if method == "PASCAL":
                p_ab, p_ba = algo_pascal(val_a_str, val_b_str)
            elif method == "POSPAIR":
                if digit_a and digit_b:
                    p_ab, p_ba = digit_a + digit_b, digit_b + digit_a
            
            if p_ab:
                win_count = sum(hits)
                total_runs = len(hits)
                win_rate = (win_count / total_runs * 100) if total_runs > 0 else 0
                
                final_pred = ""
                if prediction_type == "BACH_THU":
                    final_pred = p_ab
                else:
                    final_pred = f"{p_ab} - {p_ba}"
                
                results.append({
                    "Vị trí": f"{lbl_a} - {lbl_b}",
                    "Kiểu": method,
                    "Streak": streak,
                    "Win Rate": f"{win_rate:.1f}% ({win_count}/{total_runs})",
                    "Dự đoán": final_pred,
                    "Raw_Pred": [p_ab] if prediction_type == "BACH_THU" else [p_ab, p_ba]
                })
                
    results.sort(key=lambda x: x["Streak"], reverse=True)
    return results

# ==== 4. LOGIC CẶP LÔ ĐI CÙNG ====
def scan_cap_lo_di_cung(target, region_filter, mode_count="day", progress_callback=None):
    urls_to_scan = []
    for name, info in ALL_STATIONS.items():
        if region_filter == "ALL" or info["region"] == region_filter:
            urls_to_scan.append((name, info["url"]))
    
    if not urls_to_scan:
        return None, "Không có đài nào thuộc khu vực này."

    co_counter = Counter()
    details_log = []
    total_stations = len(urls_to_scan)
    
    for idx, (station_name, url) in enumerate(urls_to_scan):
        if progress_callback:
            progress_callback(idx / total_stations, f"Đang quét {station_name}...")
            
        issues = fetch_data(url)
        for item in issues:
            raw = parse_detail(item.get("detail", "[]"))
            los_raw = [get_last2(x) for x in raw if get_last2(x)]
            
            if target in los_raw:
                others = [x for x in los_raw if x != target]
                
                if mode_count == "day":
                    unique_others = set(others)
                    co_counter.update(unique_others)
                    nums_str = ", ".join(sorted(unique_others))
                else:
                    co_counter.update(others)
                    nums_str = ", ".join(sorted(others))
                
                details_log.append({
                    "Ngày": item.get("turnNum"),
                    "Đài": station_name,
                    "Các số về cùng": nums_str
                })

    if progress_callback:
        progress_callback(1.0, "Hoàn tất!")

    if not details_log:
        return [], []

    freq_data = []
    for num, count in co_counter.most_common():
        freq_data.append({"Số đi cùng": num, "Số lần/ngày gặp": count})
        
    try:
        details_log.sort(key=lambda x: datetime.datetime.strptime(x["Ngày"], "%d/%m/%Y"), reverse=True)
    except:
        pass
        
    return freq_data, details_log

# ==== 5. CÁC CHỨC NĂNG SOI KHÁC ====

def get_lo_gan(url, limit=100):
    issues = fetch_data(url)
    if not issues: return []
    
    issues = issues[:limit]
    gan_stats = {f"{i:02d}": -1 for i in range(100)}
    
    for idx, item in enumerate(issues):
        raw = parse_detail(item.get("detail", "[]"))
        los = set([get_last2(s) for s in raw if get_last2(s)])
        
        for num in range(100):
            s_num = f"{num:02d}"
            if gan_stats[s_num] == -1:
                if s_num in los:
                    gan_stats[s_num] = idx
                    
    result = []
    for num in range(100):
        s_num = f"{num:02d}"
        days = gan_stats[s_num]
        if days == -1: days = limit
        result.append({"Số": s_num, "Số ngày chưa về": days})
        
    result.sort(key=lambda x: x["Số ngày chưa về"], reverse=True)
    return result

def get_bac_nho_next_day(url, target, limit=100):
    issues = fetch_data(url)
    if not issues: return [], []
    
    issues = issues[:limit][::-1]
    
    next_day_counts = Counter()
    log = []
    
    for i in range(len(issues) - 1):
        curr = issues[i]
        nxt = issues[i+1]
        
        curr_raw = parse_detail(curr.get("detail", "[]"))
        curr_los = set([get_last2(s) for s in curr_raw if get_last2(s)])
        
        if target in curr_los:
            nxt_raw = parse_detail(nxt.get("detail", "[]"))
            nxt_los = [get_last2(s) for s in nxt_raw if get_last2(s)]
            
            next_day_counts.update(nxt_los)
            log.append({
                "Ngày xuất hiện": curr.get("turnNum"),
                "Ngày hôm sau": nxt.get("turnNum"),
                "Kết quả hôm sau": ", ".join(sorted(set(nxt_los)))
            })
            
    freq = []
    for num, count in next_day_counts.most_common():
        freq.append({"Số": num, "Số lần xuất hiện": count})
        
    return freq, log

# ==== 6. LỊCH QUAY XỔ SỐ THEO NGÀY ====
DAY_STATIONS = {
    "Chủ nhật": [
        ("Miền Bắc", "Miền Bắc"),
        ("Miền Nam", "Đà Lạt"),
        ("Miền Nam", "Kiên Giang"),
        ("Miền Nam", "Tiền Giang"),
        ("Miền Trung", "Thừa Thiên Huế"),
        ("Miền Trung", "Khánh Hòa"),
        ("Miền Trung", "Kon Tum"),
    ],
    "Thứ 2": [
        ("Miền Bắc", "Miền Bắc"),
        ("Miền Nam", "Cà Mau"),
        ("Miền Nam", "Đồng Tháp"),
        ("Miền Nam", "Hồ Chí Minh"),
        ("Miền Trung", "Thừa Thiên Huế"),
        ("Miền Trung", "Phú Yên"),
    ],
    "Thứ 3": [
        ("Miền Bắc", "Miền Bắc"),
        ("Miền Nam", "Bạc Liêu"),
        ("Miền Nam", "Bến Tre"),
        ("Miền Nam", "Vũng Tàu"),
        ("Miền Trung", "Đắk Lắk"),
        ("Miền Trung", "Quảng Nam"),
    ],
    "Thứ 4": [
        ("Miền Bắc", "Miền Bắc"),
        ("Miền Nam", "Cần Thơ"),
        ("Miền Nam", "Đồng Nai"),
        ("Miền Nam", "Sóc Trăng"),
        ("Miền Trung", "Đà Nẵng"),
        ("Miền Trung", "Khánh Hòa"),
    ],
    "Thứ 5": [
        ("Miền Bắc", "Miền Bắc"),
        ("Miền Nam", "An Giang"),
        ("Miền Nam", "Bình Thuận"),
        ("Miền Nam", "Tây Ninh"),
        ("Miền Trung", "Bình Định"),
        ("Miền Trung", "Quảng Bình"),
        ("Miền Trung", "Quảng Trị"),
    ],
    "Thứ 6": [
        ("Miền Bắc", "Miền Bắc"),
        ("Miền Nam", "Bình Dương"),
        ("Miền Nam", "Trà Vinh"),
        ("Miền Nam", "Vĩnh Long"),
        ("Miền Trung", "Gia Lai"),
        ("Miền Trung", "Ninh Thuận"),
    ],
    "Thứ 7": [
        ("Miền Bắc", "Miền Bắc"),
        ("Miền Nam", "Bình Phước"),
        ("Miền Nam", "Hậu Giang"),
        ("Miền Nam", "Long An"),
        ("Miền Nam", "Hồ Chí Minh"),
        ("Miền Trung", "Đà Nẵng"),
        ("Miền Trung", "Đắk Nông"),
        ("Miền Trung", "Quảng Ngãi"),
    ],
}

def get_stations_by_day(day: str):
    return DAY_STATIONS.get(day, [])

# ==== 7. QUÉT TẤT CẢ ĐÀI THEO NGÀY ====
def scan_day_stations(day, limit=30, progress_callback=None):
    """Quét tất cả các đài của một ngày trong tuần và tổng hợp theo tần suất xuất hiện"""
    stations = get_stations_by_day(day)
    if not stations:
        return [], []
    
    number_counter = Counter()
    detail_logs = []
    total_stations = len(stations)
    total_draws = 0
    
    for idx, (region, station_name) in enumerate(stations):
        if progress_callback:
            progress_callback(idx / total_stations, f"Đang quét {station_name} ({region})...")
            
        if station_name not in ALL_STATIONS:
            continue
            
        url = ALL_STATIONS[station_name]["url"]
        issues = fetch_data(url)
        
        # Limit issues
        issues = issues[:limit]
        total_draws += len(issues)
        
        for item in issues:
            raw = parse_detail(item.get("detail", "[]"))
            los = [get_last2(x) for x in raw if get_last2(x)]
            
            # Count numbers
            number_counter.update(los)
            
            # Log detail
            detail_logs.append({
                "Ngày": item.get("turnNum"),
                "Đài": station_name,
                "Miền": region,
                "Kết quả": ", ".join(sorted(set(los)))
            })
            
    if progress_callback:
        progress_callback(1.0, "Hoàn tất!")
        
    # Format results
    freq_data = []
    for num, count in number_counter.most_common():
        freq_data.append({"Số": num, "Số lần xuất hiện": count})
        
    return freq_data, detail_logs
