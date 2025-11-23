import requests
import json
import pandas as pd
from collections import Counter
import datetime

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

# ==== 3. THUẬT TOÁN CẦU ====

def algo_pascal(s_a, s_b):
    base = (s_a or "") + (s_b or "")
    base = "".join([c for c in base if c.isdigit()])
    if len(base) < 2: return (None, None)
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
        
        url = ALL_STATIONS[station_name]["url"]
        issues = fetch_data(url)
        
        if not issues:
            continue
            
        for item in issues[:limit]:
            raw = parse_detail(item.get("detail", "[]"))
            los = [get_last2(x) for x in raw if get_last2(x)]
            
            number_counter.update(los)
            total_draws += 1
            
            detail_logs.append({
                "Ngày": item.get("turnNum"),
                "Đài": station_name,
                "Miền": region,
                "Các số về": ", ".join(sorted(set(los)))
            })
    
    if progress_callback:
        progress_callback(1.0, "Hoàn tất!")
    
    if not number_counter:
        return [], []
    
    freq_data = []
    for num in range(100):
        s_num = f"{num:02d}"
        count = number_counter.get(s_num, 0)
        percentage = (count / total_draws * 100) if total_draws > 0 else 0
        freq_data.append({
            "Số": s_num,
            "Số lần xuất hiện": count,
            "Tỷ lệ %": f"{percentage:.2f}%"
        })
    
    freq_data.sort(key=lambda x: x["Số lần xuất hiện"], reverse=True)
    
    try:
        detail_logs.sort(key=lambda x: datetime.datetime.strptime(x["Ngày"], "%d/%m/%Y"), reverse=True)
    except:
        pass
    
    return freq_data, detail_logs
