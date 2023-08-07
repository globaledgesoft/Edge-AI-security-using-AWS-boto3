import os
import json
from tqdm import tqdm
import boto3
from botocore.exceptions import ClientError

class AwsAgent:
    def __init__(self, access_key, secret_key, region):
        self.s3 = boto3.client('s3',
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        region_name=region)


    def download_from_s3(self, bucket, key, filename, sse_type="default", encryption_key=None):
        if sse_type == "SSE_C":
            if encryption_key is None:
                print("Error ! Customer key must be provided in case of SSE_C method")
                exit(0)
            extra_args={
                'SSECustomerAlgorithm': 'AES256',
                'SSECustomerKey': str(encryption_key)
            }
            try:
                meta_data = self.s3.head_object(Bucket=bucket, Key=key, SSECustomerAlgorithm='AES256',SSECustomerKey=encryption_key)
            except ClientError as e:
                print(f"Error occurred:", e)
                exit()
        elif sse_type=="KMS":
            try:
                meta_data = self.s3.head_object(Bucket=bucket, Key=key)
            except ClientError as e:
                print(f"Error occurred:", e)
                exit()
            extra_args={}
        else:
            try:
                meta_data = self.s3.head_object(Bucket=bucket, Key=key)
            except ClientError as e:
                print(f"Error occurred:", e)
                exit()
            extra_args = {}
        total_length = int(meta_data.get('ContentLength', 0))
        print(f"Downloading the file : {key} From bucket : {bucket}, File size : {round(total_length/1024/1024)} MB")
        with tqdm(total=total_length,  desc=f'source: s3://{bucket}/{key}',
            bar_format="{percentage:.1f}%|{bar:25} | {rate_fmt} | {desc}",  unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            self.s3.download_file(bucket, key, Filename=filename, Callback=pbar.update, ExtraArgs=extra_args)


    def upload_to_s3(self, bucket, key, filename, sse_type="default", encryption_key=None):
        file_size = os.stat(filename).st_size
        if sse_type == "SSE_C":
            if encryption_key is None:
                print("Error ! Customer key must be provided in case of SSE_C method")
                exit(0) 
            extra_args = {
                'SSECustomerAlgorithm': 'AES256',
                'SSECustomerKey': encryption_key,

            }   
            
        elif sse_type == "KMS": 
            extra_args={'ServerSideEncryption': 'aws:kms', 'SSEKMSKeyId': encryption_key}
        else:
                extra_args = {}
        print(f"Uploading the file : {filename} To bucket : {bucket}, File size : {round(file_size/1024/1024, 3)} MB")
        with tqdm(total=file_size, bar_format="{percentage:.1f}%|{bar:50} | {rate_fmt} | {desc}" ,unit="B", unit_scale=True, desc=filename) as pbar:
                self.s3.upload_file(Filename=filename,Bucket=bucket,Key=key,
                            Callback=lambda bytes_transferred: pbar.update(bytes_transferred),
                            ExtraArgs=extra_args)
