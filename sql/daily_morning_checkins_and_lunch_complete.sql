-- 统计每天车辆和人员早上9点前打卡人员个数和午餐消费人数（完整版）
-- Daily statistics for morning check-ins (before 9 AM) and lunch consumption (Complete Version)

WITH morning_checkins AS (
    -- 合并早上9点前的车辆和人员打卡记录
    SELECT 
        DATE(record_date) as checkin_date,
        '车辆' as record_type,
        name
    FROM vehicle_records 
    WHERE EXTRACT(HOUR FROM record_date) < 9
    
    UNION
    
    SELECT 
        DATE(record_date) as checkin_date,
        '人员' as record_type,
        name
    FROM door_records 
    WHERE EXTRACT(HOUR FROM record_date) < 9
),

lunch_consumption AS (
    -- 午餐消费记录
    SELECT 
        DATE(record_date) as checkin_date,
        name
    FROM canteen_records 
    WHERE type = '午餐'
)

SELECT 
    d.checkin_date as "日期",
    COALESCE(m.vehicle_count, 0) as "早上9点前车辆打卡人数",
    COALESCE(m.personnel_count, 0) as "早上9点前人员打卡人数", 
    COALESCE(m.total_morning_count, 0) as "早上9点前总打卡人数",
    COALESCE(l.lunch_count, 0) as "午餐消费人数",
    CASE 
        WHEN COALESCE(m.total_morning_count, 0) > 0 THEN 
            ROUND(COALESCE(l.lunch_count, 0)::numeric / COALESCE(m.total_morning_count, 0) * 100, 1)
        ELSE 0
    END as "午餐消费率(%)"
FROM (
    -- 获取所有相关日期
    SELECT DISTINCT checkin_date FROM morning_checkins
    UNION
    SELECT DISTINCT checkin_date FROM lunch_consumption
) d

LEFT JOIN (
    -- 统计每天早上打卡人数
    SELECT 
        checkin_date,
        COUNT(CASE WHEN record_type = '车辆' THEN 1 END) as vehicle_count,
        COUNT(CASE WHEN record_type = '人员' THEN 1 END) as personnel_count,
        COUNT(*) as total_morning_count
    FROM morning_checkins
    GROUP BY checkin_date
) m ON d.checkin_date = m.checkin_date

LEFT JOIN (
    -- 统计每天午餐消费人数
    SELECT 
        checkin_date,
        COUNT(DISTINCT name) as lunch_count
    FROM lunch_consumption
    GROUP BY checkin_date
) l ON d.checkin_date = l.checkin_date

WHERE COALESCE(m.total_morning_count, 0) > 0 OR COALESCE(l.lunch_count, 0) > 0
ORDER BY d.checkin_date DESC
LIMIT 30;