import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes
import json

def lambda_handler(event, context):
    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
    sns = boto3.resource('sns')

    topic = sns.Topic('arn:aws:sns:us-east-1:242068192840:deployPortfolioTopic')

    try:
        portfolio_bucket = s3.Bucket('portfolio.patricklang.net')
        build_bucket = s3.Bucket('portfoliobuild.patricklang.net')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print 'Job Done'

        topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed Successfully")
    except:
        topic.publish(Subject="Portfolio Deployment Failed", Message="Portfolio Deployment Failed")
        raise

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
