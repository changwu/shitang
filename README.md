# 食堂数据导入系统 (Shitang Data Import System)

## 项目概述

本项目是一个用于导入和管理食堂消费记录、车辆打卡记录和人员打卡记录的数据系统。支持从Excel文件自动导入数据到PostgreSQL数据库，并提供数据分析功能。

## 主要特性

- **自动文件识别**: 根据文件名自动识别数据类型并导入到对应表
- **多格式支持**: 支持Excel (.xlsx/.xlsm) 文件格式
- **字段映射**: 自动将中文列名映射到英文字段名
- **数据验证**: 自动数据类型转换和验证
- **索引优化**: 为常用查询字段建立索引
- **容器化部署**: 支持Docker容器化部署

## 文件导入表对应关系

| 文件名特征 | 目标表 | 说明 |
|-----------|--------|------|
| 包含"consumelog" | canteen_records | 食堂消费记录 |
| 包含"打卡明细数据" | vehicle_records | 车辆打卡记录 |
| 包含"dooreventinfo" | door_records | 人员打卡记录 |

## 表字段对应关系

### canteen_records (食堂消费记录表)
| PostgreSQL字段 | Excel列名 | 类型 | 说明 |
|---------------|-----------|------|------|
| id | 主键 | SERIAL | 自增主键 |
| record_date | 消费时间 | TIMESTAMPTZ | 消费时间 |
| name | 姓名 | TEXT | 消费者姓名 |
| type | 餐别 | TEXT | 餐别类型 |

### vehicle_records (车辆打卡记录表)
| PostgreSQL字段 | Excel列名 | 类型 | 说明 |
|---------------|-----------|------|------|
| id | 主键 | SERIAL | 自增主键 |
| record_date | 打卡时间 | TIMESTAMPTZ | 打卡时间 |
| name | 姓名 | TEXT | 打卡人员姓名 |
| type | 打卡类型 | TEXT | 打卡类型 |

### door_records (人员打卡记录表)
| PostgreSQL字段 | Excel列名 | 类型 | 说明 |
|---------------|-----------|------|------|
| id | 主键 | SERIAL | 自增主键 |
| record_date | 事件时间 | TIMESTAMPTZ | 事件时间 |
| name | 人员姓名 | TEXT | 人员姓名 |
| type | 控制器 | TEXT | 控制器信息 |

## 快速开始

### 环境要求

- Docker 和 Docker Compose
- Python 3.11+ (本地运行)

### Docker部署

1. **构建和启动服务**:
```bash
docker compose build app
docker compose up -d db metabase
```

2. **导入数据**:
```bash
# 导入所有表
docker compose run --rm app python /app/import_data.py --data-dir /app/data --verbose

# 仅导入指定表
docker compose run --rm app python /app/import_data.py --data-dir /app/data --table canteen_records --verbose
```

### 本地运行

1. **安装依赖**:
```bash
pip install -r requirements.txt
```

2. **设置数据库**:
确保PostgreSQL正在运行，并创建数据库:
```sql
CREATE DATABASE shitang;
```

3. **初始化表结构**:
```bash
psql -U postgres -d shitang -f sql/init.sql
```

4. **导入数据**:
```bash
# 导入所有文件
python import_data.py --verbose

# 仅导入指定表
python import_data.py --table canteen_records --verbose
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| DB_URL | postgresql+psycopg2://postgres:postgres@localhost:5432/shitang | 数据库连接字符串 |
| DATA_DIR | ./data | 数据文件根目录 |
| IMPORT_DIR | import/ | 导入文件子目录 |
| EXCEL_HEADER_ROW | 1 | Excel表头行号 |

### 文件结构

```
shitang/
├── sql/
│   └── init.sql              # 数据库初始化脚本
├── data/
│   └── import/               # Excel文件导入目录
│       ├── consumelog_*.xlsx          # 食堂消费记录
│       ├── 打卡明细数据_*.xlsx        # 车辆打卡记录
│       └── dooreventinfo_*.xlsx       # 人员打卡记录
├── import_data.py            # 数据导入主程序
├── clear_tables.py           # 清空数据表工具
├── requirements.txt          # Python依赖
├── Dockerfile               # Docker镜像定义
├── docker-compose.yml      # Docker Compose配置
└── .env                    # 环境变量配置
```

## 使用说明

### 数据导入

1. **准备数据文件**:
   - 将Excel文件放入 `data/import/` 目录
   - 确保文件名包含对应的特征字符串
   - 确保Excel列名与要求一致

2. **执行导入**:
```bash
# 导入所有文件
docker compose run --rm app python /app/import_data.py --verbose

# 指定表头行号（如果表头不在第一行）
docker compose run --rm app python /app/import_data.py --excel-header-row 2 --verbose
```

### 数据清空

```bash
# 清空所有表
docker compose run --rm app python /app/clear_tables.py --yes

# 清空指定表
docker compose run --rm app python /app/clear_tables.py --table canteen_records --yes
```

### 数据分析

系统包含Metabase服务，可用于数据分析和可视化:
- 访问: http://localhost:4000
- 数据库连接: 主机`db`，端口`5432`，数据库`shitang`，用户`postgres`，密码`postgres`

## 开发说明

### 主要改进

1. **字段标准化**: 所有表统一使用英文字段名 (`id`, `record_date`, `name`, `type`)
2. **文件识别**: 基于文件名特征字符串的精确匹配
3. **索引优化**: 为常用查询字段建立复合索引
4. **代码重构**: 模块化设计，便于维护和扩展

### 添加新表

1. 在 `sql/init.sql` 中添加新表定义
2. 在 `import_data.py` 的 `TABLES` 字典中添加表配置
3. 更新 `clear_tables.py` 中的表列表
4. 更新文档说明

### 调试和测试

```bash
# 启用详细日志
python import_data.py --verbose

# 测试文件识别
python -c "
from import_data import determine_table_by_filename
print(determine_table_by_filename('consumelog_test.xlsx'))  # canteen_records
print(determine_table_by_filename('打卡明细数据_test.xlsx'))  # vehicle_records
print(determine_table_by_filename('dooreventinfo_test.xlsx'))  # door_records
"
```

## 故障排除

### 常见问题

1. **文件无法识别**: 检查文件名是否包含正确的特征字符串
2. **字段映射失败**: 检查Excel列名是否与要求一致
3. **数据库连接失败**: 检查数据库配置和网络连接
4. **权限问题**: 确保数据库用户有足够的权限

### 日志查看

```bash
# 查看应用日志
docker compose logs app

# 查看数据库日志  
docker compose logs db
```

## 版本历史

- v2.0: 重构版本，统一字段命名，优化文件识别逻辑
- v1.0: 初始版本

## 许可证

MIT License