# ====================================================
# =========== Cloudflare Unidad de Pruebas ===========
# ====================================================

from os.path import exists as file_exists
import requests
import json
import os

CurrentPath: str = os.path.dirname(os.path.realpath(__file__))
RootPath: str = os.path.dirname(CurrentPath)
EnvSettings: dict[str] = {}


if not file_exists(f"{RootPath}/env.json"):
    raise Exception("File env.json doesn't exists")


try:
    import boto3
except ImportError:
    raise Exception("boto3 module doesn't exist\nInstall with pip install boto3")


try:
    import requests
except ImportError:
    raise Exception("requests module doesn't exist")


# Check if everything is setted
try:
    with open(f"{RootPath}/env.json") as f:
        CacheSettings = json.load(f)
        EnvSettings = CacheSettings["cloudflare"]
except Exception:
    raise Exception("Error reading env.json")

if not EnvSettings["EndPoint"]:
    raise Exception("""EnvSettings["EndPoint"] doesn't exists""")

if not EnvSettings["AccessKeyID"]:
    raise Exception("""EnvSettings["AccessKeyID"] doesn't exists""")

if not EnvSettings["SecretAccessKey"]:
    raise Exception("""EnvSettings["SecretAccessKey"] doesn't exists""")

if not EnvSettings["BucketName"]:
    raise Exception("""EnvSettings["BucketName"] doesn't exists""")

if not EnvSettings["PublicURL"]:
    raise Exception("""EnvSettings["PublicURL"] doesn't exists""")

try:
    S3 = boto3.resource("s3",
        endpoint_url=EnvSettings["EndPoint"],
        aws_access_key_id=EnvSettings["AccessKeyID"],
        aws_secret_access_key=EnvSettings["SecretAccessKey"],
    )
except Exception:
    raise Exception("Error creating S3 client")

BucketTest = None
try:
    BucketTest = S3.Bucket(EnvSettings["BucketName"])
except Exception:
    raise Exception("Error getting S3 bucket")

try:
    BucketTest.upload_file(f"{CurrentPath}/dummy.txt", "works.txt")
except Exception:
    raise Exception("Error uploading file")

try:
    DownloadPath: str = f"""{EnvSettings["PublicURL"]}/works.txt"""
    FileDownloaded = requests.get(DownloadPath, timeout=10)
except Exception:
    raise Exception("Error downloading file")

try:
    with open(f"{CurrentPath}/works.txt", "wb") as f:
        f.write(FileDownloaded.content)
except Exception:
    raise Exception("Error saving file")

print("Done")
os.remove(f"{CurrentPath}/works.txt")