# Acme-client
Formerly was using Redis to notify other web servers about SSL certificates updates, but for the sake of simplicity, I created a Python script that runs as a systemd service to check for SSL certificates updates and download them to the webserver SSL directory.

## Configuration

We need to set the needed environment variables into a systemd EnvironmentFile first
```bash
cat << EOF > /lib/systemd/system/acmebot-client.env
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
CERTS_BUCKET_NAME=the_certificates_bucket_name
CERTS_BUCKET_KEY=the_certificates_key_usually_the_domain name
CERTS_LOCAL_DIR=the_local_ssl_certificates_directory
ACME_CLIENT_CHECK_DELAY=the_interval_to_check_for_updates_in_seconds
CALLBACK_CMD=after_the_certificates_update_bash_cmd
EOF
```

Example:

```bash
cat << EOF > /lib/systemd/system/acmebot-client.env
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=us-east-1
CERTS_BUCKET_NAME=letsencrypt-certs
CERTS_BUCKET_KEY=example.com
CERTS_LOCAL_DIR=/etc/ssl/crt
ACME_CLIENT_CHECK_DELAY=30
CALLBACK_CMD=service apache2 restart
EOF
```

## Install

Requires Python 3

```bash
sudo ./setup.sh
```

#### [DISCLAIMER] THE SCRIPT IS PROVIDED “AS IS”
THE SCRIPT IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE SCRIPT.
