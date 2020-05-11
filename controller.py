#!/usr/bin/env python3

import sys
import json
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
        WaitTimeSeconds=5
    )
    message = response['Messages'][0]
    try:
        yield json.loads(message['Body'])
    finally:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )
    

class MinecraftInterface:
    def __init__(self):
        pass

    def cmd(self, command):
        subprocess.run(['screen', '-S', 'minecraft', '-X', 'stuff',
                        command + '\r'], check=True)

    def schedule_shutdown(self, delay_min, message):
        self.send_message(message)
        for i in range(1, delay_min-1):
            event_sched.enter(i * 60, 1, self.send_message,
                              argument=(
                                  f'{i} minute{"s" if i>1 else ""} left...',
                              ))
        for i in range(1, 10):
            event_sched.enter((delay_min * 60) - i, 1, self.send_message,
                              argument=(f'{i} ...',))
        event_sched.enter(delay_min * 60, 1, self.cmd, argument=('stop',))

    def send_message(self, msg):
        self.cmd(f'say {msg}')
        
    def perform_action(self, msg):
        if msg is None:
            return

        if msg['action'] == 'shutdown':
            self.schedule_shutdown(msg['time'], msg['message'])
        elif msg['action'] == 'send-message':
            self.send_message(msg['message'])

        
def main(queue_url):
    mc = MinecraftInterface()
    delay_until = None
    while True:
        with command_queue(queue_url) as msg:
            mc.perform_action(msg)

        if delay_until is not None:
            delay = time.monotonic() - delay_until
            time.sleep(delay)
        delay = event_sched.run(blocking=False)
        if delay is None:
            delay_until = None
        else:
            delay_until = delay + time.monotonic()


if __name__ == '__main__':
    main(sys.argv[1])
