# Test bot that can use Google Dialogflow for response 
***
## Introduction
Application created for answering on a natural language questions. It exploits
the power of Google dialogFLow framework and social network [Vkontacte](vk.com)
and [Telegram](https://tlgrm.ru/) Messenger.      


## Local installation
For local installation use requirements:  
 `$pip install requirements.txt`  
Follow by this instruction [instructions: how-do-i-create-a-bot](https://core.telegram.org/bots/faq#how-do-i-create-a-bot).
Get chat_id which equal to user Id from the special Bot _@userinfobot_.
Create project in the [GCP](https://cloud.google.com/dialogflow/docs/quick/setup)
Create Google service account and store `Google credential.json` locally
Create [VK](vk.com) account, public group and get VK_API token on page `https://vk.com/club<your_vk_id>?act=tokens`  
Create `.env` file with settings:
* TLG_TOKEN
* VK_API
* DF_PROJECT
* GOOGLE_APPLICATION_CREDENTIALS
* VK_GROUP
* HTTPS_PROXY
   
## Google DialogFlow
Create DialogFlow [Agent](https://cloud.google.com/dialogflow/docs/quick/build-agent)
For the testing purpose it makes sense to get the set of questions and answers
 from [this place](https://dvmn.org/filer/canonical/1556745451/104/).
 To get this set execute this: `python df_intents.py --intents_mode download`
 You'll get `question.json` in the project directory. To setup intent set into the agent run:  
`python df_intents.py --intents_mode upload`. It teaches your Agent to answer.


Add these lines to the import section  
`from dotenv import load_dotenv`  
`from os import getenv`  
Add these lines of code to the `ifname` section  
`load_dotenv()`  
`dvmn_token = getenv('DVMN_TOKEN')`  
`tlg_token = getenv('TLG_TOKEN')`   
Comment all line with `os.environ` substring

## Local check how it works
Run this  `python tlg_bot.py` then go to chat with the Bot. Ask him the any phrase from `json-file`
with *question* key. He should answer from appropriate answer from the list of *answers* keys. 



## Deploying onto remote server (Heroku)
### Registration
* [Sign up](https://signup.heroku.com/login) by this link.
* Create your own repo on [Github](https://github.com/).
* Link your repo with your application.
* Your repo has to have `procfile` more information [there](https://devcenter.heroku.com/articles/procfile).  
It has to comprise this line `bot: python yourfilename.py`. Set up environment variables on the setting Tab
of  your dashboard in the _Config Var_ Section
If your acquire a free heroku account it makes sense to stop your bot if it's not needed.
You can do it by execute command:  
`heroku ps:stop DYNO -a <your-app name>`. Your  
  

## Project Goals
The code has been written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/modules/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/psergal/bitly/blob/master/license.md) file for details  

 

