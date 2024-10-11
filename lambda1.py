import json
import boto3
import re
import time
from boto3.dynamodb.types import TypeSerializer
from decimal import Decimal

def lambda_handler(event, context):
    # Extract message details from the SQS event
    print(event)
    records = event['Records']
    
    # Initialize DynamoDB client
    dynamodb_client = boto3.client('dynamodb')
    
    # Initialize SES client for sending emails
    ses_client = boto3.client('ses')  # Change region if necessary
    
    for record in records:
        sqs_message = json.loads(record['body'])
        print(sqs_message)
        image_bucket = sqs_message['Records'][0]['s3']['bucket']['name']
        image_key = sqs_message['Records'][0]['s3']['object']['key']

        #body = record['s3']
        #image_bucket = s3['bucket']['name']
        #image_key = s3['object']['key']
        
        # Initialize Rekognition client
        rekognition_client = boto3.client('rekognition')
        
        # Detect labels
        response_labels = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': image_bucket,
                    'Name': image_key
                }
            }
        )
        
        time.sleep(1)
        
        # Detect text
        response_text = rekognition_client.detect_text(
            Image={
                'S3Object': {
                    'Bucket': image_bucket,
                    'Name': image_key
                }
            }
        )
        
        # Process label and text detection responses
        labels = [{'Name': label['Name'], 'Confidence': Decimal(str(label['Confidence']))} for label in response_labels['Labels']]
        texts = [text['DetectedText'] for text in response_text['TextDetections']]
        
        serializer = TypeSerializer()
        serialized_labels = [
            {key: serializer.serialize(value) for key, value in item.items()} for item in labels
        ]

        full_pattern = r'\b\d{4}\s[A-Z]{2}\s\d{2}\b'
        h1_pattern = r'\b\d{4}\b'
        h2_pattern = r'\b[A-Z]{2}\s\d{2}\b'

        for text in texts:
            match = re.search(full_pattern, text)
            if match:
                license_no = match.group()
                print("Full format recognized:", license_no)
                break
            else:
                match_h1 = re.search(h1_pattern, text)
                match_h2 = re.search(h2_pattern, text)
                h1 = match_h1.group() if match_h1 else None
                h2 = match_h2.group() if match_h2 else None
                if h1:
                    license_no = h1
                    print("1st part format recognized:", h1)
                elif h2 and license_no:
                    license_no= license_no + ' ' + h2
                    print("2nd part format recognized:", h2)
                    break
                else:
                    print("No recognized format in:", text)
                    license_no = ''

        
        # Store results in DynamoDB
        dynamodb_table_name = 'entries_S2110978'
        
        dynamodb_client.put_item(
            TableName=dynamodb_table_name,
            Item={
                'image_name': {'S': image_key},
                'labels': {'L': [{'M': {key: {'S': str(value)} for key, value in item.items()}} for item in labels]},
                'license_no': {'S': license_no}
            }
        )
        
        # Check if vehicle is whitelisted or blacklisted
        vehicle_table_name = 'vehicles_S2110978'
        #for text in texts:
        response = dynamodb_client.get_item(
            TableName=vehicle_table_name,
            Key={
                'license_no': {'S': license_no}
            }
        )
        if 'Item' in response:
            # Vehicle found in the table, check if whitelisted or blacklisted
            vehicle_info = response['Item']
            status = vehicle_info.get('status', {}).get('S', '')
            if status == 'blacklisted':
                # Vehicle is blacklisted, send email notification
                #send_email_notification(text)
                trigger("Blacklisted vehicle.")
        else:
            # Vehicle not found in the table, send email notification
            trigger("Unidentified vehicle.")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Labels and Text detected successfully!')

    }


def trigger(value):
    lambda_client = boto3.client('lambda')

    # Define parameters for the invocation
    target_function_name = 'publish_sns'
    payload = {
        # payload to be passed to the target function if needed
        'key': value
    }

    # Invoke the target Lambda function
    response = lambda_client.invoke(
        FunctionName=target_function_name,
        InvocationType='Event',  # Use 'Event' for asynchronous invocation
        Payload=json.dumps(payload)
    )

    # Handle response if needed
    # For asynchronous invocation, you may not get a response immediately

    # Example of handling response
    if response['StatusCode'] == 202:
        print("Lambda function invoked successfully")
    else:
        print("Error invoking Lambda function")

    # Optionally, return a response to the caller
    return {
        'statusCode': 200,
        'body': json.dumps('Lambda function invoked successfully')
    }