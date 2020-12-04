# PyDejavuBot [βeta]
[![CodeFactor](https://www.codefactor.io/repository/github/zhymabekroman/pydejavubot/badge)](https://www.codefactor.io/repository/github/zhymabekroman/pydejavubot)

|**English verssion** | [Русская версия](https://github.com/ZhymabekRoman/PyDejavuBot/blob/master/README-RU.md) |

**PyDejavuBot** (a.k.a. **LenDejavuBot** - Free open source Telegram Bot, designed for recognize a melody. The main focus of the bot is stability, speed, and audio recognitions quality. In the beginning, the bot was written on PyTelegramBotApi, but an emergency decision was made to switch to a more stable and powerful library - aiogram. Audio recognition system based on Landmark audio fingerprinting system.

## Destination :
First of all, the bot is useful for professional musicians. The main focus was made for students of music schools, colleges, and conservatories. Few people know, but musicians have some music lessons, which are asked music quizzes, where you need to teach and remember each audio recording and the name of the audio recording itself. Sometimes that the list itself reaches up to 40 audio recordings. Undoubtedly, this is a very time-consuming job, and not everyone gets a good rating.

Shazam is not particularly useful here, since it sometimes does not correctly recognize the audio recording itself. If even correctly recognized, then the information of the recognized record is not enough for the teacher.

## Features :
- [x] Fully asynchronous Telegram Bot written in Python 3 with aiogram.
- [x] High speed and accuracy recognition
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
