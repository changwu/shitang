# Docker定时任务配置说明

## 🕐 定时任务配置完成

已在Dockerfile中成功配置定时任务，每天**9点10分**自动执行当天的统计数据收集。

## 📋 配置详情

### 定时任务设置
- **执行时间**: 每天上午 09:10
- **执行脚本**: `/app/daily_stats_cron.sh`
- **日志文件**: `/var/log/daily_stats.log`
- **任务内容**: 统计前一天的数据并显示最近7天汇总

### 文件结构
```
shitang/
├── Dockerfile                    # 包含定时任务配置的容器镜像
├── daily_stats_cron.sh          # 定时任务执行脚本
├── daily_stats_scheduler.py     # 核心统计脚本
├── daily_stats.py              # 统计功能模块
└── ...
```

## 🚀 使用方式

### 1. 查看定时任务状态
```bash
# 检查cron服务状态
docker-compose exec -T app service cron status

# 查看定时任务列表
docker-compose exec -T app crontab -l

# 查看定时任务执行日志
docker-compose exec -T app tail -f /var/log/daily_stats.log
```

### 2. 手动执行统计（测试用）
```bash
# 执行昨天的统计
docker-compose exec -T app python3 daily_stats_scheduler.py

# 查看最近7天汇总
docker-compose exec -T app python3 daily_stats_scheduler.py --summary --start-date $(date -d '7 days ago' +%Y-%m-%d) --end-date $(date -d 'yesterday' +%Y-%m-%d)
```

### 3. 立即执行定时任务脚本（测试用）
```bash
# 手动执行定时任务脚本
docker-compose exec -T app /app/daily_stats_cron.sh

# 查看执行结果
docker-compose exec -T app cat /var/log/daily_stats.log
```

## 📊 定时任务执行内容

每天9:10自动执行以下操作：

1. **统计前一天数据**
   - 车辆早上9点前打卡人数
   - 人员早上9点前打卡人数
   - 午餐时段（11:00-14:00）消费人数

2. **生成统计汇总**
   - 最近7天的详细统计数据
   - 平均值和比率分析

3. **日志记录**
   - 执行时间记录
   - 统计结果记录
   - 错误信息记录

## 🔧 配置说明

### Dockerfile关键配置
```dockerfile
# 安装cron服务
RUN apt-get update && apt-get install -y cron

# 复制并设置cron脚本
COPY daily_stats_cron.sh /app/daily_stats_cron.sh
RUN chmod +x /app/daily_stats_cron.sh

# 创建定时任务（每天9:10执行）
RUN echo "10 9 * * * /app/daily_stats_cron.sh >> /var/log/cron.log 2>&1" | crontab -

# 启动脚本（启动cron服务并保持容器运行）
RUN echo '#!/bin/bash\nservice cron start\ntail -f /dev/null' > /app/start.sh
CMD ["/app/start.sh"]
```

### 环境变量
```bash
DB_URL=postgresql+psycopg2://postgres:postgres@db:5432/shitang
DATA_DIR=/app/data
IMPORT_DIR=import/
```

## 📈 日志格式

定时任务日志示例：
```
==================================
2025-12-19 09:10:01 - 开始执行每日统计任务
2025-12-19 09:10:01 - 开始统计昨天的数据...
2025-12-19 09:10:01 - ✅ 昨日统计任务执行成功
2025-12-19 09:10:02 - 最近7天统计汇总：
📊 统计汇总 (2025-12-12 至 2025-12-18):
==========================================================================================
日期           车辆打卡       人员打卡       午餐消费       总计         比率
------------------------------------------------------------------------------------------
2025-12-18   84         189        313        273        114.7%
...
2025-12-19 09:10:02 - ✅ 汇总显示成功
2025-12-19 09:10:02 - 每日统计任务执行完成
==================================
```

## ⚙️ 维护操作

### 修改执行时间
如需修改执行时间，请编辑Dockerfile中的cron表达式：
```dockerfile
# 修改为其他时间，例如每天8:30
RUN echo "30 8 * * * /app/daily_stats_cron.sh >> /var/log/cron.log 2>&1" | crontab -
```

然后重新构建容器：
```bash
docker-compose build app
docker-compose up -d app
```

### 查看cron日志
```bash
# 查看cron服务日志
docker-compose exec -T app tail -f /var/log/cron.log

# 查看统计执行日志
docker-compose exec -T app tail -f /var/log/daily_stats.log
```

### 清理旧日志
日志文件会自动清理，保留最近30天的记录。如需手动清理：
```bash
docker-compose exec -T app find /var/log -name "daily_stats.log*" -mtime +30 -delete
```

## 🎯 验证定时任务

可以通过以下方式验证定时任务是否正常工作：

1. **检查服务状态**: cron服务正在运行
2. **查看任务列表**: crontab显示正确的定时任务
3. **手动执行测试**: 手动执行脚本验证功能
4. **查看日志文件**: 确认日志正常生成

## 📋 注意事项

- 定时任务会在容器启动时自动开始运行
- 如果容器重启，cron服务会自动重新启动
- 日志文件会自动轮转，避免占用过多磁盘空间
- 统计的是前一天的数据，确保数据完整性

现在系统已配置完成，每天9:10会自动执行统计任务！🎉