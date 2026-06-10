// ============================================================================
// NEXAVARA LABS - Dashboard JavaScript
// Real-time WebSocket updates and interactive UI
// ============================================================================

// Global state
let socket = null;
let workflowRunning = false;
let startTime = null;

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 NEXAVARA LABS Dashboard initializing...');
    
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Setup event listeners
    setupEventListeners();
    
    // Start clock
    updateClock();
    setInterval(updateClock, 1000);
    
    // Hide loading overlay
    setTimeout(() => {
        document.getElementById('loadingOverlay').classList.remove('active');
    }, 1000);
});

// ============================================================================
// WebSocket Connection
// ============================================================================

function initializeWebSocket() {
    console.log('📡 Connecting to WebSocket...');
    
    socket = io({
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5
    });
    
    // Connection events
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('connection_status', handleConnectionStatus);
    
    // Data events
    socket.on('state_update', handleStateUpdate);
    socket.on('incident_update', handleIncidentUpdate);
    socket.on('analysis_update', handleAnalysisUpdate);
    socket.on('coordination_update', handleCoordinationUpdate);
    socket.on('decision_update', handleDecisionUpdate);
    socket.on('metrics_update', handleMetricsUpdate);
    socket.on('audit_update', handleAuditUpdate);
    socket.on('health_update', handleHealthUpdate);
    socket.on('workflow_status', handleWorkflowStatus);
}

function handleConnect() {
    console.log('✅ WebSocket connected');
    updateConnectionStatus(true);
    showToast('Connected to server', 'success');
    
    // Request current state
    socket.emit('request_state');
}

function handleDisconnect() {
    console.log('❌ WebSocket disconnected');
    updateConnectionStatus(false);
    showToast('Disconnected from server', 'error');
}

function handleConnectionStatus(data) {
    console.log('Connection status:', data);
}

function updateConnectionStatus(connected) {
    const dot = document.getElementById('connectionDot');
    const text = document.getElementById('connectionText');
    
    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Start workflow button
    document.getElementById('startWorkflow').addEventListener('click', () => {
        if (!workflowRunning) {
            startWorkflow();
        }
    });
    
    // Reset dashboard button
    document.getElementById('resetDashboard').addEventListener('click', () => {
        if (confirm('Reset dashboard? This will clear all current data.')) {
            resetDashboard();
        }
    });
    
    // Refresh audit button
    document.getElementById('refreshAudit').addEventListener('click', () => {
        refreshAuditTrail();
    });
    
    // Download audit button
    document.getElementById('downloadAudit').addEventListener('click', () => {
        downloadAuditTrail();
    });
}

// ============================================================================
// Workflow Control
// ============================================================================

function startWorkflow() {
    console.log('▶️ Starting workflow...');
    workflowRunning = true;
    startTime = Date.now();
    
    // Update UI
    document.getElementById('startWorkflow').disabled = true;
    document.getElementById('startWorkflow').style.opacity = '0.5';
    
    // Show loading
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.add('active');
    
    // Emit start event
    socket.emit('start_workflow');
    
    showToast('Workflow started', 'info');
}

function resetDashboard() {
    location.reload();
}

// ============================================================================
// State Update Handlers
// ============================================================================

function handleStateUpdate(state) {
    console.log('📊 State update:', state);
    
    if (state.incident) {
        updateIncidentCard(state.incident);
    }
    
    if (state.analysis) {
        updateAnalysisCard(state.analysis);
    }
    
    if (state.coordination) {
        updateCoordinationCard(state.coordination);
    }
    
    if (state.decision) {
        updateDecisionCard(state.decision);
    }
    
    if (state.metrics) {
        updateMetricsCard(state.metrics);
    }
    
    if (state.audit_records && state.audit_records.length > 0) {
        updateAuditTrail(state.audit_records);
    }
}

function handleIncidentUpdate(data) {
    console.log('🚨 Incident update:', data);
    updateIncidentCard(data.incident);
    showToast('Incident detected', 'warning');
}

function handleAnalysisUpdate(data) {
    console.log('🔬 Analysis update:', data);
    updateAnalysisCard(data.analysis);
    showToast('Analysis completed', 'success');
}

function handleCoordinationUpdate(data) {
    console.log('🏢 Coordination update:', data);
    updateCoordinationCard(data.coordination);
    showToast('Coordination updated', 'info');
}

function handleDecisionUpdate(data) {
    console.log('🎯 Decision update:', data);
    updateDecisionCard(data.decision);
    showToast('Decision made', 'success');
}

function handleMetricsUpdate(data) {
    console.log('📊 Metrics update:', data);
    updateMetricsCard(data);
}

function handleAuditUpdate(data) {
    console.log('📝 Audit update:', data);
    if (data.records) {
        updateAuditTrail(data.records);
    }
}

