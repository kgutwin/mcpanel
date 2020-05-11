import os
import json
import boto3
import socket

from mcstatus import MinecraftServer

from lambdas import templates

ec2 = boto3.client('ec2')
sqs = boto3.client('sqs')


def get_instance():
    r = ec2.describe_instances(InstanceIds=[os.environ['INSTANCE_ID']])
    i = r['Reservations'][0]['Instances'][0]
    return i

IP_ADDRESS = get_instance()['PublicIpAddress']

def server_port_status():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.2)
    try:
        s.connect((IP_ADDRESS, 25565))
        return "up"
    except (socket.timeout, socket.error):
        return "down"

def minecraft_status():
    try:
        server = MinecraftServer.lookup(IP_ADDRESS)
        return server.status()
    except:
        return None
    
def render():
    return templates.admin_login()

def main_page(response=''):
    status = get_instance()['State']
    status['port'] = server_port_status()
    if status['port'] == 'up':
        mcstatus = minecraft_status()
    else:
        mcstatus = None
    
    return templates.admin_page(
        os.environ['LEADER_KEY'],
        instance_state=status,
        mcstatus=mcstatus,
        response=response
    )

def send_sqs(ev):
    sqs.send_message(
        QueueUrl=os.environ['MESSAGE_QUEUE'],
        MessageBody=json.dumps(ev)
    )

def update(data):
    print(data)
    if data.get('leaderkey') != os.environ['LEADER_KEY']:
        return templates.admin_login('Leader key is incorrect')
    elif data.get('action') == 'Start':
        ec2.start_instances(InstanceIds=[os.environ['INSTANCE_ID']])
    elif data.get('action') == 'Shutdown':
        send_sqs({
            'action': 'shutdown',
            'time': int(data.get('shutdown-time', 3)),
            'message': data.get('shutdown-message', 'Bye everyone!')
        })
    elif data.get('action') == 'Send message':
        send_sqs({
            'action': 'send-message',
            'message': data.get('message', 'Nothing to see here...')
        })
    elif data.get('action') == 'Add':
        if data.get('player-name', '').strip():
            send_sqs({
                'action': 'whitelist',
                'player': data['player-name']
            })

    return main_page()
