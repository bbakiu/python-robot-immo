
# python-robot-immo

python-robot-immo is an easy project that can be used to quickly get new announcements posted in immobilien scout.
You can choose to deploy where it fits you best. In this documentation you will see the setup in [Heroku](https://www.heroku.com/).
The general idea is to query the page of [immobilienscout24](https://www.immobilienscout24.de/) in regular basis and send notification to you via [Telegram](https://telegram.org/).

## Setup
### Telegram Bot
Use BotFather to create a chat bot in telegram. Short explanation is [here](https://core.telegram.org/bots#6-botfather).
Basically find BotFather in Telegram and send the message `/newbot` and follow the instructions.
After you have created the chat bot you should have gotten a token that allows you to control the bot, something like `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`.

```
$ export BOT_TOKEN=<TELEGRAM_BOT_TOKEN>
```

From telegram you are going to need also a chat id, which in the id of your chat with the bot. 
Send a couple of messages to the bot you just created and run this command:
```
$ curl https://api.telegram.org/bot<YourBOTToken>/getUpdates
```

Look for the "chat" object in the message you will get. It is something along the lines:
```
{"update_id":8393,
"message":{"message_id":3,"from":{"id":7474,"first_name":"AAA"},
"chat":{"id":,"title":""},
"date":25497,
"new_chat_participant":{"id":71,"first_name":"NAME","username":"YOUR_BOT_NAME"}}}
```
After you have found the chat id, export it:
```
$ export CHAT_ID=<TELEGRAM_BOT_CHAT_ID>
```
If the response does not look like that write a couple of more messages to the bot.

### Environment Variables
Create these environment variables in your machine:
```
$ export SECRET_KEY=<secret used in the app to very the requests>
$ export APP_NAME=<name of the app in heroku>
$ export IMMO_SEARCH_URL=<url with filters from [immobilienscout24](https://www.immobilienscout24.de/)>
```

### Deploying to Heroku
Install heroku cli:
```
$ brew tap heroku/brew && brew install heroku
```
Create application:
```
$ heroku create $APP_NAME
```
Export environment variables
```
$ heroku config:set -a $APP_NAME BOT_TOKEN=$BOT_TOKEN
$ heroku config:set -a $APP_NAME CHAT_ID=$CHAT_ID
$ heroku config:set -a $APP_NAME SECRET_KEY=$SECRET_KEY
$ heroku config:set -a $APP_NAME IMMO_SEARCH_URL=$IMMO_SEARCH_URL
```
