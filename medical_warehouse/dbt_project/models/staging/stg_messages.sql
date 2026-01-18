with raw_data as (
    select
        channel_name,
        message_id,
        message_data,
        scraped_at
    from {{ source('raw', 'raw_messages') }}
),

expanded_data as (
    select
        channel_name,
        message_id,
        (message_data->>'id')::int as msg_id,
        (message_data->>'date')::timestamp as message_date,
        message_data->>'text' as message_text,
        (message_data->>'views')::int as views,
        (message_data->>'forwards')::int as forwards,
        (message_data->>'media')::boolean as has_media,
        (message_data->>'sender_id')::bigint as sender_id,
        (message_data->>'reply_to')::int as reply_to_id,
        (message_data->>'channel_id')::bigint as channel_id,
        scraped_at
    from raw_data
)

select * from expanded_data
