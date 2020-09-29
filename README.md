# DiscordBot
 
This bot is meant to support media (games, movies, ect) in your discord channel.

## Dependencies
```
discord.py https://discordpy.readthedocs.io/en/latest/
```

## Configuration
Set up your config.ini file in the same directory as app.py and add the following
```
[General]
#Change to another value if you want to run the dev bot with dev secret
prod=true

secret = <Paste your discord bot secret here>

#Optional: Replace 'none' with a second bot secret
dev_secret = none

[Games]
enabled=true

#This will be prefixed onto any role that is made for games
name=game

#This is the channel category that the bot will manage games under
category_name = Games

#This will be the role that is used to manage requests for new games
approver_role = Game Approver
```
