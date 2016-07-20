# hacklab-slack-doorbot

This is the source code for [HackLab.TO](https://hacklab.to/)'s Slack Doorbot. It connects to HackLab's AMQP server and waits for when a member enters the building and notifies the Slack channel `#doorbot`.

## Requirments

* Python 2.7
* [puka](https://pypi.python.org/pypi/puka)
* [slackweb](https://pypi.python.org/pypi/slackweb)

## Usage

```bash
python bot.py --url=$SLACK_WEBHOOK_URL
```
