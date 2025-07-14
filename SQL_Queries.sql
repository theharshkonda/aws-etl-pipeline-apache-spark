
--- Query 1
SELECT * FROM cleaned_data limit 10;

--- Query 2
SELECT 
    region, 
    segment, 
    SUM(forecasted_monthly_revenue) as forcast_monthly_revenue 
FROM cleaned_data
GROUP BY segment, region;
