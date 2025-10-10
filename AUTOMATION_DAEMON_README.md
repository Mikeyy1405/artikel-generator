# WritgoAI Content Automation Daemon

Geautomatiseerd content generatie en publicatie systeem voor WritgoAI.

## 📋 Overzicht

De Content Automation Daemon is een volledig geautomatiseerd systeem dat:
- Dagelijks checkt welke websites content nodig hebben
- Automatisch blog content genereert met AI
- Content publiceert naar WordPress of opslaat voor goedkeuring
- Alle acties logt voor debugging en monitoring
- Errors gracefully afhandelt zonder crashes

## 🚀 Features

### ✅ Voltooid
- ✅ Automatische scheduling op basis van website configuratie
- ✅ Content plan generatie met keyword rotatie
- ✅ Blog generatie met OpenAI GPT-4
- ✅ Afbeeldingen van Pixabay/Pexels/Unsplash
- ✅ Interne links van sitemap
- ✅ Affiliate links integratie
- ✅ WordPress publicatie via REST API
- ✅ Approval workflow voor handmatige review
- ✅ Uitgebreide logging en error handling
- ✅ Dry-run mode voor testing
- ✅ Per-website processing

### 🔄 Posting Schedules

De daemon ondersteunt verschillende posting frequenties:
- **Daily**: Elke dag
- **5x per week**: 5 dagen per week (standaard ma-vr)
- **3x per week**: 3 dagen per week (standaard ma/wo/vr)
- **Weekly**: 1x per week (standaard maandag)
- **Monthly**: 1x per maand (eerste dag van de maand)

## 📦 Installatie

### Vereisten
```bash
# Python 3.8+
python3 --version

# Installeer dependencies
pip install -r requirements.txt

# Extra dependencies voor daemon
pip install deep-translator beautifulsoup4
```

### API Keys Configuratie

De daemon heeft de volgende API keys nodig (opgeslagen in `~/.config/abacusai_auth_secrets.json`):

```json
{
  "openai": {
    "secrets": {
      "api_key": {
        "value": "sk-..."
      }
    }
  },
  "pixabay": {
    "secrets": {
      "api_key": {
        "value": "..."
      }
    }
  },
  "pexels": {
    "secrets": {
      "api_key": {
        "value": "..."
      }
    }
  }
}
```

## 🎯 Gebruik

### Basis Gebruik

```bash
# Run daemon (normale mode)
python3 content_automation_daemon.py

# Dry-run mode (test zonder te publiceren)
python3 content_automation_daemon.py --dry-run

# Process specifieke website
python3 content_automation_daemon.py --website-id 1

# Combinatie
python3 content_automation_daemon.py --dry-run --website-id 1
```

### Via Wrapper Script

```bash
# Run via wrapper
./run_automation_daemon.sh

# Met opties
./run_automation_daemon.sh --dry-run
```

## 📅 Scheduling

### Cron Setup (Dagelijks om Middernacht)

```bash
# Edit crontab
crontab -e

# Add line:
0 0 * * * /home/ubuntu/github_repos/artikel-generator/run_automation_daemon.sh >> /home/ubuntu/github_repos/artikel-generator/logs/cron.log 2>&1
```

### Cron Setup (Elk Uur)

```bash
# Edit crontab
crontab -e

# Add line:
0 * * * * /home/ubuntu/github_repos/artikel-generator/run_automation_daemon.sh >> /home/ubuntu/github_repos/artikel-generator/logs/cron.log 2>&1
```

### Systemd Service (Aanbevolen voor Productie)

Maak `/etc/systemd/system/writgo-automation.service`:

```ini
[Unit]
Description=WritgoAI Content Automation Daemon
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/github_repos/artikel-generator
ExecStart=/home/ubuntu/github_repos/artikel-generator/run_automation_daemon.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Maak `/etc/systemd/system/writgo-automation.timer`:

```ini
[Unit]
Description=WritgoAI Content Automation Timer
Requires=writgo-automation.service

[Timer]
OnCalendar=daily
OnCalendar=00:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable en start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable writgo-automation.timer
sudo systemctl start writgo-automation.timer

# Check status
sudo systemctl status writgo-automation.timer
sudo systemctl list-timers
```

## 📊 Logging

### Log Locaties

- **Daemon logs**: `/home/ubuntu/github_repos/artikel-generator/logs/automation_daemon_YYYYMMDD.log`
- **Cron logs**: `/home/ubuntu/github_repos/artikel-generator/logs/cron.log`
- **Systemd logs**: `journalctl -u writgo-automation.service`

### Log Formaat

```
2025-10-10 13:09:21,094 - ContentAutomationDaemon - INFO - 🚀 CONTENT AUTOMATION DAEMON STARTED
2025-10-10 13:09:21,130 - ContentAutomationDaemon - INFO - ✅ Website due for posting: Test Blog (ID: 1)
2025-10-10 13:09:48,635 - ContentAutomationDaemon - INFO - ✅ Blog content generated successfully
2025-10-10 13:09:48,774 - ContentAutomationDaemon - INFO - 📊 DAEMON RUN COMPLETED
```

### Log Monitoring

```bash
# Tail live logs
tail -f logs/automation_daemon_$(date +%Y%m%d).log

# Check for errors
grep "ERROR" logs/automation_daemon_*.log

