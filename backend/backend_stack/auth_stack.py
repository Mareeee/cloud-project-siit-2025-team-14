from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    aws_lambda as _lambda,
    custom_resources as cr,
    CustomResource,
    CfnOutput,
    RemovalPolicy,
    Duration
)
from constructs import Construct

class AuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name="UserPoolApp",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(username=True, email=False),
            auto_verify=cognito.AutoVerifiedAttrs(email=False, phone=False),
            standard_attributes=cognito.StandardAttributes(
                given_name=cognito.StandardAttribute(required=True, mutable=True),
                family_name=cognito.StandardAttribute(required=True, mutable=True),
                birthdate=cognito.StandardAttribute(required=True, mutable=True),
                email=cognito.StandardAttribute(required=True, mutable=True)
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False
            ),
            account_recovery=cognito.AccountRecovery.NONE,
            removal_policy=RemovalPolicy.DESTROY,  # za testiranje
        )

        self.user_pool = user_pool

        user_pool_client = user_pool.add_client(
            "UserPoolClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                user_password=True,
                user_srp=True
            ),
            prevent_user_existence_errors=True
        )

        admin_group = cognito.CfnUserPoolGroup(
            self, "AdminGroup",
            group_name="Admin",
            user_pool_id=user_pool.user_pool_id
        )

        user_group = cognito.CfnUserPoolGroup(
            self, "UserGroup",
            group_name="User",
            user_pool_id=user_pool.user_pool_id
        )

        hosting_bucket = s3.Bucket(
            self, "FrontendHostingBucket",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        distribution = cloudfront.Distribution(
            self, "FrontendDistribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3StaticWebsiteOrigin(hosting_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            )
        )

        CfnOutput(
            self, "CognitoUserPoolId",
            value=user_pool.user_pool_id
        )

        CfnOutput(
            self, "CognitoUserPoolClientId",
            value=user_pool_client.user_pool_client_id
        )

        CfnOutput(
            self, "FrontendBucketName",
            value=hosting_bucket.bucket_name
        )

        CfnOutput(
            self, "CloudFrontURL",
            value=f"https://{distribution.domain_name}"
        )

        self.pre_signup_lambda = _lambda.Function(
            self, "PreSignUpLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="auth.pre_signup.handler"
        )

        self.pre_signup_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["cognito-idp:ListUsers"],
                resources=["*"]
            )
        )

        user_pool.add_trigger(
            cognito.UserPoolOperation.PRE_SIGN_UP,
            self.pre_signup_lambda
        )

        self.post_registration_lambda = _lambda.Function(
            self, 'PostRegistrationLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='auth.post_registration.handler'
        )

        user_pool.add_trigger(
            cognito.UserPoolOperation.POST_CONFIRMATION,
            self.post_registration_lambda
        )

        self.post_registration_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["cognito-idp:AdminAddUserToGroup"],
                resources=["*"]
            )
        )

        # hardkodovanje admina
        self.create_admin_lambda = _lambda.Function(
            self, "CreateAdminUserLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="auth.create_admin.handler",
            timeout=Duration.seconds(60)
        )

        self.create_admin_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminSetUserPassword",
                    "cognito-idp:AdminAddUserToGroup",
                    "cognito-idp:AdminGetUser"
                ],
                resources=["*"]
            )
        )

        provider = cr.Provider(
            self, "CreateAdminUserProvider",
            on_event_handler=self.create_admin_lambda
        )

        custom_resource = CustomResource(
            self, "CreateAdminUserCustomResource",
            service_token=provider.service_token,
            properties={
                "UserPoolId": user_pool.user_pool_id,
                "AdminUsername": "admin",
                "AdminPassword": "Admin123",
                "AdminEmail": "admin@example.com"
            }
        )

        custom_resource.node.add_dependency(user_pool)
