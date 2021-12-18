import json, os, logging, time, urllib
from subprocess import call, Popen, PIPE
from pipes import quote
from config import Config
from store  import Store 
from logger import CustomLogger
from dotenv import load_dotenv
from lexicon.config import ConfigResolver
from lexicon.client import Client

class Result:
    pass

class AcmeOperation:
    load_dotenv()
    def __init__(self, provider=None):
        """
        Automate certbot and lexicon to obtain and store 
        let's encrypt ssl certificates into S3-compatible object storage
        """
        self.logger                    = CustomLogger().logger
        self.dns_provider              = provider
        self.dns_provider_username     = os.getenv('DNS_PROVIDER_USERNAME')
        self.dns_provider_auth_token   = os.getenv('DNS_PROVIDER_AUTH_TOKEN')
        self.client_ip_address         = self._getPublicIP()
        self.dns_provider_update_delay = 30
        self.config                    = Config(logger=self.logger)
        self.s3_store                  = Store(logger=self.logger)
        self.test                      = False

    def _providerCheck(self):
        if self.dns_provider in self.config.getconfig['domains']:
            if len(self.config.getconfig['domains'][self.dns_provider]) > 0:
                return True
            else:
                self.logger.error('no domains stored for {0}'.format(self.dns_provider))
                return False
        
        self.logger.error("provider is not in the domains list")
        return False
    
    def _getPublicIP(self):
        return urllib.request.urlopen('https://api.ipify.org/').read().decode('utf8')

    def _getToolPath(self, tool):
        if tool is not None and tool not in self.config.getconfig:
            return None
        if 'path' in self.config.getconfig[tool]:
            return self.config.getconfig[tool]['path']


    def _runCmd(self, args):
        result  = Result()

        process = Popen(args, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        result.stdout   = stdout
        result.stderr   = stderr

        if process.returncode:
            self.logger.error('Error executing command {0}'.format(args))
            self.logger.error('StdErr: {0}'.format(stderr))

        return result
    
    def _lexiconCliHook(self, action=None):
        # the passed environment variables from certbot
        CERTBOT_DOMAIN     = os.environ.get("CERTBOT_DOMAIN", None)
        CERTBOT_VALIDATION = os.environ.get("CERTBOT_VALIDATION", None)
        
        cmd_index = 6
        lexicon = self._getToolPath('lexicon')

        if lexicon is None:
            self.logger.error("failed to run the lexicon cmd, lexicon path is not set")
            return

        args = [ 
            lexicon, 
            self.dns_provider, 
            '--auth-username={0}'.format(self.dns_provider_username), 
            '--auth-token={0}'.format(self.dns_provider_auth_token),
            '--auth-client-ip={0}'.format(self.client_ip_address),
            '--ttl=100',
            CERTBOT_DOMAIN, 
            'TXT', 
            '--name=_acme-challenge.{0}'.format(CERTBOT_DOMAIN),  
            '--content={0})'.format(CERTBOT_VALIDATION),
        ]
        if action == 'auth':
            #   https://github.com/AnalogJ/lexicon/blob/master/examples/certbot.default.sh#L46
            #   How many seconds to wait after updating your DNS records. This may be required,
            #   depending on how slow your DNS host is to begin serving new DNS records after updating
            #   them via the API. 30 seconds is a safe default, but some providers can be very slow 
            #   (e.g. Linode).
            #
            #   Defaults to 30 seconds
            args.insert(cmd_index, 'create')
            self._runCmd(args)
            time.sleep(self.dns_provider_update_delay)
            # now save the created certificates to s3-compatible object storage
            self.s3_store.saveCerts()
        elif action == 'cleanup':
            args.insert(cmd_index, 'delete')
            self._runCmd(args)

    def _lexiconLibHook(self, action=None):
        CERTBOT_DOMAIN     = os.environ.get("CERTBOT_DOMAIN", None)
        CERTBOT_VALIDATION = os.environ.get("CERTBOT_VALIDATION", None)

        lexicon_config = {
            "provider_name" : self.dns_provider,
            "action": action, # create, list, update, delete
            "domain": CERTBOT_DOMAIN, # domain name
            "type": "TXT",
            [self.dns_provider]: {
                "auth_username": self.dns_provider_username,
                "auth_token": self.dns_provider_auth_token,
                "auth_client_ip": self.client_ip_address
            },
            "content": CERTBOT_VALIDATION,
        }

        config = ConfigResolver()
        config.with_env().with_dict(dict_object=lexicon_config)
        Client(config).execute()

        
    def obtain(self, test=False, expand=False):
        """
        Obtains the initial letsencrypt certificates for specific domain name provider 
        using manual script hooks to validate the ownership of the domains

        Certbot cli cmd generated:
        certbot certonly --manual --preferred-challenges=dns 
        --manual-auth-hook "/path/to/acmebot.py auth -p namecheap" 
        --manual-cleanup-hook "/path/to/acmebot.py cleanup -p namecheap" 
        -d example.com -d sub2.example.com -d another-example.com 
        --manual-public-ip-logging-ok --noninteractive --agree-tos --test-cert
        """
        hook_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'acmebot')
        if self._providerCheck():
            certbot = self._getToolPath('certbot')

            if certbot is None:
                self.logger.error("failed to run the certbot cmd, certbot path is not set")
                return

            args = [certbot, 'certonly', '--manual', '--preferred-challenges', 'dns']
            
            args.extend(['--manual-auth-hook',quote("{0} auth -p {1}".format(hook_file, self.dns_provider))])
            args.extend(['--manual-cleanup-hook',quote("{0} cleanup -p {1}".format(hook_file, self.dns_provider))])
            for domain in self.config.getconfig['domains'][self.dns_provider]:
                args.extend(['-d', domain])
                
            # adding certbot options to run in a non interactive mode
            args.extend(['--manual-public-ip-logging-ok', '--noninteractive', '--agree-tos', '--quiet'])   

            if test:
                args.append('--test-cert')

            if expand:
                args.append('--expand')        
            
            certbot_cmd = ' '.join(args)
            # for some reason using Popen does not work with certbot
            # so we are using os.system for now
            # TODO: figure our if we can use subprocess.Popen
            os.system(certbot_cmd)
            
            
            

    def hook(self, action=None, use_cli=False):
        if use_cli:
            self._lexiconCliHook(action)
        else:
            self._lexiconLibHook(action)


    def manual_s3_upload(self):
        """manually uploads the live certificate files into the configured s3-compatible storage"""
        try:
            self.s3_store.saveCerts()
        except Exception as e:
            self.logger.error('Failed to manually upload the certificates to the s3-compatible storage, Reason: %s' % e)



