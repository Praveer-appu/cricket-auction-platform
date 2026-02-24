/**
 * Advanced Team Dashboard JavaScript
 * Version: 1.0.4
 */

// Global state
let teamData = null;
let myPlayers = [];
let allPlayers = [];
let ws = null;
let charts = {};
let currentPlayerMLPrediction = null; // Store ML prediction for overbidding detection

// Get authentication
const token = localStorage.getItem('access_token');
const teamId = localStorage.getItem('team_id');

// Check authentication
if (!token || !teamId) {
    window.location.href = '/';
}

// API helper with token refresh
async function refreshAccessToken() {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
        return false;
    }
    
    try {
        const formData = new FormData();
        formData.append("refresh_token", refreshToken);
        
        const response = await fetch("/auth/refresh", {
            method: "POST",
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("access_token", data.access_token);
            console.log("Token refreshed successfully");
            return true;
        }
    } catch (error) {
        console.error("Token refresh failed:", error);
    }
    
    return false;
}

async function api(url, options = {}) {
    // Use current page protocol (HTTP for localhost, HTTPS for production)
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        // Relative URL - construct absolute URL with current protocol
        url = `${window.location.protocol}//${window.location.host}${url}`;
    }
    
    const currentToken = localStorage.getItem('access_token');
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${currentToken}`
    };
    
    let response = await fetch(url, options);
    
    // If 401 Unauthorized, try to refresh token and retry
    if (response.status === 401) {
        console.log("Token expired, attempting refresh...");
        const refreshed = await refreshAccessToken();
        
        if (refreshed) {
            // Retry the request with new token
            const newToken = localStorage.getItem('access_token');
            options.headers = {
                ...options.headers,
                'Authorization': `Bearer ${newToken}`
            };
            response = await fetch(url, options);
        } else {
            // Refresh failed, redirect to login
            alert("Your session has expired. Please login again.");
            logout();
            return null;
        }
    }
    
    return response;
}

// Initialize dashboard
async function init() {
    console.log('Initializing Team Dashboard...');
    await loadTeamData();
    await loadMyPlayers();
    await loadAllPlayers();
    await loadAuctionStatus();
    connectWebSocket();
    initCharts();
    
    // Auto-refresh every 3 seconds (reduced from 5)
    setInterval(async () => {
        await loadTeamData();
        await loadAuctionStatus();
    }, 3000);
}

// Load team data
async function loadTeamData() {
    try {
        const res = await api(`/teams/${teamId}`);
        if (!res) return;
        
        teamData = await res.json();
        updateTeamOverview();
    } catch (error) {
        console.error('Error loading team data:', error);
    }
}

// Update team overview panel
function updateTeamOverview() {
    if (!teamData) return;
    
    // Team identity
    document.getElementById('team-name').textContent = teamData.name || 'Team';
    document.getElementById('team-username').textContent = `@${teamData.username || 'team'}`;
    
    // Team logo
    const logoContainer = document.getElementById('team-logo-container');
    if (teamData.logo_path && teamData.logo_path.trim()) {
        logoContainer.innerHTML = `<img src="${teamData.logo_path}" class="team-logo" alt="${teamData.name}">`;
    } else {
        const initial = (teamData.name || 'T')[0].toUpperCase();
        logoContainer.innerHTML = `<div class="team-logo-placeholder">${initial}</div>`;
    }
    
    // Statistics
    const budget = teamData.budget || 0;
    const spent = teamData.total_spent || 0;
    const remaining = budget - spent;
    const playersCount = teamData.players_count || 0;
    const highestPurchase = teamData.highest_purchase || 0;
    
    document.getElementById('total-budget').textContent = budget.toLocaleString();
    document.getElementById('total-spent').textContent = spent.toLocaleString();
    document.getElementById('remaining-purse').textContent = remaining.toLocaleString();
    document.getElementById('players-count').textContent = playersCount;
    document.getElementById('highest-purchase').textContent = highestPurchase.toLocaleString();
    
    // Purse progress bar
    const percentage = budget > 0 ? (remaining / budget) * 100 : 0;
    document.getElementById('purse-progress-bar').style.width = percentage + '%';
    document.getElementById('purse-percentage').textContent = percentage.toFixed(1);
    
    // Change color based on remaining budget
    const progressBar = document.getElementById('purse-progress-bar');
    if (percentage < 20) {
        progressBar.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
        // Show critical budget alert
        if (!window.budgetAlertShown20) {
            showToast('Budget Alert!', `Only ${percentage.toFixed(1)}% of budget remaining (₹${remaining.toLocaleString()})`, 'error');
            window.budgetAlertShown20 = true;
        }
    } else if (percentage < 50) {
        progressBar.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
        // Show warning budget alert
        if (!window.budgetAlertShown50) {
            showToast('Budget Warning', `${percentage.toFixed(1)}% of budget remaining (₹${remaining.toLocaleString()})`, 'warning');
            window.budgetAlertShown50 = true;
        }
    } else {
        progressBar.style.background = 'linear-gradient(90deg, #10b981, #667eea)';
    }
}

// Load auction status and current player
async function loadAuctionStatus() {
    try {
        const res = await api('/auction/status');
        if (!res) return;
        
        const status = await res.json();
        
        if (status.active && status.current_player_id) {
            await loadLivePlayer(status.current_player_id);
        } else {
            showNoAuction();
        }
    } catch (error) {
        console.error('Error loading auction status:', error);
        showNoAuction();
    }
}

// Load live player details
async function loadLivePlayer(playerId) {
    try {
        const res = await api(`/players/${playerId}`);
        if (!res) return;
        
        const player = await res.json();
        
        // Fetch ML prediction for overbidding detection
        try {
            const mlRes = await api(`/ml/predict-player/${playerId}`);
            if (mlRes && mlRes.ok) {
                const mlData = await mlRes.json();
                if (mlData.success) {
                    currentPlayerMLPrediction = mlData.predicted_price;
                    console.log(`ML Prediction for ${player.name}: ₹${currentPlayerMLPrediction.toLocaleString()}`);
                }
            }
        } catch (mlError) {
            console.log('ML prediction not available:', mlError);
            currentPlayerMLPrediction = null;
        }
        
        displayLivePlayer(player);
    } catch (error) {
        console.error('Error loading live player:', error);
    }
}

// Display live player
function displayLivePlayer(player) {
    const statusBadge = document.getElementById('live-status-badge');
    statusBadge.innerHTML = '<div class="live-badge"><i class="bi bi-circle-fill"></i> LIVE NOW</div>';
    
    const content = document.getElementById('auction-content');
    
    // Player image
    let playerImage = '';
    if (player.image_path) {
        playerImage = `<img src="${player.image_path}" class="player-image" alt="${player.name}" onerror="this.onerror=null; this.outerHTML='<div class=\\'player-image-placeholder\\'><i class=\\'bi bi-person-fill\\'></i></div>';">`;
    } else {
        playerImage = '<div class="player-image-placeholder"><i class="bi bi-person-fill"></i></div>';
    }
    
    // Current highest bid
    const currentBid = player.final_bid || player.base_price || 0;
    const leadingTeam = player.final_team ? 'You' : 'No bids yet';
    
    // Check if team can bid
    const canBid = teamData && (teamData.budget - teamData.total_spent) > currentBid;
    const isOwnPlayer = player.final_team === teamId;
    
    content.innerHTML = `
        <div class="player-showcase">
            <div class="player-image-container">
                ${playerImage}
            </div>
            <div class="player-details">
                <h3 class="player-name">${player.name}</h3>
                <div class="player-meta">
                    <span class="meta-badge role">
                        <i class="bi bi-trophy-fill"></i> ${player.role || 'Player'}
                    </span>
                    ${player.category ? `<span class="meta-badge category">
                        <i class="bi bi-tag-fill"></i> ${player.category}
                    </span>` : ''}
                </div>
                <div class="bid-info">
                    <div class="bid-info-item">
                        <div class="bid-info-label">Base Price</div>
                        <div class="bid-info-value">₹${(player.base_price || 0).toLocaleString()}</div>
                    </div>
                    <div class="bid-info-item">
                        <div class="bid-info-label">Current Bid</div>
                        <div class="bid-info-value">₹${currentBid.toLocaleString()}</div>
                    </div>
                    <div class="bid-info-item">
                        <div class="bid-info-label">Leading Team</div>
                        <div class="bid-info-value">${isOwnPlayer ? '🎯 You' : leadingTeam}</div>
                    </div>
                    ${currentPlayerMLPrediction ? `
                    <div class="bid-info-item" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)); border: 2px solid #667eea; border-radius: 10px; padding: 10px;">
                        <div class="bid-info-label" style="color: #667eea;">🤖 AI Predicted Value</div>
                        <div class="bid-info-value" style="color: #667eea;">₹${currentPlayerMLPrediction.toLocaleString()}</div>
                        <small style="color: #94a3b8; font-size: 11px; display: block; margin-top: 5px;">
                            Based on player statistics
                        </small>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
        
        <div class="bid-controls">
            <div class="bid-input-group">
                <input 
                    type="number" 
                    class="bid-input" 
                    id="bid-amount" 
                    placeholder="Enter bid amount"
                    min="${currentBid + 50}"
                    step="50"
                    value="${currentBid + 50}"
                    oninput="checkOverbiddingRealtime()"
                    onkeypress="if(event.key === 'Enter') { event.preventDefault(); placeBid('${player._id}', event); }"
                    ${!canBid || isOwnPlayer ? 'disabled' : ''}
                >
                <div id="overbid-indicator" style="display: none; margin-top: 8px; padding: 8px 12px; border-radius: 8px; font-size: 13px; font-weight: 600;"></div>
            </div>
            
            <!-- Quick Bid Presets for Mobile -->
            <div class="quick-bid-presets">
                <button class="quick-bid-btn" onclick="setQuickBid(${currentBid + 100})" ${!canBid || isOwnPlayer ? 'disabled' : ''}>
                    +100
                </button>
                <button class="quick-bid-btn" onclick="setQuickBid(${currentBid + 500})" ${!canBid || isOwnPlayer ? 'disabled' : ''}>
                    +500
                </button>
                <button class="quick-bid-btn" onclick="setQuickBid(${currentBid + 1000})" ${!canBid || isOwnPlayer ? 'disabled' : ''}>
                    +1K
                </button>
                <button class="quick-bid-btn" onclick="setQuickBid(${currentBid + 5000})" ${!canBid || isOwnPlayer ? 'disabled' : ''}>
                    +5K
                </button>
            </div>
            
            <button 
                type="button"
                class="bid-button" 
                onclick="placeBid('${player._id}')"
                ${!canBid || isOwnPlayer ? 'disabled' : ''}
            >
                <i class="bi bi-hammer"></i>
                ${isOwnPlayer ? 'You are Leading' : canBid ? 'Place Bid' : 'Insufficient Budget'}
            </button>
        </div>
        
        ${!canBid && !isOwnPlayer ? `
            <div class="alert alert-warning mt-3">
                <i class="bi bi-exclamation-triangle-fill"></i>
                Insufficient budget to bid on this player. Current bid: ₹${currentBid.toLocaleString()}, 
                Your remaining: ₹${(teamData.budget - teamData.total_spent).toLocaleString()}
            </div>
        ` : ''}
    `;
}

