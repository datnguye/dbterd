erDiagram
  "MODEL.JAFFLE_SHOP.CUSTOMERS" {
    text customer_id
    text customer_name
    bigint count_lifetime_orders
    timestamp-without-time-zone first_ordered_at
    timestamp-without-time-zone last_ordered_at
    numeric lifetime_spend_pretax
    numeric lifetime_tax_paid
    numeric lifetime_spend
    text customer_type
  }
  "MODEL.JAFFLE_SHOP.LOCATIONS" {
    text location_id
    text location_name
    double-precision tax_rate
    timestamp-without-time-zone opened_date
  }
  "MODEL.JAFFLE_SHOP.METRICFLOW_TIME_SPINE" {
    date date_day
  }
  "MODEL.JAFFLE_SHOP.ORDER_ITEMS" {
    text order_item_id
    text order_id
    text product_id
    timestamp-without-time-zone ordered_at
    text product_name
    numeric product_price
    boolean is_food_item
    boolean is_drink_item
    numeric supply_cost
  }
  "MODEL.JAFFLE_SHOP.ORDERS" {
    text order_id
    text location_id
    text customer_id
    integer subtotal_cents
    integer tax_paid_cents
    integer order_total_cents
    numeric subtotal
    numeric tax_paid
    numeric order_total
    timestamp-without-time-zone ordered_at
    numeric order_cost
    numeric order_items_subtotal
    bigint count_food_items
    bigint count_drink_items
    bigint count_order_items
    boolean is_food_order
    boolean is_drink_order
    bigint customer_order_number
  }
  "MODEL.JAFFLE_SHOP.PRODUCTS" {
    text product_id
    text product_name
    text product_type
    text product_description
    numeric product_price
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
    double-precision tax_rate
    timestamp-without-time-zone opened_date
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
    integer subtotal_cents
    integer tax_paid_cents
    integer order_total_cents
    numeric subtotal
    numeric tax_paid
    numeric order_total
    timestamp-without-time-zone ordered_at
  }
  "MODEL.JAFFLE_SHOP.STG_PRODUCTS" {
    text product_id
    text product_name
    text product_type
    text product_description
    numeric product_price
    boolean is_food_item
    boolean is_drink_item
  }
  "MODEL.JAFFLE_SHOP.STG_SUPPLIES" {
    text supply_uuid
    text supply_id
    text product_id
    text supply_name
    numeric supply_cost
    boolean is_perishable_supply
  }
  "MODEL.JAFFLE_SHOP.SUPPLIES" {
    text supply_uuid
    text supply_id
    text product_id
    text supply_name
    numeric supply_cost
    boolean is_perishable_supply
  }
  "MODEL.JAFFLE_SHOP.ORDER_ITEMS" }|--|| "MODEL.JAFFLE_SHOP.ORDERS": order_id
  "MODEL.JAFFLE_SHOP.ORDERS" }|--|| "MODEL.JAFFLE_SHOP.STG_CUSTOMERS": customer_id
  "MODEL.JAFFLE_SHOP.STG_ORDER_ITEMS" }|--|| "MODEL.JAFFLE_SHOP.STG_ORDERS": order_id
