import os
import json
import argparse
from boto_client import AwsAgent

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--encryption_type", help = "Specify the SSE encryption format. Supported Encryption : default, SSE_C, KMS", required=True)

args = parser.parse_args()
ENCRYPTED_UPLOAD = "default"
if args.encryption_type in ["default", "KMS", "SSE_C"]:
	ENCRYPTED_UPLOAD = args.encryption_type
else:
    print("Please choose from supported encryption Formats: default, SSE_C, KMS")
    exit(0)
print(ENCRYPTED_UPLOAD)

with open("config/aws_config.json") as json_data_file:
    aws_data = json.load(json_data_file)
    access_key = aws_data.get("access_key")
    secret_key = aws_data.get("secret_key")
    region = aws_data.get("region")
    bucket_name = aws_data.get("bucket_name")

if access_key is None:
    print("Please specify AWS Access key correctly in config file.")
    exit(0)
if secret_key is None:
    print("Please specify AWS Secret key correctly in config file.")
    exit(0)
if region is None:
    print("Please specify AWS region correctly in config file.")
    exit(0)
if bucket_name is None:
    print("Please specify Bucket name correctly in config file.")
    exit(0)
     
agent = AwsAgent(access_key, secret_key, region)

src_image="assets/test-image.png"

if ENCRYPTED_UPLOAD == "SSE_C": 
    key = "qdn-test/encrypted-image_sse_c"
    e_key = "sample-customer-encryption-key-1"
    filename="encrypted-image_sse_c.png"
elif ENCRYPTED_UPLOAD == "KMS":
    key = "qdn-test/encrypted-image-kms"
    e_key= "<Enter KMS key-id>"
    filename="encrypted-image-kms.png"
else:
    key = "qdn-test/encrypted-image"
    e_key=None
    filename="encrypted-image.png"

print("Uploading image using AWS ", ENCRYPTED_UPLOAD, " encyption method.")    
agent.upload_to_s3(bucket_name, key, src_image,sse_type=ENCRYPTED_UPLOAD, encryption_key=e_key)
print("Upload Completed")
print("Downloading image using AWS ", ENCRYPTED_UPLOAD, " encyption method.")    
agent.download_from_s3(bucket_name, key, filename,sse_type=ENCRYPTED_UPLOAD, encryption_key=e_key)
print("Download Completed")
