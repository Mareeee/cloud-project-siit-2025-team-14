import os
import aws_cdk as cdk
from backend.backend_stack import BackendStack
from backend.auth_stack import AuthStack

app = cdk.App()

dev_name = os.getenv("DEV_NAME", "LocalDev")
branch = os.getenv("GITHUB_REF_NAME", "")
if branch == "main":
    dev_name = "Prod"

BackendStack(app, f"BackendStack-{dev_name}")
AuthStack(app, f"AuthStack-{dev_name}")

app.synth()
