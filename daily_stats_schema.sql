-- 每日统计表结构
-- 用于存储每天车辆、人员表中在9点前打卡人数，和午餐消费人数

-- 车辆9点前打卡统计表
CREATE TABLE IF NOT EXISTS vehicle_morning_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    morning_checkin_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stat_date)
);

-- 人员9点前打卡统计表  
CREATE TABLE IF NOT EXISTS personnel_morning_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    morning_checkin_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stat_date)
);

-- 午餐消费统计表
CREATE TABLE IF NOT EXISTS lunch_consumption_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    lunch_consumption_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stat_date)
);

-- 综合每日统计表（可选，用于汇总显示）
CREATE TABLE IF NOT EXISTS daily_summary_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    vehicle_morning_count INTEGER DEFAULT 0,
    personnel_morning_count INTEGER DEFAULT 0,
    lunch_consumption_count INTEGER DEFAULT 0,
    total_morning_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stat_date)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_vehicle_morning_stats_date ON vehicle_morning_stats(stat_date);
CREATE INDEX IF NOT EXISTS idx_personnel_morning_stats_date ON personnel_morning_stats(stat_date);
CREATE INDEX IF NOT EXISTS idx_lunch_consumption_stats_date ON lunch_consumption_stats(stat_date);
CREATE INDEX IF NOT EXISTS idx_daily_summary_stats_date ON daily_summary_stats(stat_date);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_vehicle_morning_stats_updated_at 
    BEFORE UPDATE ON vehicle_morning_stats 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personnel_morning_stats_updated_at 
    BEFORE UPDATE ON personnel_morning_stats 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lunch_consumption_stats_updated_at 
    BEFORE UPDATE ON lunch_consumption_stats 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_summary_stats_updated_at 
    BEFORE UPDATE ON daily_summary_stats 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();