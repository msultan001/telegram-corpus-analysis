
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select channel_id
from "telegram"."public"."fct_image_detections"
where channel_id is null



  
  
      
    ) dbt_internal_test