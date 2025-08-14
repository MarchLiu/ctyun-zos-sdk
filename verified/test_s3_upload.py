import hashlib
import json
import os
from datetime import datetime

import httpx
from botocore.auth import S3SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials


region = os.environ["S3_REGION"]
bucket = os.environ["S3_BUCKET"]
access_key = os.environ["S3_ACCESS_KEY"]
secret_key = os.environ["S3_SECRET_KEY"]

endpoint = os.environ["S3_ENDPOINT"]
bucket = os.environ["S3_BUCKET"]
key = "share/zos/test-upload.json"

data = {"test": "hello world"}
body = json.dumps(data).encode("utf-8")
sha256_hex = hashlib.sha256(body).hexdigest()
print("[INFO] SHA256:", sha256_hex)


url = f"{endpoint}/{bucket}/{key}"
aws_req = AWSRequest(
    method="PUT",
    url=url,
    data=body,
    headers={
        "Host": f"{endpoint.replace('https://','')}",
        "Content-Type": "application/json",
        "x-amz-content-sha256": sha256_hex,
        "x-amz-date": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
    }
)

creds = Credentials(access_key, secret_key)
S3SigV4Auth(creds, "s3", region).add_auth(aws_req)

# ===== 发送请求 =====
resp = httpx.put(url, data=body, headers=dict(aws_req.headers), verify=False)  
print("[DEBUG] Status:", resp.status_code)
print("[DEBUG] Response:", resp.text)
