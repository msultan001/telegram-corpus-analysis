
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select product_label
from "telegram"."public"."fct_image_detections"
where product_label is null



  
  
      
    ) dbt_internal_test