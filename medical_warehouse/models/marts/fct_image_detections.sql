with detections as (
    select * from {{ ref('stg_image_detections') }}
)

select
    row_number() over (order by detection_timestamp desc) as detection_id,
    channel_id,
    message_id,
    image_path,
    product_label,
    score,
    detection_timestamp
from detections
