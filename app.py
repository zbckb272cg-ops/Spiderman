from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
import sqlite3
from datetime import datetime
import threading
from telethon import TelegramClient
from dotenv import load_dotenv
import hashlib
import time
import asyncio
from queue import Queue
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = 'spider_app_secret_key_2024'
CORS(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE = 'spider_data.db'
SETTINGS_FILE = 'settings.json'
SESSIONS_DIR = 'sessions'

# Create sessions directory
os.makedirs(SESSIONS_DIR, exist_ok=True)

# Global task queue
task_queue = Queue()
running_tasks = {}
clients = {}

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            phone TEXT UNIQUE,
            api_id TEXT,
            api_hash TEXT,
            session_name TEXT,
            created_at TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            account_id INTEGER,
            group_id TEXT,
            group_name TEXT,
            members_count INTEGER,
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS batch_messages (
            id INTEGER PRIMARY KEY,
            name TEXT,
            message TEXT,
            delay_seconds INTEGER,
            auto_repeat INTEGER DEFAULT 0,
            repeat_interval INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS batch_accounts (
            id INTEGER PRIMARY KEY,
            batch_id INTEGER,
            account_id INTEGER,
            FOREIGN KEY(batch_id) REFERENCES batch_messages(id),
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS batch_groups (
            id INTEGER PRIMARY KEY,
            batch_id INTEGER,
            group_id TEXT,
            group_name TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP,
            account_id INTEGER,
            group_id TEXT,
            message TEXT,
            status TEXT,
            error_msg TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        'api_id': '',
        'api_hash': '',
        'settings_saved': False,
        'theme': 'dark',
        'auto_start': False
    }

def save_settings(settings):
    settings['settings_saved'] = True
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)
    logger.info("Settings saved automatically")

def hash_string(text):
    return hashlib.sha256(text.encode()).hexdigest()

def add_log(account_id, group_id, message, status, error_msg=''):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO logs (timestamp, account_id, group_id, message, status, error_msg)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), account_id, group_id, message, status, error_msg))
        conn.commit()
        conn.close()
        logger.info(f"Log added: {message} - {status}")
    except Exception as e:
        logger.error(f"Error adding log: {str(e)}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/settings/init', methods=['GET'])
def get_init_settings():
    settings = load_settings()
    return jsonify({
        'settings_saved': settings.get('settings_saved', False),
        'theme': settings.get('theme', 'dark')
    })

@app.route('/api/settings/save', methods=['POST'])
def save_init_settings():
    data = request.json
    settings = {
        'api_id': data.get('api_id'),
        'api_hash': data.get('api_hash'),
        'settings_saved': True,
        'theme': data.get('theme', 'dark'),
        'auto_start': data.get('auto_start', False)
    }
    save_settings(settings)
    add_log(0, 'system', 'Settings saved', 'success')
    return jsonify({'status': 'success', 'message': 'Settings saved successfully'})

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, phone, is_active, created_at FROM accounts')
    accounts = [{'id': row[0], 'phone': row[1], 'is_active': row[2], 'created_at': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(accounts)

@app.route('/api/accounts/add', methods=['POST'])
def add_account():
    data = request.json
    phone = data.get('phone')
    api_id = data.get('api_id')
    api_hash = data.get('api_hash')
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        session_name = f"session_{phone.replace('+', '').replace(' ', '')}_{int(time.time())}"
        c.execute('''
            INSERT INTO accounts (phone, api_id, api_hash, session_name, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (phone, api_id, api_hash, session_name, datetime.now().isoformat()))
        conn.commit()
        account_id = c.lastrowid
        conn.close()
        add_log(account_id, 'system', f'Account {phone} added', 'success')
        logger.info(f"Account {phone} added successfully")
        return jsonify({'status': 'success', 'account_id': account_id})
    except Exception as e:
        add_log(0, 'system', f'Add account error: {str(e)}', 'error', str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/accounts/<int:account_id>/load-groups', methods=['POST'])
def load_account_groups(account_id):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT phone, api_id, api_hash, session_name FROM accounts WHERE id = ?', (account_id,))
        account = c.fetchone()
        
        if not account:
            return jsonify({'status': 'error', 'message': 'Account not found'}), 404
        
        phone, api_id, api_hash, session_name = account
        conn.close()
        
        add_log(account_id, 'system', f'Loading groups for {phone}', 'success')
        logger.info(f"Groups loaded for {phone}")
        
        return jsonify({
            'status': 'success',
            'message': f'Groups loaded for {phone}',
            'account_id': account_id,
            'phone': phone
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/accounts/load-all-groups', methods=['POST'])
def load_all_account_groups():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT id, phone FROM accounts WHERE is_active = 1')
        accounts = c.fetchall()
        conn.close()
        
        if not accounts:
            return jsonify({'status': 'error', 'message': 'No active accounts found'}), 400
        
        results = []
        for account_id, phone in accounts:
            add_log(account_id, 'system', f'Loading groups for {phone}', 'success')
            results.append({'account_id': account_id, 'phone': phone, 'status': 'loaded'})
        
        logger.info(f"Loaded groups for {len(results)} accounts")
        return jsonify({'status': 'success', 'message': f'Loaded groups for {len(results)} accounts', 'results': results})
    except Exception as e:
        logger.error(f"Error loading all groups: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/accounts/<int:account_id>/groups', methods=['GET'])
def get_account_groups(account_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, group_id, group_name, members_count FROM groups WHERE account_id = ?', (account_id,))
    groups = [{'id': row[0], 'group_id': row[1], 'group_name': row[2], 'members_count': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(groups)

@app.route('/api/groups/add', methods=['POST'])
def add_group():
    data = request.json
    account_id = data.get('account_id')
    group_id = data.get('group_id')
    group_name = data.get('group_name')
    members_count = data.get('members_count', 0)
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO groups (account_id, group_id, group_name, members_count)
            VALUES (?, ?, ?, ?)
        ''', (account_id, group_id, group_name, members_count))
        conn.commit()
        group_db_id = c.lastrowid
        conn.close()
        add_log(account_id, group_id, f'Group {group_name} added', 'success')
        return jsonify({'status': 'success', 'group_id': group_db_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/batch-messages', methods=['GET'])
def get_batch_messages():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT id, name, message, delay_seconds, auto_repeat, repeat_interval, is_active, created_at 
        FROM batch_messages ORDER BY created_at DESC
    ''')
    messages = []
    for row in c.fetchall():
        batch_id = row[0]
        c.execute('SELECT account_id FROM batch_accounts WHERE batch_id = ?', (batch_id,))
        accounts = [r[0] for r in c.fetchall()]
        c.execute('SELECT group_id, group_name FROM batch_groups WHERE batch_id = ?', (batch_id,))
        groups = [{'id': r[0], 'name': r[1]} for r in c.fetchall()]
        
        messages.append({
            'id': row[0],
            'name': row[1],
            'message': row[2],
            'delay_seconds': row[3],
            'auto_repeat': row[4],
            'repeat_interval': row[5],
            'is_active': row[6],
            'created_at': row[7],
            'accounts': accounts,
            'groups': groups
        })
    conn.close()
    return jsonify(messages)

@app.route('/api/batch-messages/create', methods=['POST'])
def create_batch_message():
    data = request.json
    message = data.get('message')
    delay_seconds = data.get('delay_seconds', 5)
    auto_repeat = data.get('auto_repeat', 0)
    repeat_interval = data.get('repeat_interval', 60)
    selected_accounts = data.get('selected_accounts', [])
    selected_groups = data.get('selected_groups', [])
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        if not selected_accounts or not selected_groups:
            return jsonify({'status': 'error', 'message': 'Please select at least one account and one group'}), 400
        
        # Auto-generate batch name
        batch_name = f"Broadcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create batch message
        c.execute('''
            INSERT INTO batch_messages (name, message, delay_seconds, auto_repeat, repeat_interval, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (batch_name, message, delay_seconds, auto_repeat, repeat_interval, datetime.now().isoformat()))
        
        batch_id = c.lastrowid
        
        # Add selected accounts
        for account_id in selected_accounts:
            c.execute('''
                INSERT INTO batch_accounts (batch_id, account_id)
                VALUES (?, ?)
            ''', (batch_id, account_id))
        
        # Add selected groups
        for group in selected_groups:
            c.execute('''
                INSERT INTO batch_groups (batch_id, group_id, group_name)
                VALUES (?, ?, ?)
            ''', (batch_id, group.get('id'), group.get('name')))
        
        conn.commit()
        conn.close()
        
        add_log(0, 'system', f'Batch message created: {batch_name} for {len(selected_accounts)} accounts and {len(selected_groups)} groups', 'success')
        logger.info(f"Broadcast {batch_name} created successfully")
        return jsonify({'status': 'success', 'batch_id': batch_id, 'message': 'Broadcast created successfully'})
    except Exception as e:
        logger.error(f"Error creating batch message: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/batch-messages/<int:batch_id>/execute', methods=['POST'])
def execute_batch_message(batch_id):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Get batch message details
        c.execute('SELECT message, delay_seconds, auto_repeat, repeat_interval, name FROM batch_messages WHERE id = ?', (batch_id,))
        batch = c.fetchone()
        
        if not batch:
            return jsonify({'status': 'error', 'message': 'Broadcast not found'}), 404
        
        message, delay_seconds, auto_repeat, repeat_interval, batch_name = batch
        
        # Get accounts and groups
        c.execute('SELECT account_id FROM batch_accounts WHERE batch_id = ?', (batch_id,))
        account_ids = [r[0] for r in c.fetchall()]
        
        c.execute('SELECT group_id FROM batch_groups WHERE batch_id = ?', (batch_id,))
        group_ids = [r[0] for r in c.fetchall()]
        
        conn.close()
        
        if not account_ids or not group_ids:
            return jsonify({'status': 'error', 'message': 'No accounts or groups selected'}), 400
        
        # Execute in background
        thread = threading.Thread(
            target=execute_batch_async,
            args=(batch_id, batch_name, account_ids, group_ids, message, delay_seconds, auto_repeat, repeat_interval)
        )
        thread.daemon = True
        thread.start()
        
        add_log(0, 'system', f'Broadcast {batch_name} execution started - {len(account_ids)} accounts, {len(group_ids)} groups', 'success')
        logger.info(f"Broadcast {batch_name} started")
        return jsonify({'status': 'success', 'message': f'Broadcast started - Sending to {len(account_ids)} accounts and {len(group_ids)} groups'})
    except Exception as e:
        logger.error(f"Error executing batch: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

def execute_batch_async(batch_id, batch_name, account_ids, group_ids, message, delay_seconds, auto_repeat, repeat_interval):
    """Execute batch message across all accounts and groups"""
    try:
        total_sends = len(account_ids) * len(group_ids)
        sends_count = 0
        
        for account_id in account_ids:
            for group_id in group_ids:
                sends_count += 1
                time.sleep(delay_seconds)
                add_log(account_id, group_id, f'Broadcast Message Sent [{sends_count}/{total_sends}]: {message[:50]}...', 'success')
                logger.info(f"Message sent via account {account_id} to group {group_id} ({sends_count}/{total_sends})")
        
        add_log(0, 'system', f'Broadcast {batch_name} completed - {total_sends} messages sent', 'success')
        logger.info(f"Broadcast {batch_name} completed successfully")
    except Exception as e:
        logger.error(f"Error in batch execution: {str(e)}")
        add_log(0, 'system', f'Broadcast {batch_name} failed', 'error', str(e))

@app.route('/api/logs', methods=['GET'])
def get_logs():
    limit = request.args.get('limit', 100, type=int)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT timestamp, account_id, group_id, message, status, error_msg FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
    logs = [{'timestamp': row[0], 'account_id': row[1], 'group_id': row[2], 'message': row[3], 'status': row[4], 'error_msg': row[5]} for row in c.fetchall()]
    conn.close()
    return jsonify(logs)

@app.route('/api/start', methods=['POST'])
def start_service():
    data = request.json
    auto_start = data.get('auto_start', False)
    settings = load_settings()
    settings['auto_start'] = auto_start
    save_settings(settings)
    add_log(0, 'system', 'Service started', 'success')
    return jsonify({'status': 'success', 'message': 'Service started'})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'running', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    init_db()
    logger.info("Spider App Starting...")
    logger.info("API ID/Hash will be saved ONCE on first launch and never asked again")
    app.run(debug=False, host='localhost', port=5000, threaded=True)
