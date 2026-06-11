const socket = io({
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 10
});

const state = {
    command: {},
    council: [],
    debate: [],
    outcomes: [],
    twin: {},
    oversight: {},
    briefing: {}
};

function $(id) {
    return document.getElementById(id);
}

function init() {
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('state_update', handleStateUpdate);
    socket.on('command_update', handleCommandUpdate);
    socket.on('council_update', handleCouncilUpdate);
    socket.on('debate_update', handleDebateUpdate);
    socket.on('outcomes_update', handleOutcomesUpdate);
    socket.on('twin_update', handleTwinUpdate);
    socket.on('oversight_update', handleOversightUpdate);
    socket.on('briefing_update', handleBriefingUpdate);
    socket.on('workflow_status', handleWorkflowStatus);

    $('startWorkflow').addEventListener('click', () => {
        socket.emit('start_workflow');
        setButtonLoading(true);
    });

    // Setup tab switching
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            switchTab(tab);
        });
    });

    updateConnection(false);
}

function handleConnect() {
    updateConnection(true);
    showToast('Connected to CrisisOS', 'success');
    socket.emit('request_state');
}

function handleDisconnect() {
    updateConnection(false);
    showToast('Connection lost. Reconnecting...', 'warning');
}

function switchTab(tabName) {
    // Update button active states
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    if (tabName === 'members') {
        $('councilList').classList.add('active');
    } else if (tabName === 'debate') {
        $('debateStream').classList.add('active');
    }
}


    if (payload.command) handleCommandUpdate(payload.command);
    if (payload.council) handleCouncilUpdate(payload.council);
    if (payload.outcomes) handleOutcomesUpdate(payload.outcomes);
    if (payload.digital_twin) handleTwinUpdate(payload.digital_twin);
    if (payload.oversight) handleOversightUpdate(payload.oversight);
    if (payload.executive_briefing) handleBriefingUpdate(payload.executive_briefing);
}

function handleCommandUpdate(command) {
    state.command = command;
    $('crisisTitle').textContent = command.crisis_title;
    $('crisisSummary').textContent = command.crisis_summary || 'The AI council is evaluating incident impact and recommendation trade-offs.';
    $('recommendedAction').textContent = command.recommended_action;
    $('expectedOutcome').textContent = command.expected_outcome;
    $('damageAvoided').textContent = command.damage_avoided;
    $('confidenceValue').textContent = command.confidence;
    $('consensusValue').textContent = command.consensus;
    $('crisisStatus').textContent = command.crisis_status;
    $('crisisStatus').className = `status-chip status-${command.crisis_status.toLowerCase().replace(/\s+/g, '-')}`;
}

function getDirectorIcon(role) {
    const roleMap = {
        'threat': '⚠️',
        'finance': '💰',
        'compliance': '⚖️',
        'legal': '📋',
        'operations': '⚙️',
        'reputation': '🎯',
        'executive': '👔',
        'oversight': '🔍'
    };
    return roleMap[role.toLowerCase()] || '👤';
}

function handleCouncilUpdate(council) {
    state.council = council;
    const container = $('councilList');
    container.innerHTML = '';
    if (!council || council.length === 0) {
        container.innerHTML = '<div class="panel-empty">No council data yet.</div>';
        return;
    }

    council.forEach(member => {
        const card = document.createElement('div');
        card.className = 'council-card';
        const icon = getDirectorIcon(member.role);
        card.innerHTML = `
            <div class="council-card-header">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.4em;">${icon}</span>
                    <div>
                        <div class="council-role">${member.role}</div>
                        <div class="council-status ${member.vote.toLowerCase()}">${member.vote}</div>
                    </div>
                </div>
                <div class="confidence-pill">${member.confidence}%</div>
            </div>
            <div class="council-opinion">${member.opinion}</div>
            <div class="council-evidence">${member.evidence}</div>
            <div class="council-tag">${member.status}</div>
        `;
        container.appendChild(card);
    });
}

