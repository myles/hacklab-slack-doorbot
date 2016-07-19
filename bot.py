import json
import logging
import argparse

import puka
import slackweb

logging.basicConfig(filename='bot.log', level=logging.INFO)


def main(slack_webhook_url):
    slack = slackweb.Slack(url=slack_webhook_url)

    # declare and connect a consumer
    consumer = puka.Client("amqp://192.168.111.14/")
    connect_promise = consumer.connect()
    consumer.wait(connect_promise)

    # create temporary queue
    queue_promise = consumer.queue_declare(exclusive=True)
    queue = consumer.wait(queue_promise)['queue']

    # bind the queue to newsletter exchange
    bind_promise = consumer.queue_bind(exchange='door.entry', queue=queue,
                                       routing_key='doorbot')
    consumer.wait(bind_promise)

    # start waiting for messages on the queue created beforehand and print
    # them out
    message_promise = consumer.basic_consume(queue=queue, no_ack=True)

    while True:
        message = consumer.wait(message_promise)

        logging.info(message)

        try:
            body = json.loads(message['body'])
        except:
            body = {'door': False}

        if body['door'] == 'Unit 6 Exit':
            slack.notify(text="{0} has left HackLab.".format(body['nickname']))
        elif body['door'] == 'Unit 6':
            slack.notify(text="{0} has entered HackLab.".format(
                                                            body['nickname']))

    consumer.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url')
    args = parser.parse_args()

    main(args.url)
