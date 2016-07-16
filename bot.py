import json

import puka
import slackweb

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T1QBV6FK3/" \
                    "B1SA3L6HJ/5qERMBlTSP73gYuWWi38jgVG"

def main():
    slack = slackweb.Slack(url=SLACK_WEBHOOK_URL)

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
        body = json.loads(message['body'])
        if body['door'] == 'Unit 6 Exit':
            slack.notify(text="{0} has left HackLab.".format(body['nickname']))
        elif body['door'] == 'Unit 6':
            slack.notify(text="{0} has entered HackLab.".format(
                                                            body['nickname']))

    consumer.close()

if __name__ == '__main__':
    main()
