import boto3
import time
import os

def upload_image_to_s3(bucket_name, image_path):
    s3_client = boto3.client('s3')
    filename = os.path.basename(image_path)
    try:
        s3_client.upload_file(image_path, bucket_name, filename)
        print(f"Uploaded {filename} to S3 bucket {bucket_name}")
        return filename
    except Exception as e:
        print(f"Failed to upload {filename}: {e}")
        return None

def send_message_to_sqs(queue_url, message_body):
    sqs_client = boto3.client('sqs')
    try:
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body
        )
        print("Sent message to SQS queue")
        return response['MessageId']
    except Exception as e:
        print(f"Failed to send message to SQS queue: {e}")
        return None

def main():
    bucket_name = 's3_s2110978'  # Replace with your S3 bucket name
    image_folder = '/home/ec2-user/Images'  # Path to the folder containing images
    sqs_queue_url = 'https://sqs.us-east-1.amazonaws.com/743442590334/SQS_S2110978'  # Replace with your SQS queue URL

    image_files = os.listdir(image_folder)
    for image_file in image_files:
        if image_file.endswith('.jpg') or image_file.endswith('.jpeg') or image_file.endswith('.png'):
            image_path = os.path.join(image_folder, image_file)
            uploaded_filename = upload_image_to_s3(bucket_name, image_path)
            if uploaded_filename:
                message_body = f"Image {uploaded_filename} uploaded to S3 bucket {bucket_name}"
                send_message_to_sqs(sqs_queue_url, message_body)
            time.sleep(30)  # Wait for 30 seconds before uploading the next image

if __name__ == "__main__":
    main()
