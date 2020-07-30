# stafi-node-monitor
##Installation
```bash
git clone https://github.com/nikolayqwerty/stafi-node-monitor.git
cd stafi-node-monitor
sudo apt install python3-pip
pip3 install -r requirements.txt
```
Edit conf file:
```bash
nano conf.ini
```
Change these lines to your email and password from the yandex mail.
```
yandex_login = your-mail@yandex.ru
yandex_password = your-password
```
Add the task to the crontab
```bash
crontab -e
```
```
SHELL=/bin/bash
*/5 * * * * python3 /path/to/stafi-node-monitor/main.py > /dev/null 2>&1
```