// Show no auction message
function showNoAuction() {
    const statusBadge = document.getElementById('live-status-badge');
    statusBadge.innerHTML = '<span class="badge bg-secondary">Auction Paused</span>';
    
    const content = document.getElementById('auction-content');
    content.innerHTML = `
        <div class="no-auction">
            <i class="bi bi-pause-circle"></i>
            <h4>No Active Auction</h4>
            <p>Waiting for admin to start the next player auction...</p>
        </div>
    `;
}

// Place bid
async function placeBid(playerId, event) {
    // Prevent any default behavior
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const bidAmount = parseInt(document.getElementById('bid-amount').value);
    
    if (!bidAmount || bidAmount <= 0) {
        showToast('Invalid Bid', 'Please enter a valid bid amount', 'error');
        return;
    }
    
    // Validate budget
    const remaining = teamData.budget - teamData.total_spent;
    if (bidAmount > remaining) {
        showToast('Insufficient Budget', `You only have ₹${remaining.toLocaleString()} remaining`, 'error');
        return;
    }
    
    // OVERBIDDING DETECTION - Check if bid exceeds ML prediction
    if (currentPlayerMLPrediction && bidAmount > currentPlayerMLPrediction) {
        const overpayAmount = bidAmount - currentPlayerMLPrediction;
        const overpayPercentage = ((overpayAmount / currentPlayerMLPrediction) * 100).toFixed(1);
        
        // Show dramatic warning if overbidding by more than 20%
        if (overpayPercentage > 20) {
            const proceed = await showOverbiddingAlert(bidAmount, currentPlayerMLPrediction, overpayPercentage);
            if (!proceed) {
                return; // User cancelled the bid
            }
        }
    }
    
    try {
        const res = await api('/auction/bid', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: playerId,
                team_id: teamId,  // Added team_id
                bid_amount: bidAmount
            })
        });
        
        if (!res) return;
        
        const data = await res.json();
        
        if (res.ok && data.ok) {
            showToast('Bid Placed!', `Your bid of ₹${bidAmount.toLocaleString()} has been placed`, 'success');
            await loadTeamData();
            await loadAuctionStatus();
        } else {
            showToast('Bid Failed', data.detail || 'Failed to place bid', 'error');
        }
    } catch (error) {
        console.error('Error placing bid:', error);
        showToast('Error', 'Failed to place bid. Please try again.', 'error');
    }
}

// Load my players
async function loadMyPlayers() {
    try {
        const res = await api(`/players?status=sold`);
        if (!res) return;
        
        const data = await res.json();
        const players = data.players || data;
        
        console.log('All sold players:', players.length);
        console.log('Team ID from localStorage:', teamId);
        
        // Filter only this team's players
        myPlayers = players.filter(p => {
            console.log(`Player ${p.name}: final_team=${p.final_team}, matches=${p.final_team === teamId}`);
            return p.final_team === teamId;
        });
        
        console.log('My players after filter:', myPlayers.length, myPlayers);
        
        displayMyPlayers();
        updateStatistics();
    } catch (error) {
        console.error('Error loading my players:', error);
    }
}

