import boto3, os, hashlib, json
from botocore.client import Config
from logger import CustomLogger
from dotenv import load_dotenv

class Store():
    load_dotenv()
    def __init__(self, logger=None):
        self.logger         = CustomLogger().logger if logger is None else logger
        self.certs_location = '/etc/letsencrypt/live'
        self.endpoint_url   = os.getenv('ENDPOINT_URL')
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY')
        self.aws_secret_key = os.getenv('AWS_SECRET_KEY')
        self.aws_region     = os.getenv('AWS_REGION')
        self.s3_bucket_name = os.getenv('CERTS_BUCKET_NAME')
        self.client         = self._client()
        
    
    def _client(self):
        try:
            return  boto3.client('s3', 
                        endpoint_url=self.endpoint_url, 
                        aws_access_key_id=self.aws_access_key, 
                        aws_secret_access_key=self.aws_secret_key, 
                        region_name=self.aws_region)
        except Exception:
            self.logger.exception('Can not in create s3 client')
            return None

    def _calcSHA256(self, filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath,'rb') as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b''):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()                               

    def getMetaData(self, object_key):
        """Get the certificate metadata"""
        resp = self.client.head_object(Bucket=self.s3_bucket_name, Key='{0}/metadata.json'.format(object_key))
        if 'Metadata' not in resp:
            return None
        
        return resp['Metadata']
    
    def saveCerts(self):
        """ Saves the letsencrypt certificates files to a s3-compatible object storage"""
        certs_files = {}
        if self.client is None:
            self.logger.error('No s3 client initialized')
            return
        for cert in os.listdir(self.certs_location):
            cert_location = os.path.join(self.certs_location, cert)
            if os.path.isdir(cert_location):
                certs_files[cert] = {}
                cert_files = list(filter(lambda filename: all(ex_str not in filename.lower() for ex_str in ['readme', 'metadata']), os.listdir(cert_location)))
                for file in cert_files:
                    filepath   = os.path.join(cert_location, file)
                    filesha256 = self._calcSHA256(filepath)
                    cert_key = os.path.splitext(file)[0]
                    certs_files[cert][cert_key] = filesha256
                    # Save the certificates to a bucket
                    self.client.put_object(
                        ACL='private',
                        Body=filepath,
                        Bucket=self.s3_bucket_name,
                        Key='{0}/{1}'.format(cert, file))
                # create and upload a metadata file contains the certificates files sha256         
                metadata_file = os.path.join(cert_location, 'metadata.json')
                try:
                    with open(metadata_file, 'w') as f:
                        f.write(json.dumps(certs_files[cert], indent=4))
                except Exception:
                    self.logger.error('Can not save the metadata json file for %s certificate' % cert)
                    return

                if os.path.isfile(metadata_file):
                    self.client.put_object(
                        ACL='private',
                        Body=metadata_file,
                        Bucket=self.s3_bucket_name,
                        Key='{0}/{1}'.format(cert, 'metadata.json'),
                        Metadata=certs_files[cert])

        self.logger.info('certificates files saved to %s bucket' % self.s3_bucket_name)      
