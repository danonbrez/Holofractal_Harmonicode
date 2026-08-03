# HHS DigitalOcean TLS renewal watchdog

This directory installs a fail-closed certificate-expiry check for the public Nginx boundary. It does not expose the loopback application port. Public traffic remains on ports 80 and 443; the HHS process should remain bound to `127.0.0.1:8080`.

## Immediate installation

```bash
cd /opt/hhs/app
sudo apt update
sudo apt install -y certbot openssl nginx
sudo bash deploy/digitalocean/tls/install.sh
```

The installer preserves an existing `/etc/hhs/tls-renew.env`. Review the active host and renewal command before running it on a host that does not use Certbot:

```bash
sudoedit /etc/hhs/tls-renew.env
sudo systemctl start hhs-tls-renew.service
sudo journalctl -u hhs-tls-renew.service -n 100 --no-pager
```

## Verification

```bash
sudo systemctl is-enabled hhs-tls-renew.timer
sudo systemctl is-active hhs-tls-renew.timer
sudo systemctl list-timers hhs-tls-renew.timer --all
sudo /usr/local/sbin/hhs-tls-renew
```

The service exits nonzero when it cannot retrieve the certificate, cannot renew it, Nginx validation fails, or the renewed certificate remains inside the configured minimum-validity window. Successful results are emitted as structured `HHS_DIGITALOCEAN_TLS_RENEWAL_V1` envelopes.

## Configuration

`HHS_TLS_RENEW_BEFORE_DAYS` defaults to 14. `HHS_TLS_MINIMUM_VALID_DAYS` defaults to 2. `HHS_TLS_RENEW_COMMAND` and `HHS_TLS_RELOAD_COMMAND` are root-controlled commands read from `/etc/hhs/tls-renew.env`.

For a domain certificate, replace `HHS_TLS_HOST` with the public hostname. For the current IP-origin deployment, retain `137.184.223.84` only when that address is present in the active certificate.
