import boto3

dynamodb_client = boto3.resource('dynamodb', region_name='us-east-2')
kinesis_client = boto3.client('kinesis', region_name='us-east-2')
KINESIS_STREAM_NAME = None

PAYWALLS = dynamodb_client.Table('PaywallBotPaywall').scan()['Items']
EMOJIS = dynamodb_client.Table('PaywallBotEmoji').scan()['Items']
REPLIES = dynamodb_client.Table('PaywallBotReply').scan()['Items']
BLOCKED_USERS = dynamodb_client.Table('PaywallBotBlockedUser').scan()['Items']