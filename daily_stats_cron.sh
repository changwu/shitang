#!/bin/bash
# Docker容器中执行的每日统计脚本
# 该脚本由cron定时任务调用，每天9:10执行

# 设置日志文件
LOG_FILE="/var/log/daily_stats.log"

# 记录开始时间
echo "==================================" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始执行每日统计任务" >> "$LOG_FILE"

# 切换到应用目录
cd /app

# 设置环境变量
export DB_URL="postgresql+psycopg2://postgres:postgres@db:5432/shitang"
export DATA_DIR="/app/data"
export IMPORT_DIR="import/"

# 执行昨天的统计（因为通常统计前一天完整的数据）
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始统计昨天的数据..." >> "$LOG_FILE"

if python3 daily_stats_scheduler.py --verbose >> "$LOG_FILE" 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ 昨日统计任务执行成功" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ❌ 昨日统计任务执行失败" >> "$LOG_FILE"
    exit 1
fi

# 可选：显示最近7天的统计汇总
echo "" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 最近7天统计汇总：" >> "$LOG_FILE"

# 计算日期范围
end_date=$(date -d 'yesterday' +%Y-%m-%d)
start_date=$(date -d '7 days ago' +%Y-%m-%d)

if python3 daily_stats_scheduler.py --summary --start-date "$start_date" --end-date "$end_date" >> "$LOG_FILE" 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ 汇总显示成功" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ⚠️ 汇总显示失败（不影响主要任务）" >> "$LOG_FILE"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - 每日统计任务执行完成" >> "$LOG_FILE"
echo "==================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 可选：清理旧的日志文件（保留最近30天的日志）
find /var/log -name "daily_stats.log*" -mtime +30 -delete 2>/dev/null || true