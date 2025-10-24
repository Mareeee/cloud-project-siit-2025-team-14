import boto3
import json
import urllib3

http = urllib3.PoolManager()

def send_response(event, context, status, data):
    response_body = json.dumps({
        "Status": status,
        "Reason": f"See the details in CloudWatch Log Stream: {context.log_stream_name}",
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Data": data
    })

    response_url = event["ResponseURL"]
    headers = {"content-type": "", "content-length": str(len(response_body))}
    http.request("PUT", response_url, body=response_body, headers=headers)

def handler(event, context):
    cognito = boto3.client('cognito-idp')
    print("Event received:", json.dumps(event))
    try:
        user_pool_id = event['ResourceProperties']['UserPoolId']
        username = event['ResourceProperties']['AdminUsername']
        password = event['ResourceProperties']['AdminPassword']
        email = event['ResourceProperties']['AdminEmail']

        if event['RequestType'] in ['Create', 'Update']:
            try:
                cognito.admin_get_user(UserPoolId=user_pool_id, Username=username)
                print("Admin already exists.")
            except cognito.exceptions.UserNotFoundException:
                print("Creating admin user...")
                cognito.admin_create_user(
                    UserPoolId=user_pool_id,
                    Username=username,
                    UserAttributes=[
                        {'Name': 'email', 'Value': email},
                        {'Name': 'email_verified', 'Value': 'true'},
                        {'Name': 'given_name', 'Value': 'Admin'},
                        {'Name': 'family_name', 'Value': 'User'}
                    ],
                    TemporaryPassword=password,
                    MessageAction='SUPPRESS'
                )

                cognito.admin_set_user_password(
                    UserPoolId=user_pool_id,
                    Username=username,
                    Password=password,
                    Permanent=True
                )

            cognito.admin_add_user_to_group(
                UserPoolId=user_pool_id,
                Username=username,
                GroupName='Admin'
            )

        send_response(event, context, "SUCCESS", {"Message": "Admin user created or already exists."})
    except Exception as e:
        print(f"Error: {e}")
        send_response(event, context, "FAILED", {"Error": str(e)})
