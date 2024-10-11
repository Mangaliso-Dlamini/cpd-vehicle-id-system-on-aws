import json
import boto3
import re
import time

def lambda_handler(event, context):
    # Extract message details from the SQS event
    records = event['Records']
    
    # Initialize DynamoDB client
    dynamodb_client = boto3.client('dynamodb')
    
    # Initialize SES client for sending emails
    ses_client = boto3.client('ses')  # Change region if necessary
    
    for record in records:
        s3 = record['s3']
        image_bucket = s3['bucket']['name']
        image_key = s3['object']['key']
        
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
        labels = [{'Name': label['Name'], 'Confidence': label['Confidence']} for label in response_labels['Labels']]
        texts = [text['DetectedText'] for text in response_text['TextDetections']]

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

                else:
                    print("No recognized format in:", text)
                    license_no = None

        
        # Store results in DynamoDB
        dynamodb_table_name = 'entries_S2110978'
        for label in labels:
            dynamodb_client.put_item(
                TableName=dynamodb_table_name,
                Item={
                    'image_name': {'S': image_key},
                    'label': {'S': label['Name']},
                    'confidence_score': {'N': str(label['Confidence'])},
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
                send_email_notification(text)
        else:
            # Vehicle not found in the table, send email notification
            send_email_notification(f"Unidentified vehicle: {text}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Labels and Text detected successfully!')
    }

def send_email_notification(message):
    ses_client = boto3.client('ses')
    
    # Specify sender and recipient email addresses
    sender = "john.doe@example.com"
    recipient = "m.dlamini@alustudent.com"  # Change to security officer's email address
    
    # Specify email subject and body
    subject = "Security Alert: Suspicious Vehicle Detected"
    body = f"Attention Security Officer,\n\n{message}\n\nPlease take necessary action."
    
    # Send email using Amazon SES
    ses_client.send_email(
        Source=sender,
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
