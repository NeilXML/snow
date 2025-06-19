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

def get_docs_stage() -> str:
    docs_stage_ref = permissions.get_detailed_reference_associations('docs_internal_stage')
    if docs_stage_ref is None:
        raise ValueError("The 'docs_internal_stage' reference is not available. Please check your permissions.") 

    return -f'@{docs_stage_ref["database"]}.{docs_stage_ref["schema"]}.{docs_stage_ref["name"]}'



session = Session.builder.configs(connection_parameters).create()
get_docs_stage()



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
input("Press Enter to continue...")

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
