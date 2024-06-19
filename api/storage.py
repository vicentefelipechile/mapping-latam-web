# ====================================================
# ================ Librerias y Clases ================
# ====================================================

from mappinglatam.settings import CUSTOM_CONFIG
from boto3 import resource as boto3_resource


# ====================================================
# ====================== Storage =====================
# ====================================================

CloudFlareSettings: dict[str] = CUSTOM_CONFIG["cloudflare"]

class CloudFlareStorage():
    __Boto3Resource = None
    __Bucket = None

    def __init__(self):
        self.__Boto3Resource = boto3_resource(
            "s3",
            endpoint_url=CloudFlareSettings["EndPoint"],
            aws_access_key_id=CloudFlareSettings["AccessKeyID"],
            aws_secret_access_key=CloudFlareSettings["SecretAccessKey"]
        )

        self.__BucketS3 = self.__Boto3Resource.Bucket(CloudFlareSettings["BucketName"])

        print("[Storage] Successfully connected to CloudFlare")

    def GetBucket(self):
        return self.__BucketS3
    
    def UploadFile(self, FilePath: str, Key: str = "", ExtraArgs: dict = None):
        if not ExtraArgs: ExtraArgs = {}

        self.GetBucket().upload_file(FilePath, Key, ExtraArgs)
    
    def UploadFileObject(self, FileObject, Key: str = "", ExtraArgs: dict = None):
        if not ExtraArgs: ExtraArgs = {}

        self.GetBucket().upload_fileobj(FileObject, Key, ExtraArgs)



Storage: CloudFlareStorage = CloudFlareStorage()