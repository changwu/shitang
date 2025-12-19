#!/usr/bin/env python3
"""
食堂数据每日统计脚本
用于统计每天车辆、人员表中在9点前打卡人数，和午餐消费人数
"""

import os
import argparse
import logging
from datetime import datetime, date, time
from typing import Dict, List, Optional

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Date, DateTime, Text
from sqlalchemy.sql import func, select, insert, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from dotenv import load_dotenv


class DailyStatsCollector:
    """每日统计数据收集器"""
    
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, future=True)
        self.metadata = MetaData()
        self.metadata.bind = self.engine
        
        # 定义统计表结构
        self._define_tables()
    
    def _define_tables(self):
        """定义统计表结构"""
        # 原始数据表
        self.vehicle_records = Table(
            'vehicle_records', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('record_date', DateTime(timezone=True)),
            Column('name', Text),
            Column('type', Text),
            extend_existing=True
        )
        
        self.door_records = Table(
            'door_records', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('record_date', DateTime(timezone=True)),
            Column('name', Text),
            Column('type', Text),
            extend_existing=True
        )
        
        self.canteen_records = Table(
            'canteen_records', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('record_date', DateTime(timezone=True)),
            Column('name', Text),
            Column('type', Text),
            extend_existing=True
        )
        
        # 统计表
        self.vehicle_morning_stats = Table(
            'vehicle_morning_stats', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('stat_date', Date),
            Column('morning_checkin_count', Integer, default=0),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), server_default=func.now()),
            extend_existing=True
        )
        
        self.personnel_morning_stats = Table(
            'personnel_morning_stats', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('stat_date', Date),
            Column('morning_checkin_count', Integer, default=0),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), server_default=func.now()),
            extend_existing=True
        )
        
        self.lunch_consumption_stats = Table(
            'lunch_consumption_stats', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('stat_date', Date),
            Column('lunch_consumption_count', Integer, default=0),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), server_default=func.now()),
            extend_existing=True
        )
        
        self.daily_summary_stats = Table(
            'daily_summary_stats', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('stat_date', Date),
            Column('vehicle_morning_count', Integer, default=0),
            Column('personnel_morning_count', Integer, default=0),
            Column('lunch_consumption_count', Integer, default=0),
            Column('total_morning_count', Integer, default=0),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), server_default=func.now()),
            extend_existing=True
        )
    
    def get_morning_checkin_stats(self, target_date: date, table_name: str) -> int:
        """获取指定日期的早上9点前打卡统计
        
        Args:
            target_date: 目标日期
            table_name: 表名 ('vehicle_records' 或 'door_records')
        
        Returns:
            9点前打卡人数（按姓名去重）
        """
        table = self.vehicle_records if table_name == 'vehicle_records' else self.door_records
        
        # 定义早上9点的时间边界
        morning_start = datetime.combine(target_date, time(0, 0, 0))
        morning_end = datetime.combine(target_date, time(9, 0, 0))
        
        query = select(
            func.count(func.distinct(table.c.name))
        ).where(
            func.date(table.c.record_date) == target_date,
            table.c.record_date >= morning_start,
            table.c.record_date < morning_end
        )
        
        with self.engine.connect() as conn:
            result = conn.execute(query)
            count = result.scalar()
            return count if count else 0
    
    def get_lunch_consumption_stats(self, target_date: date) -> int:
        """获取指定日期的午餐消费统计
        
        Args:
            target_date: 目标日期
        
        Returns:
            午餐消费人数（按姓名去重）
        """
        # 定义午餐时间范围（11:00-14:00）
        lunch_start = datetime.combine(target_date, time(11, 0, 0))
        lunch_end = datetime.combine(target_date, time(14, 0, 0))
        
        query = select(
            func.count(func.distinct(self.canteen_records.c.name))
        ).where(
            func.date(self.canteen_records.c.record_date) == target_date,
            self.canteen_records.c.record_date >= lunch_start,
            self.canteen_records.c.record_date < lunch_end,
            self.canteen_records.c.type.ilike('%午餐%')  # 包含午餐的餐别
        )
        
        with self.engine.connect() as conn:
            result = conn.execute(query)
            count = result.scalar()
            return count if count else 0
    
    def save_stats_to_db(self, target_date: date, stats: Dict[str, int]) -> None:
        """保存统计数据到数据库
        
        Args:
            target_date: 统计日期
            stats: 统计数据字典
        """
        with self.engine.begin() as conn:
            # 保存车辆早上打卡统计
            if 'vehicle_morning' in stats:
                vehicle_stmt = pg_insert(self.vehicle_morning_stats).values(
                    stat_date=target_date,
                    morning_checkin_count=stats['vehicle_morning']
                ).on_conflict_do_update(
                    index_elements=['stat_date'],
                    set_={'morning_checkin_count': stats['vehicle_morning']}
                )
                conn.execute(vehicle_stmt)
            
            # 保存人员早上打卡统计
            if 'personnel_morning' in stats:
                personnel_stmt = pg_insert(self.personnel_morning_stats).values(
                    stat_date=target_date,
                    morning_checkin_count=stats['personnel_morning']
                ).on_conflict_do_update(
                    index_elements=['stat_date'],
                    set_={'morning_checkin_count': stats['personnel_morning']}
                )
                conn.execute(personnel_stmt)
            
            # 保存午餐消费统计
            if 'lunch_consumption' in stats:
                lunch_stmt = pg_insert(self.lunch_consumption_stats).values(
                    stat_date=target_date,
                    lunch_consumption_count=stats['lunch_consumption']
                ).on_conflict_do_update(
                    index_elements=['stat_date'],
                    set_={'lunch_consumption_count': stats['lunch_consumption']}
                )
                conn.execute(lunch_stmt)
            
            # 保存综合统计
            if all(k in stats for k in ['vehicle_morning', 'personnel_morning', 'lunch_consumption']):
                total_morning = stats['vehicle_morning'] + stats['personnel_morning']
                summary_stmt = pg_insert(self.daily_summary_stats).values(
                    stat_date=target_date,
                    vehicle_morning_count=stats['vehicle_morning'],
                    personnel_morning_count=stats['personnel_morning'],
                    lunch_consumption_count=stats['lunch_consumption'],
                    total_morning_count=total_morning
                ).on_conflict_do_update(
                    index_elements=['stat_date'],
                    set_={
                        'vehicle_morning_count': stats['vehicle_morning'],
                        'personnel_morning_count': stats['personnel_morning'],
                        'lunch_consumption_count': stats['lunch_consumption'],
                        'total_morning_count': total_morning
                    }
                )
                conn.execute(summary_stmt)
    
    def collect_daily_stats(self, target_date: date, verbose: bool = False) -> Dict[str, int]:
        """收集指定日期的统计数据
        
        Args:
            target_date: 统计日期
            verbose: 是否显示详细信息
        
        Returns:
            统计数据字典
        """
        if verbose:
            logging.info(f"开始收集 {target_date} 的统计数据...")
        
        # 收集各项统计数据
        vehicle_morning = self.get_morning_checkin_stats(target_date, 'vehicle_records')
        personnel_morning = self.get_morning_checkin_stats(target_date, 'door_records')
        lunch_consumption = self.get_lunch_consumption_stats(target_date)
        
        stats = {
            'vehicle_morning': vehicle_morning,
            'personnel_morning': personnel_morning,
            'lunch_consumption': lunch_consumption
        }
        
        if verbose:
            logging.info(f"车辆早上打卡人数: {vehicle_morning}")
            logging.info(f"人员早上打卡人数: {personnel_morning}")
            logging.info(f"午餐消费人数: {lunch_consumption}")
            logging.info(f"总计早上打卡人数: {vehicle_morning + personnel_morning}")
        
        return stats
    
    def get_stats_summary(self, start_date: date, end_date: date) -> List[Dict]:
        """获取指定日期范围的统计汇总
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            统计汇总列表
        """
        query = select(
            self.daily_summary_stats.c.stat_date,
            self.daily_summary_stats.c.vehicle_morning_count,
            self.daily_summary_stats.c.personnel_morning_count,
            self.daily_summary_stats.c.lunch_consumption_count,
            self.daily_summary_stats.c.total_morning_count
        ).where(
            self.daily_summary_stats.c.stat_date >= start_date,
            self.daily_summary_stats.c.stat_date <= end_date
        ).order_by(self.daily_summary_stats.c.stat_date)
        
        with self.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
            
            summary = []
            for row in rows:
                summary.append({
                    'date': row.stat_date,
                    'vehicle_morning': row.vehicle_morning_count,
                    'personnel_morning': row.personnel_morning_count,
                    'lunch_consumption': row.lunch_consumption_count,
                    'total_morning': row.total_morning_count
                })
            
            return summary


