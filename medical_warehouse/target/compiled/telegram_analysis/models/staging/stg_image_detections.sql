-- staging model for image detections loaded by scripts/load_detections.py
with raw as (
    select * from "telegram"."public"."stg_image_detections"
)

select
    cast(channel_id as bigint) as channel_id,
    cast(message_id as bigint) as message_id,
    image_path,
    product_label,
    original_label,
    cast(score as double precision) as score,
    cast(detection_timestamp as timestamp) as detection_timestamp
from raw