#!/bin/bash
# Docker环境中执行完整数据导入和统计收集的脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."
    
    if ! docker-compose ps | grep -q "Up"; then
        log_error "Docker容器未运行，请先启动服务"
        exit 1
    fi
    
    log_info "Docker环境正常"
}

# 导入Excel数据
import_data() {
    log_info "开始导入Excel数据..."
    
    # 设置数据库连接
    export DB_URL="postgresql+psycopg2://postgres:postgres@db:5432/shitang"
    
    # 执行导入
    if docker-compose exec -T app python3 import_data.py --verbose; then
        log_info "✅ Excel数据导入成功"
    else
        log_error "❌ Excel数据导入失败"
        exit 1
    fi
}

# 获取数据日期范围
get_date_range() {
    log_info "获取数据日期范围..."
    
    # 从数据库中查询实际的日期范围
    local query="SELECT 
        MIN(DATE(record_date)) as start_date,
        MAX(DATE(record_date)) as end_date
    FROM (
        SELECT record_date FROM canteen_records
        UNION ALL
        SELECT record_date FROM vehicle_records  
        UNION ALL
        SELECT record_date FROM door_records
    ) all_records;"
    
    local result=$(docker-compose exec -T db psql -U postgres -d shitang -c "$query" -t -A)
    
    if [[ -n "$result" ]]; then
        local start_date=$(echo "$result" | cut -d'|' -f1)
        local end_date=$(echo "$result" | cut -d'|' -f2)
        
        if [[ "$start_date" != "" && "$end_date" != "" ]]; then
            log_info "数据日期范围: $start_date 到 $end_date"
            echo "$start_date $end_date"
            return 0
        fi
    fi
    
    log_warn "无法自动确定日期范围，使用默认范围"
    local default_start=$(date -d "2024-01-01" +%Y-%m-%d)
    local default_end=$(date -d "yesterday" +%Y-%m-%d)
    echo "$default_start $default_end"
}

# 收集统计数据
collect_stats() {
    local date_range=$1
    local start_date=$(echo "$date_range" | cut -d' ' -f1)
    local end_date=$(echo "$date_range" | cut -d' ' -f2)
    
    log_info "开始收集统计数据: $start_date 到 $end_date"
    
    # 执行统计收集
    if docker-compose exec -T app python3 daily_stats_scheduler.py \
        --start-date "$start_date" \
        --end-date "$end_date" \
        --verbose; then
        log_info "✅ 统计数据收集成功"
    else
        log_error "❌ 统计数据收集失败"
        exit 1
    fi
}

# 验证统计数据
verify_stats() {
    log_info "验证统计数据..."
    
    local tables=("vehicle_morning_stats" "personnel_morning_stats" "lunch_consumption_stats" "daily_summary_stats")
    local all_valid=true
    
    for table in "${tables[@]}"; do
        local count=$(docker-compose exec -T db psql -U postgres -d shitang -c "SELECT COUNT(*) FROM $table;" -t -A)
        if [[ -n "$count" && "$count" -gt 0 ]]; then
            log_info "✅ $table: $count 条记录"
        else
            log_warn "⚠️  $table: 无记录或查询失败"
            all_valid=false
        fi
    done
    
    if $all_valid; then
        log_info "✅ 统计数据验证完成"
    else
        log_warn "⚠️  部分统计表无数据"
    fi
}

# 显示统计汇总
show_summary() {
    local date_range=$1
    local start_date=$(echo "$date_range" | cut -d' ' -f1)
    local end_date=$(echo "$date_range" | cut -d' ' -f2)
    
    log_info "显示统计汇总..."
    
    # 显示最近30天的汇总（如果数据范围足够）
    local summary_start=$(date -d "$end_date - 30 days" +%Y-%m-%d)
    if [[ "$summary_start" < "$start_date" ]]; then
        summary_start="$start_date"
    fi
    
    docker-compose exec -T app python3 daily_stats_scheduler.py \
        --summary --start-date "$summary_start" --end-date "$end_date"
}

# 主函数
main() {
    echo "🚀 Docker环境数据导入和统计收集脚本"
    echo "=================================="
    
    # 检查Docker环境
    check_docker
    
    # 导入数据
    import_data
    
    # 获取日期范围
    local date_range=$(get_date_range)
    
    # 收集统计数据
    collect_stats "$date_range"
    
    # 验证统计数据
    verify_stats
    
    # 显示汇总信息
    show_summary "$date_range"
    
    echo "=================================="
    echo "🎉 所有任务执行完成！"
}

# 运行主函数
main "$@"