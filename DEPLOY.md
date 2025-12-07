# Deployment Guide

## 1. Environment Setup (Server)
Create a new Unix user and set up the project:
```bash
sudo adduser botuser
sudo su - botuser
# Clone repo here or copy files
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Configuration
Create a `.env` file **outside** the repo (or inside, but it's gitignored) with restricted permissions:
```bash
nano .env
# Paste:
# TELEGRAM_BOT_TOKEN=...
# GEMINI_API_KEY=...

chmod 600 .env
```

## 3. Running with Systemd
Create a service file: `/etc/systemd/system/seo-bot.service`

```ini
[Unit]
Description=YouTube to SEO Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/project_youtube_to_seo
ExecStart=/home/botuser/project_youtube_to_seo/.venv/bin/python bot.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/seo-bot.log
StandardError=append:/var/log/seo-bot.error.log

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable seo-bot
sudo systemctl start seo-bot
```

## 4. Maintenance
- **Logs**: `tail -f /var/log/seo-bot.log`
- **Cleanup**: Add a cron job to clean `output/` folder periodically.
  `0 4 * * * find /home/botuser/project_youtube_to_seo/output -name "Article_*" -mtime +7 -delete`
