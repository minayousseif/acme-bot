#!/usr/bin/env python

import argparse
from operation import AcmeOperation

def main():
    parser     = argparse.ArgumentParser(description='Automate and store let\'s encrypt ssl certificates into S3')
    subparsers = parser.add_subparsers(dest='action')
    
    for action in ['obtain', 'auth', 'cleanup']:
       action_parser = subparsers.add_parser(action)
       action_parser.add_argument('-p', dest='provider', help='the domain name provider', action='store', required=True)
       action_parser.add_argument('--test', dest='test', help='obtain a test certificate from a staging server', action='store_true')
        

    domains_parser     = subparsers.add_parser('domains')
    domains_subparsers = domains_parser.add_subparsers(dest='subaction')

    for domains_action in ['add', 'remove', 'list']:
        domain_action_parser = domains_subparsers.add_parser(domains_action)
        if domains_action in ['add', 'remove']:
            domain_action_parser.add_argument('-d', dest='domain',   help='the domain to {0}'.format(domains_action), action='store', required=True)
            domain_action_parser.add_argument('-p', dest='provider', help='the domain name provider', action='store', required=True)

    args = parser.parse_args()
    operation = AcmeOperation(provider=args.provider)
    if args.action == 'obtain':
        operation.obtain(test=args.test)
    if args.action in ['auth', 'cleanup']:
        operation.hook(action=args.action)
    elif args.action == 'domains':
        operation.domains.action(args)

if __name__ == '__main__':
    main()