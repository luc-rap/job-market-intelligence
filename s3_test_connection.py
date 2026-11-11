import boto3

# creates AWS session
session = boto3.Session(
    profile_name="job-market",
    region_name="us-east-1"
)

#creates S3 client
s3 = session.client("s3")

# we only gave access to this specific bucket (list, upload, read)
response = s3.list_objects_v2(
    Bucket="job-market-intelligence-raw-lr"
)

print("Successfully connected to S3!")
print("Objects in bucket:", response.get("KeyCount", 0))

# Least Privilege: give an application only the permissions it needs to perform its job
