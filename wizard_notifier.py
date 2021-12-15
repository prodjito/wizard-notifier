import os
import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slack_sdk import WebClient

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

token = os.environ['BOT_USER_OAUTH_TOKEN']
product_to_channel_mapping = json.loads(os.environ['PRODUCT_TO_CHANNEL_MAPPING'])

app = Flask(__name__)

client = WebClient(token)

@app.route('/ask-wizard', methods=['POST'])
def ask_wizard():
    data = request.form
    user_name = data.get('user_name')
    customer_channel_id = data.get('channel_id')
    customer_channel_name = data.get('channel_name')
    text = data.get('text')

    if customer_channel_name.startswith('shared'):
        parsed = text.split(' ', 1)
        key_word = parsed[0]
        if key_word in product_to_channel_mapping:
            message = parsed[1]
            wizard_channel_id = product_to_channel_mapping[key_word]
            wizard_channel_name = client.conversations_info(token=token,channel=wizard_channel_id)['channel']['name']
            client.chat_postMessage(channel=wizard_channel_id, text='`%s` in `#%s` posted: ```%s```'%(user_name, customer_channel_name, message))
            client.chat_postMessage(channel=customer_channel_id, text='`%s`, your message: ```%s``` has been reposted on `#%s`.'%(user_name, message, wizard_channel_name))
        else:
            client.chat_postMessage(channel=customer_channel_id, text='Your message must start with one of the following: ' + str(", ".join(list(product_to_channel_mapping.keys()))))

    return Response(), 200

if __name__ == "__main__":
    app.run(debug=True)