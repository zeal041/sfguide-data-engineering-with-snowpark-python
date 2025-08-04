#------------------------------------------------------------------------------
# Hands-On Lab: Data Engineering with Snowpark
# Script:       02_load_raw.py
# Author:       Jeremiah Hansen, Caleb Baechtold
# Last Updated: 1/9/2023
#------------------------------------------------------------------------------

import time
from snowflake.snowpark import Session
#import snowflake.snowpark.types as T
#import snowflake.snowpark.functions as F


POS_TABLES = ['country', 'franchise', 'location', 'menu', 'truck', 'order_header', 'order_detail']
CUSTOMER_TABLES = ['customer_loyalty']
TABLE_DICT = {
    "pos": {"schema": "RAW_POS", "tables": POS_TABLES},
    "customer": {"schema": "RAW_CUSTOMER", "tables": CUSTOMER_TABLES}
}

# SNOWFLAKE ADVANTAGE: Schema detection
# SNOWFLAKE ADVANTAGE: Data ingestion with COPY
# SNOWFLAKE ADVANTAGE: Snowflake Tables (not file-based)

def load_raw_table(session, tname=None, s3dir=None, year=None, schema=None):
    session.use_schema(schema)
    if year is None:
        location = "@external.frostbyte_raw_stage/{}/{}".format(s3dir, tname)
    else:
        print('\tLoading year {}'.format(year)) 
        location = "@external.frostbyte_raw_stage/{}/{}/year={}".format(s3dir, tname, year)
    
    # we can infer schema using the parquet read option
    df = session.read.option("compression", "snappy") \
                            .parquet(location)
    df.copy_into_table("{}".format(tname))
    comment_text = '''{"origin":"sf_sit-is","name":"snowpark_101_de","version":{"major":1, "minor":0},"attributes":{"is_quickstart":1, "source":"sql"}}'''
    sql_command = f"""COMMENT ON TABLE {tname} IS '{comment_text}';"""
    session.sql(sql_command).collect()

# SNOWFLAKE ADVANTAGE: Warehouse elasticity (dynamic scaling)

def load_all_raw_tables(session):
    _ = session.sql("ALTER WAREHOUSE HOL_WH SET WAREHOUSE_SIZE = XLARGE WAIT_FOR_COMPLETION = TRUE").collect()

    for s3dir, data in TABLE_DICT.items():
        tnames = data['tables']
        schema = data['schema']
        for tname in tnames:
            print("Loading {}".format(tname))
            # Only load the first 3 years of data for the order tables at this point
            # We will load the 2022 data later in the lab
            if tname in ['order_header', 'order_detail']:
                for year in ['2019', '2020', '2021']:
                    load_raw_table(session, tname=tname, s3dir=s3dir, year=year, schema=schema)
            else:
                load_raw_table(session, tname=tname, s3dir=s3dir, schema=schema)

    _ = session.sql("ALTER WAREHOUSE HOL_WH SET WAREHOUSE_SIZE = XSMALL").collect()

def validate_raw_tables(session):
    # check column names from the inferred schema
    for tname in POS_TABLES:
        print('{}: \n\t{}\n'.format(tname, session.table('RAW_POS.{}'.format(tname)).columns))

    for tname in CUSTOMER_TABLES:
        print('{}: \n\t{}\n'.format(tname, session.table('RAW_CUSTOMER.{}'.format(tname)).columns))


# For local debugging
if __name__ == "__main__":
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

    #session = Session.builder.configs(connection_parameters).create()


# 以降、session を使って処理
#df = session.table("RAW_WEATHER_DATA")
#df.show()

# 最後にセッションを閉じる（任意）
#session.close()

   # with Session.builder.getOrCreate() as session:
      #  load_all_raw_tables(session)
#        validate_raw_tables(session)
