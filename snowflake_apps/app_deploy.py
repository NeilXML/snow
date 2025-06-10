import subprocess

# Deploy the 'esg_pdf_search' app to Snowflake using the Snowflake CLI
def deploy_app():
    try:
        result = subprocess.run(
            ["snow", "app", "deploy", "esg_pdf_search"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Deployment output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Deployment failed:\n", e.stderr)

if __name__ == "__main__":
    deploy_app()