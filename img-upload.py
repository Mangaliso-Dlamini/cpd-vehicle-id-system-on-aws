import boto3
import time
import os

def upload_image_to_s3(bucket_name, image_path):
    s3_client = boto3.client('s3')
    filename = os.path.basename(image_path)
    try:
        s3_client.upload_file(image_path, bucket_name, filename)
        print(f"Uploaded {filename} to S3 bucket {bucket_name}")
    except Exception as e:
        print(f"Failed to upload {filename}: {e}")

def main():
    bucket_name = 's3-s2110978'  # Replace with your S3 bucket name
    image_folder = '/home/ec2-user/Images'  # Path to the folder containing images

    image_files = os.listdir(image_folder)
    for image_file in image_files:
        if image_file.endswith('.jpg') or image_file.endswith('.jpeg') or image_file.endswith('.png'):
            image_path = os.path.join(image_folder, image_file)
            upload_image_to_s3(bucket_name, image_path)
            time.sleep(30)  # Wait for 30 seconds before uploading the next image

if __name__ == "__main__":
    main()
