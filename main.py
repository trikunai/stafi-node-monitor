import requests
import json
import psutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser


config = configparser.ConfigParser()
config.read('conf.ini')
trust_node_url = config['NODES']['trust_node_url']
my_node_url = config['NODES']['my_node_url']
smtp_login = config['MAIL']['yandex_login']
smtp_password = config['MAIL']['yandex_password']
recipients = config['MAIL']['to_mail'].split(' ')

def send_email(message):
    subject = 'Your Stafi node has a problem!'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = '<' + smtp_login + '>'
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = smtp_login
    msg['Return-Path'] = smtp_login
    part_text = MIMEText(message, 'plain')
    msg.attach(part_text)
    mail = smtplib.SMTP_SSL('smtp.yandex.ru:465')
    mail.login(smtp_login, smtp_password)
    mail.sendmail(smtp_login, recipients, msg.as_string())
    mail.quit()


def get_node_info(url, method):
    data = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": method,
        "params": []
    }
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r.json()


def version_check():
    my_node = get_node_info(my_node_url, 'system_version')
    trust_node = get_node_info(trust_node_url, 'system_version')
    if my_node['result'] != trust_node['result']:
        message = 'Trust node version: {}\n' \
                  'My node version: {}\n' \
                  'Check new update https://github.com/stafiprotocol/stafi-node'.format(trust_node['result'], my_node['result'])
        send_email(message)
    else:
        print('Version check OK')


def peers_check():
    my_node = get_node_info(my_node_url, 'system_health')
    if my_node['result']['peers'] < 20:
        trust_node = get_node_info(trust_node_url, 'system_health')
        message = 'Low number of peers!\n' \
                  'You have {} peers.\n' \
                  'Trust node have {} peers.'.format(my_node['result']['peers'], trust_node['result']['peers'])
        send_email(message)
    else:
        print('Peers check OK')


def new_blocks_check():
    my_node = get_node_info(my_node_url, 'chain_getHeader')
    trust_node = get_node_info(trust_node_url, 'chain_getHeader')
    if int(my_node['result']['number'], 16) - int(my_node['result']['number'], 16) > 60:
        message = 'You have problem with new blocks\n' \
                  'Your last block: {}\n' \
                  'Trust node last block: {}'.format(int(my_node['result']['number'], 16), int(trust_node['result']['number'], 16))
        send_email(message)
        print(message)
    else:
        print('New blocks check OK')


def system_check():
    cpu = psutil.cpu_percent(interval=20)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    if cpu > 80 or mem > 80 or disk > 80:
        message = 'You have problems with system:\n' \
                  'CPU usage: {}%\nMemory usage: {}%\nDisk usage: {}%'.format(cpu,mem,disk)
        send_email(message)
        print(message)
    else:
        print('System check OK')


def check_my_node():
    r = requests.post(my_node_url, headers={'Content-Type': 'application/json'})
    if r.status_code == 200:
        return True
    else:
        message = 'Your node is down'
        send_email(message)
        print(message)
        return False


if __name__ == '__main__':
    print(recipients)
    if check_my_node():
        version_check()
        peers_check()
        new_blocks_check()
        system_check()