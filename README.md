<h1 align="center">Bot Luminary</h1>

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

This is a general purpose discord bot written in **Python** for the [Black Luminary Discord Server](https://discord.gg/ZWKswJRsjC) with support for moderation, logging, reaction roles etc.
<br>

The bot's command prefix is `;`<br>

# Current Features

## Moderation
The  features include automatic temp-mute and unmute triggered by banned words, purge messages, warn, mute, unmute, ban, unban and kick commands.

## Reaction Roles

## Logging

The bot logs the following events-
- Username, Nickname & Avatar update
- Message edit & deletion
- Member join & leave
- Role add & remove
- Voice channel join & leave 

It sends the logs to the following channels-
- SERVER_LOG
- MESSAGE_LOG
- MEMBER_LOG
- VOICE_LOG
- JOIN_LEAVE_LOG

The CHANNEL IDs for the channels need to be present in the `.env` file in the root directory.

## The `.env` file

This file contains the Bot's TOKEN, DATABASE_TOKEN and GUILD & CHANNEL IDs.
<br>We used `PostgreSQL` database for the bot so the credentials also need to be present in the `.env` file. In the `.env` file, you have to include `DATABASE_URL`.<br> If you use `sqlite` db, then you won't need to put the `DATABASE_URL` in the env file, just open and read the file in the `utils/database.py` for the SQL operations.


# Notes

The bot has been programmed with Black Luminary Discord Server specific configurations, so unless you have Python programming knowledge and can change the configurations on you own, you won't be able to use this bot on your server.<br>If you do have the Python experience and decide to configure it for your server, you can have ask us any questions in the repository's Discussion section, If we have free time, we will try to answer your questions.



