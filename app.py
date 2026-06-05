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

load_dotenv()

app = Flask(__name__)
app.secret_key = 'spider_app_secret_key_2024'
CORS(app)

# Database setup
DATABASE = 'spider_data.db'
SETTINGS_FILE = 'settings.json'
LOGS_FILE = 'logs.json'

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
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            account_id INTEGER,
            group_id TEXT,
            message TEXT,
            delay_seconds INTEGER,
            auto_repeat INTEGER DEFAULT 0,
            repeat_interval INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP,
            FOREIGN KEY(account_id) REFERENCES accounts(id)
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
        'first_time': True,
        'theme': 'dark',
        'auto_start': False
    }

def save_settings(settings):
    settings['first_time'] = False
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def hash_string(text):
    return hashlib.sha256(text.encode()).hexdigest()

def add_log(account_id, group_id, message, status, error_msg=''):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO logs (timestamp, account_id, group_id, message, status, error_msg)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), account_id, group_id, message, status, error_msg))
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/settings/init', methods=['GET'])
def get_init_settings():
    settings = load_settings()
    return jsonify({
        'first_time': settings.get('first_time', True),
        'theme': settings.get('theme', 'dark')
    })

@app.route('/api/settings/save', methods=['POST'])
def save_init_settings():
    data = request.json
    settings = {
        'api_id': data.get('api_id'),
        'api_hash': data.get('api_hash'),
        'first_time': False,
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
    accounts = [{
        'id': row[0],
        'phone': row[1],
        'is_active': row[2],
        'created_at': row[3]
    } for row in c.fetchall()]
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
        session_name = f"session_{phone}_{int(time.time())}"
        c.execute('''
            INSERT INTO accounts (phone, api_id, api_hash, session_name, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (phone, api_id, api_hash, session_name, datetime.now().isoformat()))
        conn.commit()
        account_id = c.lastrowid
        conn.close()
        add_log(account_id, 'system', f'Account {phone} added', 'success')
        return jsonify({'status': 'success', 'account_id': account_id})
    except Exception as e:
        add_log(0, 'system', f'Add account error: {str(e)}', 'error', str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/accounts/<int:account_id>/groups', methods=['GET'])
def get_account_groups(account_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, group_id, group_name, members_count FROM groups WHERE account_id = ?', (account_id,))
    groups = [{
        'id': row[0],
        'group_id': row[1],
        'group_name': row[2],
        'members_count': row[3]
    } for row in c.fetchall()]
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

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, account_id, group_id, message, delay_seconds, auto_repeat, is_active FROM tasks')
    tasks = [{
        'id': row[0],
        'account_id': row[1],
        'group_id': row[2],
        'message': row[3],
        'delay_seconds': row[4],
        'auto_repeat': row[5],
        'is_active': row[6]
    } for row in c.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route('/api/tasks/add', methods=['POST'])
def add_task():
    data = request.json
    account_id = data.get('account_id')
    group_id = data.get('group_id')
    message = data.get('message')
    delay_seconds = data.get('delay_seconds', 5)
    auto_repeat = data.get('auto_repeat', 0)
    repeat_interval = data.get('repeat_interval', 60)
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO tasks (account_id, group_id, message, delay_seconds, auto_repeat, repeat_interval, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (account_id, group_id, message, delay_seconds, auto_repeat, repeat_interval, datetime.now().isoformat()))
        conn.commit()
        task_id = c.lastrowid
        conn.close()
        add_log(account_id, group_id, f'Task created: {message[:50]}', 'success')
        return jsonify({'status': 'success', 'task_id': task_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/logs', methods=['GET'])
def get_logs():
    limit = request.args.get('limit', 100, type=int)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT timestamp, account_id, group_id, message, status, error_msg FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
    logs = [{
        'timestamp': row[0],
        'account_id': row[1],
        'group_id': row[2],
        'message': row[3],
        'status': row[4],
        'error_msg': row[5]
    } for row in c.fetchall()]
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='localhost', port=5000)
