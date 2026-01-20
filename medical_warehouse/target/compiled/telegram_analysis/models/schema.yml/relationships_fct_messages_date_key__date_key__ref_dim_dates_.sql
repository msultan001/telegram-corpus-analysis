
    
    

with child as (
    select date_key as from_field
    from "telegram"."public"."fct_messages"
    where date_key is not null
),

parent as (
    select date_key as to_field
    from "telegram"."public"."dim_dates"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


