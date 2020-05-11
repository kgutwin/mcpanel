import os
import json
import boto3

from lambdas import templates

ec2 = boto3.client('ec2')
sqs = boto3.client('sqs')


def render():
    return templates.admin_login()

def main_page(response=''):
    r = ec2.describe_instances(InstanceIds=[os.environ['INSTANCE_ID']])
    i = r['Reservations'][0]['Instances'][0]
    status = i['State']
    return templates.admin_page(
        os.environ['LEADER_KEY'],
        instance_state=status,
        response=response
    )

def update(data):
    print(data)
    if data.get('leaderkey') != os.environ['LEADER_KEY']:
        return templates.admin_login('Leader key is incorrect')
    elif data.get('action') == 'Start':
        ec2.start_instances(InstanceIds=[os.environ['INSTANCE_ID']])
    elif data.get('action') == 'Shutdown':
        sqs.send_message(
            QueueUrl=os.environ['MESSAGE_QUEUE'],
            MessageBody=json.dumps({
                    'action': 'shutdown',
                    'time': int(data.get('shutdown-time', 3)),
                    'message': data.get('shutdown-message', 'Bye everyone!')
                    })
            )
    elif data.get('action') == 'Send message':
        sqs.send_message(
            QueueUrl=os.environ['MESSAGE_QUEUE'],
            MessageBody=json.dumps({
                    'action': 'send-message',
                    'message': data.get('message', 'Nothing to see here...')
                    })
            )
    return main_page()
