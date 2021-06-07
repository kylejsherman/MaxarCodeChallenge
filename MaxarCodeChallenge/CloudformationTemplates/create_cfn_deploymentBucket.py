from troposphere import Output, Ref, Template
from troposphere.s3 import Bucket
template = Template()

s3_bucket = template.add_resource(
    Bucket(
        'CodeChallengeDeploymentBucket',
        BucketName='code-challenge-deployment-bucket'
    )
)

template.add_output(
    Output(
        "BucketName",
        Value=Ref(s3_bucket),
        Description='Name of s3 bucket to hold deployment package'
    )
)

with open('deploymentBucket.json', 'w') as f:
    f.write(template.to_json())