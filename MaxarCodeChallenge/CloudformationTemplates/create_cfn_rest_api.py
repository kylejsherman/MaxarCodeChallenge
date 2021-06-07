from troposphere import (GetAtt, 
                         Join,
                         Output, 
                         Ref,
                         Template)
from troposphere.apigateway import (Deployment,
                                    Integration,
                                    IntegrationResponse,
                                    Method,
                                    MethodResponse,
                                    Resource,
                                    RestApi,
                                    Stage)
from troposphere.iam import Policy, Role
from troposphere.awslambda import Code, Function, Permission

template = Template()

# Create Lambda execution role
template.add_resource(
    Role(
        "jsonCompareLambdaExecutionRole",
        RoleName='jsonCompareLambdaExecutionRole',
        AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": ["lambda.amazonaws.com"]
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
    )
)

# Create Lambda function
lambda_function = template.add_resource(
    Function(
        'JsonCompareFunction',
        DependsOn='jsonCompareLambdaExecutionRole',
        Handler='jsonCompare.polygon_intersect',
        Code=Code(
            S3Bucket='code-challenge-deployment-bucket',
            S3Key='jsonCompareLambdaPackage.zip'),
        Role=GetAtt('jsonCompareLambdaExecutionRole', 'Arn'),
        Runtime='python3.8',
        FunctionName='JsonCompareFunction'
    )
)

# Create permission for Api Gateway to invoke Lambda
template.add_resource(
    Permission(
        'jsonCompareLambdaInvokePermission',
        DependsOn='JsonCompareFunction',
        Action='lambda:InvokeFunction',
        FunctionName=GetAtt('JsonCompareFunction', 'Arn'),
        Principal='apigateway.amazonaws.com'
    )
)

# Create Api Gateway
rest_api = template.add_resource(
    RestApi(
        'JsonCompareAPI',
        Name='JsonCompareAPI'
    )
)

# Create an API resource
api_resource = template.add_resource(
    Resource(
        "jsonCompareLambdaResource",
        RestApiId=Ref(rest_api),
        PathPart='polygon_intersect',
        ParentId=GetAtt('JsonCompareAPI', 'RootResourceId')
    )
)

# Create API method for Lambda resource
api_method = template.add_resource(
    Method(
        'jsonCompareLambdaMethod',
        DependsOn='JsonCompareFunction',
        ApiKeyRequired=False,
        AuthorizationType='NONE',
        HttpMethod='POST',
        ResourceId=Ref(api_resource),
        RestApiId=Ref(rest_api),
        Integration=Integration(
            Type='AWS',
            IntegrationHttpMethod='POST',
            IntegrationResponses=[
                IntegrationResponse(
                    StatusCode='200'
                )
            ],
            Uri=Join(
                '',
                [
                    'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/',
                    GetAtt('JsonCompareFunction', 'Arn'),
                    '/invocations'
                ]
            )
        ),
        MethodResponses=[
            MethodResponse(
                'jsonCompareLambdaResponse',
                StatusCode='200'
            )
        ]
    )
)

stage_name = 'v1'
deployment_name = 'Test'

api_deployment = template.add_resource(
    Deployment(
        f'{deployment_name}Deployment',
        DependsOn='jsonCompareLambdaMethod',
        RestApiId=Ref(rest_api)
    )
)

api_stage = template.add_resource(
    Stage(
        f'Stage{stage_name}',
        StageName=stage_name,
        RestApiId=Ref(rest_api),
        DeploymentId=Ref(api_deployment)
    )
)

template.add_output(
    [
        Output(
            'ApiInformation',
            Value=Join(
                '',
                [
                    'https://',
                    Ref(rest_api),
                    '.execute-api.us-east-1.amazonaws.com/',
                    stage_name,
                    '/polygon_intersect'
                ]
            ),
            Description='Enpoint address for this stage of the API'
        )
    ]
)

with open('apiDeployment.json', 'w') as f:
    f.write(template.to_json())