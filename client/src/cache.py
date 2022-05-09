import boto3

dynamodb_client = boto3.resource('dynamodb')

PAYWALLS = []
EMOJIS = []
REPLIES = []