-- 统计每天车辆和人员早上9点前打卡人员个数和午餐消费人数（仅工作日）
-- Daily statistics for morning check-ins (before 9 AM) and lunch consumption (Weekdays Only)

WITH weekdays_list AS (
    -- 生成工作日日期列表
    SELECT DISTINCT 
        DATE(record_date) as checkin_date,
        CASE 
            WHEN EXTRACT(DOW FROM record_date) = 1 THEN '周一'
            WHEN EXTRACT(DOW FROM record_date) = 2 THEN '周二'
            WHEN EXTRACT(DOW FROM record_date) = 3 THEN '周三'
            WHEN EXTRACT(DOW FROM record_date) = 4 THEN '周四'
            WHEN EXTRACT(DOW FROM record_date) = 5 THEN '周五'
        END as weekday_name
    FROM vehicle_records 
    WHERE EXTRACT(DOW FROM record_date) BETWEEN 1 AND 5
),

morning_vehicles AS (
    -- 工作日早上9点前车辆打卡统计
    SELECT 
        DATE(record_date) as checkin_date,
        COUNT(DISTINCT name) as vehicle_count
    FROM vehicle_records 
    WHERE EXTRACT(HOUR FROM record_date) < 9
        AND EXTRACT(DOW FROM record_date) BETWEEN 1 AND 5
    GROUP BY DATE(record_date)
),

morning_personnel AS (
    -- 工作日早上9点前人员打卡统计
    SELECT 
        DATE(record_date) as checkin_date,
        COUNT(DISTINCT name) as personnel_count
    FROM door_records 
    WHERE EXTRACT(HOUR FROM record_date) < 9
        AND EXTRACT(DOW FROM record_date) BETWEEN 1 AND 5
    GROUP BY DATE(record_date)
),

lunch_consumers AS (
    -- 工作日午餐消费统计
    SELECT 
        DATE(record_date) as checkin_date,
        COUNT(DISTINCT name) as lunch_count
    FROM canteen_records 
    WHERE type = '午餐'
        AND EXTRACT(DOW FROM record_date) BETWEEN 1 AND 5
    GROUP BY DATE(record_date)
)

SELECT 
    w.checkin_date as "日期",
    w.weekday_name as "星期",
    COALESCE(mv.vehicle_count, 0) as "早上9点前车辆打卡人数",
    COALESCE(mp.personnel_count, 0) as "早上9点前人员打卡人数", 
    COALESCE(mv.vehicle_count, 0) + COALESCE(mp.personnel_count, 0) as "早上9点前总打卡人数",
    COALESCE(lc.lunch_count, 0) as "午餐消费人数",
    CASE 
        WHEN COALESCE(mv.vehicle_count, 0) + COALESCE(mp.personnel_count, 0) > 0 THEN 
            ROUND(COALESCE(lc.lunch_count, 0)::numeric / (COALESCE(mv.vehicle_count, 0) + COALESCE(mp.personnel_count, 0)) * 100, 1)
        ELSE 0
    END as "午餐消费率(%)"
FROM weekdays_list w

LEFT JOIN morning_vehicles mv ON w.checkin_date = mv.checkin_date
LEFT JOIN morning_personnel mp ON w.checkin_date = mp.checkin_date
LEFT JOIN lunch_consumers lc ON w.checkin_date = lc.checkin_date

WHERE COALESCE(mv.vehicle_count, 0) + COALESCE(mp.personnel_count, 0) > 0 
   OR COALESCE(lc.lunch_count, 0) > 0
ORDER BY w.checkin_date DESC
LIMIT 30;