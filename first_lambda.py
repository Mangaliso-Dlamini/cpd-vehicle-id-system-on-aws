import json
import boto3

def lambda_handler(event, context):
    # Extract message details from the SQS event
    records = event['Records']
    for record in records:
        sqs_message = json.loads(record['body'])
        image_bucket = sqs_message['image_bucket']
        image_key = sqs_message['image_key']
        
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
        labels = [label['Name'] for label in response_labels['Labels']]
        texts = [text['DetectedText'] for text in response_text['TextDetections']]

        # Output the results
        print("Detected Labels:", labels)
        print("Detected Texts:", texts)
        
    return {
        'statusCode': 200,
        'body': json.dumps('Labels and Text detected successfully!')
    }
