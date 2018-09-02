import boto3
import click

from botocore.exceptions import ClientError

session = boto3.Session(profile_name='PythonAutomation')
s3 = session.resource('s3')

@click.group()
def cli():
    """
    Webotran deploys website to AWS\n
        s3.buckets.all()\n
        s3.Bucket('bucket').objects.all()\n
        s3.create_bucket(Bucket=bucket)\n
        bucket.Policy
    """
    pass

@cli.command("list-buckets")
def list_buckets():
    "List all of s3 buckets"
    for bucket in s3.buckets.all():
        print(bucket)

@cli.command("list-bucket-objects")
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List bucket objects"
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)

@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "Create and configure s3 bucket"
    new_bucket = None
    try:
       
        print(session.region_name)
        new_bucket = s3.create_bucket(Bucket=bucket)
        #new_bucket = s3.create_bucket(Bucket=bucket,
        # CreateBucketConfiguration={'LocationConstraint':session.region_name}
        # )

    except ClientError as e:
        print(e)
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            new_bucket = s3.Bucket(bucket)
        elif e.response['Error']['Code'] == 'BucketAlreadyExists':
            new_bucket = s3.Bucket(bucket)
            print("MM:Bucket Already Exists Exception Trapped")
            print(e.response)
            print(new_bucket)
            print("MM End:Bucket Already Exists Exception Trapped")
        else:
            raise e

    policy = """
    {
      "Version": "2012-10-17",
      "Statement": 
      [
      {
        "Sid":"PublicReadGetObjectMM",
        "Effect": "Allow",
        "Principal":"*",
        "Action": "s3:GetObject",
        "Resource": [ "arn:aws:s3:::%s/*" ]
      }
      ]
    }
    """ % new_bucket.name

    print("Policy is: ")
    print(policy)

    policy = policy.strip()
    pol = new_bucket.Policy()
        
    try:
        pol.put(Policy=policy)
    except Exception as e:
        print("Exception in put policy")
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e)
        raise(e)
        
    print("Creating new website")
    try:
        ws = new_bucket.Website()
    except  Exception as e:
        print("Exception in new_bucket.Website")
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e)
        raise(e)

    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key':'error.html'
            },
        'IndexDocument': {
            'Suffix': 'index.html'
            }}
    )

    return


if __name__ == '__main__':
    cli()
