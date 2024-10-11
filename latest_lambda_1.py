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
        
        full_patterns = [r'\b\d{3}\s[A-Z]{2}\s\d{2}\b', r'\b\d{4}\s[A-Z]{2}\s\d{2}\b', r'\b\d{5}\s[A-Z]{2}\s\d{2}\b']
        h1_patterns = [r'\b\d{3}\b', r'\b\d{4}\b', r'\b\d{5}\b']
        h2_pattern = r'\b[A-Z]{2}\s\d{2}\b'

        license_no = None
        temp = None

        for text in texts:
            for full_pattern in full_patterns:
                match = re.search(full_pattern, text)
                if match:
                    license_no = match.group()
                    print("Full format recognized:", license_no)
                    break

            if license_no:
                break
            else:
                # Define temp here
                for h1_pattern in h1_patterns:
                    #if temp:
                        #break
                    match_h1 = re.search(h1_pattern, text)
                    if match_h1:
                        temp = match_h1.group()  # Update temp if a match is found
                        print("1st part format recognized:", temp)
                        break  # Break out of the loop once a match is found
                match_h2 = re.search(h2_pattern, text)
                h2 = match_h2.group() if match_h2 else None
                if temp and h2:
                    license_no = temp + ' ' + h2
                    print("2nd part format recognized:", h2)
                    break
                else:
                    print("No recognized format in:", text)
                    license_no = None

        print("Final license number:", license_no)


       """ full_pattern = r'\b\d{4}\s[A-Z]{2}\s\d{2}\b'
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

        """
        


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
                publish_to_sns("Blacklisted vehicle.")
        else:
            # Vehicle not found in the table, send email notification
            publish_to_sns("Unidentified vehicle.")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Labels and Text detected successfully!')

    }

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


