import json, os, logging, time
from subprocess import Popen, PIPE
from domains import Domains
from logger  import CustomLogger

class Result:
    pass

class AcmeOperation:
    def __init__(self, provider=None):
        """
        Automate certbot and lexicon to obtain and store 
        let's encrypt ssl certificates into S3-compatible object storage
        """
        self.logger                     = CustomLogger().logger
        self.dns_provider               = provider
        self.dns_provider_username      = None
        self.dns_provider_auth_token    = None
        self.dns_provider_update_delay  = 30
        self.domains                    = Domains(logger=self.logger)
        self.test                       = False

    def _providerCheck(self):
        if self.dns_provider in self.domains.list['domains']:
            if len(self.domains.list['domains'][self.dns_provider]) > 0:
                return True
            else:
                self.logger.error('no domains stored for {0}'.format(self.dns_provider))
                return False
        
        self.logger.error("provider is not in the domains list")
        return False
    

    def _runCmd(self, args):
        result  = Result()

        process = Popen(args, stdout=PIPE, stderr=PIPE, shell=True)
        process.wait()
        stdout, stderr = process.communicate()

        result.exitcode = process.wait()
        result.stdout   = stdout
        result.stderr   = stderr

        if process.returncode != 0:
            self.logger.error('Error executing command {0}'.format(args))
            self.logger.error('StdErr: {0}'.format(stderr))

        return result
        
    def obtain(self, test=False):
        """
        Obtains the initial letsencrypt certificates for specific domain name provider 
        using manual script hooks to validate the ownership of the domains

        Certbot cli cmd generated:
        certbot certonly --manual --preferred-challenges=dns 
        --manual-auth-hook "/path/to/acmebot.py auth -p namecheap" 
        --manual-cleanup-hook "/path/to/acmebot.py cleanup -p namecheap" 
        -d sub1.example.com -d sub2.example.com -d another-example.com 
        --manual-public-ip-logging-ok --noninteractive --agree-tos --test-cert
        """
        hook_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'acmebot.py')
        if self._providerCheck():
            args = ['certbot', 'certonly', '--manual', '--preferred-challenges', 'dns']
            
            args.extend(['--manual-auth-hook',"'{0} auth -p {1}'".format(hook_file, self.dns_provider)])
            args.extend(['--manual-cleanup-hook',"'{0} cleanup -p {1}'".format(hook_file, self.dns_provider)])
            
            for domain in self.domains.list['domains'][self.dns_provider]:
                args.extend(['-d', domain])
            
            # adding certbot options to run in a non interactive mode
            args.extend(['--manual-public-ip-logging-ok', '--noninteractive', '--agree-tos', '--quiet'])   

            if test:
                args.append('--test-cert')    
            
            print 'cmd: {0}'.format(' '.join(args))    
            self._runCmd(args)
            

    def hook(self, action=None):
        # the passed environment variables from certbot
        CERTBOT_DOMAIN     = os.environ.get("CERTBOT_DOMAIN", None)
        CERTBOT_VALIDATION = os.environ.get("CERTBOT_VALIDATION", None)
        CERTBOT_TOKEN      = os.environ.get("CERTBOT_TOKEN", None)
        
        print "CERTBOT_DOMAIN: {0}".format(CERTBOT_DOMAIN)
        print "CERTBOT_VALIDATION: {0}".format(CERTBOT_VALIDATION)
        print "CERTBOT_TOKEN: {0}".format(CERTBOT_TOKEN)
        
        self.logger.info("Auth the domain")
        args = [ 
            'lexicon', 
            self.dns_provider, 
            '--auth-usernam={0}'.format(self.dns_provider_username), 
            '--auth-token={0}'.format(self.dns_provider_auth_token),
            'create', 
            CERTBOT_DOMAIN, 
            'TXT', 
            '--name', 
            '_acme-challenge.{0}'.format(CERTBOT_DOMAIN), 
            '--content', 
            CERTBOT_VALIDATION
            ]

        self._runCmd(args)

        if action == 'auth':
            #   https://github.com/AnalogJ/lexicon/blob/master/examples/certbot.default.sh#L46
            #   How many seconds to wait after updating your DNS records. This may be required,
            #   depending on how slow your DNS host is to begin serving new DNS records after updating
            #   them via the API. 30 seconds is a safe default, but some providers can be very slow 
            #   (e.g. Linode).
            #
            #   Defaults to 30 seconds
            time.sleep(self.dns_provider_update_delay)           


