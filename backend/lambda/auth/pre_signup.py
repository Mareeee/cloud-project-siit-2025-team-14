import boto3

client = boto3.client('cognito-idp')

def handler(event, context):
    user_pool_id = event['userPoolId']
    email = event['request']['userAttributes'].get('email')

    if email:
        existing_users = client.list_users(
            UserPoolId=user_pool_id,
            AttributesToGet=['email'],
            Filter=f'email = "{email}"'
        )

        if existing_users['Users']:
            raise Exception("Email already exists")

    event['response']['autoConfirmUser'] = True
    event['response']['autoVerifyEmail'] = True

    return event
