import subprocess
import shlex
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
# import snowflake.permissions as permissions

# API Ref: https://docs.snowflake.com/developer-guide/snowpark/reference/python/latest/snowpark/index

app_name = "ESG PDF Search"
app_package_name = "esg_pdf_search_pkg_u101099"
connection_parameters = {
    "user": "nedasi",
    "password": "!Working on 77th Tonight!",
    "account": "wxthvsy-rob57157"
}

# pip install snowflake-native-apps-permission
# pip install snowflake-snowpark-python
# Deploy the 'esg_pdf_search' app to Snowflake using the Snowflake CLI
def run_snow_cli(cmd_args: str):
    try:
        args = shlex.split(cmd_args)
        result = subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
            cwd="./snowflake_apps/esg_pdf_search"
        )
        print("Deployment output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Deployment failed:\n", e.stderr)


# run_snow_cli("snow app deploy --connection SF_TRIAL_7 --verbose")
sql = f'DROP APPLICATION IF EXISTS \\\"{app_name}\\\" CASCADE;'
print(f'snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose')
run_snow_cli(f'snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose')

sql = 'DROP APPLICATION PACKAGE IF EXISTS ESG_PDF_SEARCH_PKG_U101099;'
print(f'snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose')
run_snow_cli(f"snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose")
# input("Press Enter to continue...")

run_snow_cli("snow app deploy --connection SF_TRIAL_7 --verbose")

# run_snow_cli("snow app publish --create-version --connection SF_TRIAL_7 --verbose --force")
# input("Press Enter to continue...")


# sql = f'CREATE APPLICATION \\\"{app_name}\\\" FROM APPLICATION PACKAGE {app_package_name} USING VERSION v1_0;'
# print(f'snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose')
# run_snow_cli(f"snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose")

# sql = 'ALTER APPLICATION \\\"{app_name}\\\" SET DEBUG_MODE = TRUE;'
# print(f'snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose')
# run_snow_cli(f"snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose")


sql = f'create application \\\"{app_name}\\\" from application package {app_package_name} using @{app_package_name}.app_src.stage debug_mode = True comment = GENERATED_BY_NEILSNOWFLAKECLI;'
print(f'snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose')
run_snow_cli(f"snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose")


sql = f'GRANT READ SESSION ON ACCOUNT TO APPLICATION \\\"{app_name}\\\"'
print(f'snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose')
run_snow_cli(f"snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose")


sql = f'GRANT READ on stage CC_QUICKSTART_CORTEX_SEARCH_DOCS.data.docs TO APPLICATION \\\"{app_name}\\\"'
print(f'snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose')
run_snow_cli(f"snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose")


sql = f"CALL \\\"{app_name}\\\".config.register_single_reference('DOCS_INTERNAL_STAGE' , 'ADD', SYSTEM$REFERENCE('stage', 'CC_QUICKSTART_CORTEX_SEARCH_DOCS.DATA.docs', 'persistent', 'read'));"
print(f'snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose')
run_snow_cli(f"snow sql -c SF_TRIAL_7 -q \"{sql}\" --verbose")

# SHOW REFERENCES IN APPLICATION "ESG PDF Search";
# SELECT SYSTEM$REFERENCE('stage', 'CC_QUICKSTART_CORTEX_SEARCH_DOCS.DATA.docs', 'persistent', 'read');
