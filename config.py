import os, json
from logger import CustomLogger

class Config():
    def __init__(self, logger=None):
        if logger is None:
            logger = CustomLogger().logger
        
        self.logger           = logger
        self.config_file_path = os.path.join(os.getcwd(), 'config.json')
        self.getconfig        = self._getConfig()

    def _getConfig(self):
        config = {}
        config["certbot"] = {}
        config["certbot"]['path'] = ''
        config["lexicon"] = {}
        config["lexicon"]['path'] = ''
        config["domains"] = {}

        if not os.path.isfile(self.config_file_path):
            return config

        try:
            with open(self.config_file_path) as jsonfile:  
                return json.load(jsonfile)
        except Exception:
            self.logger.critical("An exception occured, can not get the configs")

        return config  
    
    def domainAction(self, args=None):
        """
        Handles the domains actions [add, remove and list]
        """
        if args is not None:
            if args.subaction in ['add', 'remove'] and args.provider and args.domain:
                if args.provider not in self.getconfig['domains']:
                    self.getconfig['domains'][args.provider] = []
                    
                provider_domains  = self.getconfig['domains'][args.provider]   

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
                print json.dumps(self.getconfig['domains'], indent=4)
                return
                    
        try:
            with open(self.config_file_path, 'w') as jsonfile:  
                json.dump(self.getconfig, jsonfile, indent=4)
        except Exception:
            self.logger.critical("An exception occured, can not %s the domain" % args.subaction)

    def configAction(self, args=None):
        if args is not None:
            if args.subaction in ['lexicon', 'certbot']:
                if args.path is not None and args.path != '':
                    if os.path.isfile(args.path):
                        if args.subaction not in self.getconfig:
                            self.getconfig[args.subaction] = {}

                        self.getconfig[args.subaction]['path'] = args.path
                        self.logger.info("%s path added to config" % args.subaction)
                    else:
                        self.logger.error("can not add %s path to the config, it has to be a file path" % args.subaction)
                else:
                    self.logger.error("-path can not be empty")
            elif args.subaction == 'show':
                print json.dumps(self.getconfig, indent=4)
                return        

        try:
            with open(self.config_file_path, 'w') as jsonfile:  
                json.dump(self.getconfig, jsonfile, indent=4)
        except Exception:
            self.logger.critical("An exception occured, can not edit the config file")
                    
                
        pass            