#!/usr/bin/env python3
import boto3, os, time, hashlib, json
import logging
from pythonjsonlogger import jsonlogger
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()

class ClientLogger:
    """
    Stand alone json logger for the Acme Client
    """
    def __init__(self):
        self.logger = self._addJsonFormat()
    
    def _addJsonFormat(self):
        logger     = logging.getLogger('AcmeCheckClient')
        logHandler = logging.StreamHandler()
        logHandler.setLevel(logging.INFO)
        
        # TODO: unify the json logger default fields
        custom_format = ' '.join([
            '%(asctime)s',
            '%(name)s',
            '%(module)s',
            '%(funcName)s',
            '%(levelname)s',
            '%(message)s'])

        logHandler.setFormatter(jsonlogger.JsonFormatter(custom_format, datefmt='%m/%d/%Y %I:%M:%S %p'))
        logger.addHandler(logHandler)
        logger.setLevel(logging.INFO)
        return logger

class AcmeClient():
    def __init__(self):
        self.logger          = ClientLogger().logger
        self.check_delay     = os.getenv('ACME_CLIENT_CHECK_DELAY')
        self.endpoint_url    = os.getenv('ENDPOINT_URL')
        self.aws_access_key  = os.getenv('AWS_ACCESS_KEY')
        self.aws_secret_key  = os.getenv('AWS_SECRET_KEY')
        self.aws_region      = os.getenv('AWS_REGION')
        self.s3_bucket_name  = os.getenv('CERTS_BUCKET_NAME')
        self.s3_bucket_key   = os.getenv('CERTS_BUCKET_KEY')
        self.certs_local_dir = os.getenv('CERTS_LOCAL_DIR')
        self.callback_cmd    = os.getenv('CALLBACK_CMD')
        self.metadata_path   = os.path.join(self.certs_local_dir, 'metadata.json')
        self.metadata_obj    = self._readMetaDataFile()
        self.s3_client       = self._s3Client()
        self._createLocalDir()

    def  _createLocalDir(self):
        try:
            if not os.path.exists(self.certs_local_dir):
                os.mkdir(self.certs_local_dir)
        except Exception:
            self.logger.exception('Local certs dir does not exists or can not created')

    def _s3Client(self):
        try:
            return  boto3.client('s3', 
                        endpoint_url=self.endpoint_url, 
                        aws_access_key_id=self.aws_access_key, 
                        aws_secret_access_key=self.aws_secret_key, 
                        region_name=self.aws_region)
        except Exception:
            self.logger.exception('Can not in create s3 client')
            return None
    
    def _readMetaDataFile(self):
        try:
            if os.path.isfile(self.metadata_path):
                with open(self.metadata_path) as jsonfile:  
                    return json.load(jsonfile)
            return {}
        except Exception:
            self.logger.error("An exception occured, can not read the local metadata file")
            return {}

    def _writeMetaDataFile(self, metadata):
        try:
            with open(self.metadata_path, 'w') as jsonfile:  
                json.dump(metadata, jsonfile, indent=4)
            self.metadata_obj = metadata
        except Exception:
            self.logger.error("Metadata can not be saved locally!")
            self.metadata_obj = {}

    def _calcSHA256(self, filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath,'rb') as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b''):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()

    def _getMetaData(self):
        """Get the certificate metadata"""
        resp = self.s3_client.head_object(Bucket=self.s3_bucket_name, Key='%s/metadata.json' % self.s3_bucket_key)
        if 'Metadata' not in resp:
            return None
        
        return resp['Metadata']

    def _getCerts(self):
        resp = self.s3_client.list_objects(Bucket=self.s3_bucket_name, Prefix=self.s3_bucket_key)

        if 'Contents' not in resp:
            return None
        
        for obj in resp['Contents']:
            if 'Key' in obj and 'metadata' not in obj['Key']:
                cert_filename = os.path.basename(obj['Key'])
                if cert_filename:
                    self.s3_client.download_file(
                        Bucket=self.s3_bucket_name, 
                        Key=obj['Key'],
                        Filename= os.path.join(self.certs_local_dir, cert_filename)
                    )
                    self.logger.info("certificate file %s is saved" % obj['Key'])

    
    def check(self):
        try:
            if self.s3_client is None:
                self.logger.error('No s3 client initialized')
                return
            
            metadata = self._getMetaData()
            if metadata == self.metadata_obj:
                return None
            # if there are changes, write the new metadata and downlaod the new cert files
            self._writeMetaDataFile(metadata)
            self._getCerts()

            if self.callback_cmd:
                os.system(self.callback_cmd)
        except Exception as e:
           self.logger.error("Failed to check for ssl certificate changes, Reason: %s" % e) 

def main():
    client = AcmeClient()
    delay  = int(client.check_delay) 
    while True:
        client.check()
        time.sleep(delay)

if __name__ == '__main__':
    main()