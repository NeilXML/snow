-- This is the setup script that runs while installing a Snowflake Native App in a consumer account.
-- For more information on how to create setup file, visit https://docs.snowflake.com/en/developer-guide/native-apps/creating-setup-script

-- A general guideline to building this script looks like:
-- 1. Create application roles
CREATE APPLICATION ROLE IF NOT EXISTS app_public;

-- 2. Create a versioned schema to hold those UDFs/Stored Procedures
CREATE OR ALTER VERSIONED SCHEMA core;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_public;

-- 3. Create UDFs and Stored Procedures using the python code you wrote in src/module-add, as shown below.
CREATE OR REPLACE FUNCTION core.add(x NUMBER, y NUMBER)
  RETURNS NUMBER
  LANGUAGE PYTHON
  RUNTIME_VERSION=3.8
  PACKAGES=('snowflake-snowpark-python')
  IMPORTS=('/module-add/add.py')
  HANDLER='add.add_fn';

CREATE OR REPLACE PROCEDURE core.increment_by_one(x NUMBER)
  RETURNS NUMBER
  LANGUAGE PYTHON
  RUNTIME_VERSION=3.8
  PACKAGES=('snowflake-snowpark-python')
  IMPORTS=('/module-add/add.py')
  HANDLER='add.increment_by_one_fn';


-- 4. Grant appropriate privileges over these objects to your application roles.
GRANT USAGE ON FUNCTION core.add(NUMBER, NUMBER) TO APPLICATION ROLE app_public;
GRANT USAGE ON PROCEDURE core.increment_by_one(NUMBER) TO APPLICATION ROLE app_public;

-- 5. Create a streamlit object using the code you wrote in you wrote in src/module-ui, as shown below.
-- The `from` value is derived from the stage path described in snowflake.yml
CREATE OR REPLACE STREAMLIT core.ui
     FROM '/streamlit/'
     MAIN_FILE = 'ui.py';

-- 6. Grant appropriate privileges over these objects to your application roles.
GRANT USAGE ON STREAMLIT core.ui TO APPLICATION ROLE app_public;

-- A detailed explanation can be found at https://docs.snowflake.com/en/developer-guide/native-apps/adding-streamlit

-- Neil ref https://docs.snowflake.com/en/developer-guide/native-apps/requesting-refs#label-native-apps-reference-supported-functions
-- CREATE or replace ROLE app_admin;
CREATE OR ALTER VERSIONED SCHEMA config;
CREATE APPLICATION ROLE if not exists app_admin;
GRANT USAGE ON SCHEMA config TO APPLICATION ROLE app_admin;
CREATE or alter PROCEDURE CONFIG.REGISTER_SINGLE_REFERENCE(ref_name STRING, operation STRING, ref_or_alias STRING)
  RETURNS STRING
  LANGUAGE SQL
  AS $$
    BEGIN
      CASE (operation)
        WHEN 'ADD' THEN
          SELECT SYSTEM$SET_REFERENCE(:ref_name, :ref_or_alias);
        WHEN 'REMOVE' THEN
          SELECT SYSTEM$REMOVE_REFERENCE(:ref_name, :ref_or_alias);
        WHEN 'CLEAR' THEN
          SELECT SYSTEM$REMOVE_ALL_REFERENCES(:ref_name);
      ELSE
        RETURN 'unknown operation: ' || operation;
      END CASE;
      RETURN NULL;
    END;
  $$;

GRANT USAGE ON PROCEDURE CONFIG.REGISTER_SINGLE_REFERENCE(STRING, STRING, STRING) TO APPLICATION ROLE app_admin;
