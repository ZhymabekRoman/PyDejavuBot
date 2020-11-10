# PyDejavuBot
[![CodeFactor](https://www.codefactor.io/repository/github/zhymabekroman/pydejavubot/badge)](https://www.codefactor.io/repository/github/zhymabekroman/pydejavubot)

PyDejavuBot (a.k.a. LenDejavuBot) - Telegram bot, designed for solving music quizzes. The main focus of the bot is stability, speed, and audio recognitions quality. In the beginning, the bot was written on PyTelegramBotApi, but an emergency decision was made to switch to a more stable and powerful library - aiogram. Audio recognition system based on Landmark audio fingerprinting system.

## Destination :
First of all, the bot is useful for professional musicians. The main focus was made for students of music schools, colleges, and conservatories. Few people know, but musicians have music lessons (some), which are asked music quizzes that you need to learn and remember. Sometimes it happens that this list is impossible to learn and it even happens that the list itself reaches up to 50 audio recordings. And all this needs to be taught. Undoubtedly, this is a very time-consuming job, and not everyone gets a good rating. 

## Features :
- [x] Fully asynchronous Telegram bot written in Python 3.
- [x] High speed audio recognition 
- [x] High recognition accuracy
- [ ] Multilanguage supporting : En,  Ru, Kz (WIP)

## Used libraries and third-party programs :
audfprint - Python version of Matlab implementation of Landmark audio recognition system. This is the heart of the bot itself. A huge thank to Dan Ellis, Columbia University, and Google. Link : https://github.com/dpwe/audfprint

ffmpeg - third-party super-powerful program for working with audio and video. Used for converting and working with audio hashes.

## Installation : 
1) In Ubuntu or Debian based distribution install ffmpeg, python 3 and pip3 :
`sudo apt install python3 python3-pip ffmpeg git -y`
2) Clone this repository :
`git clone https://github.com/ZhymabekRoman/PyDejavuBot`
3) Install all python depends via pip3: 
`cd PyDejavuBot/
pip3 install -r requirements.txt`
4) Initialize bot configurations:
`cd src/
python3 first_start.py`
and answer the script's questions.
5) Launching the bot:
`python3 main.py`

_*WIP - Working in process_