// Display my players
function displayMyPlayers() {
    const grid = document.getElementById('my-players-grid');
    
    if (myPlayers.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <h4>No Players Yet</h4>
                <p>Start bidding to build your squad!</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = myPlayers.map(player => createPlayerCard(player, true)).join('');
}

// Sort my players
function sortMyPlayers() {
    const sortBy = document.getElementById('my-players-sort').value;
    
    switch(sortBy) {
        case 'price-desc':
            myPlayers.sort((a, b) => (b.final_bid || 0) - (a.final_bid || 0));
            break;
        case 'price-asc':
            myPlayers.sort((a, b) => (a.final_bid || 0) - (b.final_bid || 0));
            break;
        case 'name':
            myPlayers.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'role':
            myPlayers.sort((a, b) => (a.role || '').localeCompare(b.role || ''));
            break;
    }
    
    displayMyPlayers();
}

// Load all players
async function loadAllPlayers() {
    try {
        const res = await api('/players');
        if (!res) return;
        
        const data = await res.json();
        allPlayers = data.players || data;
        
        filterPlayers();
    } catch (error) {
        console.error('Error loading all players:', error);
    }
}

// Filter players
function filterPlayers() {
    const search = document.getElementById('player-search').value.toLowerCase();
    const role = document.getElementById('role-filter').value;
    const category = document.getElementById('category-filter').value;
    const status = document.getElementById('status-filter').value;
    
    let filtered = allPlayers.filter(player => {
        // HIDE SOLD PLAYERS - they shouldn't appear in available players list
        if (player.status === 'sold') {
            return false;
        }
        
        const matchSearch = !search || player.name.toLowerCase().includes(search);
        const matchRole = !role || player.role === role;
        const matchCategory = !category || player.category === category;
        const matchStatus = !status || player.status === status;
        
        return matchSearch && matchRole && matchCategory && matchStatus;
    });
    
    const grid = document.getElementById('all-players-grid');
    
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-search"></i>
                <h4>No Players Found</h4>
                <p>Try adjusting your filters</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = filtered.map(player => createPlayerCard(player, false)).join('');
}

// Create player card HTML
function createPlayerCard(player, isOwned) {
    const defaultImg = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="280" height="220"%3E%3Crect fill="%230a0a0a" width="280" height="220"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="80" fill="%23ffd700"%3E👤%3C/text%3E%3C/svg%3E';
    
    // Handle image path - accept both Cloudinary URLs and local paths
    let imageSrc = defaultImg;
    if (player.image_path) {
        if (player.image_path.startsWith('http') || player.image_path.includes('/static/uploads/players/')) {
            imageSrc = player.image_path;
        }
    }
    
    const price = isOwned 
        ? '₹' + (player.final_bid || 0).toLocaleString()
        : player.status === 'sold'
        ? '₹' + (player.final_bid || 0).toLocaleString()
        : 'Base: ₹' + (player.base_price || 0).toLocaleString();
    
    const statusClass = player.status === 'sold' ? 'status-sold' : player.status === 'unsold' ? 'status-unsold' : 'status-available';
    const statusText = (player.status || 'available').toUpperCase();
    
    const roleInfo = (player.role || 'Player') + ' &bull; ' + (player.category || 'N/A');
    const teamInfo = player.team_name && !isOwned ? '<div class="player-card-info" style="color: #00d4ff;">Team: ' + player.team_name + '</div>' : '';
    
    // Player details for modal
    const age = player.age ? player.age + ' years' : 'N/A';
    const battingStyle = player.batting_style || 'N/A';
    const bowlingStyle = player.bowling_style || 'N/A';
    const bio = player.bio || 'No achievements/bio available';
    
    // ML Prediction badge (will be loaded asynchronously)
    const mlBadge = !isOwned && player.status !== 'sold' ? 
        '<div class="ml-prediction-badge" id="ml-pred-' + player._id + '" style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 4px 8px; border-radius: 5px; margin-top: 5px; font-size: 0.7rem;">' +
        '<span style="color: #fff;">🤖 AI: Loading...</span>' +
        '</div>' : '';
    
    const cardHtml = '<div class="player-card" onclick="showPlayerDetails(\'' + player._id + '\')" style="cursor: pointer;" title="Click to view details">' +
            '<img src="' + imageSrc + '" class="player-card-img" alt="' + player.name + '">' +
            '<div class="player-card-name">' + player.name + '</div>' +
            '<div class="player-card-info">' + roleInfo + '</div>' +
            '<div class="player-card-price">' + price + '</div>' +
            teamInfo +
            mlBadge +
            '<span class="status-badge ' + statusClass + '">' + statusText + '</span>' +
            '<div class="player-card-info" style="font-size: 0.75rem; color: #888; margin-top: 5px;">👁️ Click for details</div>' +
            // Hidden data for modal
            '<div style="display:none;" class="player-data" ' +
            'data-id="' + player._id + '" ' +
            'data-name="' + player.name + '" ' +
            'data-role="' + (player.role || 'N/A') + '" ' +
            'data-category="' + (player.category || 'N/A') + '" ' +
            'data-age="' + age + '" ' +
            'data-batting="' + battingStyle + '" ' +
            'data-bowling="' + bowlingStyle + '" ' +
            'data-bio="' + bio.replace(/"/g, '&quot;') + '" ' +
            'data-image="' + imageSrc + '" ' +
            'data-price="' + price + '">' +
            '</div>' +
        '</div>';
    
    // Load ML prediction asynchronously for available players
    if (!isOwned && player.status !== 'sold') {
        setTimeout(() => loadMLPrediction(player._id), 100);
    }
    
    return cardHtml;
}

// Initialize charts
function initCharts() {
    // Role spending chart
    const roleCtx = document.getElementById('role-chart');
    if (roleCtx) {
        charts.role = new Chart(roleCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: ['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
    
    // Category chart
    const categoryCtx = document.getElementById('category-chart');
    if (categoryCtx) {
        charts.category = new Chart(categoryCtx, {
            type: 'pie',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: ['#667eea', '#10b981', '#f59e0b']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
    
    // Budget chart
    const budgetCtx = document.getElementById('budget-chart');
    if (budgetCtx) {
        charts.budget = new Chart(budgetCtx, {
            type: 'bar',
            data: {
                labels: ['Total Budget', 'Spent', 'Remaining'],
                datasets: [{
                    label: 'Amount (₹)',
                    data: [0, 0, 0],
                    backgroundColor: ['#667eea', '#ef4444', '#10b981']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
}

// Update statistics
function updateStatistics() {
    if (!teamData || myPlayers.length === 0) return;
    
    // Role spending
    const roleSpending = {};
    myPlayers.forEach(player => {
        const role = player.role || 'Unknown';
        roleSpending[role] = (roleSpending[role] || 0) + (player.final_bid || 0);
    });
    
    if (charts.role) {
        charts.role.data.labels = Object.keys(roleSpending);
        charts.role.data.datasets[0].data = Object.values(roleSpending);
        charts.role.update();
    }
    
    // Category distribution
    const categoryCount = {};
    myPlayers.forEach(player => {
        const category = player.category || 'Unknown';
        categoryCount[category] = (categoryCount[category] || 0) + 1;
    });
    
    if (charts.category) {
        charts.category.data.labels = Object.keys(categoryCount);
        charts.category.data.datasets[0].data = Object.values(categoryCount);
        charts.category.update();
    }
    
    // Budget overview
    if (charts.budget) {
        const budget = teamData.budget || 0;
        const spent = teamData.total_spent || 0;
        const remaining = budget - spent;
        
        charts.budget.data.datasets[0].data = [budget, spent, remaining];
        charts.budget.update();
    }
}

// WebSocket connection
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/auction/ws`;
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
    };
    
    ws.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        console.log('WebSocket message:', data);
        
        // Handle different event types
        switch(data.type) {
            case 'bid_placed':
                await loadTeamData();
                await loadAuctionStatus();
                
                // Show notification if outbid
                if (data.data && data.data.team_id !== teamId && data.data.previous_team_id === teamId) {
                    showToast('Outbid!', `You have been outbid on ${data.data.player_name}`, 'warning');
                    
                    // Browser notification if enabled
                    if (notificationPreferences.outbid && teamNotificationPermission === 'granted') {
                        showTeamNotification('🔔 Outbid!', {
                            body: `You have been outbid on ${data.data.player_name}`,
                            tag: 'outbid',
                            vibrate: [200, 100, 200, 100, 200]
                        });
                    }
                }
                break;
                
            case 'player_sold':
                await loadTeamData();
                await loadMyPlayers();
                await loadAuctionStatus();
                
                if (data.data && data.data.team_id === teamId) {
                    showToast('Player Acquired!', `You won ${data.data.player_name} for ₹${data.data.final_bid.toLocaleString()}`, 'success');
                    
                    // Browser notification if enabled
                    if (notificationPreferences.playerSold && teamNotificationPermission === 'granted') {
                        showTeamNotification('🎉 Player Acquired!', {
                            body: `You won ${data.data.player_name} for ₹${data.data.final_bid.toLocaleString()}`,
                            tag: 'player-sold',
                            vibrate: [300, 100, 300]
                        });
                    }
                }
                break;
                
            case 'player_unsold':
                await loadAuctionStatus();
                break;
                
            case 'player_live':
                await loadAuctionStatus();
                
                // Browser notification if enabled
                if (data.data && notificationPreferences.playerLive && teamNotificationPermission === 'granted') {
                    showTeamNotification('🔴 New Player Live', {
                        body: `${data.data.player_name} is now live for bidding`,
                        tag: 'player-live',
                        vibrate: [200]
                    });
                }
                break;
                
            case 'player_undo':
                // Handle undo event - refresh team data and players
                await loadTeamData();
                await loadMyPlayers();
                await loadAuctionStatus();
                
                if (data.data && data.data.team_id === teamId) {
                    showToast('Sale Undone', `${data.data.player_name} removed from your roster. ₹${data.data.refund_amount.toLocaleString()} refunded.`, 'warning');
                }
                break;
                
            case 'auction_reset':
                // Handle auction reset
                await loadTeamData();
                await loadMyPlayers();
                await loadAllPlayers();
                await loadAuctionStatus();
                showToast('Auction Reset', 'The auction has been reset by admin', 'warning');
                break;
                
            case 'chat_message':
                // Handle incoming chat message
                if (typeof handleChatMessage === 'function') {
                    handleChatMessage(data.data);
                }
                break;
                
            case 'auction_status':
                await loadAuctionStatus();
                
                // Check if wishlist player went live
                if (data.data && data.data.current_player_id && typeof handleWishlistPlayerLive === 'function') {
                    handleWishlistPlayerLive(data.data.current_player_id);
                }
                break;
                
            case 'timer_update':
                updateTeamAuctionTimer(data.data.seconds);
                break;
                
            case 'team_update':
                await loadTeamData();
                break;
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected, reconnecting...');
        setTimeout(connectWebSocket, 3000);
    };
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.custom-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    // Load data if needed
    if (tabName === 'statistics') {
        updateStatistics();
    }
}

// Toast notifications
function showToast(title, message, type = 'success') {
    const container = document.getElementById('toast-container');
    
    const icons = {
        success: 'bi-check-circle-fill',
        error: 'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast-custom ${type}`;
    toast.innerHTML = `
        <i class="bi ${icons[type]} toast-icon ${type}"></i>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('team_id');
    localStorage.removeItem('team_name');
    window.location.href = '/';
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);


// Auction Timer Display for Team Dashboard
let teamLastBeepSecond = -1;

function updateTeamAuctionTimer(seconds) {
    console.log('Team timer update:', seconds);
    const timerCard = document.getElementById('team-auction-timer-card');
    const timerDisplay = document.getElementById('team-auction-timer-display');
    const progressBar = document.getElementById('team-timer-progress-bar');
    
    console.log('Team timer elements:', {
        timerCard: !!timerCard,
        timerDisplay: !!timerDisplay,
        progressBar: !!progressBar
    });
    
    if (!timerCard || !timerDisplay || !progressBar) {
        console.error('Team timer elements not found!');
        return;
    }
    
    if (seconds > 0) {
        console.log('Showing team timer with', seconds, 'seconds');
        timerCard.style.display = 'block';
        
        // Format time
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        timerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        
        // Update progress - use 30 as max
        const percentage = Math.min(100, (seconds / 30) * 100);
        progressBar.style.width = percentage + '%';
        
        // Color changes
        if (seconds <= 5) {
            progressBar.classList.remove('bg-warning', 'bg-success');
            progressBar.classList.add('bg-danger');
            timerDisplay.style.color = '#ff4444';
            timerDisplay.style.animation = 'pulse 0.5s infinite';
        } else if (seconds <= 10) {
            progressBar.classList.remove('bg-success', 'bg-danger');
            progressBar.classList.add('bg-warning');
            timerDisplay.style.color = '#ffaa00';
            timerDisplay.style.animation = 'none';
        } else {
            progressBar.classList.remove('bg-warning', 'bg-danger');
            progressBar.classList.add('bg-success');
            timerDisplay.style.color = '#ffffff';
            timerDisplay.style.animation = 'none';
        }
        
        // Play beeps
        if (seconds <= 10 && seconds !== teamLastBeepSecond) {
            playTeamCountdownBeep(seconds);
            teamLastBeepSecond = seconds;
        }
        
        // Enable bid button when timer is running
        const bidButton = document.querySelector('.bid-button');
        if (bidButton) {
            bidButton.disabled = false;
        }
    } else {
        // Timer expired - disable bidding
        timerCard.style.display = 'none';
        teamLastBeepSecond = -1;
        
        // Disable bid button when timer expires
        const bidButton = document.querySelector('.bid-button');
        if (bidButton) {
            bidButton.disabled = true;
            bidButton.textContent = 'Auction Closed';
        }
        
        // Show message that auction is closing
        showToast('Auction Closed', 'Time expired! Auction is being finalized...', 'warning');
    }
}

function playTeamCountdownBeep(seconds) {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        if (seconds <= 3) {
            oscillator.frequency.value = 1200;
            gainNode.gain.value = 0.3;
        } else if (seconds <= 5) {
            oscillator.frequency.value = 900;
            gainNode.gain.value = 0.2;
        } else {
            oscillator.frequency.value = 600;
            gainNode.gain.value = 0.15;
        }
        
        oscillator.type = 'sine';
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.1);
    } catch (error) {
        console.log('Audio not supported');
    }
}


/* ============================================================
    NOTIFICATION SYSTEM FOR TEAMS
    Version: 3.5.0
============================================================ */
let teamNotificationPermission = 'default';
let notificationPreferences = {
    outbid: true,
    playerSold: true,
    budgetWarning: true,
    playerLive: false
};

// Load notification preferences from localStorage
function loadNotificationPreferences() {
    const saved = localStorage.getItem('notification_preferences');
    if (saved) {
        try {
            notificationPreferences = JSON.parse(saved);
        } catch (e) {
            console.error('Error loading notification preferences:', e);
        }
    }
}

// Save notification preferences
function saveNotificationPreferences() {
    localStorage.setItem('notification_preferences', JSON.stringify(notificationPreferences));
}

// Request notification permission
async function requestTeamNotificationPermission() {
    if (!('Notification' in window)) {
        console.log('Browser does not support notifications');
        return false;
    }
    
    if (Notification.permission === 'granted') {
        teamNotificationPermission = 'granted';
        return true;
    }
    
    if (Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission();
        teamNotificationPermission = permission;
        return permission === 'granted';
    }
    
    return false;
}

// Show team notification
function showTeamNotification(title, options = {}) {
    if (teamNotificationPermission !== 'granted') {
        console.log('Notification permission not granted');
        return;
    }
    
    const defaultOptions = {
        icon: '/static/logo.png',
        badge: '/static/badge.png',
        vibrate: [200, 100, 200],
        requireInteraction: false,
        ...options
    };
    
    try {
        const notification = new Notification(title, defaultOptions);
        
        // Auto-close after 6 seconds
        setTimeout(() => notification.close(), 6000);
        
        // Handle click - focus window
        notification.onclick = function(event) {
            event.preventDefault();
            window.focus();
            notification.close();
        };
        
        return notification;
    } catch (error) {
        console.error('Error showing notification:', error);
        return null;
    }
}

// Show notification settings modal
function showNotificationSettings() {
    const modal = document.createElement('div');
    modal.className = 'notification-settings-modal';
    
    const content = document.createElement('div');
    content.className = 'notification-settings-content';
    
    content.innerHTML = 
        '<h3>🔔 Notification Settings</h3>' +
        '<p class="text-muted">Choose which notifications you want to receive</p>' +
        
        '<div class="notification-option">' +
            '<label>' +
                '<input type="checkbox" id="notif-outbid" ' + (notificationPreferences.outbid ? 'checked' : '') + '>' +
                '<div><span style="font-size:16px;font-weight:600;display:block;margin-bottom:4px;">Outbid Alerts</span>' +
                '<small style="display:block;color:rgba(255,255,255,0.6);font-size:13px;">When another team outbids you</small></div>' +
            '</label>' +
        '</div>' +
        
        '<div class="notification-option">' +
            '<label>' +
                '<input type="checkbox" id="notif-player-sold" ' + (notificationPreferences.playerSold ? 'checked' : '') + '>' +
                '<div><span style="font-size:16px;font-weight:600;display:block;margin-bottom:4px;">Player Acquired</span>' +
                '<small style="display:block;color:rgba(255,255,255,0.6);font-size:13px;">When you successfully acquire a player</small></div>' +
            '</label>' +
        '</div>' +
        
        '<div class="notification-option">' +
            '<label>' +
                '<input type="checkbox" id="notif-budget-warning" ' + (notificationPreferences.budgetWarning ? 'checked' : '') + '>' +
                '<div><span style="font-size:16px;font-weight:600;display:block;margin-bottom:4px;">Budget Warnings</span>' +
                '<small style="display:block;color:rgba(255,255,255,0.6);font-size:13px;">When your budget is running low</small></div>' +
            '</label>' +
        '</div>' +
        
        '<div class="notification-option">' +
            '<label>' +
                '<input type="checkbox" id="notif-player-live" ' + (notificationPreferences.playerLive ? 'checked' : '') + '>' +
                '<div><span style="font-size:16px;font-weight:600;display:block;margin-bottom:4px;">New Player Live</span>' +
                '<small style="display:block;color:rgba(255,255,255,0.6);font-size:13px;">When a new player goes live for bidding</small></div>' +
            '</label>' +
        '</div>' +
        
        '<div class="notification-settings-actions">' +
            '<button class="btn btn-primary" onclick="saveNotificationSettings()">Save Settings</button>' +
            '<button class="btn btn-secondary" onclick="closeNotificationSettings()">Cancel</button>' +
        '</div>';
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeNotificationSettings();
        }
    });
}

// Save notification settings
function saveNotificationSettings() {
    notificationPreferences.outbid = document.getElementById('notif-outbid').checked;
    notificationPreferences.playerSold = document.getElementById('notif-player-sold').checked;
    notificationPreferences.budgetWarning = document.getElementById('notif-budget-warning').checked;
    notificationPreferences.playerLive = document.getElementById('notif-player-live').checked;
    
    saveNotificationPreferences();
    closeNotificationSettings();
    showToast('Settings Saved', 'Notification preferences updated', 'success');
}

// Close notification settings
function closeNotificationSettings() {
    const modal = document.querySelector('.notification-settings-modal');
    if (modal) {
        modal.remove();
    }
}

// Expose functions globally
window.showNotificationSettings = showNotificationSettings;
window.saveNotificationSettings = saveNotificationSettings;
window.closeNotificationSettings = closeNotificationSettings;

// Initialize notifications
loadNotificationPreferences();
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            requestTeamNotificationPermission();
        }, 3000);
    });
} else {
    setTimeout(() => {
        requestTeamNotificationPermission();
    }, 3000);
}


/* ============================================================
    QUICK BID PRESETS FOR MOBILE
    Version: 3.5.0
============================================================ */
function setQuickBid(amount) {
    const bidInput = document.getElementById('bid-amount');
    if (bidInput) {
        bidInput.value = amount;
        
        // Add haptic feedback animation
        bidInput.classList.add('haptic-feedback');
        setTimeout(() => {
            bidInput.classList.remove('haptic-feedback');
        }, 200);
        
        // Vibrate if supported
        if ('vibrate' in navigator) {
            navigator.vibrate(50);
        }
    }
}

// Expose function globally
window.setQuickBid = setQuickBid;


// Show player details modal
async function showPlayerDetails(playerId) {
    // Find player in allPlayers array
    const player = allPlayers.find(p => p._id === playerId);
    if (!player) {
        console.error('Player not found:', playerId);
        return;
    }
    
    const defaultImg = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="280" height="220"%3E%3Crect fill="%230a0a0a" width="280" height="220"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="80" fill="%23ffd700"%3E👤%3C/text%3E%3C/svg%3E';
    let imageSrc = defaultImg;
    if (player.image_path) {
        if (player.image_path.startsWith('http') || player.image_path.includes('/static/uploads/players/')) {
            imageSrc = player.image_path;
        }
    }
    
    // Load ML prediction for available players
    let mlPredictionHTML = '';
    if (player.status !== 'sold') {
        mlPredictionHTML = `
            <div id="ml-prediction-section" style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <strong style="color: #fff;"><i class="fas fa-robot"></i> AI Price Prediction:</strong><br>
                <div style="color: #fff; margin-top: 10px; font-size: 0.9rem;">
                    <i class="fas fa-spinner fa-spin"></i> Loading prediction...
                </div>
            </div>
        `;
    }
    
    const modalHTML = `
        <div class="modal fade" id="playerDetailsModal" tabindex="-1" style="z-index: 10000;">
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border: 2px solid #ffd700;">
                    <div class="modal-header" style="border-bottom: 2px solid #ffd700;">
                        <h5 class="modal-title" style="color: #ffd700;">
                            <i class="fas fa-user-circle"></i> Player Profile
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-4 text-center">
                                <img src="${imageSrc}" class="img-fluid rounded" style="max-height: 300px; border: 3px solid #ffd700;" alt="${player.name}">
                            </div>
                            <div class="col-md-8">
                                <h3 style="color: #ffd700; margin-bottom: 20px;">${player.name}</h3>
                                
                                ${mlPredictionHTML}
                                
                                <div class="row mb-3">
                                    <div class="col-6">
                                        <strong style="color: #00d4ff;">Role:</strong><br>
                                        <span style="color: #fff;">${player.role || 'N/A'}</span>
                                    </div>
                                    <div class="col-6">
                                        <strong style="color: #00d4ff;">Category:</strong><br>
                                        <span style="color: #fff;">${player.category || 'N/A'}</span>
                                    </div>
                                </div>
                                
                                <div class="row mb-3">
                                    <div class="col-6">
                                        <strong style="color: #00d4ff;">Age:</strong><br>
                                        <span style="color: #fff;">${player.age || 'N/A'} years</span>
                                    </div>
                                    <div class="col-6">
                                        <strong style="color: #00d4ff;">Base Price:</strong><br>
                                        <span style="color: #10b981; font-size: 1.2rem;">₹${(player.base_price || 0).toLocaleString()}</span>
                                    </div>
                                </div>
                                
                                <div class="row mb-3">
                                    <div class="col-6">
                                        <strong style="color: #00d4ff;">Batting Style:</strong><br>
                                        <span style="color: #fff;">${player.batting_style || 'N/A'}</span>
                                    </div>
                                    <div class="col-6">
                                        <strong style="color: #00d4ff;">Bowling Style:</strong><br>
                                        <span style="color: #fff;">${player.bowling_style || 'N/A'}</span>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <strong style="color: #00d4ff;">Achievements / Bio:</strong><br>
                                    <div style="color: #fff; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; margin-top: 10px; max-height: 150px; overflow-y: auto;">
                                        ${player.bio || 'No achievements or bio available'}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer" style="border-top: 2px solid #ffd700;">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('playerDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('playerDetailsModal'));
    modal.show();
    
    // Load ML prediction asynchronously
    if (player.status !== 'sold') {
        loadMLPredictionForModal(playerId);
    }
    
    // Clean up modal after it's hidden
    document.getElementById('playerDetailsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}


// ============================================================
// ML PREDICTION FUNCTIONS
// ============================================================

/**
 * Load ML prediction for a player
 */
async function loadMLPrediction(playerId) {
    try {
        const res = await api(`/ml/predict-player/${playerId}`);
        if (!res || !res.ok) {
            updateMLBadge(playerId, null);
            return;
        }
        
        const data = await res.json();
        
        if (data.success) {
            updateMLBadge(playerId, {
                predicted: data.predicted_price_formatted,
                confidence: data.confidence_range,
                current: data.current_base_price
            });
        } else {
            updateMLBadge(playerId, null);
        }
    } catch (error) {
        console.error('ML Prediction error:', error);
        updateMLBadge(playerId, null);
    }
}

/**
 * Update ML prediction badge in player card
 */
function updateMLBadge(playerId, prediction) {
    const badge = document.getElementById(`ml-pred-${playerId}`);
    if (!badge) return;
    
    if (prediction) {
        badge.innerHTML = `<span style="color: #fff; font-weight: 600;">🤖 AI: ${prediction.predicted}</span>`;
        badge.title = `Confidence: ${prediction.confidence.min_formatted} - ${prediction.confidence.max_formatted}`;
    } else {
        badge.style.display = 'none';
    }
}

/**
 * Load ML prediction for modal display
 */
async function loadMLPredictionForModal(playerId) {
    const section = document.getElementById('ml-prediction-section');
    if (!section) return;
    
    try {
        const res = await api(`/ml/predict-player/${playerId}`);
        if (!res || !res.ok) {
            section.innerHTML = `
                <strong style="color: #fff;"><i class="fas fa-robot"></i> AI Price Prediction:</strong><br>
                <div style="color: #fff; margin-top: 10px; font-size: 0.9rem;">
                    <i class="fas fa-exclamation-circle"></i> Prediction unavailable
                </div>
            `;
            return;
        }
        
        const data = await res.json();
        
        if (data.success) {
            const difference = data.predicted_price - data.current_base_price;
            const diffPercent = ((difference / data.current_base_price) * 100).toFixed(1);
            const diffColor = difference > 0 ? '#10b981' : '#ef4444';
            const diffIcon = difference > 0 ? '📈' : '📉';
            
            section.innerHTML = `
                <strong style="color: #fff;"><i class="fas fa-robot"></i> AI Price Prediction:</strong><br>
                <div style="color: #fff; margin-top: 10px;">
                    <div style="font-size: 1.5rem; font-weight: bold; margin: 10px 0;">
                        ${data.predicted_price_formatted}
                    </div>
                    <div style="font-size: 0.85rem; opacity: 0.9; margin-bottom: 8px;">
                        Confidence Range: ${data.confidence_range.min_formatted} - ${data.confidence_range.max_formatted}
                    </div>
                    <div style="font-size: 0.85rem; color: ${diffColor};">
                        ${diffIcon} ${difference > 0 ? '+' : ''}₹${Math.abs(difference).toLocaleString()} (${diffPercent > 0 ? '+' : ''}${diffPercent}%) vs Base Price
                    </div>
                    <div style="font-size: 0.75rem; opacity: 0.7; margin-top: 8px;">
                        Model: ${data.model_used.replace('_', ' ').toUpperCase()}
                    </div>
                </div>
            `;
        } else {
            section.innerHTML = `
                <strong style="color: #fff;"><i class="fas fa-robot"></i> AI Price Prediction:</strong><br>
                <div style="color: #fff; margin-top: 10px; font-size: 0.9rem;">
                    <i class="fas fa-exclamation-circle"></i> Prediction unavailable
                </div>
            `;
        }
    } catch (error) {
        console.error('ML Prediction error:', error);
        section.innerHTML = `
            <strong style="color: #fff;"><i class="fas fa-robot"></i> AI Price Prediction:</strong><br>
            <div style="color: #fff; margin-top: 10px; font-size: 0.9rem;">
                <i class="fas fa-exclamation-circle"></i> Error loading prediction
            </div>
        `;
    }
}


// ============================================================
// ML CALCULATOR FUNCTIONS
// ============================================================

/**
 * Load all players into the search dropdown
 */
async function loadPlayersForMLCalculator() {
    try {
        const res = await api('/players');
        if (!res || !res.ok) return;
        
        const data = await res.json();
        const players = data.players || data;
        
        const dropdown = document.getElementById('ml-player-search');
        if (!dropdown) return;
        
        // Clear existing options except first
        dropdown.innerHTML = '<option value="">-- Select a player to auto-fill data --</option>';
        
        // Add players to dropdown
        players.forEach(player => {
            const option = document.createElement('option');
            option.value = player._id;
            option.textContent = `${player.name} (${player.role || 'Player'}) - ${player.status || 'Available'}`;
            option.dataset.player = JSON.stringify(player);
            dropdown.appendChild(option);
        });
        
        console.log(`Loaded ${players.length} players into ML calculator`);
    } catch (error) {
        console.error('Error loading players for ML calculator:', error);
    }
}

/**
 * Load selected player's data into the form
 */
function loadPlayerData() {
    const dropdown = document.getElementById('ml-player-search');
    const selectedOption = dropdown.options[dropdown.selectedIndex];
    
    if (!selectedOption.value) {
        // Reset form if no player selected
        resetMLForm();
        return;
    }
    
    try {
        const player = JSON.parse(selectedOption.dataset.player);
        
        // Set player type
        document.getElementById('ml-player-type').value = player.role || 'Batsman';
        updateFieldsForPlayerType();
        
        // Set statistics
        document.getElementById('ml-matches').value = player.matches_played || 50;
        document.getElementById('ml-batting-avg').value = player.batting_average || 25.0;
        document.getElementById('ml-strike-rate').value = player.strike_rate || 120.0;
        document.getElementById('ml-wickets').value = player.wickets || 10;
        document.getElementById('ml-economy').value = player.economy_rate || 8.0;
        document.getElementById('ml-performance').value = player.recent_performance_score || 70.0;
        
        showToast('Player Loaded', `${player.name}'s data has been loaded`, 'success');
    } catch (error) {
        console.error('Error loading player data:', error);
        showToast('Error', 'Failed to load player data', 'error');
    }
}

/**
 * Update form fields based on player type
 */
function updateFieldsForPlayerType() {
    const playerType = document.getElementById('ml-player-type').value;
    const battingFields = document.getElementById('batting-fields');
    const bowlingFields = document.getElementById('bowling-fields');
    
    // Show/hide fields based on player type
    switch(playerType) {
        case 'Batsman':
        case 'Wicketkeeper':
            // Show batting, hide bowling
            battingFields.style.display = 'block';
            bowlingFields.style.display = 'none';
            // Set default bowling values for calculation
            document.getElementById('ml-wickets').value = '5';
            document.getElementById('ml-economy').value = '9.0';
            break;
            
        case 'Bowler':
            // Hide batting, show bowling
            battingFields.style.display = 'none';
            bowlingFields.style.display = 'block';
            // Set default batting values for calculation
            document.getElementById('ml-batting-avg').value = '15.0';
            document.getElementById('ml-strike-rate').value = '100.0';
            break;
            
        case 'All-Rounder':
            // Show both
            battingFields.style.display = 'block';
            bowlingFields.style.display = 'block';
            break;
    }
}

/**
 * Load ML model information
 */
async function loadMLModelInfo() {
    try {
        const res = await api('/ml/model-info');
        if (!res || !res.ok) return;
        
        const data = await res.json();
        
        if (data.available) {
            document.getElementById('model-name').textContent = data.model_name.replace('_', ' ').toUpperCase();
            document.getElementById('model-accuracy').textContent = '75.31% (R²)';
            document.getElementById('model-features').textContent = data.features ? data.features.length : '7';
            document.getElementById('model-trained').textContent = data.trained_at || 'Recently';
        } else {
            document.getElementById('model-name').textContent = 'Not Available';
            document.getElementById('model-accuracy').textContent = 'N/A';
            document.getElementById('model-features').textContent = 'N/A';
            document.getElementById('model-trained').textContent = 'N/A';
        }
    } catch (error) {
        console.error('Error loading model info:', error);
    }
}

/**
 * Calculate ML prediction from manual input
 */
async function calculateMLPrediction() {
    // Get input values
    const matchesPlayed = parseInt(document.getElementById('ml-matches').value) || 0;
    const battingAverage = parseFloat(document.getElementById('ml-batting-avg').value) || 0;
    const strikeRate = parseFloat(document.getElementById('ml-strike-rate').value) || 0;
    const wickets = parseInt(document.getElementById('ml-wickets').value) || 0;
    const economy = parseFloat(document.getElementById('ml-economy').value) || 0;
    const performance = parseFloat(document.getElementById('ml-performance').value) || 0;
    const playerType = document.getElementById('ml-player-type').value;

    // Validate inputs
    if (matchesPlayed < 0 || battingAverage < 0 || strikeRate < 0 || wickets < 0 || economy < 0) {
        showToast('Invalid Input', 'All values must be non-negative', 'error');
        return;
    }

    if (performance < 0 || performance > 100) {
        showToast('Invalid Input', 'Performance score must be between 0 and 100', 'error');
        return;
    }

    // Show loading state
    const resultsContainer = document.getElementById('ml-results-container');
    resultsContainer.innerHTML = `
        <div style="text-align: center; padding: 60px 20px;">
            <i class="bi bi-hourglass-split" style="font-size: 64px; color: #667eea; margin-bottom: 20px; animation: spin 2s linear infinite;"></i>
            <p style="color: #fff; font-size: 18px;">Calculating prediction...</p>
        </div>
    `;

    try {
        // Call ML API
        const res = await api('/ml/predict-price', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                matches_played: matchesPlayed,
                batting_average: battingAverage,
                strike_rate: strikeRate,
                wickets: wickets,
                economy_rate: economy,
                recent_performance_score: performance,
                player_type: playerType
            })
        });

        if (!res || !res.ok) {
            throw new Error('Prediction failed');
        }

        const data = await res.json();

        if (data.success) {
            // Display results
            displayMLResults(data, {
                matchesPlayed,
                battingAverage,
                strikeRate,
                wickets,
                economy,
                performance,
                playerType
            });
            
            showToast('Success', 'Prediction calculated successfully!', 'success');
        } else {
            throw new Error(data.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('ML Prediction error:', error);
        resultsContainer.innerHTML = `
            <div style="text-align: center; padding: 60px 20px;">
                <i class="bi bi-exclamation-triangle" style="font-size: 64px; color: #ef4444; margin-bottom: 20px;"></i>
                <p style="color: #ef4444; font-size: 18px; margin-bottom: 10px;">Prediction Failed</p>
                <p style="color: #94a3b8; font-size: 14px;">${error.message}</p>
            </div>
        `;
        showToast('Error', 'Failed to calculate prediction', 'error');
    }
}

/**
 * Display ML prediction results
 */
function displayMLResults(data, inputs) {
    const resultsContainer = document.getElementById('ml-results-container');
    
    const predictedPrice = data.predicted_price;
    const formattedPrice = data.predicted_price_formatted;
    const confidence = data.confidence_range;
    const modelUsed = data.model_used;

    resultsContainer.innerHTML = `
        <div style="animation: fadeIn 0.5s;">
            <!-- Main Prediction -->
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 12px; padding: 25px; text-align: center; margin-bottom: 20px;">
                <div style="color: rgba(255,255,255,0.9); font-size: 14px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">
                    Predicted Auction Price
                </div>
                <div style="color: #fff; font-size: 42px; font-weight: 700; margin-bottom: 15px;">
                    ${formattedPrice}
                </div>
                <div style="color: rgba(255,255,255,0.8); font-size: 13px;">
                    Model: ${modelUsed.replace('_', ' ').toUpperCase()}
                </div>
            </div>

            <!-- Confidence Range -->
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                <h5 style="color: #10b981; margin-bottom: 15px; font-size: 16px;">
                    <i class="bi bi-graph-up"></i> Confidence Range (±15%)
                </h5>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div>
                        <div style="color: #94a3b8; font-size: 12px;">Minimum</div>
                        <div style="color: #fff; font-size: 18px; font-weight: 600;">${confidence.min_formatted}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #94a3b8; font-size: 12px;">Maximum</div>
                        <div style="color: #fff; font-size: 18px; font-weight: 600;">${confidence.max_formatted}</div>
                    </div>
                </div>
                <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #10b981, #667eea); height: 100%; width: 100%;"></div>
                </div>
            </div>

            <!-- Input Summary -->
            <div style="background: rgba(17, 17, 17, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px;">
                <h5 style="color: #ffd700; margin-bottom: 15px; font-size: 16px;">
                    <i class="bi bi-list-check"></i> Input Statistics
                </h5>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 13px;">
                    <div>
                        <span style="color: #94a3b8;">Matches:</span>
                        <span style="color: #fff; float: right; font-weight: 600;">${inputs.matchesPlayed}</span>
                    </div>
                    <div>
                        <span style="color: #94a3b8;">Batting Avg:</span>
                        <span style="color: #fff; float: right; font-weight: 600;">${inputs.battingAverage.toFixed(1)}</span>
                    </div>
                    <div>
                        <span style="color: #94a3b8;">Strike Rate:</span>
                        <span style="color: #fff; float: right; font-weight: 600;">${inputs.strikeRate.toFixed(1)}</span>
                    </div>
                    <div>
                        <span style="color: #94a3b8;">Wickets:</span>
                        <span style="color: #fff; float: right; font-weight: 600;">${inputs.wickets}</span>
                    </div>
                    <div>
                        <span style="color: #94a3b8;">Economy:</span>
                        <span style="color: #fff; float: right; font-weight: 600;">${inputs.economy.toFixed(1)}</span>
                    </div>
                    <div>
                        <span style="color: #94a3b8;">Performance:</span>
                        <span style="color: #fff; float: right; font-weight: 600;">${inputs.performance}/100</span>
                    </div>
                    <div style="grid-column: 1 / -1;">
                        <span style="color: #94a3b8;">Player Type:</span>
                        <span style="color: #fff; float: right; font-weight: 600;">${inputs.playerType}</span>
                    </div>
                </div>
            </div>

            <!-- Tips -->
            <div style="margin-top: 20px; padding: 15px; background: rgba(102, 126, 234, 0.1); border-left: 4px solid #667eea; border-radius: 8px;">
                <div style="color: #667eea; font-size: 13px; margin-bottom: 5px; font-weight: 600;">
                    <i class="bi bi-lightbulb-fill"></i> Bidding Tip
                </div>
                <div style="color: #94a3b8; font-size: 12px;">
                    This prediction is based on statistical analysis. Consider the confidence range when planning your bids. 
                    The actual auction price may vary based on team strategies and competition.
                </div>
            </div>
        </div>
    `;
}

/**
 * Reset ML calculator form
 */
function resetMLForm() {
    document.getElementById('ml-matches').value = '100';
    document.getElementById('ml-batting-avg').value = '35.0';
    document.getElementById('ml-strike-rate').value = '130.0';
    document.getElementById('ml-wickets').value = '15';
    document.getElementById('ml-economy').value = '8.0';
    document.getElementById('ml-performance').value = '75';
    document.getElementById('ml-player-type').value = 'Batsman';
    
    // Update field visibility
    updateFieldsForPlayerType();
    
    // Reset results
    const resultsContainer = document.getElementById('ml-results-container');
    resultsContainer.innerHTML = `
        <div style="text-align: center; padding: 60px 20px; color: #94a3b8;">
            <i class="bi bi-robot" style="font-size: 64px; color: #667eea; margin-bottom: 20px;"></i>
            <p>Select player type, enter statistics, and click "Calculate Price Prediction" to see AI-powered estimates</p>
        </div>
    `;
    
    showToast('Reset', 'Form has been reset to default values', 'success');
}

// Load model info and set initial field visibility when ML calculator tab is opened
const originalSwitchTab = switchTab;
switchTab = function(tabName) {
    originalSwitchTab(tabName);
    if (tabName === 'ml-calculator') {
        loadMLModelInfo();
        loadPlayersForMLCalculator(); // Load players into dropdown
        updateFieldsForPlayerType(); // Set initial field visibility
    }
};


/**
 * ============================================================
 * OVERBIDDING DETECTION SYSTEM
 * Shows dramatic full-screen red alert when team is overpaying
 * ============================================================
 */

function showOverbiddingAlert(bidAmount, predictedPrice, overpayPercentage) {
    return new Promise((resolve) => {
        // Create full-screen overlay
        const overlay = document.createElement('div');
        overlay.id = 'overbidding-alert-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(220, 38, 38, 0.95);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: redPulse 1.5s ease-in-out infinite;
        `;
        
        // Add pulsing animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes redPulse {
                0%, 100% { background: rgba(220, 38, 38, 0.95); }
                50% { background: rgba(185, 28, 28, 0.98); }
            }
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
                20%, 40%, 60%, 80% { transform: translateX(10px); }
            }
            @keyframes warningBlink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
        `;
        document.head.appendChild(style);
        
        // Create alert content
        const alertBox = document.createElement('div');
        alertBox.style.cssText = `
            background: #000000;
            border: 5px solid #ef4444;
            border-radius: 20px;
            padding: 50px;
            max-width: 600px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
            animation: shake 0.5s ease-in-out;
        `;
        
        alertBox.innerHTML = `
            <div style="font-size: 80px; margin-bottom: 20px; animation: warningBlink 1s ease-in-out infinite;">
                ⚠️
            </div>
            
            <h2 style="color: #ef4444; font-size: 36px; font-weight: 800; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px;">
                🤖 AI ALERT: OVERBIDDING!
            </h2>
            
            <div style="background: rgba(239, 68, 68, 0.2); border: 2px solid #ef4444; border-radius: 12px; padding: 25px; margin: 30px 0;">
                <div style="color: #fff; font-size: 18px; margin-bottom: 15px;">
                    You are about to overpay by
                </div>
                <div style="color: #ffd700; font-size: 48px; font-weight: 900; margin: 15px 0;">
                    ${overpayPercentage}%
                </div>
                <div style="color: #94a3b8; font-size: 14px; margin-top: 15px;">
                    Overpaying: ₹${(bidAmount - predictedPrice).toLocaleString()}
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; text-align: left;">
                <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 12px;">
                    <div style="color: #94a3b8; font-size: 14px; margin-bottom: 8px;">Your Bid</div>
                    <div style="color: #ef4444; font-size: 28px; font-weight: 700;">₹${bidAmount.toLocaleString()}</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 12px;">
                    <div style="color: #94a3b8; font-size: 14px; margin-bottom: 8px;">AI Predicted Value</div>
                    <div style="color: #10b981; font-size: 28px; font-weight: 700;">₹${predictedPrice.toLocaleString()}</div>
                </div>
            </div>
            
            <div style="background: rgba(251, 191, 36, 0.1); border-left: 4px solid #fbbf24; padding: 15px; margin: 25px 0; text-align: left; border-radius: 8px;">
                <div style="color: #fbbf24; font-weight: 600; margin-bottom: 8px;">
                    <i class="bi bi-lightbulb-fill"></i> AI Recommendation
                </div>
                <div style="color: #cbd5e1; font-size: 14px; line-height: 1.6;">
                    Based on player statistics and market analysis, this bid significantly exceeds the predicted fair value. 
                    Consider bidding closer to ₹${Math.round(predictedPrice * 1.1).toLocaleString()} (10% premium).
                </div>
            </div>
            
            <div style="display: flex; gap: 15px; margin-top: 35px;">
                <button id="cancel-bid-btn" style="
                    flex: 1;
                    padding: 18px;
                    background: linear-gradient(135deg, #10b981, #059669);
                    color: #fff;
                    border: none;
                    border-radius: 12px;
                    font-size: 18px;
                    font-weight: 700;
                    cursor: pointer;
                    transition: all 0.3s;
                ">
                    <i class="bi bi-x-circle"></i> Cancel Bid
                </button>
                <button id="proceed-bid-btn" style="
                    flex: 1;
                    padding: 18px;
                    background: rgba(239, 68, 68, 0.2);
                    color: #ef4444;
                    border: 2px solid #ef4444;
                    border-radius: 12px;
                    font-size: 18px;
                    font-weight: 700;
                    cursor: pointer;
                    transition: all 0.3s;
                ">
                    <i class="bi bi-exclamation-triangle"></i> Proceed Anyway
                </button>
            </div>
            
            <div style="color: #64748b; font-size: 12px; margin-top: 20px; font-style: italic;">
                This is an AI-powered warning to help you make informed decisions
            </div>
        `;
        
        overlay.appendChild(alertBox);
        document.body.appendChild(overlay);
        
        // Add button event listeners
        document.getElementById('cancel-bid-btn').addEventListener('click', () => {
            document.body.removeChild(overlay);
            document.head.removeChild(style);
            resolve(false); // Don't proceed with bid
        });
        
        document.getElementById('proceed-bid-btn').addEventListener('click', () => {
            document.body.removeChild(overlay);
            document.head.removeChild(style);
            resolve(true); // Proceed with bid
        });
        
        // Add hover effects
        const cancelBtn = document.getElementById('cancel-bid-btn');
        const proceedBtn = document.getElementById('proceed-bid-btn');
        
        cancelBtn.addEventListener('mouseenter', () => {
            cancelBtn.style.transform = 'translateY(-2px)';
            cancelBtn.style.boxShadow = '0 10px 25px rgba(16, 185, 129, 0.4)';
        });
        cancelBtn.addEventListener('mouseleave', () => {
            cancelBtn.style.transform = 'translateY(0)';
            cancelBtn.style.boxShadow = 'none';
        });
        
        proceedBtn.addEventListener('mouseenter', () => {
            proceedBtn.style.transform = 'translateY(-2px)';
            proceedBtn.style.boxShadow = '0 10px 25px rgba(239, 68, 68, 0.4)';
        });
        proceedBtn.addEventListener('mouseleave', () => {
            proceedBtn.style.transform = 'translateY(0)';
            proceedBtn.style.boxShadow = 'none';
        });
    });
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', init);


/**
 * Real-time overbidding indicator
 * Changes color as user types bid amount
 */
function checkOverbiddingRealtime() {
    const bidInput = document.getElementById('bid-amount');
    const indicator = document.getElementById('overbid-indicator');
    
    if (!bidInput || !indicator || !currentPlayerMLPrediction) {
        return;
    }
    
    const bidAmount = parseInt(bidInput.value);
    
    if (!bidAmount || bidAmount <= 0) {
        indicator.style.display = 'none';
        bidInput.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        return;
    }
    
    const difference = bidAmount - currentPlayerMLPrediction;
    const percentage = ((difference / currentPlayerMLPrediction) * 100).toFixed(1);
    
    if (bidAmount > currentPlayerMLPrediction) {
        // Overbidding
        indicator.style.display = 'block';
        
        if (percentage > 50) {
            // Extreme overbidding
            indicator.style.background = 'rgba(220, 38, 38, 0.2)';
            indicator.style.border = '2px solid #dc2626';
            indicator.style.color = '#dc2626';
            indicator.innerHTML = `⚠️ EXTREME OVERBID: +${percentage}% (₹${difference.toLocaleString()} over AI value)`;
            bidInput.style.borderColor = '#dc2626';
            bidInput.style.boxShadow = '0 0 20px rgba(220, 38, 38, 0.4)';
        } else if (percentage > 20) {
            // High overbidding
            indicator.style.background = 'rgba(239, 68, 68, 0.2)';
            indicator.style.border = '2px solid #ef4444';
            indicator.style.color = '#ef4444';
            indicator.innerHTML = `⚠️ Overbidding: +${percentage}% (₹${difference.toLocaleString()} over AI value)`;
            bidInput.style.borderColor = '#ef4444';
            bidInput.style.boxShadow = '0 0 15px rgba(239, 68, 68, 0.3)';
        } else {
            // Slight overbidding
            indicator.style.background = 'rgba(251, 191, 36, 0.2)';
            indicator.style.border = '2px solid #fbbf24';
            indicator.style.color = '#fbbf24';
            indicator.innerHTML = `⚡ Slight premium: +${percentage}% (₹${difference.toLocaleString()} over AI value)`;
            bidInput.style.borderColor = '#fbbf24';
            bidInput.style.boxShadow = '0 0 10px rgba(251, 191, 36, 0.2)';
        }
    } else if (bidAmount < currentPlayerMLPrediction * 0.8) {
        // Great value
        indicator.style.display = 'block';
        indicator.style.background = 'rgba(16, 185, 129, 0.2)';
        indicator.style.border = '2px solid #10b981';
        indicator.style.color = '#10b981';
        const savings = currentPlayerMLPrediction - bidAmount;
        indicator.innerHTML = `✅ Great Value! ${Math.abs(percentage).toFixed(1)}% below AI value (Save ₹${savings.toLocaleString()})`;
        bidInput.style.borderColor = '#10b981';
        bidInput.style.boxShadow = '0 0 10px rgba(16, 185, 129, 0.2)';
    } else {
        // Fair value
        indicator.style.display = 'block';
        indicator.style.background = 'rgba(102, 126, 234, 0.2)';
        indicator.style.border = '2px solid #667eea';
        indicator.style.color = '#667eea';
        indicator.innerHTML = `✓ Fair Value (Within AI predicted range)`;
        bidInput.style.borderColor = '#667eea';
        bidInput.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.2)';
    }
}