function handleDebateUpdate(debateMessages) {
    if (!debateMessages) return;
    state.debate = Array.isArray(debateMessages) ? debateMessages : [debateMessages];
    
    const container = $('debateStream');
    container.innerHTML = '';
    
    if (state.debate.length === 0) {
        container.innerHTML = '<div class="panel-empty">Debate stream will appear here.</div>';
        return;
    }
    
    state.debate.forEach(msg => {
        const msgEl = document.createElement('div');
        msgEl.className = 'debate-message';
        const timestamp = new Date(msg.timestamp || Date.now()).toLocaleTimeString();
        msgEl.innerHTML = `
            <div class="debate-speaker">${getDirectorIcon(msg.speaker)} ${msg.speaker}</div>
            <div class="debate-text">${msg.text}</div>
            <div class="debate-timestamp">${timestamp}</div>
        `;
        container.appendChild(msgEl);
    });
    
    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function handleOutcomesUpdate(outcomes) {
    state.outcomes = outcomes;
    const container = $('scenarioList');
    container.innerHTML = '';
    if (!outcomes || outcomes.length === 0) {
        container.innerHTML = '<div class="panel-empty">Awaiting scenario simulation.</div>';
        return;
    }

    outcomes.forEach((scenario, index) => {
        const card = document.createElement('div');
        card.className = `scenario-card ${index === 0 ? 'primary' : ''}`;
        card.innerHTML = `
            <div class="scenario-label">${scenario.name}</div>
            <div class="scenario-loss">${scenario.expected_loss}</div>
            <div class="scenario-probability">Probability ${scenario.probability}%</div>
            <div class="scenario-summary">${scenario.summary}</div>
            <button class="scenario-action">Select</button>
        `;
        container.appendChild(card);
    });
}

function handleTwinUpdate(twin) {
    state.twin = twin;
    const canvas = $('twinCanvas');
    
    if (!twin || !twin.nodes || twin.nodes.length === 0) {
        canvas.innerHTML = '<div class="twin-empty">Digital Twin is initializing.</div>';
        return;
    }

    // Use existing SVG or create new one
    let svg = canvas.querySelector('svg.twin-graph-svg');
    if (!svg) {
        svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'twin-graph-svg');
        svg.setAttribute('viewBox', '0 0 480 400');
        svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
        
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        // Add gradients and filters
        defs.innerHTML = `
            <filter id="node-shadow">
                <feDropShadow dx="0" dy="0" stdDeviation="3" flood-opacity="0.5"/>
            </filter>
            <linearGradient id="edge-active" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#36d9ff;stop-opacity:0" />
                <stop offset="50%" style="stop-color:#36d9ff;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#36d9ff;stop-opacity:0" />
            </linearGradient>
            <linearGradient id="edge-at-risk" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#ffb85c;stop-opacity:0" />
                <stop offset="50%" style="stop-color:#ffb85c;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#ffb85c;stop-opacity:0" />
            </linearGradient>
            <linearGradient id="edge-critical" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#ff5f73;stop-opacity:0" />
                <stop offset="50%" style="stop-color:#ff5f73;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#ff5f73;stop-opacity:0" />
            </linearGradient>
        `;
        svg.appendChild(defs);
        
        const edgesContainer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        edgesContainer.setAttribute('class', 'edges-container');
        edgesContainer.setAttribute('id', 'edgesContainer');
        svg.appendChild(edgesContainer);
        
        const nodesContainer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        nodesContainer.setAttribute('class', 'nodes-container');
        nodesContainer.setAttribute('id', 'nodesContainer');
        svg.appendChild(nodesContainer);
        
        canvas.innerHTML = '';
        canvas.appendChild(svg);
    }

    // Position nodes in a circular layout
    const positions = {};
    const nodeCount = twin.nodes.length;
    const centerX = 240;
    const centerY = 200;
    const radius = 120;
    
    twin.nodes.forEach((node, index) => {
        const angle = (index / nodeCount) * Math.PI * 2;
        positions[node.id] = {
            x: centerX + Math.cos(angle) * radius,
            y: centerY + Math.sin(angle) * radius
        };
    });

    // Render edges
    const edgesContainer = $('edgesContainer');
    edgesContainer.innerHTML = '';
    
    if (twin.links && twin.links.length > 0) {
        twin.links.forEach((link, idx) => {
            const source = positions[link.source];
            const target = positions[link.target];
            
            if (source && target) {
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', source.x);
                line.setAttribute('y1', source.y);
                line.setAttribute('x2', target.x);
                line.setAttribute('y2', target.y);
                line.setAttribute('stroke', '#36d9ff');
                line.setAttribute('stroke-width', '1.5');
                
                // Determine edge severity and animation
                const sourceNode = twin.nodes.find(n => n.id === link.source);
                const status = sourceNode?.status?.toLowerCase() || 'standby';
                line.setAttribute('class', `edge ${status === 'compromised' ? 'critical' : status === 'exposed' ? 'active' : status === 'at-risk' ? 'at-risk' : 'standby'}`);
                
                // Set animation delay for sequential propagation
                line.style.animationDelay = `${idx * 0.1}s`;
                edgesContainer.appendChild(line);
            }
        });
    }

    // Render nodes
    const nodesContainer = $('nodesContainer');
    nodesContainer.innerHTML = '';
    
    twin.nodes.forEach((node, idx) => {
        const pos = positions[node.id];
        const statusLower = node.status?.toLowerCase() || 'standby';
        
        // Create circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', pos.x);
        circle.setAttribute('cy', pos.y);
        circle.setAttribute('r', '14');
        circle.setAttribute('class', `node ${statusLower}`);
        circle.setAttribute('filter', 'url(#node-shadow)');
        circle.style.animationDelay = `${idx * 0.08}s`;
        nodesContainer.appendChild(circle);
        
        // Create label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', pos.x);
        text.setAttribute('y', pos.y + 28);
        text.setAttribute('class', 'node-status');
        text.setAttribute('fill', '#08c1ff');
        text.setAttribute('font-family', 'Inter, sans-serif');
        text.textContent = node.id;
        text.style.animationDelay = `${idx * 0.08}s`;
        nodesContainer.appendChild(text);
    });
    
    // Add focus description
    let focusDiv = canvas.querySelector('.twin-focus');
    if (!focusDiv) {
        focusDiv = document.createElement('div');
        focusDiv.className = 'twin-focus';
        canvas.appendChild(focusDiv);
    }
    focusDiv.textContent = twin.focus || 'Crisis propagation model is computing...';
}

