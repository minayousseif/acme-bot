# Acme-bot
Letsencrypt automation using certbot dns challenge and storing the certificate to s3-compatible object storage

## Install
**Requires Python 3**

#### This tool uses both certbot and dns-lexicon cli

- Install certbot specific to your system, from here https://certbot.eff.org/
- Install lexicon from here https://github.com/AnalogJ/lexicon

Clone the repo

```bash
git clone https://github.com/minayousseif/acme-bot.git
```

Install the requirements

```bash
python3 -m pip install -r requirements.txt
```

You can use the cli to create a configuration file

```bash
./acmebot config -h
```
or create a json formatted configuration file using any text editor, name it `config.json` and place it inside the project root.

config.json example:
```json
{
    "domains": {
        "route53": [
            "example.com", 
            "www.example.com", 
            "sub1.example.com",
            "sub2.example.com"
        ]
    }, 
    "lexicon": {
        "path": "/path/to/bin/lexicon"
    }, 
    "certbot": {
        "path": "/path/to/bin/certbot"
    }
}
```

then set the needed environment variables
```bash
export DNS_PROVIDER_USERNAME=your_domain_provider_username
export DNS_PROVIDER_AUTH_TOKEN=your_domain_provider_token
export AWS_ACCESS_KEY=your_aws_access_key
export AWS_SECRET_KEY=your_aws_secret_key
export AWS_REGION=your_aws_region
export CERTS_BUCKET_NAME=the_certs_bucket_name
```

Optional, if you want to add acmebot to your PATH.

```bash
cd /usr/bin
ln -s /path/to/the/acme-bot/acmebot acmebot
```

to learn how you can let's encrypt ssl certificates run:

```bash
./acmebot -h
```

### Acme-client
a Python script that runs as a service to check for SSL certificates updates.

for more details please refer to [acme-client readme](/client/README.md)


#### [DISCLAIMER] THE SCRIPT IS PROVIDED “AS IS”
THE SCRIPT IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE SCRIPT.




