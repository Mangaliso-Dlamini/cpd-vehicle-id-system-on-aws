import boto3
import json

def lambda_handle(event, context):
    payload = json.loads(event['body'])
    message = payload['key']
    

def publish_to_sns(message):
    # Initialize the SNS client
    sns_client = boto3.client('sns')
    topic_arn = "arn:aws:sns:us-east-1:743442590334:topic_s2110978"
    subject = "Security Alert: Suspicious Vehicle Detected"
    body = f"Attention Security Officer,\n\n{message}\n\nPlease take necessary action."

    # Publish the message to the specified SNS topic
    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=body,
        Subject=subject
    )

    return response
