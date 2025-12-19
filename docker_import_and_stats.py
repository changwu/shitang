#!/usr/bin/env python3
"""
Docker环境中执行完整数据导入和统计收集的脚本
"""

import os
import sys
import subprocess
import logging
from datetime import datetime, date
from pathlib import Path

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def run_command(cmd, description):
    """运行shell命令"""
    logging.info(f"执行: {description}")
    logging.debug(f"命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"失败: {result.stderr}")
            return False
        else:
            if result.stdout:
                logging.info(f"输出: {result.stdout.strip()}")
            return True
    except Exception as e:
        logging.error(f"异常: {e}")
        return False

def import_excel_data():
    """导入Excel数据到数据库"""
    logging.info("开始导入Excel数据...")
    
    # 设置Docker环境变量
    os.environ['DB_URL'] = 'postgresql+psycopg2://postgres:postgres@db:5432/shitang'
    
    # 使用docker-compose运行导入脚本
    cmd = "docker-compose exec -T app python3 import_data.py --verbose"
    
    return run_command(cmd, "导入Excel数据")

def get_date_range_from_files():
    """从Excel文件中获取日期范围"""
    data_dir = Path("/home/changwu/work_home/shitang/data/import")
    
    if not data_dir.exists():
        logging.warning(f"数据目录不存在: {data_dir}")
        return None, None
    
    # 这里可以根据文件名或文件内容分析日期范围
    # 简化处理：返回一个合理的日期范围
    start_date = date(2024, 1, 1)  # 假设从2024年开始
    end_date = date.today() - timedelta(days=1)  # 到昨天
    
    logging.info(f"分析日期范围: {start_date} 到 {end_date}")
    return start_date, end_date

def collect_all_stats():
    """收集所有日期的统计数据"""
    logging.info("开始收集统计数据...")
    
    # 获取日期范围
    start_date, end_date = get_date_range_from_files()
    
    if not start_date or not end_date:
        logging.error("无法确定日期范围")
        return False
    
    # 使用docker-compose运行统计脚本
    cmd = f"docker-compose exec -T app python3 daily_stats_scheduler.py --start-date {start_date} --end-date {end_date} --verbose"
    
    return run_command(cmd, f"收集 {start_date} 到 {end_date} 的统计数据")

def verify_stats():
    """验证统计数据"""
    logging.info("验证统计数据...")
    
    # 查询统计表中的记录数
    queries = [
        ("vehicle_morning_stats", "车辆早上打卡统计"),
        ("personnel_morning_stats", "人员早上打卡统计"),
        ("lunch_consumption_stats", "午餐消费统计"),
        ("daily_summary_stats", "每日综合统计")
    ]
    
    for table, description in queries:
        cmd = f"docker-compose exec -T db psql -U postgres -d shitang -c 'SELECT COUNT(*) as {table}_count FROM {table};'"
        
        if not run_command(cmd, f"验证 {description}"):
            return False
    
    return True

def show_summary_stats():
    """显示统计汇总"""
    logging.info("显示统计汇总...")
    
    # 获取最近7天的统计汇总
    cmd = "docker-compose exec -T app python3 daily_stats_scheduler.py --summary --start-date $(date -d '7 days ago' +%Y-%m-%d) --end-date $(date -d 'yesterday' +%Y-%m-%d)"
    
    return run_command(cmd, "显示最近7天统计汇总")

def main():
    """主函数"""
    setup_logging()
    
    logging.info("🚀 开始Docker环境数据导入和统计收集任务")
    logging.info("=" * 60)
    
    # 步骤1: 导入Excel数据
    if not import_excel_data():
        logging.error("数据导入失败")
        return 1
    
    logging.info("✅ 数据导入完成")
    
    # 步骤2: 收集统计数据
    if not collect_all_stats():
        logging.error("统计数据收集失败")
        return 1
    
    logging.info("✅ 统计数据收集完成")
    
    # 步骤3: 验证统计数据
    if not verify_stats():
        logging.error("统计数据验证失败")
        return 1
    
    logging.info("✅ 统计数据验证完成")
    
    # 步骤4: 显示汇总信息
    show_summary_stats()
    
    logging.info("=" * 60)
    logging.info("🎉 所有任务执行完成！")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())