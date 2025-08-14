import httpx
from botocore.awsrequest import AWSRequest
from botocore.auth import SigV4Auth
from botocore.credentials import Credentials
from datetime import datetime, timezone
import os

# 配置信息
endpoint = "https://huabei-2.zos.ctyun.cn"
bucket = "pq-devel"
object_key = "share/zos/test-upload.json"
region = "huabei-2"
access_key = os.environ["S3_ACCESS_KEY"]
secret_key = os.environ["S3_SECRET_KEY"]

credentials = Credentials(access_key, secret_key)

def verify_file():
    url = f"{endpoint}/{bucket}/{object_key}"  # path-style
    headers = {
        "x-amz-date": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "x-amz-content-sha256": "UNSIGNED-PAYLOAD"  # 关键：CTyun 特殊要求
    }

    request = AWSRequest(method="GET", url=url, headers=headers)
    SigV4Auth(credentials, "s3", region).add_auth(request)

    resp = httpx.request(
        method=request.method,
        url=request.url,
        headers=dict(request.headers),
        verify=False
    )
    print("[DEBUG] Status:", resp.status_code)
    print("[DEBUG] Headers:", resp.headers)
    print("[DEBUG] Body:", resp.text)

if __name__ == "__main__":
    verify_file()