# Check statistics
grep "Statistics:" logs/automation_daemon_*.log
```

## 🔧 Database Schema

### Websites Table

```sql
CREATE TABLE websites (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    posting_schedule TEXT DEFAULT 'weekly',
    posting_days TEXT,
    posting_time TEXT DEFAULT '09:00',
    auto_publish INTEGER DEFAULT 0,
    last_post_date TEXT,
    wordpress_url TEXT,
    wordpress_username TEXT,
    wordpress_password TEXT,
    ...
);
```

### Content Plans Table

```sql
CREATE TABLE content_plans (
    id INTEGER PRIMARY KEY,
    wordpress_site_id INTEGER,
    title TEXT NOT NULL,
    keyword TEXT,
    scheduled_date TEXT,
    scheduled_time TEXT,
    auto_generated INTEGER DEFAULT 0,
    approval_status TEXT,
    generated_content TEXT,
    wordpress_post_id TEXT,
    ...
);
```

## 🔄 Workflow

### 1. Check Websites Due for Posting

```python
# Daemon checkt welke websites moeten posten vandaag
websites = daemon.get_websites_due_for_posting()

# Gebruikt automation_utils.should_post_today()
if should_post_today(website):
    # Process website
```

### 2. Get or Create Content Plan

```python
# Check of er al een content plan is voor vandaag
content_plan = daemon.get_or_create_content_plan(website)

# Als niet: maak nieuwe met volgende keyword
# Keywords komen van onboarding_sessions.keyword_research_data
```

### 3. Generate Blog Content

```python
# Gebruik BlogGenerator om content te maken
blog_content = daemon.generate_blog_content(website, content_plan)

# Inclusief:
# - AI gegenereerde tekst (OpenAI GPT-4)
# - Afbeeldingen (Pixabay/Pexels)
# - Interne links (van sitemap)
# - Affiliate links
```

### 4. Publish or Save for Approval

```python
if website.auto_publish == 1:
    # Publiceer direct naar WordPress
    daemon.publish_to_wordpress(website, content_plan, blog_content)
else:
    # Sla op voor handmatige goedkeuring
    daemon.save_for_approval(content_plan, blog_content)
```

### 5. Update Website

```python
# Update last_post_date
daemon.update_website_post_date(website)
```

## 📈 Monitoring & Statistics

### Run Statistics

Na elke run logt de daemon:
- Websites checked
- Websites processed
- Websites failed
- Content generated
- Content published
- Content pending approval
- Execution time
- Errors

### Example Output

```
📊 DAEMON RUN COMPLETED
⏱️ Duration: 27.68 seconds
################################################################################
📈 Statistics:
   - Websites checked: 5
   - Websites processed: 5
   - Websites failed: 0
   - Content generated: 5
   - Content published: 3
   - Content pending approval: 2
```

## 🐛 Troubleshooting

### Daemon Niet Gestart

```bash
# Check Python versie
python3 --version

# Check dependencies
pip list | grep -E "openai|requests|beautifulsoup4"

# Check database
sqlite3 writgo_content.db "SELECT COUNT(*) FROM websites"
```

### Geen Websites Gevonden

```bash
# Check websites in database
sqlite3 writgo_content.db "SELECT id, name, posting_schedule, last_post_date FROM websites"

# Check of websites WordPress credentials hebben
sqlite3 writgo_content.db "SELECT id, name, wordpress_url FROM websites WHERE wordpress_url IS NOT NULL"
```

### Content Generatie Faalt

```bash
# Check OpenAI API key
cat ~/.config/abacusai_auth_secrets.json | jq '.openai.secrets.api_key.value'

# Check Pixabay API key
cat ~/.config/abacusai_auth_secrets.json | jq '.pixabay.secrets.api_key.value'

# Test blog generator
python3 -c "from blog_generator import BlogGenerator; print('OK')"
```

### WordPress Publicatie Faalt

```bash
# Test WordPress API
curl -u username:password https://example.com/wp-json/wp/v2/posts

# Check credentials in database
sqlite3 writgo_content.db "SELECT wordpress_url, wordpress_username FROM websites WHERE id = 1"
```

## 🔐 Security

### API Keys
- Opgeslagen in `~/.config/abacusai_auth_secrets.json`
- Niet in git repository
- Alleen leesbaar door user

### WordPress Credentials
- Opgeslagen in database (encrypted aanbevolen)
- Gebruik Application Passwords (WordPress 5.6+)
- Niet plain text passwords

### Database
- SQLite database met file permissions
- Backup aanbevolen
- Niet publiek toegankelijk

## 📝 Configuration

### daemon_config.json

```json
{
  "schedule": {
    "type": "daily",
    "time": "00:00"
  },
  "limits": {
    "max_websites_per_run": 50,
    "max_execution_time_minutes": 120
  },
  "features": {
    "auto_publish": true,
    "generate_images": true,
    "add_internal_links": true,
    "add_affiliate_links": true
  }
}
```

## 🚦 Status Codes

- **0**: Success - alle websites succesvol verwerkt
- **1**: Failure - één of meer websites gefaald

## 📞 Support

Voor vragen of problemen:
- Check logs in `/home/ubuntu/github_repos/artikel-generator/logs/`
- Run met `--dry-run` voor testing
- Check database met SQLite browser

## 🔄 Updates

### Version 1.0.0 (2025-10-10)
- ✅ Initial release
- ✅ Automated content generation
- ✅ WordPress publishing
- ✅ Approval workflow
- ✅ Comprehensive logging
- ✅ Error handling

## 📄 License

Proprietary - WritgoAI

## 👥 Authors

- WritgoAI Development Team
- Powered by Abacus.AI Deep Agent
