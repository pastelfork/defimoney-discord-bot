# This is a loans tracking Discord bot for defi.money

## Requirements
This project is managed using `uv`
```bash
pip install uv
```
You will also need:
* A Discord bot token
* A Discord channel ID for the bot to send messages to
* Websocket RPC URLs for Arbitrum and Optimism

## Setup
```bash
git clone https://github.com/pastelfork/defimoney-discord-bot
```
```bash
cd defimoney-discord-bot
```
```bash
cp .env.example .env
```
Paste your enviroment variables in the .env file (see requirements above).

```bash
uv run main.py
```
The bot should now be running and monitoring blockchain logs in realtime.
