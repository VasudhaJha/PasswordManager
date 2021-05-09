import boto3

s3 = boto3.resource('s3')

def create_bucket():
    bucket = s3.Bucket('password-manager-us-west-2')
    bucket.create(
        ACL='private',
        CreateBucketConfiguration={
            'LocationConstraint': 'us-west-2'
        }
    )

if __name__ == "__main__":
    create_bucket()


