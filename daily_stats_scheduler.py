#!/usr/bin/env python3
"""
食堂数据自动统计调度脚本
用于定期执行每日统计数据收集
"""

import os
import sys
import argparse
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional

# 将当前目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daily_stats import DailyStatsCollector


def setup_logging(verbose: bool = False):
    """设置日志配置"""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def collect_single_day_stats(collector: DailyStatsCollector, target_date: date, verbose: bool = False) -> bool:
    """收集单日统计数据
    
    Args:
        collector: 数据收集器实例
        target_date: 目标日期
        verbose: 是否显示详细信息
    
    Returns:
        是否成功
    """
    try:
        if verbose:
            logging.info(f"开始收集 {target_date} 的统计数据...")
        
        # 收集统计数据
        stats = collector.collect_daily_stats(target_date, verbose)
        
        # 保存到数据库
        collector.save_stats_to_db(target_date, stats)
        
        if verbose:
            logging.info(f"✓ {target_date} 统计数据收集完成")
            logging.info(f"  - 车辆早上打卡: {stats['vehicle_morning']} 人")
            logging.info(f"  - 人员早上打卡: {stats['personnel_morning']} 人")
            logging.info(f"  - 午餐消费: {stats['lunch_consumption']} 人")
            logging.info(f"  - 总计早上打卡: {stats['vehicle_morning'] + stats['personnel_morning']} 人")
        
        return True
        
    except Exception as e:
        logging.error(f"收集 {target_date} 统计数据失败: {e}")
        return False


def collect_range_stats(collector: DailyStatsCollector, start_date: date, end_date: date, verbose: bool = False) -> dict:
    """收集日期范围统计数据
    
    Args:
        collector: 数据收集器实例
        start_date: 开始日期
        end_date: 结束日期
        verbose: 是否显示详细信息
    
    Returns:
        统计结果字典
    """
    success_count = 0
    failed_dates = []
    
    current_date = start_date
    while current_date <= end_date:
        if collect_single_day_stats(collector, current_date, verbose):
            success_count += 1
        else:
            failed_dates.append(current_date)
        
        current_date += timedelta(days=1)
    
    return {
        'success_count': success_count,
        'failed_count': len(failed_dates),
        'failed_dates': failed_dates,
        'total_days': (end_date - start_date).days + 1
    }


def show_statistics_summary(collector: DailyStatsCollector, start_date: date, end_date: date):
    """显示统计汇总信息"""
    summary = collector.get_stats_summary(start_date, end_date)
    
    if not summary:
        print(f"\n在 {start_date} 至 {end_date} 范围内没有找到统计数据")
        return
    
    print(f"\n📊 统计汇总 ({start_date} 至 {end_date}):")
    print("=" * 90)
    print(f"{'日期':<12} {'车辆打卡':<10} {'人员打卡':<10} {'午餐消费':<10} {'总计':<10} {'比率':<10}")
    print("-" * 90)
    
    total_vehicle = total_personnel = total_lunch = total_all = 0
    
    for stat in summary:
        date_str = stat['date'].strftime('%Y-%m-%d')
        vehicle = stat['vehicle_morning']
        personnel = stat['personnel_morning']
        lunch = stat['lunch_consumption']
        total_morning = stat['total_morning']
        
        # 计算午餐消费占早上打卡人数的比率
        ratio = f"{lunch/total_morning*100:.1f}%" if total_morning > 0 else "0%"
        
        print(f"{date_str:<12} {vehicle:<10} {personnel:<10} {lunch:<10} {total_morning:<10} {ratio:<10}")
        
        total_vehicle += vehicle
        total_personnel += personnel
        total_lunch += lunch
        total_all += total_morning
    
    print("-" * 90)
    print(f"{'总计'::<12} {total_vehicle:<10} {total_personnel:<10} {total_lunch:<10} {total_all:<10} {'':<10}")
    
    if total_all > 0:
        overall_ratio = total_lunch / total_all * 100
        print(f"\n📈 整体统计:")
        print(f"  - 平均每日早上打卡人数: {total_all/len(summary):.1f} 人")
        print(f"  - 平均每日午餐消费人数: {total_lunch/len(summary):.1f} 人")
        print(f"  - 午餐消费占早上打卡比率: {overall_ratio:.1f}%")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='食堂数据自动统计调度脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 统计昨天的数据
  python daily_stats_scheduler.py
  
  # 统计指定日期的数据
  python daily_stats_scheduler.py --date 2024-01-15
  
  # 统计日期范围的数据
  python daily_stats_scheduler.py --start-date 2024-01-01 --end-date 2024-01-31
  
  # 显示统计汇总
  python daily_stats_scheduler.py --summary --start-date 2024-01-01 --end-date 2024-01-31
  
  # 显示详细信息
  python daily_stats_scheduler.py --date 2024-01-15 --verbose
        """
    )
    
    parser.add_argument('--db-url', 
                       default=os.environ.get('DB_URL', 'postgresql+psycopg2://postgres:postgres@localhost:5432/shitang'),
                       help='数据库连接URL')
    
    parser.add_argument('--date', 
                       help='统计指定日期 (YYYY-MM-DD)，默认为昨天')
    
    parser.add_argument('--start-date', 
                       help='开始日期 (YYYY-MM-DD)')
    
    parser.add_argument('--end-date', 
                       help='结束日期 (YYYY-MM-DD)')
    
    parser.add_argument('--summary', 
                       action='store_true',
                       help='显示统计汇总信息')
    
    parser.add_argument('--verbose', 
                       action='store_true',
                       help='显示详细执行信息')
    
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='试运行模式，不保存数据到数据库')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    try:
        # 创建数据收集器
        collector = DailyStatsCollector(args.db_url)
        
        if args.summary:
            # 显示统计汇总
            if not args.start_date or not args.end_date:
                print("错误: 使用 --summary 时必须指定 --start-date 和 --end-date")
                return 1
            
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
            show_statistics_summary(collector, start_date, end_date)
            
        elif args.start_date and args.end_date:
            # 统计日期范围
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
            
            if args.verbose:
                logging.info(f"开始统计日期范围: {start_date} 至 {end_date}")
            
            result = collect_range_stats(collector, start_date, end_date, args.verbose)
            
            print(f"\n📅 统计完成:")
            print(f"  - 成功处理: {result['success_count']}/{result['total_days']} 天")
            print(f"  - 失败: {result['failed_count']} 天")
            
            if result['failed_dates']:
                print(f"  - 失败日期: {', '.join(str(d) for d in result['failed_dates'])}")
            
            if result['failed_count'] > 0:
                return 1
                
        elif args.date:
            # 统计指定日期
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
            
            if args.verbose:
                logging.info(f"开始统计指定日期: {target_date}")
            
            if not collect_single_day_stats(collector, target_date, args.verbose):
                return 1
                
        else:
            # 默认为昨天
            yesterday = date.today() - timedelta(days=1)
            
            if args.verbose:
                logging.info(f"开始统计昨天数据: {yesterday}")
            
            if not collect_single_day_stats(collector, yesterday, args.verbose):
                return 1
        
        return 0
        
    except Exception as e:
        logging.error(f"执行失败: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())