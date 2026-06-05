let currentAccount = null;
let selectedAccounts = [];
let selectedGroups = [];

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
        })
        .catch(error => console.error('Error initializing app:', error));
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
    })
    .catch(error => {
        alert('Error saving settings: ' + error);
        console.error(error);
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
    if (tabName === 'broadcast') loadBroadcasts();
    if (tabName === 'logs') loadLogs();
}

// Dashboard
function loadDashboard() {
    fetch('/api/accounts')
        .then(response => response.json())
        .then(accounts => {
            document.getElementById('active-accounts').textContent = accounts.filter(a => a.is_active).length;
            document.getElementById('total-groups').textContent = 0;
        });
    
    fetch('/api/batch-messages')
        .then(response => response.json())
        .then(messages => {
            document.getElementById('batch-count').textContent = messages.length;
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
            
            if (accounts.length === 0) {
                list.innerHTML = '<p style="text-align: center; color: var(--text-gray);">No accounts added yet</p>';
            }
            
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
                        <button class="btn btn-primary btn-sm" onclick="loadGroupsForAccount(${account.id})">📥 Load Groups</button>
                        <button class="btn btn-warning btn-sm" onclick="selectAccountForBroadcast(${account.id}, '${account.phone}')">Select</button>
                        <button class="btn btn-danger btn-sm" onclick="removeAccount(${account.id})">Remove</button>
                    </div>
                `;
                list.appendChild(item);
            });
            
            loadBroadcastAccountsList(accounts);
        })
        .catch(error => {
            console.error('Error loading accounts:', error);
            alert('Error loading accounts');
        });
}

function loadGroupsForAccount(accountId) {
    fetch(`/api/accounts/${accountId}/load-groups`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`✓ Groups loaded for ${data.phone}`);
            loadAccounts();
        }
    })
    .catch(error => {
        alert('Error loading groups: ' + error);
        console.error(error);
    });
}

function loadAllAccountsGroups() {
    fetch('/api/accounts/load-all-groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`✓ ${data.message}`);
            loadAccounts();
        }
    })
    .catch(error => {
        alert('Error loading groups: ' + error);
        console.error(error);
    });
}

function selectAccountForBroadcast(accountId, phone) {
    currentAccount = { id: accountId, phone };
    alert(`Selected account: ${phone}`);
}

function removeAccount(accountId) {
    if (confirm('Are you sure you want to remove this account?')) {
        alert('Account removal functionality coming soon');
    }
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
        if (data.status === 'success') {
            hideAddAccountForm();
            loadAccounts();
            alert('✓ Account added successfully!');
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error: ' + error);
        console.error(error);
    });
});

// Broadcast Functions
function loadBroadcastAccountsList(accounts) {
    const accountsList = document.getElementById('broadcast-accounts-list');
    if (!accountsList) return;
    
    accountsList.innerHTML = '';
    accounts.forEach(account => {
        const label = document.createElement('label');
        label.className = 'checkbox-item';
        label.innerHTML = `
            <input type="checkbox" value="${account.id}" class="account-checkbox" onchange="updateSelectedAccounts()">
            <span>📱 ${account.phone}</span>
        `;
        accountsList.appendChild(label);
    });
}

function loadBroadcastGroupsList() {
    if (selectedAccounts.length === 0) {
        const groupsList = document.getElementById('broadcast-groups-list');
        if (groupsList) groupsList.innerHTML = '<p style="color: var(--text-gray);">Select accounts first to load groups</p>';
        return;
    }

    const groupsList = document.getElementById('broadcast-groups-list');
    if (!groupsList) return;
    
    groupsList.innerHTML = '<p style="color: var(--text-gray);">Loading groups...</p>';
    
    // Fetch groups for all selected accounts
    Promise.all(selectedAccounts.map(accountId => 
        fetch(`/api/accounts/${accountId}/groups`).then(r => r.json())
    ))
    .then(allGroups => {
        const uniqueGroups = {};
        allGroups.forEach(groups => {
            groups.forEach(group => {
                if (!uniqueGroups[group.group_id]) {
                    uniqueGroups[group.group_id] = group;
                }
            });
        });
        
        groupsList.innerHTML = '';
        Object.values(uniqueGroups).forEach(group => {
            const label = document.createElement('label');
            label.className = 'checkbox-item';
            label.innerHTML = `
                <input type="checkbox" value="${group.group_id}" class="group-checkbox" data-name="${group.group_name}" onchange="updateSelectedGroups()">
                <span>👥 ${group.group_name}</span>
            `;
            groupsList.appendChild(label);
        });
    })
    .catch(error => {
        console.error('Error loading groups:', error);
        groupsList.innerHTML = '<p style="color: var(--danger);">Error loading groups</p>';
    });
}

function updateSelectedAccounts() {
    const checkboxes = document.querySelectorAll('.account-checkbox:checked');
    selectedAccounts = Array.from(checkboxes).map(cb => parseInt(cb.value));
    loadBroadcastGroupsList();
}

function updateSelectedGroups() {
    const checkboxes = document.querySelectorAll('.group-checkbox:checked');
    selectedGroups = Array.from(checkboxes).map(cb => ({
        id: cb.value,
        name: cb.dataset.name
    }));
}

function selectAllAccounts() {
    document.querySelectorAll('.account-checkbox').forEach(cb => cb.checked = true);
    updateSelectedAccounts();
}

function deselectAllAccounts() {
    document.querySelectorAll('.account-checkbox').forEach(cb => cb.checked = false);
    updateSelectedAccounts();
}

function selectAllGroups() {
    document.querySelectorAll('.group-checkbox').forEach(cb => cb.checked = true);
    updateSelectedGroups();
}

function deselectAllGroups() {
    document.querySelectorAll('.group-checkbox').forEach(cb => cb.checked = false);
    updateSelectedGroups();
}

function showBroadcastForm() {
    loadBroadcastAccountsList([]);
    fetch('/api/accounts')
        .then(r => r.json())
        .then(accounts => loadBroadcastAccountsList(accounts));
    document.getElementById('broadcast-form').style.display = 'block';
}

function hideBroadcastForm() {
    document.getElementById('broadcast-form').style.display = 'none';
    document.getElementById('broadcast-message-form').reset();
    selectedAccounts = [];
    selectedGroups = [];
}

// Update broadcast delay display
document.getElementById('broadcast-delay')?.addEventListener('input', function() {
    document.getElementById('broadcast-delay-value').textContent = this.value;
});

// Show/hide broadcast repeat interval
document.getElementById('broadcast-auto-repeat')?.addEventListener('change', function() {
    document.getElementById('broadcast-repeat-group').style.display = this.checked ? 'block' : 'none';
});

document.getElementById('broadcast-message-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (selectedAccounts.length === 0) {
        alert('❌ Please select at least one account');
        return;
    }
    
    if (selectedGroups.length === 0) {
        alert('❌ Please select at least one group');
        return;
    }
    
    const name = document.getElementById('broadcast-name').value;
    const message = document.getElementById('broadcast-message').value;
    const delay = parseInt(document.getElementById('broadcast-delay').value);
    const autoRepeat = document.getElementById('broadcast-auto-repeat').checked ? 1 : 0;
    const repeatInterval = parseInt(document.getElementById('broadcast-repeat-interval').value) || 60;
    
    const payload = {
        name,
        message,
        delay_seconds: delay,
        auto_repeat: autoRepeat,
        repeat_interval: repeatInterval,
        selected_accounts: selectedAccounts,
        selected_groups: selectedGroups
    };
    
    fetch('/api/batch-messages/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            hideBroadcastForm();
            loadBroadcasts();
            alert(`✓ Broadcast "${name}" created successfully!\nAccounts: ${selectedAccounts.length} | Groups: ${selectedGroups.length}`);
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error creating broadcast: ' + error);
        console.error(error);
    });
});

function loadBroadcasts() {
    fetch('/api/batch-messages')
        .then(response => response.json())
        .then(broadcasts => {
            const list = document.getElementById('broadcasts-list');
            list.innerHTML = '';
            
            if (broadcasts.length === 0) {
                list.innerHTML = '<p style="text-align: center; color: var(--text-gray);">No broadcasts created yet</p>';
            }
            
            broadcasts.forEach(broadcast => {
                const item = document.createElement('div');
                item.className = 'list-item';
                item.innerHTML = `
                    <div class="list-item-header">
                        <div class="list-item-title">📢 ${broadcast.name}</div>
                        <span class="list-item-status ${broadcast.is_active ? 'status-active' : 'status-inactive'}">
                            ${broadcast.is_active ? 'ACTIVE' : 'INACTIVE'}
                        </span>
                    </div>
                    <div class="list-item-details">
                        Message: ${broadcast.message.substring(0, 80)}...<br>
                        Accounts: ${broadcast.accounts.length} | Groups: ${broadcast.groups.length}<br>
                        Delay: ${broadcast.delay_seconds}s | Auto Repeat: ${broadcast.auto_repeat ? 'Yes' : 'No'}
                    </div>
                    <div class="list-item-actions">
                        <button class="btn btn-success" onclick="executeBroadcast(${broadcast.id})">▶️ Execute Now</button>
                        <button class="btn btn-secondary" onclick="viewBroadcastDetails(${broadcast.id})">👁️ View</button>
                        <button class="btn btn-danger" onclick="deleteBroadcast(${broadcast.id})">🗑️ Delete</button>
                    </div>
                `;
                list.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Error loading broadcasts:', error);
        });
}

function executeBroadcast(broadcastId) {
    if (!confirm('Execute this broadcast now? Messages will be sent to all selected accounts and groups.')) {
        return;
    }
    
    fetch(`/api/batch-messages/${broadcastId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`✓ ${data.message}`);
            loadBroadcasts();
            loadLogs();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error executing broadcast: ' + error);
        console.error(error);
    });
}

function viewBroadcastDetails(broadcastId) {
    fetch('/api/batch-messages')
        .then(r => r.json())
        .then(broadcasts => {
            const broadcast = broadcasts.find(b => b.id === broadcastId);
            if (broadcast) {
                alert(`📢 Broadcast: ${broadcast.name}\n\nMessage:\n${broadcast.message}\n\nAccounts: ${broadcast.accounts.length}\nGroups: ${broadcast.groups.length}\nDelay: ${broadcast.delay_seconds}s`);
            }
        });
}

function deleteBroadcast(broadcastId) {
    if (confirm('Are you sure you want to delete this broadcast?')) {
        alert('Delete functionality coming soon');
    }
}

// Logs
function loadLogs() {
    fetch('/api/logs?limit=100')
        .then(response => response.json())
        .then(logs => {
            const recentContainer = document.getElementById('recent-logs');
            const logsContainer = document.getElementById('logs-container');
            
            const displayLogs = (container, logsList) => {
                if (!container) return;
                container.innerHTML = '';
                
                if (logsList.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: var(--text-gray);">No logs yet</p>';
                    return;
                }
                
                logsList.slice(0, 20).forEach(log => {
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
            };
            
            displayLogs(recentContainer, logs);
            displayLogs(logsContainer, logs);
            
            document.getElementById('total-logs').textContent = logs.length;
        })
        .catch(error => {
            console.error('Error loading logs:', error);
        });
}

function refreshLogs() {
    loadLogs();
}

function clearAllLogs() {
    if (confirm('Clear all logs?')) {
        alert('Clear logs functionality coming soon');
    }
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
        alert('✓ Service Started!');
        this.style.background = 'var(--success)';
        this.textContent = '✓ RUNNING';
        this.disabled = true;
        setTimeout(() => {
            this.style.background = '';
            this.textContent = '▶️ START SERVICE';
            this.disabled = false;
        }, 3000);
    })
    .catch(error => {
        alert('Error: ' + error);
        console.error(error);
    });
});

// Auto-refresh logs every 5 seconds
setInterval(() => {
    const logsTab = document.getElementById('logs-container');
    if (logsTab && logsTab.offsetParent !== null) {
        loadLogs();
    }
}, 5000);
