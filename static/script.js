let currentAccount = null;
let currentTask = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    fetch('/api/settings/init')
        .then(response => response.json())
        .then(data => {
            if (data.first_time) {
                document.getElementById('init-modal').style.display = 'flex';
            } else {
                showMainApp();
            }
        });
}

// Init Form
document.getElementById('init-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const apiId = document.getElementById('api-id').value;
    const apiHash = document.getElementById('api-hash').value;
    const autoStart = document.getElementById('auto-start').checked;
    
    fetch('/api/settings/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_id: apiId, api_hash: apiHash, auto_start: autoStart })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('init-modal').style.display = 'none';
        showMainApp();
    });
});

function showMainApp() {
    document.getElementById('init-modal').style.display = 'none';
    document.getElementById('main-app').style.display = 'flex';
    loadDashboard();
    loadAccounts();
}

function showTab(tabName, event) {
    event.preventDefault();
    
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Load tab-specific data
    if (tabName === 'dashboard') loadDashboard();
    if (tabName === 'accounts') loadAccounts();
    if (tabName === 'tasks') loadTasks();
    if (tabName === 'logs') loadLogs();
}

// Dashboard
function loadDashboard() {
    fetch('/api/accounts')
        .then(response => response.json())
        .then(accounts => {
            document.getElementById('active-accounts').textContent = accounts.filter(a => a.is_active).length;
        });
    
    fetch('/api/tasks')
        .then(response => response.json())
        .then(tasks => {
            document.getElementById('running-tasks').textContent = tasks.filter(t => t.is_active).length;
        });
    
    loadLogs();
}

// Accounts
function loadAccounts() {
    fetch('/api/accounts')
        .then(response => response.json())
        .then(accounts => {
            const list = document.getElementById('accounts-list');
            list.innerHTML = '';
            
            accounts.forEach(account => {
                const item = document.createElement('div');
                item.className = 'list-item';
                item.innerHTML = `
                    <div class="list-item-header">
                        <div class="list-item-title">📱 ${account.phone}</div>
                        <span class="list-item-status ${account.is_active ? 'status-active' : 'status-inactive'}">
                            ${account.is_active ? 'ACTIVE' : 'INACTIVE'}
                        </span>
                    </div>
                    <div class="list-item-details">Added: ${new Date(account.created_at).toLocaleDateString()}</div>
                    <div class="list-item-actions">
                        <button class="btn btn-primary" onclick="selectAccount(${account.id}, '${account.phone}')">Select</button>
                        <button class="btn btn-danger">Remove</button>
                    </div>
                `;
                list.appendChild(item);
            });
            
            // Update task account select
            const select = document.getElementById('task-account');
            if (select) {
                select.innerHTML = '<option value="">Select Account</option>';
                accounts.forEach(account => {
                    const option = document.createElement('option');
                    option.value = account.id;
                    option.textContent = account.phone;
                    select.appendChild(option);
                });
            }
        });
}

function selectAccount(accountId, phone) {
    currentAccount = { id: accountId, phone };
    loadAccountGroups(accountId);
}

function loadAccountGroups(accountId) {
    fetch(`/api/accounts/${accountId}/groups`)
        .then(response => response.json())
        .then(groups => {
            document.getElementById('total-groups').textContent = groups.length;
        });
}

function showAddAccountForm() {
    document.getElementById('add-account-form').style.display = 'block';
}

function hideAddAccountForm() {
    document.getElementById('add-account-form').style.display = 'none';
    document.getElementById('account-form').reset();
}

document.getElementById('account-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const phone = document.getElementById('phone').value;
    const apiId = document.getElementById('acc-api-id').value;
    const apiHash = document.getElementById('acc-api-hash').value;
    
    fetch('/api/accounts/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, api_id: apiId, api_hash: apiHash })
    })
    .then(response => response.json())
    .then(data => {
        hideAddAccountForm();
        loadAccounts();
        alert('Account added successfully!');
    })
    .catch(error => alert('Error: ' + error));
});

// Tasks
function loadTasks() {
    fetch('/api/tasks')
        .then(response => response.json())
        .then(tasks => {
            const list = document.getElementById('tasks-list');
            list.innerHTML = '';
            
            tasks.forEach(task => {
                const item = document.createElement('div');
                item.className = 'list-item';
                item.innerHTML = `
                    <div class="list-item-header">
                        <div class="list-item-title">📨 ${task.message.substring(0, 50)}...</div>
                        <span class="list-item-status ${task.is_active ? 'status-active' : 'status-inactive'}">
                            ${task.is_active ? 'ACTIVE' : 'INACTIVE'}
                        </span>
                    </div>
                    <div class="list-item-details">Delay: ${task.delay_seconds}s | Auto Repeat: ${task.auto_repeat ? 'Yes' : 'No'}</div>
                    <div class="list-item-actions">
                        <button class="btn btn-primary">Edit</button>
                        <button class="btn btn-danger">Delete</button>
                    </div>
                `;
                list.appendChild(item);
            });
        });
}

function showAddTaskForm() {
    document.getElementById('add-task-form').style.display = 'block';
}

function hideAddTaskForm() {
    document.getElementById('add-task-form').style.display = 'none';
    document.getElementById('task-form').reset();
}

// Update delay display
document.getElementById('task-delay')?.addEventListener('input', function() {
    document.getElementById('delay-value').textContent = this.value;
});

// Show/hide repeat interval
document.getElementById('task-auto-repeat')?.addEventListener('change', function() {
    document.getElementById('repeat-interval-group').style.display = this.checked ? 'block' : 'none';
});

document.getElementById('task-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const accountId = document.getElementById('task-account').value;
    const groupId = document.getElementById('task-group').value;
    const message = document.getElementById('task-message').value;
    const delay = parseInt(document.getElementById('task-delay').value);
    const autoRepeat = document.getElementById('task-auto-repeat').checked ? 1 : 0;
    const repeatInterval = parseInt(document.getElementById('task-repeat-interval').value) || 60;
    
    fetch('/api/tasks/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            account_id: accountId,
            group_id: groupId,
            message,
            delay_seconds: delay,
            auto_repeat: autoRepeat,
            repeat_interval: repeatInterval
        })
    })
    .then(response => response.json())
    .then(data => {
        hideAddTaskForm();
        loadTasks();
        alert('Task created successfully!');
    })
    .catch(error => alert('Error: ' + error));
});

// Logs
function loadLogs() {
    fetch('/api/logs?limit=50')
        .then(response => response.json())
        .then(logs => {
            const container = document.getElementById('logs-container') || document.getElementById('recent-logs');
            if (!container) return;
            
            container.innerHTML = '';
            logs.slice(0, 10).forEach(log => {
                const item = document.createElement('div');
                item.className = 'list-item';
                const statusClass = log.status === 'success' ? 'status-success' : 'status-error';
                item.innerHTML = `
                    <div class="list-item-header">
                        <div class="list-item-title">${log.message}</div>
                        <span class="list-item-status ${statusClass}">${log.status.toUpperCase()}</span>
                    </div>
                    <div class="list-item-details">${new Date(log.timestamp).toLocaleString()}</div>
                    ${log.error_msg ? `<div class="list-item-details" style="color: var(--danger);">Error: ${log.error_msg}</div>` : ''}
                `;
                container.appendChild(item);
            });
        });
}

function refreshLogs() {
    loadLogs();
}

// Start Service
document.getElementById('start-btn')?.addEventListener('click', function() {
    fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auto_start: true })
    })
    .then(response => response.json())
    .then(data => {
        alert('Service Started!');
        this.style.background = '#00cc00';
        this.textContent = '✓ RUNNING';
    });
});