function handleHealthUpdate(data) {
    console.log('💚 Health update:', data);
    // Could update system health indicators here
}

function handleWorkflowStatus(data) {
    console.log('⚙️ Workflow status:', data);
    
    const overlay = document.getElementById('loadingOverlay');
    const statusText = document.getElementById('statusText');
    const statusDot = document.getElementById('statusDot');
    
    switch (data.status) {
        case 'started':
            statusText.textContent = 'RUNNING';
            statusDot.className = 'status-dot running';
            break;
        case 'initializing':
            overlay.querySelector('.loading-text').textContent = 'Initializing agents...';
            break;
        case 'agents_ready':
            overlay.querySelector('.loading-text').textContent = 'Agents ready, injecting incident...';
            break;
        case 'incident_injected':
            overlay.querySelector('.loading-text').textContent = 'Processing incident...';
            break;
        case 'completed':
            overlay.classList.remove('active');
            statusText.textContent = 'COMPLETED';
            statusDot.className = 'status-dot';
            workflowRunning = false;
            document.getElementById('startWorkflow').disabled = false;
            document.getElementById('startWorkflow').style.opacity = '1';
            showToast('Workflow completed successfully', 'success');
            break;
        case 'error':
            overlay.classList.remove('active');
            statusText.textContent = 'ERROR';
            statusDot.className = 'status-dot error';
            workflowRunning = false;
            showToast('Workflow error: ' + (data.error || 'Unknown error'), 'error');
            break;
    }
}

// ============================================================================
// Card Update Functions
// ============================================================================

function updateIncidentCard(incident) {
    document.getElementById('incidentId').textContent = incident.incident_id || 'N/A';
    document.getElementById('incidentDescription').textContent = incident.description || 'No description';
    document.getElementById('incidentSource').textContent = incident.source || 'Unknown';
    
    // Update severity badge
    const severityBadge = document.getElementById('severityBadge');
    const severity = incident.severity_initial || 'unknown';
    severityBadge.textContent = severity.toUpperCase();
    severityBadge.className = 'severity-badge';
    
    // Financial impact (will be updated by analysis)
    document.getElementById('financialImpact').textContent = '$0/min';
}

function updateAnalysisCard(analysis) {
    const content = document.getElementById('analysisContent');
    const progress = document.getElementById('analysisProgress');
    const status = document.getElementById('analysisStatus');
    const confidence = document.getElementById('confidenceScore');
    const severity = document.getElementById('severityLevel');
    
    // Update status
    status.textContent = 'COMPLETED';
    status.className = 'status-badge active';
    
    // Update progress
    progress.style.width = '100%';
    
    // Update content
    const rootCause = analysis.root_cause_hypothesis || 'Analysis in progress...';
    content.innerHTML = `
        <div style="margin-bottom: 1rem;">
            <strong>Root Cause:</strong><br>
            ${rootCause}
        </div>
    `;
    
    // Update metrics
    const confidenceValue = analysis.confidence_score || 0;
    confidence.textContent = `${(confidenceValue * 100).toFixed(0)}%`;
    
    const severityLevel = analysis.severity_level || 'Unknown';
    severity.textContent = severityLevel;
    
    // Update severity badge
    const severityBadge = document.getElementById('severityBadge');
    severityBadge.textContent = severityLevel;
    if (severityLevel.includes('5')) {
        severityBadge.className = 'severity-badge level-5';
    } else if (severityLevel.includes('4')) {
        severityBadge.className = 'severity-badge level-4';
    } else if (severityLevel.includes('3')) {
        severityBadge.className = 'severity-badge level-3';
    }
    
    // Update financial impact
    const financial = analysis.financial_exposure_per_minute || 0;
    document.getElementById('financialImpact').textContent = `$${financial.toLocaleString()}/min`;
}

function updateCoordinationCard(coordination) {
    const crisisRoom = document.getElementById('crisisRoom');
    const status = document.getElementById('coordinationStatus');
    const channelCount = document.getElementById('channelCount');
    const teamCount = document.getElementById('teamCount');
    const stakeholderCount = document.getElementById('stakeholderCount');
    
    // Update status
    status.textContent = 'ACTIVE';
    status.className = 'status-badge active';
    
    // Update crisis room info
    const roomId = coordination.crisis_room_id || 'N/A';
    const channels = coordination.channels_initialized || [];
    const stakeholders = coordination.stakeholders_notified || [];
    
    crisisRoom.innerHTML = `
        <div style="margin-bottom: 0.5rem;">
            <strong>Crisis Room:</strong> ${roomId}
        </div>
        <div style="font-size: 0.875rem; color: var(--text-secondary);">
            <strong>Channels:</strong> ${channels.slice(0, 3).join(', ')}${channels.length > 3 ? '...' : ''}
        </div>
    `;
    
    // Update stats
    channelCount.textContent = channels.length;
    
    // Count unique teams from stakeholders
    const teams = new Set();
    stakeholders.forEach(s => {
        if (s.team) teams.add(s.team);
    });
    teamCount.textContent = teams.size;
    stakeholderCount.textContent = stakeholders.length;
}

