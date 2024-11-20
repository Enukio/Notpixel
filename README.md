# 🎨 AUTO FARM FOR NotPixel 🎨

> [!WARNING]
> I make every effort to avoid bot detection, but using bots is prohibited in all airdrops. I cannot guarantee that you won't be flagged as a bot. Use this software at your own risk. I am not liable for any consequences that may arise from its use.

# 🔥🔥 PYTHON version must be 3.10 - 3.11.5 🔥🔥

## Features  
|                      Feature                       | Supported |
|:--------------------------------------------------:|:----------:|
|                   Multithreading                   |     ✅     |
|              Proxy binding to session              |     ✅     |
|           Support for pyrogram .session            |     ✅     |
| Auto-register your account with your referral code |     ✅     |
|                     X3 POINTS                      |     ✅     |
|                     Auto tasks                     |     ✅     |
|                     Auto games                     |     ✅     |
|                    Auto drawing                    |     ✅     |
|                    Auto upgrade                    |     ✅     |
|              Auto claiming of reward               |     ✅     |


## [Settings](https://github.com/Enukio/Notpixel/blob/main/.env-example)
| Settings | Description |
|----------------------------|:-------------------------------------------------------------------------------------------------------------:|
| **API_ID / API_HASH**      | Platform data from which to run the Telegram session (default - android)                                      |       
| **REF_LINK**               | Put your ref link here (default: my ref link)                                                                 |
| **AUTO_TASK**              |  Auto do tasks (default: True)                                                                                |
| **AUTO_UPGRADE_PAINT_REWARD** | AUTO upgrade paint reward if possible (default: True)                                                      |
| **AUTO_UPGRADE_RECHARGE_SPEED** | AUTO upgrade recharge speed if possible (default: True)                                                  |
| **AUTO_UPGRADE_RECHARGE_ENERGY** | AUTO upgrade energy limit if possible (default: True)                                                   |
| **USE_CUSTOM_TEMPLATE** | Use custom template if it's disabled global template will be used (default: True)                                |
| **CUSTOM_TEMPLATE_ID** | your custom template id (default: my template id)                                                                 |
| **USE_RANDOM_TEMPLATES** | Option to use random templates on catalog (default: False)                                                      |
| **RANDOM_TEMPLATES_ID** |List of templates id (default: list of templates on catalog )                                                     |
| **NIGHT_MODE** | Sleep time for the bot (default: True)                                                                                    |
| **SLEEP_TIME** | Sleep in your timezone for the bot (default: [0, 7] 0am to 7am)                                                           |
| **DELAY_EACH_ACCOUNT** | Sleep time in second between each account(non multi thread) (default: [10, 15])                                   |
| **SLEEP_BETWEEN_EACH_ROUND** | Sleep time in second between each round (default: [1000, 1500])                                             |
| **ADVANCED_ANTI_DETECTION** | More protection for your account ;-; (default: False)                                                        |
| **USE_PROXY_FROM_FILE**    | Whether to use a proxy from the bot/config/proxies.txt file (True / False)                                    |
| **BOT_TOKEN**    | Get Bot Token from [@BotFather](https://t.me/BotFather) (default: )                                                     |


## Quick Start 📚

To fast install libraries and run bot -> open run.bat on Windows or run.sh on Linux

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10 - 3.11.5**

## Obtaining API Keys
1. Go to my.telegram.org and log in using your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Record the API_ID and API_HASH provided after registering your application in the .env file.

## Installation
You can download the [**repository**](https://github.com/Enukio/Notpixel) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/Enukio/Notpixel.git
```
```shell
cd NotPixels
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Windows manual installation
```shell
python -m venv venv
```
```shell
venv\Scripts\activate
```
```shell
pip install -r requirements.txt
```
```shell
copy .env-example .env
```
```shell
notepad .env
```
# Here you must specify your API_ID and API_HASH, the rest is taken by default
```shell
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/np >>> python main.py --action (1/2)
# Or
~/np >>> python main.py -a (1/2)

# 1 - Start drawing
# 2 - Create session
```

# Linux manual installation
```shell
python3 -m venv venv
```
```shell
source venv/bin/activate
```
```shell
pip3 install -r requirements.txt
```
```shell
cp .env-example .env
```
```shell
nano .env 
```
 Here you must specify your API_ID and API_HASH, the rest is taken by default
 ```shell
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/np >>> python3 main.py --action (1/2)
# Or
~/np >>> python3 main.py -a (1/2)

# 1 - Start Drawing
# 2 - Create Session
# 3 - Using Query
```

# Termux manual installation
```
> pkg update && pkg upgrade -y
> pkg install python rust git -y
> git clone https://github.com/Enukio/Notpixel.git
> cd Notpixel-bot
> cp .env-example .env
> nano .env
# edit your api_id and api_hash
> pip install -r requirements.txt
> python main.py
```

You can also use arguments for quick start, for example:
```termux
~/Notpixel-bot > python main.py --action (1/2)
# Or
~/Notpixel-bot > python main.py -a (1/2)

# 1 - Start drawing
# 2 - Create session
```
