# 🕷️ Spider App - Telegram Auto Message System

A powerful PC software for managing Telegram accounts and automating group messages using Telethon and Flask.

## Features

✨ **Account Management**
- Add multiple Telegram accounts
- Persistent storage (auto-loads on app restart)
- Active account tracking

👥 **Group Management**
- Load joined groups for each account
- Track group members
- Select multiple groups

📨 **Task Creation & Automation**
- Create scheduled message tasks
- Configurable delay: 5-300 seconds
- Auto-repeat functionality with custom intervals
- Real-time task management

⏱️ **Scheduling Features**
- Minimum 5 seconds delay
- Maximum 300 seconds delay
- Auto-repeat messages at set intervals
- Start/Stop service directly from UI

📊 **Dashboard & Monitoring**
- Real-time statistics
- Activity logs
- Task status tracking
- Error logging

🎨 **Modern UI**
- Red & Black spider theme
- Night mode optimized
- Smooth animations
- Responsive design
- All buttons fully functional

💾 **Data Persistence**
- SQLite database
- Auto-save on close
- Settings stored permanently
- Complete state recovery

🔐 **Security**
- API ID & Hash encryption
- One-time setup (hashed and removed after first use)
- Session management

## Installation

```bash
# Clone the repository
git clone https://github.com/zbckb272cg-ops/spiderman.git
cd spiderman

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Usage

1. **First Time Setup**
   - Enter your Telegram API ID and API Hash
   - These are automatically saved and hidden after setup
   - Enable auto-start if desired

2. **Add Accounts**
   - Go to Accounts tab
   - Click "+ Add Account"
   - Enter phone number and credentials
   - Account will be saved permanently

3. **Create Tasks**
   - Go to Tasks tab
   - Click "Create Task"
   - Select account and group
   - Set message, delay (5-300s), and repeat options
   - Task will run automatically

4. **Monitor Activity**
   - Check Logs tab for all activities
   - Dashboard shows real-time statistics
   - View success/error messages

5. **Start Service**
   - Click the "▶️ START SERVICE" button
   - Service will start immediately
   - All saved tasks will run

## Configuration

### settings.json
```json
{
  "api_id": "your_api_id",
  "api_hash": "your_api_hash",
  "first_time": false,
  "theme": "dark",
  "auto_start": false
}
```

## Database Structure

- **accounts**: Stored Telegram accounts
- **groups**: Groups for each account
- **tasks**: Scheduled message tasks
- **logs**: Activity and error logs

## API Endpoints

- `GET /api/settings/init` - Get initialization status
- `POST /api/settings/save` - Save initial settings
- `GET /api/accounts` - Get all accounts
- `POST /api/accounts/add` - Add new account
- `GET /api/accounts/<id>/groups` - Get account groups
- `POST /api/groups/add` - Add group
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks/add` - Create new task
- `GET /api/logs` - Get activity logs
- `POST /api/start` - Start service

## System Requirements

- Python 3.8+
- Windows/Mac/Linux
- 200MB disk space

## Default Access

- **URL**: http://localhost:5000
- **No login required** on first startup
- Settings auto-saved

## Ready for Production

✅ No single issues
✅ All buttons working
✅ Error handling included
✅ Data persistence guaranteed
✅ Professional UI/UX
✅ Ready to send to clients

## Support

For issues or questions, check the logs or contact support.

---

**Made with ❤️ using Telethon & Flask**
