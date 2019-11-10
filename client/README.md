# Acme-client
Formerly was using Redis to notify other web servers about SSL certificates updates, but for the sake of simplicity, I created a Python script that runs as a systemd service to check for SSL certificates updates and download them to the webserver SSL directory.

## Configuration

We need to set the needed environment variables first
```bash
export AWS_ACCESS_KEY=your_aws_access_key
export AWS_SECRET_KEY=your_aws_secret_key
export AWS_REGION=your_aws_region
export CERTS_BUCKET_NAME=the_certificates_bucket_name
export CERTS_BUCKET_KEY=the_certificates_key_usually_the_domain name
export CERTS_LOCAL_DIR=the_local_ssl_certificates_directory
export ACME_CLIENT_CHECK_DELAY=the_interval_to_check_for_updates_in_seconds
export CALLBACK_CMD=after_the_certificates_update_bash_cmd
```

Example:

```bash
export AWS_ACCESS_KEY=your_aws_access_key
export AWS_SECRET_KEY=your_aws_secret_key
export AWS_REGION=us-east-1
export CERTS_BUCKET_NAME=letsencrypt-certs
export CERTS_BUCKET_KEY=example.com
export CERTS_LOCAL_DIR=/etc/ssl/crt
export ACME_CLIENT_CHECK_DELAY=30
export CALLBACK_CMD=service apache2 restart
```

If you need to set them as a system-wide variables, you may want to think about adding them to /etc/profile, /etc/bash.bashrc, or /etc/environment.

## Install

Requires Python 3

```bash
sudo ./setup.sh
```

#### [DISCLAIMER] THE SCRIPT IS PROVIDED “AS IS”
THE SCRIPT IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE SCRIPT.
