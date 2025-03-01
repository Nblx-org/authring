// Application data
const applications = [
    { port: 8080, name: 'Jupyter', url: 'https://142.188.58.246:15277' },
    { port: 6006, name: 'Tensorboard', url: 'https://142.188.58.246:15565' }
];

function createAppCard(app) {
    const card = document.createElement('div');
    card.className = 'card';
    
    card.innerHTML = `
        <div class="card-content">
            <div class="card-header">
                <h2 class="app-name">${app.name}</h2>
            </div>
            
            <button class="launch-btn" onclick="window.open('${app.url}', '_blank')">
                Launch Application
            </button>
            
            <div class="advanced-section">
                <button class="advanced-toggle" onclick="toggleAdvanced(this)">
                    Advanced Connection Options
                </button>
                
                <div class="advanced-content">
                    <div class="advanced-details">
                        <div>
                            <div>Port: ${app.port}</div>
                            <div class="ip-info">IP: ${app.url.split('//')[1].split(':')[0]}</div>
                        </div>
                        <button class="copy-btn" onclick="copyUrl('${app.url}')">
                            Copy URL
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

function toggleAdvanced(button) {
    const content = button.nextElementSibling;
    content.classList.toggle('show');
}

function toggleSidebar() {
    document.body.classList.toggle('sidebar-open');
}

async function copyUrl(url) {
    try {
        await navigator.clipboard.writeText(url);
    } catch (err) {
        console.error('Failed to copy URL:', err);
    }
}

function showPage(pageId) {
    // Update URL hash without triggering the hashchange event
    const newHash = pageId.replace('-page', '');
    history.replaceState(null, '', `#/${newHash}`);
    
    // Hide all pages
    document.querySelectorAll('.page-container').forEach(container => {
        container.style.display = 'none';
    });
    
    // Show selected page
    const selectedPage = document.getElementById(pageId);
    if (selectedPage) {
        selectedPage.style.display = 'block';
    }
    
    // Update active state in navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
    
    // Update page title
    const pageTitle = document.querySelector('.page-title');
    switch(pageId) {
        case 'apps-page':
            pageTitle.textContent = 'Applications';
            break;
        case 'tunnels-page':
            pageTitle.textContent = 'Tunnels (Open New Ports)';
            break;
        case 'logs-page':
            pageTitle.textContent = 'Instance Logs';
            break;
        case 'tools-page':
            pageTitle.textContent = 'Tools & Help';
            break;
    }

    // Close sidebar on mobile after navigation
    document.body.classList.remove('sidebar-open');
}

function createTunnel(event) {
    event.preventDefault();
    const targetUrl = document.getElementById('target-url').value;
    console.log('Creating tunnel for:', targetUrl);
}

function cloneInstance() {
    console.log('Cloning instance...');
    // Implementation for cloning instance
}

function upgradeInstance() {
    console.log('Upgrading instance...');
    // Implementation for upgrading instance
}

// Tunnel import/export functionality
function exportTunnels() {
    const tunnels = [
        {
            targetUrl: 'https://localhost:22',
            tunnelUrl: 'https://aw-nebraska-cultures-availability.trycloudflare.com'
        }
    ];
    
    const dataStr = JSON.stringify(tunnels, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'tunnels.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function importTunnels(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const tunnels = JSON.parse(e.target.result);
            console.log('Imported tunnels:', tunnels);
            // Here you would typically update the UI with the imported tunnels
        } catch (err) {
            console.error('Failed to parse tunnels file:', err);
        }
    };
    reader.readAsText(file);
}

// Logs functionality
function copyLogs() {
    const logsContent = document.querySelector('.logs-viewer').textContent;
    navigator.clipboard.writeText(logsContent).catch(err => {
        console.error('Failed to copy logs:', err);
    });
}

function downloadLogs() {
    const instanceId = document.querySelector('.instance-id').textContent.split(': ')[1];
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${instanceId}_logs_${timestamp}.txt`;
    
    const logsContent = document.querySelector('.logs-viewer').textContent;
    const dataBlob = new Blob([logsContent], { type: 'text/plain' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Handle URL routing on page load and hash changes
function handleRoute() {
    const hash = window.location.hash.slice(2) || 'apps'; // Remove #/ and default to 'apps'
    showPage(`${hash}-page`);
}

// Initialize the app
function init() {
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeApp);
    } else {
        initializeApp();
    }
}

function initializeApp() {
    const grid = document.getElementById('app-grid');
    if (grid) {
        applications.forEach(app => {
            grid.appendChild(createAppCard(app));
        });
    }
    
    // Handle initial route
    handleRoute();

    // Listen for hash changes
    window.addEventListener('hashchange', handleRoute);

    // Start updating system stats
    updateSystemStats();
}

// System stats simulation
function updateSystemStats() {
    // In a real implementation, this would fetch actual system stats
    // For now, we'll just simulate some fluctuation
    setInterval(() => {
        const gpuLoad = 70 + Math.random() * 20;
        const gpuMemory = 6.2 + Math.random() * 0.4;
        const disk = 156 + Math.random() * 2;

        document.querySelector('.stat-item:nth-child(1) .stat-fill').style.width = `${gpuLoad}%`;
        document.querySelector('.stat-item:nth-child(1) .stat-tooltip').textContent = 
            `Load: ${Math.round(gpuLoad)}% | Memory: ${gpuMemory.toFixed(1)}/8 GB`;
        
        document.querySelector('.stat-item:nth-child(2) .stat-fill').style.width = `${77.5}%`;
        document.querySelector('.stat-item:nth-child(2) .stat-tooltip').textContent = 
            `13.4/16 GB (83.75%)`;
        
        document.querySelector('.stat-item:nth-child(3) .stat-fill').style.width = `${(disk/512)*100}%`;
        document.querySelector('.stat-item:nth-child(3) .stat-tooltip').textContent = 
            `${Math.round(disk)}/512 GB (${((disk/512)*100).toFixed(2)}%)`;
    }, 2000);
}

// Start the app
init();