import requests
import json
import pandas as pd
from collections import Counter
import datetime

# ==== 1. DANH SÁCH API ĐẦY ĐỦ (MB, MN, MT) ====
# Cấu trúc: "Tên đài": {"url": "...", "region": "MB/MN/MT"}
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
        res = requests.get(url, timeout=5) # Timeout ngắn để ko treo
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

def scan_cau_dong(url, method="POSPAIR", depth=30, min_streak=2):
    issues = fetch_data(url)
    if not issues: return []
    issues = issues[:depth][::-1] 
    days = []
    for it in issues:
        raw = parse_detail(it.get("detail", "[]"))
        los = set([get_last2(s) for s in raw if get_last2(s)])
        days.append({"date": it.get("turnNum"), "raw": raw, "los": los})
    if len(days) < 2: return []

    limit_pos = min(len(days[-1]["raw"]), 20) 
    results = []
    for i in range(limit_pos):
        for j in range(i+1, limit_pos):
            hits = []
            for k in range(len(days)-1):
                curr_raw = days[k]["raw"]
                next_los = days[k+1]["los"]
                val_a = curr_raw[i] if i < len(curr_raw) else ""
                val_b = curr_raw[j] if j < len(curr_raw) else ""
                pred_ab, pred_ba = (None, None)
                if method == "PASCAL":
                    pred_ab, pred_ba = algo_pascal(val_a, val_b)
                else: # POSPAIR
                    digit_a = val_a[-1] if val_a and val_a[-1].isdigit() else None
                    digit_b = val_b[-1] if val_b and val_b[-1].isdigit() else None
                    if digit_a and digit_b:
                        pred_ab, pred_ba = digit_a + digit_b, digit_b + digit_a
                if pred_ab:
                    hits.append((pred_ab in next_los) or (pred_ba in next_los))
                else:
                    hits.append(False)
            streak = 0
            for h in reversed(hits):
                if h: streak += 1
                else: break
            if streak >= min_streak:
                last_raw = days[-1]["raw"]
                v_a = last_raw[i] if i < len(last_raw) else ""
                v_b = last_raw[j] if j < len(last_raw) else ""
                p_ab, p_ba = (None, None)
                if method == "PASCAL":
                    p_ab, p_ba = algo_pascal(v_a, v_b)
                elif method == "POSPAIR":
                    da = v_a[-1] if v_a and v_a[-1].isdigit() else ""
                    db = v_b[-1] if v_b and v_b[-1].isdigit() else ""
                    if da and db: p_ab, p_ba = da+db, db+da
                if p_ab:
                    win_count = sum(hits)
                    total_runs = len(hits)
                    win_rate = (win_count / total_runs * 100) if total_runs > 0 else 0
                    
                    results.append({
                        "Vị trí": f"Pos {i} - Pos {j}",
                        "Kiểu": method,
                        "Streak": streak,
                        "Win Rate": f"{win_rate:.1f}% ({win_count}/{total_runs})",
                        "Dự đoán": f"{p_ab} - {p_ba}"
                    })
    results.sort(key=lambda x: x["Streak"], reverse=True)
    return results

# ==== 4. LOGIC CẶP LÔ ĐI CÙNG (MỚI) ====
def scan_cap_lo_di_cung(target, region_filter, mode_count="day", progress_callback=None):
    """
    target: Số cần tìm (ví dụ "68")
    region_filter: "MB", "MN", "MT", "ALL"
    mode_count: "day" (đếm số ngày trùng) hoặc "hit" (đếm tổng số lần xuất hiện)
    """
    # 1. Lọc danh sách URL cần quét
    urls_to_scan = []
    for name, info in ALL_STATIONS.items():
        if region_filter == "ALL" or info["region"] == region_filter:
            urls_to_scan.append((name, info["url"]))
    
    if not urls_to_scan:
        return None, "Không có đài nào thuộc khu vực này."

    co_counter = Counter()
    details_log = []
    
    total_stations = len(urls_to_scan)
    
    # 2. Quét từng đài
    for idx, (station_name, url) in enumerate(urls_to_scan):
        if progress_callback:
            progress_callback(idx / total_stations, f"Đang quét {station_name}...")
            
        issues = fetch_data(url)
        for item in issues:
            raw = parse_detail(item.get("detail", "[]"))
            # Lấy danh sách lô 2 số trong kỳ quay này
            los_raw = [get_last2(x) for x in raw if get_last2(x)]
            
            if target in los_raw:
                # Tìm thấy target trong kỳ này
                
                # Lọc ra các số đi cùng (trừ chính nó)
                others = [x for x in los_raw if x != target]
                
                if mode_count == "day":
                    # Chế độ 'day': Mỗi số chỉ đếm 1 lần mỗi ngày (dùng set)
                    unique_others = set(others)
                    co_counter.update(unique_others)
                    nums_str = ", ".join(sorted(unique_others))
                else:
                    # Chế độ 'hit': Đếm tất cả (bao gồm nháy)
                    co_counter.update(others)
                    nums_str = ", ".join(sorted(others))
                
                details_log.append({
                    "Ngày": item.get("turnNum"),
                    "Đài": station_name,
                    "Các số về cùng": nums_str
                })

    if progress_callback:
        progress_callback(1.0, "Hoàn tất!")

    # 3. Tổng hợp kết quả
    if not details_log:
        return [], []

    # Bảng tần suất
    freq_data = []
    for num, count in co_counter.most_common():
        freq_data.append({"Số đi cùng": num, "Số lần/ngày gặp": count})
        
    # Sắp xếp log chi tiết theo ngày mới nhất
    try:
        details_log.sort(key=lambda x: datetime.datetime.strptime(x["Ngày"], "%d/%m/%Y"), reverse=True)
    except:
        pass
        
    return freq_data, details_log

# ==== 5. CÁC CHỨC NĂNG SOI KHÁC (MỚI) ====

def get_lo_gan(url, limit=100):
    """Thống kê lô gan (số ngày chưa về)"""
    issues = fetch_data(url)
    if not issues: return []
    
    # issues là list từ Mới -> Cũ
    issues = issues[:limit]
    gan_stats = {f"{i:02d}": -1 for i in range(100)}
    
    for idx, item in enumerate(issues):
        raw = parse_detail(item.get("detail", "[]"))
        los = set([get_last2(s) for s in raw if get_last2(s)])
        
        for num in range(100):
            s_num = f"{num:02d}"
            if gan_stats[s_num] == -1: # Chưa thấy
                if s_num in los:
                    gan_stats[s_num] = idx # idx chính là số ngày cách đây (0 = hôm nay)
                    
    result = []
    for num in range(100):
        s_num = f"{num:02d}"
        days = gan_stats[s_num]
        if days == -1: days = limit # Chưa về trong limit ngày
        result.append({"Số": s_num, "Số ngày chưa về": days})
        
    result.sort(key=lambda x: x["Số ngày chưa về"], reverse=True)
    return result

def get_bac_nho_next_day(url, target, limit=100):
    """Bạc nhớ: Tìm các số hay về ngày hôm sau khi ngày hôm trước có target"""
    issues = fetch_data(url)
    if not issues: return [], []
    
    # Cần duyệt theo thời gian Cũ -> Mới để xem "hôm sau"
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
