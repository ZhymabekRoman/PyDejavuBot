# PyDejavuBot [βeta]
[![CodeFactor](https://www.codefactor.io/repository/github/zhymabekroman/pydejavubot/badge)](https://www.codefactor.io/repository/github/zhymabekroman/pydejavubot)

|**English verssion** | [Русская версия](https://github.com/ZhymabekRoman/PyDejavuBot/blob/master/README-RU.md) |

**PyDejavuBot** (a.k.a. **LenDejavuBot** - Telegram bot, designed for solving music quizzes. The main focus of the bot is stability, speed, and audio recognitions quality. In the beginning, the bot was written on PyTelegramBotApi, but an emergency decision was made to switch to a more stable and powerful library - aiogram. Audio recognition system based on Landmark audio fingerprinting system.

## Destination :
First of all, the bot is useful for professional musicians. The main focus was made for students of music schools, colleges, and conservatories. Few people know, but musicians have music lessons (some), which are asked music quizzes that you need to learn and remember each audio recording and with the name of the audio recording itself . Sometimes it happens that this list is impossible to learn and it even happens that the list itself reaches up to 50 audio recordings. And all this needs to be taught. Undoubtedly, this is a very time-consuming job, and not everyone gets a good rating. 

## Features :
- [x] Fully asynchronous Telegram bot written in Python 3.
- [x] High speed audio recognition 
- [x] High recognition accuracy
- [ ] Multilanguage supporting : En,  Ru, Kz (_WIP*_)

## Installation : 
1) In Ubuntu or Debian based distribution install ffmpeg, python3, pip3 and git:
```
sudo apt install python3 python3-pip ffmpeg git -y
```
2) Clone this repository :
```
git clone https://github.com/ZhymabekRoman/PyDejavuBot
```
3) Install all python depends, that required for bot operation, via pip3: 
```
cd PyDejavuBot/
pip3 install -r requirements.txt
```

4) Initialize bot configurations. This should only be done at the very first start of the bot:
```
cd src/
python3 first_start.py
```
and answer the script's questions.

5) Launching the bot:
```
python3 main.py
```

## Used libraries and third-party programs :
[audfprint](https://github.com/dpwe/audfprint) - Python version of Matlab implementation of Landmark audio recognition system. This is the heart of the bot itself. A huge thank to Dan Ellis, Columbia University, and Google.

[aiogram](https://github.com/aiogram/aiogram) - a pretty simple and fully asynchronous framework for Telegram Bot API written in Python 3.7 with asyncio and aiohttp.

[ffmpeg](https://ffmpeg.org/) - third-party super-powerful program for working with audio and video. Used for converting and working with audio hashes.



_*WIP - Working in process_
