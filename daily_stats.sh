#!/bin/bash
# 食堂数据每日统计脚本 - 简化版本
# 用于快速执行统计任务

# 设置默认参数
DB_URL="${DB_URL:-postgresql+psycopg2://postgres:postgres@localhost:5432/shitang}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/daily_stats_scheduler.py"

# 显示使用帮助
show_help() {
    echo "食堂数据每日统计脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -d, --date DATE      统计指定日期 (YYYY-MM-DD)，默认为昨天"
    echo "  -s, --start DATE     开始日期 (YYYY-MM-DD)"
    echo "  -e, --end DATE       结束日期 (YYYY-MM-DD)"
    echo "  --summary            显示统计汇总"
    echo "  -v, --verbose        显示详细信息"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                   # 统计昨天数据"
    echo "  $0 -d 2024-01-15    # 统计指定日期"
    echo "  $0 -s 2024-01-01 -e 2024-01-31  # 统计日期范围"
    echo "  $0 --summary -s 2024-01-01 -e 2024-01-31  # 显示汇总"
}

# 解析命令行参数
DATE=""
START_DATE=""
END_DATE=""
SUMMARY=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--date)
            DATE="$2"
            shift 2
            ;;
        -s|--start)
            START_DATE="$2"
            shift 2
            ;;
        -e|--end)
            END_DATE="$2"
            shift 2
            ;;
        --summary)
            SUMMARY=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 构建Python命令
PYTHON_CMD="python3 \"$PYTHON_SCRIPT\" --db-url \"$DB_URL\""

if [[ -n "$DATE" ]]; then
    PYTHON_CMD="$PYTHON_CMD --date $DATE"
elif [[ -n "$START_DATE" && -n "$END_DATE" ]]; then
    PYTHON_CMD="$PYTHON_CMD --start-date $START_DATE --end-date $END_DATE"
fi

if $SUMMARY; then
    PYTHON_CMD="$PYTHON_CMD --summary"
fi

if $VERBOSE; then
    PYTHON_CMD="$PYTHON_CMD --verbose"
fi

# 检查Python脚本是否存在
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "错误: Python脚本不存在: $PYTHON_SCRIPT"
    exit 1
fi

# 执行Python脚本
echo "执行统计脚本..."
echo "命令: $PYTHON_CMD"
echo ""

eval $PYTHON_CMD

EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
    echo ""
    echo "✓ 统计任务执行完成"
else
    echo ""
    echo "✗ 统计任务执行失败 (退出码: $EXIT_CODE)"
fi

exit $EXIT_CODE