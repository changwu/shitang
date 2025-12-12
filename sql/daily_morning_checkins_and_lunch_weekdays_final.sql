-- 统计每天车辆和人员早上9点前打卡人员个数和午餐消费人数（仅工作日 - 最终版）
-- Daily statistics for morning check-ins (before 9 AM) and lunch consumption (Weekdays Only - Final)

WITH weekdays_data AS (
    -- 筛选工作日数据（周一到周五）
    SELECT 
        DATE(record_date) as checkin_date,
        EXTRACT(DOW FROM record_date) as day_of_week,
        CASE 
            WHEN EXTRACT(DOW FROM record_date) = 1 THEN '周一'
            WHEN EXTRACT(DOW FROM record_date) = 2 THEN '周二'
            WHEN EXTRACT(DOW FROM record_date) = 3 THEN '周三'
            WHEN EXTRACT(DOW FROM record_date) = 4 THEN '周四'
            WHEN EXTRACT(DOW FROM record_date) = 5 THEN '周五'
        END as weekday_name
    FROM (
        SELECT record_date FROM vehicle_records WHERE EXTRACT(DOW FROM record_date) BETWEEN 1 AND 5
        UNION
        SELECT record_date FROM door_records WHERE EXTRACT(DOW FROM record_date) BETWEEN 1 AND 5
        UNION
        SELECT record_date FROM canteen_records WHERE EXTRACT(DOW FROM record_date) BETWEEN 1 AND 5
    ) all_dates
    GROUP BY DATE(record_date), EXTRACT(DOW FROM record_date)
),

morning_checkins AS (
    -- 工作日早上9点前打卡记录
    SELECT 
        checkin_date,
        COUNT(CASE WHEN record_type = '车辆' THEN 1 END) as vehicle_count,
        COUNT(CASE WHEN record_type = '人员' THEN 1 END) as personnel_count,
        COUNT(*) as total_morning_count
    FROM (
        SELECT 
            DATE(record_date) as checkin_date,
            '车辆' as record_type,
            name
        FROM vehicle_records 
        WHERE EXTRACT(HOUR FROM record_date) < 9
            AND EXTRACT(DOW FROM record_date) BETWEEN 1 AND 5
        
        UNION ALL
        
        SELECT 
            DATE(record_date) as checkin_date,
            '人员' as record_type,
            name
        FROM door_records 
        WHERE EXTRACT(HOUR FROM record_date) < 9
            AND EXTRACT(DOW FROM record_date) BETWEEN 1 AND 5
    ) combined
    GROUP BY checkin_date
),

lunch_consumption AS (
    -- 工作日午餐消费记录
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
    COALESCE(m.vehicle_count, 0) as "早上9点前车辆打卡人数",
    COALESCE(m.personnel_count, 0) as "早上9点前人员打卡人数", 
    COALESCE(m.total_morning_count, 0) as "早上9点前总打卡人数",
    COALESCE(l.lunch_count, 0) as "午餐消费人数",
    CASE 
        WHEN COALESCE(m.total_morning_count, 0) > 0 THEN 
            ROUND(COALESCE(l.lunch_count, 0)::numeric / COALESCE(m.total_morning_count, 0) * 100, 1)
        ELSE 0
    END as "午餐消费率(%)"
FROM weekdays_data w

LEFT JOIN morning_checkins m ON w.checkin_date = m.checkin_date
LEFT JOIN lunch_consumption l ON w.checkin_date = l.checkin_date

WHERE COALESCE(m.total_morning_count, 0) > 0 OR COALESCE(l.lunch_count, 0) > 0
ORDER BY w.checkin_date DESC
LIMIT 30;