erDiagram
  "MODEL.DBT_RESTO.DIM_BOX" {
    varchar box_key
    varchar box_id
    date box_date
    nvarchar box_result_numbers
    int box_result_number_1
    int box_result_number_2
    int box_result_number_3
    int box_result_number_4
    int box_result_number_5
    int box_result_number_6
    int box_result_number_7
  }
  "MODEL.DBT_RESTO.DIM_DATE" {
    date date_key
    date box_date
    int box_day
    int box_week
    int box_month
    varchar box_month_name
    int box_year
  }
  "MODEL.DBT_RESTO.DIM_PRIZE" {
    varchar prize_key
    nvarchar prize_name
    int prize_order
  }
  "MODEL.DBT_RESTO.FACT_NUMBER" {
    int number_value
    int occurrence
    int occurrence_pos_1
    int occurrence_pos_2
    int occurrence_pos_3
    int occurrence_pos_4
    int occurrence_pos_5
    int occurrence_pos_6
    int occurrence_pos_7
    date last_appearance
    date last_appearance_pos_1
    date last_appearance_pos_2
    date last_appearance_pos_3
    date last_appearance_pos_4
    date last_appearance_pos_5
    date last_appearance_pos_6
    date last_appearance_pos_7
  }
  "MODEL.DBT_RESTO.FACT_NUMBER_FORECAST" {
    date forecast_date
    date last_box_date
    varchar forecast_numbers
    nvarchar last_box_result_numbers
    int forecast_1
    int last_box_result_number_1
    int forecast_2
    int last_box_result_number_2
    int forecast_3
    int last_box_result_number_3
    int forecast_4
    int last_box_result_number_4
    int forecast_5
    int last_box_result_number_5
    int forecast_6
    int last_box_result_number_6
  }
  "MODEL.DBT_RESTO.FACT_NUMBER_SCORING" {
    varchar fact_key
    date forecast_date
    int number_value
    int score_1
    int score_2
    int score_3
    int score_4
    int score_5
    int score_6
    float rank_pos_1
    float rank_pos_2
    float rank_pos_3
    float rank_pos_4
    float rank_pos_5
    float rank_pos_6
  }
  "MODEL.DBT_RESTO.FACT_RESULT" {
    varchar fact_result_key
    varchar box_key
    varchar prize_key
    date date_key
    int no_of_won
    float prize_value
    float prize_paid
    int is_prize_taken
  }
  "MODEL.DBT_RESTO.FACT_SET_NUMBER" {
    nvarchar box_result_numbers
    int occurrence
    date last_appearance
  }
  "MODEL.DBT_RESTO.STAGING_POWER655_BOX" {
    varchar sk_box
    date box_date
    varchar box_id
    nvarchar box_name
    nvarchar box_result_numbers
    int box_result_number_1
    int box_result_number_2
    int box_result_number_3
    int box_result_number_4
    int box_result_number_5
    int box_result_number_6
    int box_result_number_7
  }
  "MODEL.DBT_RESTO.STAGING_POWER655_BOX_DETAIL" {
    varchar sk_box_detail
    varchar box_id
    nvarchar prize_name_raw
    nvarchar prize_name
    int prize_won
    nvarchar prize_value_raw
    float prize_value
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_DATEPART" {
    datetime input
    varchar date_part
    int actual
    int expected
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_GENERATE_SCHEMA_NAME" {
    varchar actual
    varchar expected
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_GET_BASE_TIMES_HOUR" {
    datetime time_value
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_GET_BASE_TIMES_MINUTE" {
    datetime time_value
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_GET_BASE_TIMES_SECOND" {
    datetime time_value
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_GET_TABLE_ALIAS" {
    varchar actual
    varchar expected
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_GET_TIME_DIMENSION_HOUR" {
    datetime time_value
    nvarchar time_string
    nvarchar time24_string
    int hour_number
    nvarchar hour_name
    int hour24_number
    nvarchar hour24_name
    bigint time_key
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_GET_TIME_DIMENSION_MINUTE" {
    datetime time_value
    nvarchar time_string
    nvarchar time24_string
    int hour_number
    nvarchar hour_name
    int hour24_number
    nvarchar hour24_name
    int minute_number
    nvarchar hour_minute_name
    nvarchar hour24_minute_name
    bigint time_key
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_GET_TIME_DIMENSION_SECOND" {
    datetime time_value
    nvarchar time_string
    nvarchar time24_string
    int hour_number
    nvarchar hour_name
    int hour24_number
    nvarchar hour24_name
    int minute_number
    nvarchar hour_minute_name
    nvarchar hour24_minute_name
    int second_number
    bigint time_key
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_GET_TIME_KEY" {
    nvarchar actual
    varchar expected
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_IF_COLUMN_VALUE_TO_MATCH_REGEX" {
    varchar text_only
    varchar number_only
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_MATERIALIZED_VIEW" {
    int time_key
    int time_value
  }
  "MODEL.INTEGRATION_TESTS.VERIFY_STR_TO_DATE" {
    date actual
    date expected
  }
