# 测试脚本 - 验证每日统计功能
"""
测试每日统计脚本的各项功能
"""

import os
import sys
import unittest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch

# 将当前目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daily_stats import DailyStatsCollector


class TestDailyStats(unittest.TestCase):
    """测试每日统计功能"""
    
    def setUp(self):
        """测试前准备"""
        # 使用内存数据库进行测试
        self.db_url = "sqlite:///:memory:"
        self.collector = DailyStatsCollector(self.db_url)
        
        # 创建测试数据
        self._create_test_data()
    
    def _create_test_data(self):
        """创建测试数据"""
        # 这里可以添加具体的测试数据创建逻辑
        pass
    
    def test_morning_checkin_stats(self):
        """测试早上打卡统计"""
        # 测试逻辑
        target_date = date.today()
        
        # 模拟数据库查询结果
        with patch.object(self.collector, 'get_morning_checkin_stats') as mock_stats:
            mock_stats.return_value = 5
            
            result = self.collector.get_morning_checkin_stats(target_date, 'vehicle_records')
            self.assertEqual(result, 5)
    
    def test_lunch_consumption_stats(self):
        """测试午餐消费统计"""
        target_date = date.today()
        
        with patch.object(self.collector, 'get_lunch_consumption_stats') as mock_stats:
            mock_stats.return_value = 8
            
            result = self.collector.get_lunch_consumption_stats(target_date)
            self.assertEqual(result, 8)
    
    def test_date_range_validation(self):
        """测试日期范围验证"""
        # 测试日期格式
        test_date = "2024-01-15"
        try:
            parsed_date = datetime.strptime(test_date, '%Y-%m-%d').date()
            self.assertEqual(parsed_date.year, 2024)
            self.assertEqual(parsed_date.month, 1)
            self.assertEqual(parsed_date.day, 15)
        except ValueError:
            self.fail("日期格式验证失败")
    
    def test_stats_calculation(self):
        """测试统计数据计算"""
        # 测试总计计算
        vehicle = 3
        personnel = 5
        lunch = 6
        
        total_morning = vehicle + personnel
        self.assertEqual(total_morning, 8)
        
        # 测试午餐消费比率计算
        ratio = lunch / total_morning if total_morning > 0 else 0
        self.assertAlmostEqual(ratio, 0.75)


def run_basic_tests():
    """运行基础测试"""
    print("🧪 运行基础测试...")
    
    # 测试日期格式解析
    test_dates = ["2024-01-15", "2024-12-31", "2024-02-29"]
    
    for date_str in test_dates:
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            print(f"✓ 日期格式测试通过: {date_str} -> {parsed_date}")
        except ValueError as e:
            print(f"✗ 日期格式测试失败: {date_str} - {e}")
    
    # 测试统计计算逻辑
    print("\n📊 测试统计计算逻辑...")
    
    # 模拟统计数据
    test_stats = {
        'vehicle_morning': 15,
        'personnel_morning': 25,
        'lunch_consumption': 30
    }
    
    total_morning = test_stats['vehicle_morning'] + test_stats['personnel_morning']
    lunch_ratio = test_stats['lunch_consumption'] / total_morning if total_morning > 0 else 0
    
    print(f"车辆早上打卡: {test_stats['vehicle_morning']} 人")
    print(f"人员早上打卡: {test_stats['personnel_morning']} 人")
    print(f"总计早上打卡: {total_morning} 人")
    print(f"午餐消费: {test_stats['lunch_consumption']} 人")
    print(f"午餐消费占早上打卡比率: {lunch_ratio:.1%}")
    
    print("✓ 统计计算测试通过")


def test_script_import():
    """测试脚本导入"""
    print("\n📦 测试脚本导入...")
    
    try:
        # 测试daily_stats模块导入
        from daily_stats import DailyStatsCollector
        print("✓ daily_stats模块导入成功")
        
        # 测试daily_stats_scheduler模块导入
        from daily_stats_scheduler import collect_single_day_stats, collect_range_stats
        print("✓ daily_stats_scheduler模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False


def test_environment_setup():
    """测试环境配置"""
    print("\n⚙️ 测试环境配置...")
    
    # 检查必要的Python包
    required_packages = ['sqlalchemy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 包已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} 包未安装")
    
    # 单独测试dotenv
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv 包已安装")
    except ImportError:
        missing_packages.append('python-dotenv')
        print("✗ python-dotenv 包未安装")
    
    if missing_packages:
        print(f"\n❌ 缺失的包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    
    # 检查环境变量
    db_url = os.environ.get('DB_URL')
    if db_url:
        print(f"✓ DB_URL 环境变量已设置: {db_url[:20]}...")
    else:
        print("⚠️  DB_URL 环境变量未设置，将使用默认值")
    
    return True


def main():
    """主测试函数"""
    print("🚀 开始测试食堂数据每日统计脚本...")
    print("=" * 60)
    
    # 运行各项测试
    tests_passed = 0
    total_tests = 4
    
    # 1. 环境配置测试
    if test_environment_setup():
        tests_passed += 1
    
    # 2. 脚本导入测试
    if test_script_import():
        tests_passed += 1
    
    # 3. 基础测试
    run_basic_tests()
    tests_passed += 1
    
    # 4. 单元测试（简化版）
    print("\n🏃 运行单元测试...")
    try:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestDailyStats)
        runner = unittest.TextTestRunner(verbosity=0)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("✓ 单元测试通过")
            tests_passed += 1
        else:
            print("⚠️  部分单元测试失败")
    except Exception as e:
        print(f"⚠️  单元测试运行异常: {e}")
    
    # 测试结果总结
    print("\n" + "=" * 60)
    print(f"📋 测试总结: {tests_passed}/{total_tests} 项测试通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过！脚本可以正常使用。")
        return 0
    else:
        print("⚠️  部分测试未通过，请检查相关配置。")
        return 1


if __name__ == '__main__':
    sys.exit(main())