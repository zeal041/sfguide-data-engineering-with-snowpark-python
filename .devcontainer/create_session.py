from snowflake.snowpark import Session

connection_parameters = {
    "account": "urxxlpr-dp02760",
    "user": "zeal041",
    "password": "Snowflake20021025",
    "role": "HOL_ROLE",
    "warehouse": "HOL_WH",
    "database": "HOL_DB",
    "schema": "ANALYTICS"
}

session = Session.builder.configs(connection_parameters).create()
print("✅ セッション作成成功")
