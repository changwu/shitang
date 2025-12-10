#!/usr/bin/env python3
"""
测试文件识别功能
"""

def determine_table_by_filename(filename: str) -> str:
    """
    根据文件名确定目标表
    文件名含有"consumelog"的excel文件对应食堂消费记录表"canteen_records"
    文件名含有"打卡明细数据"的excel文件对应车辆打卡记录表"vehicle_records" 
    文件名含有"dooreventinfo"的excel文件对应人员打卡记录表"door_records"
    """
    fname = filename.lower()
    
    if "consumelog" in fname:
        return "canteen_records"
    elif "打卡明细数据" in fname:
        return "vehicle_records"
    elif "dooreventinfo" in fname:
        return "door_records"
    else:
        return None


def test_file_recognition():
    """测试文件识别功能"""
    test_cases = [
        # 正确的文件名
        ("consumelog_20241210.xlsx", "canteen_records"),
        ("食堂消费记录_consumelog_20241210.xlsx", "canteen_records"),
        ("打卡明细数据_20241210.xlsx", "vehicle_records"),
        ("车辆打卡_打卡明细数据_20241210.xlsx", "vehicle_records"),
        ("dooreventinfo_20241210.xlsx", "door_records"),
        ("门禁事件_dooreventinfo_20241210.xlsx", "door_records"),
        
        # 不支持的文件名
        ("test_file.xlsx", None),
        ("data_20241210.xlsx", None),
        ("", None),
        
        # 大小写测试
        ("CONSUMELOG_20241210.xlsx", "canteen_records"),
        ("Consumelog_20241210.xlsx", "canteen_records"),
        ("DoOrEvEnTiNfO_20241210.xlsx", "door_records"),
    ]
    
    print("测试文件识别功能:")
    print("=" * 50)
    
    all_passed = True
    for filename, expected in test_cases:
        result = determine_table_by_filename(filename)
        status = "✅ 通过" if result == expected else "❌ 失败"
        if result != expected:
            all_passed = False
        expected_str = str(expected) if expected is not None else "None"
        result_str = str(result) if result is not None else "None"
        print(f"{status} | 文件名: {filename:<30} | 期望: {expected_str:<15} | 实际: {result_str}")
    
    print("=" * 50)
    if all_passed:
        print("🎉 所有测试用例都通过了!")
    else:
        print("⚠️  部分测试用例失败，请检查实现逻辑")
    
    return all_passed


if __name__ == "__main__":
    test_file_recognition()