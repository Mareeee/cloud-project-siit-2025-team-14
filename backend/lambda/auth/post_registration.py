import boto3

def handler(event, context):
    client = boto3.client('cognito-idp')
    user_pool_id = event['userPoolId']
    username = event['userName']
    group_name = 'User'
    
    try:
        client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=group_name
        )
        print(f"User {username} added to group {group_name}")
    except Exception as e:
        print(f"Error adding user to group: {e}")

    return event
