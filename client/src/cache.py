import boto3

dynamodb_client = boto3.resource('dynamodb', region_name='us-east-2')

PAYWALLS = dynamodb_client.Table('PaywallBotPaywall').scan()['Items']
EMOJIS = dynamodb_client.Table('PaywallBotEmoji').scan()['Items']
REPLIES = dynamodb_client.Table('PaywallBotReply').scan()['Items']