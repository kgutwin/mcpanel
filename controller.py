#!/usr/bin/env python3

import sys
import json
import time
import boto3
import sched
import subprocess
from contextlib import contextmanager

sqs = boto3.client('sqs')

event_sched = sched.scheduler()


@contextmanager
def command_queue(queue_url):
    response = sqs.receive_message(
        QueueUrl=queue_url,
        WaitTimeSeconds=2
    )
    if 'Messages' in response:
        message = response['Messages'][0]
        try:
            print('[controller] Inbound message:', message['Body'])
            yield json.loads(message['Body'])
        finally:
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
    else:
        yield None
    

class MinecraftInterface:
    def __init__(self):
        pass

    def cmd(self, command):
        print('[controller] minecraft server command:', command)
        subprocess.run(['screen', '-S', 'minecraft', '-p', '1',
                        '-X', 'stuff', command + '\r'], check=True)

    def schedule_shutdown(self, delay_min, message):
        self.send_message(
            f'{message} {delay_min} minute{"s" if delay_min>1 else ""}'
            f' until server shutdown!'
        )
        for i in range(1, delay_min):
            event_sched.enter((delay_min - i) * 60, 1, self.send_message,
                              argument=(
                                  f'{i} minute{"s" if i>1 else ""} left...',
                              ))
        if delay_min > 0:
            for i in range(1, 11):
                event_sched.enter((delay_min * 60) - (i*2), 1,
                                  self.send_message,
                                  argument=(f'{i} ...',))
        event_sched.enter(delay_min * 60, 1, self.cmd, argument=('stop',))

    def send_message(self, msg):
        self.cmd(f'say {msg}')

    def set_world(self, world_name):
        self.send_message(
            f'Changing world to {world_name}, log off in 1 minute...'
        )

        for i in range(1, 11):
            event_sched.enter(60 - (i * 2), 1, self.send_message,
                              argument=f('{i} ...',))

        event_sched.enter(60, 1, self.change_world, argument=(world_name,))

    def change_world(self, world_name):
        subprocess.run(
            ['/home/ec2-user/change-world.sh', world_name],
            check=True
        )
        
    def perform_action(self, msg):
        if msg is None:
            return

        if msg['action'] == 'shutdown':
            self.schedule_shutdown(msg['time'], msg['message'])
        elif msg['action'] == 'send-message':
            self.send_message(msg['message'])
        elif msg['action'] == 'whitelist':
            self.cmd(f'whitelist add {msg["player"]}')
        elif msg['action'] == 'set-world':
            self.set_world(msg['world'])

        
def main(queue_url):
    # Drain all queued commands at startup (so that we don't shutdown
    # right after start)
    draining = True
    while draining:
        with command_queue(queue_url) as msg:
            if msg is None:
                draining = False
    
    mc = MinecraftInterface()
    delay_until = None
    while True:
        with command_queue(queue_url) as msg:
            mc.perform_action(msg)

        event_sched.run(blocking=False)


if __name__ == '__main__':
    main(sys.argv[1])
