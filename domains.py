import os, json
from logger import CustomLogger

class Domains():
    """
    Handles the domains actions [add, remove and list]
    """
    def __init__(self, logger=None):
        if logger is None:
            logger = CustomLogger().logger
        
        self.logger            = logger
        self.domains_file_path = os.path.join(os.getcwd(), 'domains.json')
        self.list              = self._getDomains()

    def _getDomains(self):
        domains = {}
        if not os.path.isfile(self.domains_file_path):
            domains["domains"] = {}
            return domains

        try:
            with open(self.domains_file_path) as jsonfile:  
                return json.load(jsonfile)
        except Exception:
            self.logger.critical("An exception occured, can not get the domains list")

        return domains    
    
    def action(self, args=None):
        if args is not None:
            if args.subaction in ['add', 'remove'] and args.provider and args.domain:
                if args.provider not in self.list['domains']:
                    self.list['domains'][args.provider] = []
                    
                provider_domains  = self.list['domains'][args.provider]   

            if args.subaction == 'add':
                if args.domain not in provider_domains:
                    provider_domains.append(args.domain)
                else:
                    self.logger.error('{0} already exists'.format(args.domain))    
            elif args.subaction == 'remove':
                if args.domain in provider_domains:
                    provider_domains.remove(args.domain)
                else:
                    self.logger.error('{0} does not exist to remove it'.format(args.domain))
            elif args.subaction == 'list':
                print self.list
                return
                    
        try:
            with open(self.domains_file_path, 'w') as jsonfile:  
                json.dump(self.list, jsonfile, indent=4)
        except Exception:
            self.logger.critical("An exception occured, can not add %s to the domains list" % args.domain)    