function updateDecisionCard(decision) {
    const content = document.getElementById('decisionContent');
    const priorityBadge = document.getElementById('priorityBadge');
    const approvalRequired = document.getElementById('approvalRequired');
    const estimatedDowntime = document.getElementById('estimatedDowntime');
    
    // Update priority badge
    const priority = decision.priority || 'P2';
    priorityBadge.textContent = priority;
    priorityBadge.className = `priority-badge ${priority.toLowerCase()}`;
    
    // Update content
    const recommendation = decision.recommendation || 'Processing...';
    content.innerHTML = `
        <div style="line-height: 1.6;">
            <strong>Executive Recommendation:</strong><br>
            ${recommendation}
        </div>
    `;
    
    // Update metadata
    approvalRequired.textContent = decision.approval_required ? 'Yes' : 'No';
    const downtime = decision.estimated_downtime_minutes || 0;
    estimatedDowntime.textContent = `${downtime} min`;
}

function updateMetricsCard(metrics) {
    const executionTime = document.getElementById('executionTime');
    const agentsActive = document.getElementById('agentsActive');
    const messagesProcessed = document.getElementById('messagesProcessed');
    const systemUptime = document.getElementById('systemUptime');
    const metricsStatus = document.getElementById('metricsStatus');
    
    // Update execution time
    const time = metrics.execution_time || 0;
    executionTime.textContent = `${time.toFixed(2)}s`;
    
    // Update agents
    const active = metrics.agents_active || 0;
    agentsActive.textContent = `${active}/4`;
    
    // Update messages
    messagesProcessed.textContent = metrics.messages_processed || 0;
    
    // Update status
    const status = metrics.system_status || 'initializing';
    metricsStatus.textContent = status.toUpperCase();
    metricsStatus.className = 'status-badge';
    if (status === 'running') {
        metricsStatus.classList.add('processing');
    } else if (status === 'completed') {
        metricsStatus.classList.add('active');
    }
}

function updateAuditTrail(records) {
    const auditLog = document.getElementById('auditLog');
    const recordCount = document.getElementById('recordCount');
    
    if (!records || records.length === 0) {
        auditLog.innerHTML = '<div class="placeholder">No audit records yet...</div>';
        recordCount.textContent = '0 records';
        return;
    }
    
    // Update count
    recordCount.textContent = `${records.length} records`;
    
    // Display last 10 records
    const displayRecords = records.slice(-10).reverse();
    
    auditLog.innerHTML = displayRecords.map(record => {
        const timestamp = new Date(record.timestamp).toLocaleTimeString();
        const agent = record.agent_name || 'System';
        const action = record.action || 'Unknown';
        
        return `
            <div class="audit-record">
                <div style="color: var(--accent-cyan); font-weight: 600;">
                    [${timestamp}] ${agent}
                </div>
                <div style="color: var(--text-secondary); margin-top: 0.25rem;">
                    ${action}
                </div>
            </div>
        `;
    }).join('');
}

// ============================================================================
// Utility Functions
// ============================================================================

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('headerTimestamp').textContent = timeString;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    // Remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 5000);
}

function refreshAuditTrail() {
    fetch('/api/audit')
        .then(response => response.json())
        .then(data => {
            if (data.records) {
                updateAuditTrail(data.records);
                showToast('Audit trail refreshed', 'success');
            }
        })
        .catch(error => {
            console.error('Error refreshing audit trail:', error);
            showToast('Failed to refresh audit trail', 'error');
        });
}

function downloadAuditTrail() {
    fetch('/api/audit')
        .then(response => response.json())
        .then(data => {
            if (data.records) {
                const blob = new Blob([JSON.stringify(data.records, null, 2)], {
                    type: 'application/json'
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `audit_trail_${Date.now()}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                showToast('Audit trail downloaded', 'success');
            }
        })
        .catch(error => {
            console.error('Error downloading audit trail:', error);
            showToast('Failed to download audit trail', 'error');
        });
}

// ============================================================================
// Error Handling
// ============================================================================

window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showToast('An error occurred. Check console for details.', 'error');
});

// ============================================================================
// Console Banner
// ============================================================================

console.log('%c🚀 NEXAVARA LABS', 'font-size: 24px; font-weight: bold; color: #06b6d4;');
console.log('%cPQC Crisis Response Dashboard', 'font-size: 14px; color: #9ca3af;');
console.log('%cReal-time Multi-Agent System Monitoring', 'font-size: 12px; color: #6b7280;');
console.log('');
console.log('Dashboard initialized successfully ✅');
console.log('WebSocket connection: Establishing...');
console.log('');

// Made with Bob