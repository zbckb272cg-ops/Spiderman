# 🕷️ Spider App - Telegram Auto Message System

A professional PC software for managing multiple Telegram accounts and broadcasting messages to groups automatically using Telethon and Flask.

## ✨ Features

### 🎯 **Core Functionality**
- ✅ **Multiple Account Management** - Add and manage unlimited Telegram accounts
- ✅ **Group Loading** - Load groups one-by-one or all at once
- ✅ **Batch Broadcasting** - Send messages to all accounts in all selected groups simultaneously
- ✅ **Flexible Scheduling** - Delay: 5-300 seconds between messages
- ✅ **Auto Repeat** - Automatically repeat messages at custom intervals
- ✅ **Select All/Deselect All** - Quick selection for accounts and groups
- ✅ **Activity Logging** - Real-time logging with auto-refresh
- ✅ **Persistent Storage** - All data automatically saved and restored

### 🎨 **User Interface**
- Red & Black Spider theme with night mode optimization
- Smooth animations and transitions
- Fully responsive design
- 5 main tabs: Dashboard | Accounts | Broadcast | Logs | Settings
- All buttons fully functional and tested
- Real-time dashboard with statistics

### 🔒 **Security & Data**
- First-time API setup wizard
- Settings automatically saved and encrypted
- SQLite database for persistence
- Session management
- Complete error handling

## 📦 Installation

### Option 1: Quick Start (Recommended)
```bash
# Clone the repository
git clone https://github.com/zbckb272cg-ops/spiderman.git
cd spiderman

# Run the startup script (ONE CLICK!)
python start.py
```

### Option 2: Manual Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
```

Then open your browser and visit: **http://localhost:5000**

## 🚀 How to Use

### 1. **Initial Setup**
- Launch the app for the first time
- Enter your Telegram API ID and API Hash
- Settings are automatically saved and hidden

### 2. **Add Accounts**
- Go to **Accounts** tab
- Click **"+ Add Account"**
- Enter phone number and API credentials
- Account is saved automatically

### 3. **Load Groups**
- **Option A:** Load groups for single account
  - Click the **"📥 Load Groups"** button next to the account
  - Groups are loaded from Telegram
  
- **Option B:** Load groups for all accounts
  - Click **"⬇️ Load All Groups"** button
  - All groups from all accounts are loaded

### 4. **Create & Execute Broadcast**
- Go to **Broadcast** tab
- Click **"+ Create Broadcast"**
- **Select Accounts:**
  - Check accounts to include
  - Use **"✓ Select All"** / **"✗ Deselect All"** buttons
- **Select Groups:**
  - Check groups to target
  - Use **"✓ Select All"** / **"✗ Deselect All"** buttons
- **Configure Message:**
  - Enter message text
  - Set delay (5-300 seconds)
  - Enable auto-repeat if needed
- **Execute:**
  - Click **"Create & Schedule"** to save
  - Click **"▶️ Execute Now"** to send immediately

### 5. **Monitor & Logs**
- Go to **Logs** tab to see all activity
- Dashboard shows real-time statistics
- Auto-refresh every 5 seconds

## 🔧 Configuration

### API Setup
The app uses Telegram's Telethon library. You need:
1. **API ID** - Get from https://my.telegram.org/apps
2. **API Hash** - Get from https://my.telegram.org/apps

These are entered during first-time setup and saved securely.

### Database
- **File:** `spider_data.db` (SQLite)
- **Backup:** Automatically created with each save
- **Reset:** Delete the file to start fresh

### Settings
- **File:** `settings.json`
- **Theme:** Dark (default) or Light
- **Auto-start:** Optional service auto-start

## 📊 Dashboard

The dashboard displays:
- **Active Accounts** - Number of active Telegram accounts
- **Total Groups** - Total groups across all accounts
- **Batch Messages** - Number of saved broadcasts
- **Total Logs** - Activity log entries
- **Recent Activity** - Latest operations

## 📋 System Requirements

- **OS:** Windows, Mac, or Linux
- **Python:** 3.8 or higher
- **Memory:** 512MB minimum
- **Disk:** 200MB for application and database
- **Internet:** Required (Telegram API calls)

## 📝 Database Structure

### Tables
- `accounts` - Stored Telegram accounts and sessions
- `groups` - Groups associated with each account
- `batch_messages` - Saved broadcast configurations
- `batch_accounts` - Account selections for broadcasts
- `batch_groups` - Group selections for broadcasts
- `logs` - Activity and operation logs

## 🔌 API Endpoints

- `GET /` - Main application page
- `GET /api/settings/init` - Get initialization status
- `POST /api/settings/save` - Save settings
- `GET /api/accounts` - List all accounts
- `POST /api/accounts/add` - Add new account
- `POST /api/accounts/load-all-groups` - Load groups for all accounts
- `GET /api/accounts/<id>/load-groups` - Load groups for specific account
- `GET /api/batch-messages` - List all broadcasts
- `POST /api/batch-messages/create` - Create new broadcast
- `POST /api/batch-messages/<id>/execute` - Execute broadcast
- `GET /api/logs` - Get activity logs

## 🎓 Tips & Tricks

### Performance
- Keep delays at 10+ seconds to avoid rate limiting
- Load groups before creating broadcasts
- Check logs for success/error status

### Broadcasting
- Test with one group first
- Use delays to prevent account bans
- Enable auto-repeat for recurring messages
- Monitor logs during execution

### Maintenance
- Regularly check logs for errors
- Clear old logs periodically
- Backup `spider_data.db` regularly
- Keep settings.json safe

## ❌ Troubleshooting

### App won't start
- Ensure Python 3.8+ is installed
- Check that port 5000 is not in use
- Verify all files are in the correct directory

### Can't load groups
- Verify API ID and Hash are correct
- Check internet connection
- Ensure account is added properly
- Check logs for error messages

### Broadcasts not sending
- Verify groups are loaded
- Check account selection
- Review logs for failures
- Ensure proper delays set

### Performance issues
- Clear old logs
- Reduce number of concurrent broadcasts
- Increase delays between messages
- Check system resources

## 📞 Support

For issues or questions:
1. Check the logs for detailed error information
2. Verify all settings are correct
3. Ensure internet connection is stable
4. Restart the application

## ⚖️ Legal Notice

This software is for educational purposes. Users are responsible for:
- Complying with Telegram's Terms of Service
- Not using for spam or harassment
- Obtaining proper consent from recipients
- Following applicable laws and regulations

## 📄 License

This project is provided as-is for educational use.

## 🙏 Credits

Built with:
- **Telethon** - Telegram client library
- **Flask** - Web framework
- **SQLite** - Database

---

**🕷️ Spider App v1.0** - Ready for Production ✅

*No issues | All buttons working | Professional UI | Complete functionality*
