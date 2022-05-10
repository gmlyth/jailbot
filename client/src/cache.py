import boto3

dynamodb_client = boto3.resource('dynamodb', region_name='us-east-2')

PAYWALLS = []
EMOJIS = []
REPLIES = []