def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='食堂数据每日统计脚本')
    parser.add_argument('--db-url', default=os.environ.get('DB_URL', 'postgresql+psycopg2://postgres:postgres@localhost:5432/shitang'))
    parser.add_argument('--date', help='统计日期 (YYYY-MM-DD)，默认为昨天')
    parser.add_argument('--start-date', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--summary', action='store_true', help='显示统计汇总')
    parser.add_argument('--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    collector = DailyStatsCollector(args.db_url)
    
    if args.summary and args.start_date and args.end_date:
        # 显示统计汇总
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        
        summary = collector.get_stats_summary(start_date, end_date)
        
        print(f"\n统计汇总 ({start_date} 至 {end_date}):")
        print("-" * 80)
        print(f"{'日期':<12} {'车辆打卡':<8} {'人员打卡':<8} {'午餐消费':<8} {'总计':<8}")
        print("-" * 80)
        
        total_vehicle = total_personnel = total_lunch = total_all = 0
        for stat in summary:
            print(f"{stat['date']:<12} {stat['vehicle_morning']:<8} {stat['personnel_morning']:<8} "
                  f"{stat['lunch_consumption']:<8} {stat['total_morning']:<8}")
            total_vehicle += stat['vehicle_morning']
            total_personnel += stat['personnel_morning']
            total_lunch += stat['lunch_consumption']
            total_all += stat['total_morning']
        
        print("-" * 80)
        print(f"{'总计':<12} {total_vehicle:<8} {total_personnel:<8} {total_lunch:<8} {total_all:<8}")
        
    else:
        # 收集并保存统计数据
        if args.date:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        else:
            # 默认为昨天
            target_date = date.today() - timedelta(days=1)
        
        # 收集统计数据
        stats = collector.collect_daily_stats(target_date, args.verbose)
        
        # 保存到数据库
        collector.save_stats_to_db(target_date, stats)
        
        if args.verbose:
            logging.info(f"统计数据已保存到数据库: {target_date}")


if __name__ == '__main__':
    from datetime import timedelta
    main()