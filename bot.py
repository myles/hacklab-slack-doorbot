import re
import json
import logging
import argparse

import puka
import slackweb

logging.basicConfig(filename='bot.log', format='%(asctime)s %(message)s',
                    level=logging.DEBUG)

ENTRY_TEXT = '{0} has entered HackLab.'
EXIT_TEXT = '{0} has left HackLab.'


def json_loads(raw):
    """
    Make sure JSON is valid and fix it if it's not.
    """

    try:
        body = json.loads(raw)
    except ValueError as e:
        # StackOverflow: <http://stackoverflow.com/a/18515887/43363>
        # Find the position of the bad apostrophe from the exception.
        unexp = int(re.findall(r'\(char (\d+)\)', str(e))[0])

        # Position of the unescaped '""' before that.
        unesc = raw.rfind('"', 0, unexp)
        raw = raw[:unesc] + r'\"' + raw[unesc+1:]

        # The position of the corresponding closing '"'
        closg = raw.find(r'"', unesc + 2)
        raw = raw[:closg] + r'\"' + raw[closg+1:]

        body = json.loads(raw)
    except:
        logging.debug("JSON `{0}` failed to be parsed.".format(raw))

    return body


def send_slack_message(webhook_url, msg):
    """
    Send a Slack message.
    """
    slack = slackweb.Slack(url=webhook_url)

    try:
        return slack.notify(msg)
    except:
        return None


def main(slack_webhook_url):
    # declare and connect a consumer
    consumer = puka.Client("amqp://192.168.111.14/")
    connect_promise = consumer.connect()
    consumer.wait(connect_promise)

    # create temporary queue
    queue_promise = consumer.queue_declare(exclusive=True)
    queue = consumer.wait(queue_promise)['queue']

    # bind the queue to door.entry exchange
    bind_doorbot_promise = consumer.queue_bind(exchange='door.entry',
                                               queue=queue,
                                               routing_key='doorbot')
    consumer.wait(bind_doorbot_promise)

    # bind the queue to autodoor exchange
    # bind_autodoor_promise = consumer.queue_bind(exchange='', queue=queue,
    #                                             routing_key='autodoor')
    # consumer.wait(bind_autodoor_promise)

    # start waiting for messages on the queue created beforehand
    message_promise = consumer.basic_consume(queue=queue, no_ack=True)

    while True:
        message = consumer.wait(message_promise)

        body = json_loads(message['body'])

        if body['door'] == 'Unit 6 Exit':
            send_slack_message(slack_webhook_url,
                               EXIT_TEXT.format(body['nickname']))
            logging.info('Notify Slack about {0} exiting the '
                         'HackLab.'.format(body['nickname']))
        elif body['door'] == 'Unit 6':
            send_slack_message(slack_webhook_url,
                               ENTRY_TEXT.format(body['nickname']))
            logging.info('Notify Slack about {0} entering the '
                         'HackLab.'.format(body['nickname']))

    consumer.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url')
    args = parser.parse_args()

    main(args.url)
