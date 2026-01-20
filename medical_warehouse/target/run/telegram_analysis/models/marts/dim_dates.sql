
  
    

  create  table "telegram"."public"."dim_dates__dbt_tmp"
  
  
    as
  
  (
    with date_spine as (
    select 
        cast(generate_series(
            '2023-01-01'::date, 
            '2026-12-31'::date, 
            '1 day'::interval
        ) as date) as date_day
)

select
    date_day as date_key,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    extract(dow from date_day) as day_of_week,
    to_char(date_day, 'Month') as month_name,
    to_char(date_day, 'Day') as day_name
from date_spine
  );
  