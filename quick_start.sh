#!/bin/bash

# Shitang项目快速启动脚本

echo "🚀 Shitang项目快速启动"
echo "======================"

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/import/{shitang,che,ren}

# 构建镜像
echo "🔨 构建应用镜像..."
docker compose build app

if [ $? -ne 0 ]; then
    echo "❌ 镜像构建失败"
    exit 1
fi

# 启动数据库和Metabase
echo "🗄️  启动数据库和Metabase服务..."
docker compose up -d db metabase

if [ $? -ne 0 ]; then
    echo "❌ 服务启动失败"
    exit 1
fi

echo "⏳ 等待数据库初始化..."
sleep 10

# 显示状态
echo "📊 服务状态:"
docker compose ps

echo ""
echo "🎉 启动完成！"
echo ""
echo "📋 服务访问信息:"
echo "- Metabase: http://localhost:4000"
echo "- PostgreSQL: localhost:5432 (数据库: shitang, 用户: postgres, 密码: postgres)"
echo ""
echo "📁 数据导入目录:"
echo "- 食堂数据: data/import/shitang/ (文件名需包含 'consumelog')"
echo "- 车辆数据: data/import/che/ (文件名需包含 '打卡明细数据')"
echo "- 门禁数据: data/import/ren/ (文件名需包含 'dooreventinfo')"
echo ""
echo "🔧 常用命令:"
echo "- 导入数据: docker compose run --rm app python /app/import_data.py --verbose"
echo "- 查看日志: docker compose logs -f"
echo "- 停止服务: docker compose down"
echo "- 清空数据: docker compose run --rm app python /app/clear_tables.py --table all --yes"
echo ""
echo "📖 详细文档请查看 README.md"