erDiagram
  "MODEL.JAFFLE_SHOP.CUSTOMERS" {
    text customer_id
    text customer_name
    number count_lifetime_orders
    timestamp_ntz first_ordered_at
    timestamp_ntz last_ordered_at
    number lifetime_spend_pretax
    number lifetime_tax_paid
    number lifetime_spend
    text customer_type
  }
  "MODEL.JAFFLE_SHOP.DIM_CUSTOMER_SEGMENT" {
    text customer_id PK
    varchar segment_code PK
    bigint lifetime_order_count
  }
  "MODEL.JAFFLE_SHOP.FCT_CUSTOMER_SEGMENT_ORDERS" {
    text order_id PK
    text customer_id
    varchar segment_code
    timestamp_ntz ordered_at
    numeric order_total
  }
  "MODEL.JAFFLE_SHOP.LOCATIONS" {
    text location_id PK
    text location_name
    float tax_rate
    timestamp_ntz opened_date
  }
  "MODEL.JAFFLE_SHOP.METRICFLOW_TIME_SPINE" {
    date date_day
  }
  "MODEL.JAFFLE_SHOP.ORDER_ITEMS" {
    text order_item_id
    text order_id
    text product_id
    timestamp_ntz ordered_at
    text product_name
    number product_price
    boolean is_food_item
    boolean is_drink_item
    number supply_cost
  }
  "MODEL.JAFFLE_SHOP.ORDERS" {
    text order_id PK
    text location_id
    text customer_id
    number subtotal_cents
    number tax_paid_cents
    number order_total_cents
    number subtotal
    number tax_paid
    number order_total
    timestamp_ntz ordered_at
    number order_cost
    number order_items_subtotal
    number count_food_items
    number count_drink_items
    number count_order_items
    boolean is_food_order
    boolean is_drink_order
    number customer_order_number
  }
  "MODEL.JAFFLE_SHOP.PRODUCTS" {
    text product_id
    text product_name
    text product_type
    text product_description
    number product_price
    boolean is_food_item
    boolean is_drink_item
  }
  "MODEL.JAFFLE_SHOP.STG_CUSTOMERS" {
    text customer_id
    text customer_name
  }
  "MODEL.JAFFLE_SHOP.STG_LOCATIONS" {
    text location_id
    text location_name
    float tax_rate
    timestamp_ntz opened_date
  }
  "MODEL.JAFFLE_SHOP.STG_ORDER_ITEMS" {
    text order_item_id
    text order_id
    text product_id
  }
  "MODEL.JAFFLE_SHOP.STG_ORDERS" {
    text order_id
    text location_id
    text customer_id
    number subtotal_cents
    number tax_paid_cents
    number order_total_cents
    number subtotal
    number tax_paid
    number order_total
    timestamp_ntz ordered_at
  }
  "MODEL.JAFFLE_SHOP.STG_PRODUCTS" {
    text product_id
    text product_name
    text product_type
    text product_description
    number product_price
    boolean is_food_item
    boolean is_drink_item
  }
  "MODEL.JAFFLE_SHOP.STG_SUPPLIES" {
    text supply_uuid
    text supply_id
    text product_id
    text supply_name
    number supply_cost
    boolean is_perishable_supply
  }
  "MODEL.JAFFLE_SHOP.SUPPLIES" {
    text supply_uuid
    text supply_id
    text product_id
    text supply_name
    number supply_cost
    boolean is_perishable_supply
  }
  "MODEL.JAFFLE_SHOP.FCT_CUSTOMER_SEGMENT_ORDERS" }|--|| "MODEL.JAFFLE_SHOP.DIM_CUSTOMER_SEGMENT": customer_id__segment_code
  "MODEL.JAFFLE_SHOP.ORDERS" }|--|| "MODEL.JAFFLE_SHOP.LOCATIONS": location_id
