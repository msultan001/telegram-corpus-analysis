
  
    

  create  table "telegram"."public"."fct_messages__dbt_tmp"
  
  
    as
  
  (
    with messages as (
    select * from "telegram"."public"."stg_messages"
)

select
    message_id,
    channel_id,
    cast(message_date as date) as date_key,
    message_text,
    views,
    forwards,
    has_media,
    sender_id,
    reply_to_id
from messages
  );
  