function handleOversightUpdate(oversight) {
    state.oversight = oversight;
    $('oversightSummary').textContent = oversight.summary;
    $('oversightVerdict').textContent = oversight.verdict;
    $('oversightConfidence').textContent = oversight.confidence;
    const flags = $('oversightFlags');
    flags.innerHTML = '';
    if (oversight.flags && oversight.flags.length > 0) {
        oversight.flags.forEach(flag => {
            const chip = document.createElement('span');
            chip.className = 'flag';
            chip.textContent = flag;
            flags.appendChild(chip);
        });
    }
}

function handleBriefingUpdate(briefing) {
    state.briefing = briefing;
    $('briefingHeadline').textContent = briefing.headline;
    $('briefingSituation').textContent = briefing.situation;
    $('briefingAction').textContent = briefing.action;
    $('briefingOutcome').textContent = briefing.outcome;
    $('briefingFinancial').textContent = briefing.financial_exposure;
    $('briefingBoard').textContent = briefing.board_impact;
    $('briefingRegulatory').textContent = briefing.regulatory_impact;
}

function handleWorkflowStatus(status) {
    if (!status || !status.status) return;
    if (status.status === 'completed') {
        setButtonLoading(false);
        showToast('Crisis response completed.', 'success');
    }
    if (status.status === 'error') {
        setButtonLoading(false);
        showToast('Workflow error occurred.', 'error');
    }
}

function updateConnection(connected) {
    const text = $('connectionText');
    text.textContent = connected ? 'online' : 'offline';
    text.className = connected ? 'connection-online' : 'connection-offline';
}

function setButtonLoading(active) {
    const button = $('startWorkflow');
    button.disabled = active;
    button.classList.toggle('button-loading', active);
    button.textContent = active ? 'PROCESSING…' : 'LAUNCH CRISIS RESPONSE';
}

function showToast(message, type = 'info') {
    const container = $('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('expired');
        setTimeout(() => container.removeChild(toast), 300);
    }, 4000);
}

window.addEventListener('DOMContentLoaded', init);
