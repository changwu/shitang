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
