# ====================================================
# ================= Unidad de Prueba =================
# ====================================================

REMOVE_AFTER_UNIT: bool = True

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
    with open(f"{RootPath}/env.json") as f:
        EnvSettings = json.load(f)
except Exception:
    raise Exception("Error reading env.json")


# ====================================================
# ==================== Cloudflare ====================
# ====================================================

try:
    import boto3
except ImportError:
    raise Exception("boto3 module doesn't exist\nInstall with pip install boto3")


try:
    import requests
except ImportError:
    raise Exception("requests module doesn't exist")


if not EnvSettings["cloudflare"]["EndPoint"]:
    raise Exception("""EnvSettings["cloudflare"]["EndPoint"] doesn't exists""")

if not EnvSettings["cloudflare"]["AccessKeyID"]:
    raise Exception("""EnvSettings["cloudflare"]["AccessKeyID"] doesn't exists""")

if not EnvSettings["cloudflare"]["SecretAccessKey"]:
    raise Exception("""EnvSettings["cloudflare"]["SecretAccessKey"] doesn't exists""")

if not EnvSettings["cloudflare"]["BucketName"]:
    raise Exception("""EnvSettings["cloudflare"]["BucketName"] doesn't exists""")

if not EnvSettings["cloudflare"]["PublicURL"]:
    raise Exception("""EnvSettings["cloudflare"]["PublicURL"] doesn't exists""")

try:
    S3 = boto3.resource("s3",
        endpoint_url=EnvSettings["cloudflare"]["EndPoint"],
        aws_access_key_id=EnvSettings["cloudflare"]["AccessKeyID"],
        aws_secret_access_key=EnvSettings["cloudflare"]["SecretAccessKey"],
    )
except Exception:
    raise Exception("Error creating S3 client")

BucketTest = None
try:
    BucketTest = S3.Bucket(EnvSettings["cloudflare"]["BucketName"])
except Exception:
    raise Exception("Error getting S3 bucket")

try:
    BucketTest.upload_file(f"{CurrentPath}/dummy.txt", "works.txt")
    BucketTest.upload_file(f"{CurrentPath}/videotest.webm", "videotest.webm")
except Exception:
    raise Exception("Error uploading file")

try:
    DownloadPath: str = f"""{EnvSettings["cloudflare"]["PublicURL"]}/works.txt"""
    FileDownloaded = requests.get(DownloadPath, timeout=10)
except Exception:
    raise Exception("Error downloading file")

try:
    with open(f"{CurrentPath}/works.txt", "wb") as f:
        f.write(FileDownloaded.content)
except Exception:
    raise Exception("Error saving file")

print("[Unit-test] Cloudflare: Done!")
# os.remove(f"{CurrentPath}/works.txt")



# ====================================================
# =================== CloudConvert ===================
# ====================================================

cloudconvert_payload: dict[str | dict[str]] = {
    "tasks": {
        "unittest-import-s3": {
            "operation": "import/s3",
            "bucket": f"""{EnvSettings["cloudflare"]["BucketName"]}""",
            "region": "us-east-1",
            "access_key_id": f"""{EnvSettings["cloudflare"]["AccessKeyID"]}""",
            "secret_access_key": f"""{EnvSettings["cloudflare"]["SecretAccessKey"]}""",
            "endpoint": f"""{EnvSettings["cloudflare"]["EndPoint"]}""",
            "key": "videotest.webm"
        },
        "unittest-convert": {
            "operation": "convert",
            "input": [
                "unittest-import-s3"
            ],
            "output_format": "mp4",
            "filename": "videotest.mp4"
        },
        "unittest-thumbnail": {
            "operation": "thumbnail",
            "input": [
                "unittest-import-s3"
            ],
            "output_format": "jpg",
            "filename": "videotest.jpg"
        },
        "unittest-export-s3": {
            "operation": "export/s3",
            "input": [
                "unittest-convert",
                "unittest-thumbnail"
            ],
            "bucket": f"""{EnvSettings["cloudflare"]["BucketName"]}""",
            "region": "us-east-1",
            "access_key_id": f"""{EnvSettings["cloudflare"]["AccessKeyID"]}""",
            "secret_access_key": f"""{EnvSettings["cloudflare"]["SecretAccessKey"]}""",
            "endpoint": f"""{EnvSettings["cloudflare"]["EndPoint"]}"""
        }
    },
    "tag": "jobbuilder"
}


try:
    import cloudconvert
except ImportError:
    raise Exception("cloudconvert module doesn't exist\nInstall with pip install cloudconvert")

from cloudconvert.job import Job

if not EnvSettings["cloudconvert"]["APIKey"]:
    raise Exception("""EnvSettings["cloudconvert"]["APIKey"] doesn't exists""")

try:
    cloudconvert.configure(api_key=EnvSettings["cloudconvert"]["APIKey"], sandbox=True)
except Exception:
    raise Exception("Error configuring CloudConvert")

CloudconvertJobTask: Job = Job.create(cloudconvert_payload)

print("[Unit-test] CloudConvert: Done!")

if REMOVE_AFTER_UNIT:

    ObjectToRemove: list[ dict[str] ] = [
        { "Key": "videotest.mp4" },
        { "Key": "videotest.webm" },
        { "Key": "videotest.jpg" },
        { "Key": "works.txt"}
    ] 

    BucketTest.delete_objects(Delete={"Objects": ObjectToRemove})

    os.remove(f"{CurrentPath}/works.txt")