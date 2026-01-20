with unique_channels as (
    select distinct
        channel_id,
        channel_name
    from "telegram"."public"."stg_messages"
)

select
    channel_id,
    channel_name,
    current_timestamp as created_at
from unique_channels