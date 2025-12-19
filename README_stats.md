# 食堂数据每日统计系统

## 功能说明

本系统用于自动统计食堂相关数据，包括：
- 车辆早上9点前打卡人数统计
- 人员早上9点前打卡人数统计  
- 午餐时段消费人数统计

## 文件结构

```
shitang/
├── import_data.py              # 原始数据导入脚本（现有）
├── daily_stats.py              # 核心统计脚本
├── daily_stats_scheduler.py     # 统计调度脚本
├── daily_stats.sh              # 简化版shell调用脚本
├── daily_stats_schema.sql      # 数据库表结构
└── README_stats.md             # 本说明文档
```

## 数据库表结构

### 统计表

1. **vehicle_morning_stats** - 车辆早上打卡统计
   - `stat_date`: 统计日期
   - `morning_checkin_count`: 早上打卡人数

2. **personnel_morning_stats** - 人员早上打卡统计  
   - `stat_date`: 统计日期
   - `morning_checkin_count`: 早上打卡人数

3. **lunch_consumption_stats** - 午餐消费统计
   - `stat_date`: 统计日期
   - `lunch_consumption_count`: 午餐消费人数

4. **daily_summary_stats** - 每日综合统计汇总
   - `stat_date`: 统计日期
   - `vehicle_morning_count`: 车辆早上打卡人数
   - `personnel_morning_count`: 人员早上打卡人数
   - `lunch_consumption_count`: 午餐消费人数
   - `total_morning_count`: 总计早上打卡人数

## 使用方法

### 1. 创建数据库表

```bash
# 使用psql或其他数据库客户端执行SQL脚本
psql -d shitang -f daily_stats_schema.sql
```

### 2. 执行统计任务

#### 方式1：使用Shell脚本（推荐）

```bash
# 统计昨天数据（默认）
./daily_stats.sh

# 统计指定日期
./daily_stats.sh -d 2024-01-15

# 统计日期范围
./daily_stats.sh -s 2024-01-01 -e 2024-01-31

# 显示统计汇总
./daily_stats.sh --summary -s 2024-01-01 -e 2024-01-31

# 显示详细信息
./daily_stats.sh -d 2024-01-15 -v
```

#### 方式2：使用Python脚本

```bash
# 统计昨天数据（默认）
python3 daily_stats_scheduler.py

# 统计指定日期
python3 daily_stats_scheduler.py --date 2024-01-15

# 统计日期范围
python3 daily_stats_scheduler.py --start-date 2024-01-01 --end-date 2024-01-31

# 显示统计汇总
python3 daily_stats_scheduler.py --summary --start-date 2024-01-01 --end-date 2024-01-31
```

### 3. 定时任务设置

可以将统计脚本添加到crontab中，实现自动每日统计：

```bash
# 编辑crontab
crontab -e

# 添加以下内容（每天早上6点执行前一天统计）
0 6 * * * cd /path/to/shitang && ./daily_stats.sh >> /var/log/shitang_stats.log 2>&1
```

## 统计规则说明

### 早上打卡统计
- **时间范围**: 当日00:00-09:00
- **统计方式**: 按姓名去重计数
- **数据来源**: 
  - 车辆打卡数据：`vehicle_records`表
  - 人员打卡数据：`door_records`表

### 午餐消费统计
- **时间范围**: 当日11:00-14:00
- **餐别筛选**: 餐别字段包含"午餐"
- **统计方式**: 按姓名去重计数
- **数据来源**: `canteen_records`表

## 环境配置

确保设置正确的数据库连接：

```bash
# 在.env文件中配置或设置环境变量
export DB_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/shitang"
```

## 依赖安装

```bash
# 安装Python依赖
pip install sqlalchemy psycopg2-binary python-dotenv
```

## 故障排查

### 常见问题

1. **数据库连接失败**
   - 检查数据库URL配置
   - 确认PostgreSQL服务运行正常
   - 验证数据库和表是否存在

2. **统计数据为0**
   - 检查原始数据是否已导入
   - 确认数据时间范围是否正确
   - 验证数据格式和字段映射

3. **权限错误**
   - 确保数据库用户有读写权限
   - 检查表结构是否正确创建

### 日志查看

使用`-v`或`--verbose`参数可以查看详细的执行日志：

```bash
./daily_stats.sh -d 2024-01-15 -v
```

## 扩展功能

可以根据需要扩展以下功能：
- 添加更多时间段统计
- 增加部门维度的统计
- 生成图表和报表
- 添加数据导出功能
- 集成邮件通知