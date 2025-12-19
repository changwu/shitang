-- 初始化数据库表结构
-- 按照新的字段对应关系重构所有表

\set dbname_shitang shitang
SELECT 'CREATE DATABASE ' || quote_ident(:'dbname_shitang')
  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'dbname_shitang');
\gexec
\set dbname_metabase metabase
SELECT 'CREATE DATABASE ' || quote_ident(:'dbname_metabase')
  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'dbname_metabase');
\gexec
\connect shitang

-- 创建统计表结构（新增）
-- 车辆9点前打卡统计表
CREATE TABLE IF NOT EXISTS vehicle_morning_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    morning_checkin_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stat_date)
);

-- 人员9点前打卡统计表  
CREATE TABLE IF NOT EXISTS personnel_morning_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    morning_checkin_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stat_date)
);

-- 午餐消费统计表
CREATE TABLE IF NOT EXISTS lunch_consumption_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    lunch_consumption_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stat_date)
);

-- 综合每日统计表（用于汇总显示）
CREATE TABLE IF NOT EXISTS daily_summary_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    vehicle_morning_count INTEGER DEFAULT 0,
    personnel_morning_count INTEGER DEFAULT 0,
    lunch_consumption_count INTEGER DEFAULT 0,
    total_morning_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stat_date)
);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为统计表创建触发器
CREATE TRIGGER update_vehicle_morning_stats_updated_at 
    BEFORE UPDATE ON vehicle_morning_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personnel_morning_stats_updated_at 
    BEFORE UPDATE ON personnel_morning_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lunch_consumption_stats_updated_at 
    BEFORE UPDATE ON lunch_consumption_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_summary_stats_updated_at 
    BEFORE UPDATE ON daily_summary_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_vehicle_morning_stats_date ON vehicle_morning_stats(stat_date);
CREATE INDEX IF NOT EXISTS idx_personnel_morning_stats_date ON personnel_morning_stats(stat_date);
CREATE INDEX IF NOT EXISTS idx_lunch_consumption_stats_date ON lunch_consumption_stats(stat_date);
CREATE INDEX IF NOT EXISTS idx_daily_summary_stats_date ON daily_summary_stats(stat_date);

-- 食堂消费记录表 canteen_records
CREATE TABLE IF NOT EXISTS canteen_records (
  id SERIAL PRIMARY KEY,
  record_date TIMESTAMPTZ,
  name TEXT,
  type TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_canteen_records_name_time 
  ON canteen_records (name, record_date);
CREATE INDEX IF NOT EXISTS idx_canteen_records_record_date 
  ON canteen_records (record_date);
CREATE INDEX IF NOT EXISTS idx_canteen_records_name 
  ON canteen_records (name);

-- 车辆打卡记录表 vehicle_records  
CREATE TABLE IF NOT EXISTS vehicle_records (
  id SERIAL PRIMARY KEY,
  record_date TIMESTAMPTZ,
  name TEXT,
  type TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vehicle_records_name_time 
  ON vehicle_records (name, record_date);
CREATE INDEX IF NOT EXISTS idx_vehicle_records_record_date 
  ON vehicle_records (record_date);
CREATE INDEX IF NOT EXISTS idx_vehicle_records_name 
  ON vehicle_records (name);

-- 人员打卡记录表 door_records (原person_records)
CREATE TABLE IF NOT EXISTS door_records (
  id SERIAL PRIMARY KEY,
  record_date TIMESTAMPTZ,
  name TEXT,
  type TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_door_records_name_time 
  ON door_records (name, record_date);
CREATE INDEX IF NOT EXISTS idx_door_records_record_date 
  ON door_records (record_date);
CREATE INDEX IF NOT EXISTS idx_door_records_name 
  ON door_records (name);
