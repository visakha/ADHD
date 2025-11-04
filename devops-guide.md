# ADHD Productivity Trio - DevOps & Installation Guide

## Overview

This guide covers installation, configuration, troubleshooting, and maintenance of the ADHD Productivity Trio application.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Management](#database-management)
5. [API Setup](#api-setup)
6. [Troubleshooting](#troubleshooting)
7. [Backup & Recovery](#backup--recovery)
8. [Updating](#updating)
9. [Advanced Configuration](#advanced-configuration)
10. [Security Best Practices](#security-best-practices)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Python**: 3.12 or higher (3.14 when available)
- **RAM**: 2 GB minimum, 4 GB recommended
- **Disk Space**: 500 MB for application and data
- **Internet**: Active connection required for Claude API

### Recommended Specifications
- **Python**: Latest stable version (3.12+)
- **RAM**: 8 GB for comfortable multitasking
- **Disk Space**: 2 GB for growth
- **Display**: 1400x900 or higher resolution

---

## Installation

### Method 1: Standard Installation (Recommended)

#### Step 1: Install Python

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify: Open Command Prompt and type:
   ```bash
   python --version
   ```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.12

# Verify
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3-pip python3-tk

# Verify
python3 --version
```

#### Step 2: Create Project Directory

```bash
# Navigate to where you want the app
cd ~
mkdir productivity-trio
cd productivity-trio
```

#### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

#### Step 4: Download Application Files

Place these files in your `productivity-trio` directory:
- `productivity_trio.py` (main application)
- `requirements.txt` (dependencies)

#### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `anthropic` - Claude API SDK
- All necessary dependencies

#### Step 6: First Run

```bash
python productivity_trio.py
```

**First launch will:**
1. Create `productivity_trio.db` (SQLite database)
2. Create `config.json` (settings file)
3. Show settings dialog for API key

---

### Method 2: Quick Installation (One Command)

```bash
# Clone/download files first, then:
cd productivity-trio
python -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
python productivity_trio.py
```

---

## Configuration

### Configuration File Structure

The app creates `config.json` in the same directory:

```json
{
  "anthropic_api_key": "your-api-key-here",
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 1024,
  "theme": "light"
}
```

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `anthropic_api_key` | string | "" | Your Claude API key |
| `model` | string | "claude-sonnet-4-5-20250929" | Claude model to use |
| `max_tokens` | integer | 1024 | Max response length |
| `theme` | string | "light" | UI theme (future use) |

### Editing Configuration

**Method 1: Through UI**
1. Open app
2. Go to `File > Settings`
3. Update values
4. Click Save

**Method 2: Direct File Edit**
1. Close app
2. Open `config.json` in text editor
3. Make changes
4. Save file
5. Restart app

---

## Database Management

### Database File

- **Location**: `productivity_trio.db` (same directory as app)
- **Type**: SQLite 3
- **Size**: Grows with usage (typically < 100 MB)

### Database Schema

#### Projects Table
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    initial_enthusiasm INTEGER DEFAULT 10,
    abandonment_count INTEGER DEFAULT 0
);
```

#### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    agent TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_snapshot TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);
```

#### Tasks Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    description TEXT NOT NULL,
    size TEXT DEFAULT 'tiny',
    completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    dopamine_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);
```

#### Insights Table
```sql
CREATE TABLE insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    insight_type TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);
```

### Viewing Database

**Using DB Browser for SQLite (Recommended):**
1. Download from https://sqlitebrowser.org/
2. Open `productivity_trio.db`
3. Browse tables and data
4. Run custom queries

**Using Python:**
```python
import sqlite3
conn = sqlite3.connect('productivity_trio.db')
cursor = conn.cursor()

# Example: View all projects
cursor.execute('SELECT * FROM projects')
for row in cursor.fetchall():
    print(row)

conn.close()
```

### Database Maintenance

**Vacuum (Optimize)**
```python
import sqlite3
conn = sqlite3.connect('productivity_trio.db')
conn.execute('VACUUM')
conn.close()
```

**Check Integrity**
```python
import sqlite3
conn = sqlite3.connect('productivity_trio.db')
result = conn.execute('PRAGMA integrity_check').fetchone()
print(result)  # Should be ('ok',)
conn.close()
```

---

## API Setup

### Getting Your Claude API Key

1. **Sign up at Anthropic**
   - Visit: https://console.anthropic.com
   - Create account (if needed)
   - Verify email

2. **Generate API Key**
   - Go to "API Keys" section
   - Click "Create Key"
   - Copy the key immediately (you can't see it again!)
   - Store securely

3. **Add to App**
   - Open Productivity Trio
   - Go to `File > Settings`
   - Paste API key
   - Click Save

### API Key Security

**DO:**
- Keep key private
- Never commit to version control
- Use environment variables for extra security
- Regenerate if exposed

**DON'T:**
- Share your key
- Store in plain text online
- Include in screenshots
- Email to others

### Environment Variable Method (Advanced)

Instead of storing in config file:

**Linux/macOS:**
```bash
export ANTHROPIC_API_KEY="your-key-here"
python productivity_trio.py
```

**Windows:**
```cmd
set ANTHROPIC_API_KEY=your-key-here
python productivity_trio.py
```

**Modify app to use environment variable:**
```python
import os
api_key = os.environ.get('ANTHROPIC_API_KEY', '')
```

### API Usage and Costs

**Current Pricing (as of Nov 2025):**
- Claude Sonnet 4.5: ~$3 per million input tokens
- Typical conversation: 500-2000 tokens
- Estimated monthly cost: $5-20 for moderate use

**Monitor Usage:**
- Check Anthropic Console for usage stats
- Track via dashboard
- Set up billing alerts

---

## Troubleshooting

### Common Issues

#### Issue: "Module not found: anthropic"

**Solution:**
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Issue: "API Error: Authentication failed"

**Causes:**
1. Missing API key
2. Invalid API key
3. Expired API key

**Solutions:**
1. Check `config.json` has your key
2. Verify key at console.anthropic.com
3. Generate new key if needed
4. Restart app after updating

#### Issue: "Database is locked"

**Causes:**
- Multiple instances running
- Previous crash didn't close properly

**Solutions:**
```bash
# Close all instances of the app
# Check for processes
ps aux | grep productivity_trio  # Linux/macOS
tasklist | findstr python        # Windows

# If needed, restart computer
# Reopen app
```

#### Issue: TKinter not found

**Linux:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
```bash
# Usually included, but if needed:
brew install python-tk
```

#### Issue: Slow API responses

**Possible causes:**
- Network latency
- API service issues
- Complex conversations (long context)

**Solutions:**
1. Check internet connection
2. Check Anthropic status page
3. Clear old conversations (start fresh project)
4. Reduce `max_tokens` in settings

#### Issue: Database corruption

**Prevention:**
- Regular backups
- Proper app shutdown (don't force quit)

**Recovery:**
```bash
# Try integrity check
sqlite3 productivity_trio.db "PRAGMA integrity_check;"

# If corrupt, restore from backup
cp productivity_trio.db.backup productivity_trio.db
```

---

## Backup & Recovery

### Manual Backup

**Simple method:**
```bash
# Copy database file
cp productivity_trio.db productivity_trio_backup_$(date +%Y%m%d).db
```

**Include config:**
```bash
# Create backup folder
mkdir backups

# Copy everything
cp productivity_trio.db backups/
cp config.json backups/
```

### Automated Backup Script

**Linux/macOS** (`backup.sh`):
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"

mkdir -p $BACKUP_DIR

cp productivity_trio.db "$BACKUP_DIR/db_backup_$DATE.db"
cp config.json "$BACKUP_DIR/config_backup_$DATE.json"

echo "Backup created: $DATE"

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
```

**Windows** (`backup.bat`):
```batch
@echo off
set DATE=%date:~-4,4%%date:~-7,2%%date:~-10,2%
set BACKUP_DIR=backups

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

copy productivity_trio.db "%BACKUP_DIR%\db_backup_%DATE%.db"
copy config.json "%BACKUP_DIR%\config_backup_%DATE%.json"

echo Backup created: %DATE%
```

### Cloud Backup

**Using Git (without API key):**
```bash
# Create .gitignore
echo "config.json" > .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__" >> .gitignore

# Initialize repo
git init
git add productivity_trio.db
git add *.py
git add requirements.txt
git commit -m "Backup $(date)"

# Push to private GitHub repo
git remote add origin YOUR_PRIVATE_REPO
git push
```

### Recovery

**From backup:**
```bash
# Stop app
# Replace current database
cp backups/db_backup_20251104.db productivity_trio.db

# Restart app
python productivity_trio.py
```

---

## Updating

### Update Application Code

```bash
# Backup first!
cp productivity_trio.py productivity_trio.py.backup

# Download new version
# Replace productivity_trio.py

# Update dependencies if needed
pip install -r requirements.txt --upgrade

# Test
python productivity_trio.py
```

### Update Dependencies

```bash
# Update specific package
pip install --upgrade anthropic

# Update all packages
pip install -r requirements.txt --upgrade

# Check versions
pip list
```

### Database Migrations

**If schema changes (future versions):**

```python
import sqlite3

conn = sqlite3.connect('productivity_trio.db')
cursor = conn.cursor()

# Example: Add new column
try:
    cursor.execute('ALTER TABLE projects ADD COLUMN priority INTEGER DEFAULT 0')
    conn.commit()
    print("Migration successful")
except sqlite3.OperationalError as e:
    print(f"Migration not needed or failed: {e}")

conn.close()
```

---

## Advanced Configuration

### Custom Agent Prompts

Edit `productivity_trio.py` to modify agent personalities:

```python
self.agents = {
    "spark": {
        "system_prompt": """Your custom Spark prompt here..."""
    },
    "proto": {
        "system_prompt": """Your custom Proto prompt here..."""
    }
}
```

### Performance Tuning

**Reduce API calls:**
```python
# In config.json
{
    "max_tokens": 512,  # Shorter responses
    "model": "claude-haiku-4-5",  # Faster, cheaper model
}
```

**Database performance:**
```sql
-- Add indexes for faster queries
CREATE INDEX idx_project_id ON conversations(project_id);
CREATE INDEX idx_timestamp ON conversations(timestamp);
```

### Network Configuration

**Using proxy:**
```python
# Add to app initialization
import os
os.environ['HTTPS_PROXY'] = 'http://proxy.example.com:8080'
```

---

## Security Best Practices

### 1. Protect Your API Key

```bash
# Never commit config.json
echo "config.json" >> .gitignore

# Use environment variables
export ANTHROPIC_API_KEY="key-here"
```

### 2. Database Security

```bash
# Set file permissions (Linux/macOS)
chmod 600 productivity_trio.db
chmod 600 config.json
```

### 3. Regular Backups

- Daily automated backups
- Test restores monthly
- Store offsite (cloud)

### 4. Monitor API Usage

- Check console.anthropic.com regularly
- Set up billing alerts
- Review usage patterns

### 5. Update Regularly

```bash
# Keep Python updated
python --version

# Keep packages updated
pip list --outdated
pip install --upgrade anthropic
```

---

## Deployment Scenarios

### Single User (Desktop)

```
productivity-trio/
├── productivity_trio.py
├── requirements.txt
├── config.json (gitignored)
├── productivity_trio.db
└── venv/
```

### Multiple Users (Separate Databases)

Each user runs their own instance with their own database and config.

### Shared Development

```bash
# Use separate config per developer
config.local.json  # Developer 1 (gitignored)
config.dev2.json   # Developer 2 (gitignored)
config.example.json # Template (committed)

# Modify app to load specific config
python productivity_trio.py --config config.local.json
```

---

## Monitoring & Logs

### Enable Logging

Add to beginning of `productivity_trio.py`:

```python
import logging

logging.basicConfig(
    filename='productivity_trio.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### View Logs

```bash
# Real-time monitoring
tail -f productivity_trio.log

# Search errors
grep ERROR productivity_trio.log
```

---

## Platform-Specific Notes

### Windows

**Executable creation (optional):**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed productivity_trio.py
```

**Startup shortcut:**
1. Create `.bat` file:
```batch
@echo off
cd C:\path\to\productivity-trio
call venv\Scripts\activate
python productivity_trio.py
```
2. Pin to Start Menu

### macOS

**Create app bundle (optional):**
```bash
pip install py2app
# Follow py2app documentation
```

**Launch at login:**
1. System Preferences > Users & Groups
2. Login Items
3. Add Python script

### Linux

**Desktop entry:**
Create `~/.local/share/applications/productivity-trio.desktop`:
```ini
[Desktop Entry]
Name=ADHD Productivity Trio
Exec=/path/to/venv/bin/python /path/to/productivity_trio.py
Terminal=false
Type=Application
Icon=/path/to/icon.png
Categories=Utility;
```

---

## FAQ

### Can I use this without internet?

No. The app requires Claude API access which needs internet.

### Can I use a different AI model?

The app is designed for Claude. Porting to other APIs would require code changes.

### How much does API usage cost?

Typically $5-20/month for moderate use. Check Anthropic's pricing.

### Can multiple people use the same API key?

Technically yes, but each person should have their own key for:
- Security
- Usage tracking
- Billing clarity

### What happens if Anthropic is down?

The app will show errors. Your data is safe locally. Wait for service restoration.

### Can I export my conversations?

Yes! Access `productivity_trio.db` with any SQLite tool and export as needed.

---

## Support Resources

- **Anthropic Documentation**: https://docs.anthropic.com
- **Claude API Status**: https://status.anthropic.com
- **Python Documentation**: https://docs.python.org
- **SQLite Documentation**: https://sqlite.org/docs.html

---

## Version History

**v1.0.0** (November 2025)
- Initial release
- Two agent system
- SQLite database
- TKinter UI
- Claude Sonnet 4.5 integration

---

**Remember**: The best DevOps is the one that lets you focus on building, not maintaining. Keep it simple, automate backups, and don't over-engineer.

**Now go build something amazing!** 🚀

---

*Version 1.0 - November 4, 2025*
