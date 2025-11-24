# ==== ADDITIONAL FUNCTIONS TO ADD TO utils.py ====
# Add these functions at the end of utils.py

def get_stations_by_region_and_day(region, day):
    """Lấy danh sách các đài theo miền và ngày
    
    Args:
        region: "MB", "MN", "MT", or "ALL"
        day: Ngày trong tuần (e.g., "Thứ 2", "Chủ nhật")
    
    Returns:
        List of station names
    """
    stations = get_stations_by_day(day)
    if not stations:
        return []
    
    if region == "ALL":
        return [station_name for _, station_name in stations]
    
    # Map region code to display name
    region_map = {"MB": "Miền Bắc", "MN": "Miền Nam", "MT": "Miền Trung"}
    region_display = region_map.get(region, region)
    
    filtered_stations = []
    for r, station_name in stations:
        if r == region_display:
            filtered_stations.append(station_name)
    
    return filtered_stations

def scan_region_by_day_with_methods(region, day, methods=["POSPAIR", "PASCAL"], 
                                    min_streak=2, depth=30, progress_callback=None):
    """Quét tất cả các đài của một miền trong một ngày với các phương pháp dự đoán
    
    Args:
        region: "MB", "MN", "MT", or "ALL"
        day: Ngày trong tuần
        methods: Danh sách các phương pháp ["POSPAIR", "PASCAL"]
        min_streak: Chuỗi tối thiểu
        depth: Số kỳ quét
        progress_callback: Hàm callback để cập nhật tiến độ
    
    Returns:
        prediction_summary: Dict with frequency groups of predictions
        station_details: List of all predictions by station
        total_stats: Dict with total statistics
    """
    stations = get_stations_by_region_and_day(region, day)
    if not stations:
        return {}, [], {"total_stations": 0, "total_predictions": 0}
    
    all_predictions = []  # All predicted numbers from all cầu
    station_details = []  # Detailed results per station
    total_predictions = 0
    
    total_stations = len(stations)
    total_tasks = total_stations * len(methods)
    current_task = 0
    
    for station_name in stations:
        if station_name not in ALL_STATIONS:
            continue
        
        url = ALL_STATIONS[station_name]["url"]
        station_results = {
            "station": station_name,
            "methods": {},
            "total_cau": 0
        }
        
        for method in methods:
            current_task += 1
            if progress_callback:
                progress_callback(
                    current_task / total_tasks, 
                    f"Đang quét {station_name} - Phương pháp {method}..."
                )
            
            # Run the appropriate scanning method
            results = []
            if method == "POSPAIR":
                results = scan_cau_dong(
                    url, 
                    method="POSPAIR", 
                    depth=depth,
                    min_streak=min_streak,
                    position_pairs=None,  # Auto scan all positions
                    use_last=True,
                    use_near_last=False,
                    prediction_type="SONG_THU"
                )
            elif method == "PASCAL":
                results = scan_cau_dong(
                    url, 
                    method="PASCAL", 
                    depth=depth,
                    min_streak=min_streak,
                    position_pairs=None,
                    use_last=True,
                    use_near_last=False,
                    prediction_type="SONG_THU"
                )
            
            # Extract predictions
            method_predictions = []
            if results:
                for r in results:
                    if "Raw_Pred" in r:
                        method_predictions.extend(r["Raw_Pred"])
                        all_predictions.extend(r["Raw_Pred"])
                
                station_results["methods"][method] = {
                    "count": len(results),
                    "predictions": method_predictions
                }
                station_results["total_cau"] += len(results)
                total_predictions += len(results)
        
        if station_results["total_cau"] > 0:
            station_details.append(station_results)
    
    if progress_callback:
        progress_callback(1.0, "Hoàn tất!")
    
    # Aggregate predictions by frequency
    from collections import Counter
    pred_counter = Counter(all_predictions)
    
    # Group by frequency level
    freq_groups = {}
    for num, count in pred_counter.items():
        if count not in freq_groups:
            freq_groups[count] = []
        freq_groups[count].append(num)
    
    # Sort frequency groups
    prediction_summary = {}
    for count in sorted(freq_groups.keys(), reverse=True):
        nums = sorted(freq_groups[count])
        prediction_summary[count] = {
            "level": f"{count} cầu",
            "numbers": nums,
            "total_numbers": len(nums)
        }
    
    total_stats = {
        "total_stations": len(station_details),
        "total_predictions": total_predictions,
        "unique_numbers": len(pred_counter)
    }
    
    return prediction_summary, station_details, total_stats
