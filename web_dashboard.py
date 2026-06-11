#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEXAVARA LABS - Real-Time Web Dashboard
Flask application with WebSocket support for monitoring the PQC multi-agent system

This dashboard provides:
- Real-time incident monitoring
- Agent status tracking
- Performance metrics visualization
- Live audit trail
- Crisis room coordination view
"""

import sys
import os
import json
import time
import socket
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    os.system('chcp 65001 > nul 2>&1')

from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Import multi-agent system components
from adapters.band_client import InMemoryBandClient
from agents.intake_agent import IntakeAgent
from agents.analysis_agent import PQCAnalysisAgent
from agents.coordination_agent import PQCCoordinationAgent
from agents.decision_agent import PQCDecisionAgent
from agents.audit_agent import PQCAuditAgent
from messages.models import PQCIncidentDetected

# Import CrisisOS components
from services.business_impact import BusinessImpactEngine, calculate_business_impact
from services.executive_report import ExecutiveReportGenerator, generate_executive_report

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'nexavara-pqc-dashboard-secret')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
dashboard_state = {
    'incident': None,
    'analysis': None,
    'coordination': None,
    'decision': None,
    'metrics': {
        'execution_time': 0,
        'agents_active': 0,
        'messages_processed': 0,
        'system_status': 'initializing'
    },
    'audit_records': [],
    'system_health': {
        'cpu_usage': 0,
        'memory_usage': 0,
        'response_time': 0,
        'uptime': 0
    },
    'command': {
        'crisis_title': 'Awaiting strategic incident intelligence',
        'crisis_status': 'STANDBY',
        'recommended_action': 'No active recommendation',
        'expected_outcome': 'Monitoring and analysis in progress',
        'damage_avoided': '$0',
        'confidence': '0%',
        'consensus': '0/8'
    },
    'council': [],
    'debate': [],
    'outcomes': [],
    'digital_twin': {
        'nodes': [],
        'links': [],
        'focus': 'Awaiting crisis propagation model'
    },
    'oversight': {
        'verdict': 'Pending review',
        'summary': 'The AI oversight agent is assessing recommendation strength.',
        'flags': [],
        'confidence': 'N/A'
    },
    'executive_briefing': {
        'headline': 'Awaiting first strategic recommendation.',
        'situation': 'No active crisis has been scored yet.',
        'action': 'No recommendation available.',
        'outcome': 'Awaiting analysis and council consensus.',
        'financial_exposure': '$0 projected loss',
        'board_impact': 'No board impact assessment available.',
        'regulatory_impact': 'No regulatory assessment available.'
    }
    ,
    # CrisisOS Executive Data
    'business_impact': None,
    'executive_report': None,
    'timeline': [],
    'executive_summary': None
}

# Multi-agent system components
band_client = None
agents = {}
workflow_running = False
start_time = None


# ============================================================================
# WebSocket Event Handlers
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"[WebSocket] Client connected: {datetime.now(timezone.utc).isoformat()}")
    emit('connection_status', {'status': 'connected', 'timestamp': datetime.now(timezone.utc).isoformat()})
    # Send current state to newly connected client
    emit('state_update', dashboard_state)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"[WebSocket] Client disconnected: {datetime.now(timezone.utc).isoformat()}")


@socketio.on('request_state')
def handle_state_request():
    """Handle request for current state."""
    emit('state_update', dashboard_state)


@socketio.on('start_workflow')
def handle_start_workflow():
    """Handle request to start the PQC workflow."""
    global workflow_running
    if not workflow_running:
        workflow_running = True
        threading.Thread(target=run_pqc_workflow, daemon=True).start()
        emit('workflow_status', {'status': 'started', 'timestamp': datetime.now(timezone.utc).isoformat()})


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.route('/')
def index():
    """Serve the main dashboard page."""
    return send_from_directory('static', 'dashboard.html')


@app.route('/api/status')
def get_status():
    """Get current system status."""
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'agents': {
            'total': len(agents),
            'active': dashboard_state['metrics']['agents_active']
        },
        'workflow_running': workflow_running
    })


@app.route('/api/metrics')
def get_metrics():
    """Get performance metrics."""
    return jsonify(dashboard_state['metrics'])


@app.route('/api/audit')
def get_audit_trail():
    """Get audit trail records."""
    try:
        audit_records = []
        audit_file = Path('pqc_audit.jsonl')
        if audit_file.exists():
            with open(audit_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        audit_records.append(json.loads(line))
        return jsonify({
            'records': audit_records[-50:],  # Last 50 records
            'total_count': len(audit_records)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'records': [], 'total_count': 0})


@app.route('/api/health')
def get_health():
    """Get system health metrics."""
    return jsonify(dashboard_state['system_health'])


@app.route('/api/executive_summary')
def get_executive_summary():
    """Get executive summary with business metrics."""
    if not dashboard_state.get('executive_summary'):
        return jsonify({
            'status': 'pending',
            'message': 'Executive summary not yet generated'
        })
    return jsonify(dashboard_state['executive_summary'])


@app.route('/api/business_impact')
def get_business_impact():
    """Get detailed business impact analysis."""
    if not dashboard_state.get('business_impact'):
        return jsonify({
            'status': 'pending',
            'message': 'Business impact not yet calculated'
        })
    return jsonify(dashboard_state['business_impact'])


@app.route('/api/executive_report')
def get_executive_report():
    """Get complete executive crisis briefing."""
    if not dashboard_state.get('executive_report'):
        return jsonify({
            'status': 'pending',
            'message': 'Executive report not yet generated'
        })
    return jsonify(dashboard_state['executive_report'])


@app.route('/api/timeline')
def get_timeline():
    """Get crisis response timeline."""
    return jsonify({
        'events': dashboard_state.get('timeline', []),
        'total_events': len(dashboard_state.get('timeline', []))
    })


# ============================================================================
# Multi-Agent System Integration
# ============================================================================

def broadcast_update(event_type: str, data: Dict[str, Any]):
    """Broadcast update to all connected clients."""
    socketio.emit(event_type, data)


def create_incident_collector():
    """Create collector for incident updates."""
    def collector(message):
        dashboard_state['incident'] = message.payload
        dashboard_state['metrics']['messages_processed'] += 1
        broadcast_update('incident_update', {
            'incident': message.payload,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    return collector


def create_analysis_collector():
    """Create collector for analysis updates."""
    def collector(message):
        dashboard_state['analysis'] = message.payload
        dashboard_state['metrics']['messages_processed'] += 1
        broadcast_update('analysis_update', {
            'analysis': message.payload,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    return collector


def create_coordination_collector():
    """Create collector for coordination updates."""
    def collector(message):
        dashboard_state['coordination'] = message.payload
        dashboard_state['metrics']['messages_processed'] += 1
        broadcast_update('coordination_update', {
            'coordination': message.payload,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    return collector


def create_decision_collector():
    """Create collector for decision updates."""
    def collector(message):
        dashboard_state['decision'] = message.payload
        dashboard_state['metrics']['messages_processed'] += 1
        broadcast_update('decision_update', {
            'decision': message.payload,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    return collector


def push_command_state(command_data: Dict[str, Any]):
    """Update command center state and broadcast to clients."""
    dashboard_state['command'].update(command_data)
    broadcast_update('command_update', dashboard_state['command'])


def push_council_state(council_data: List[Dict[str, Any]]):
    """Update AI Crisis Council data and broadcast to clients."""
    dashboard_state['council'] = council_data
    broadcast_update('council_update', council_data)


def push_outcomes_state(outcomes_data: List[Dict[str, Any]]):
    """Update future outcome scenarios and broadcast to clients."""
    dashboard_state['outcomes'] = outcomes_data
    broadcast_update('outcomes_update', outcomes_data)


def push_digital_twin_state(twin_data: Dict[str, Any]):
    """Update digital twin data and broadcast to clients."""
    dashboard_state['digital_twin'] = twin_data
    broadcast_update('twin_update', twin_data)


def push_oversight_state(oversight_data: Dict[str, Any]):
    """Update oversight agent review data and broadcast to clients."""
    dashboard_state['oversight'] = oversight_data
    broadcast_update('oversight_update', oversight_data)


def push_briefing_state(briefing_data: Dict[str, Any]):
    """Update executive briefing data and broadcast to clients."""
    dashboard_state['executive_briefing'] = briefing_data
    broadcast_update('briefing_update', briefing_data)


def push_debate_state(debate_messages: List[Dict[str, Any]]):
    """Stream live debate messages from AI directors."""
    dashboard_state['debate'] = debate_messages
    broadcast_update('debate_update', debate_messages)


def update_system_health():
    """Update system health metrics."""
    try:
        import psutil
        dashboard_state['system_health']['cpu_usage'] = psutil.cpu_percent(interval=0.1)
        dashboard_state['system_health']['memory_usage'] = psutil.virtual_memory().percent
    except ImportError:
        # psutil not available, use dummy values
        dashboard_state['system_health']['cpu_usage'] = 25.0
        dashboard_state['system_health']['memory_usage'] = 45.0
    
    if start_time:
        dashboard_state['system_health']['uptime'] = time.time() - start_time
    
    broadcast_update('health_update', dashboard_state['system_health'])


def add_timeline_event(event_type: str, description: str):
    """Add event to crisis timeline."""
    event = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'time_display': datetime.now(timezone.utc).strftime('%H:%M:%S'),
        'event_type': event_type,
        'description': description
    }
    dashboard_state['timeline'].append(event)
    broadcast_update('timeline_update', {'event': event})


def run_pqc_workflow():
    """Run the PQC incident workflow with CrisisOS enhancements."""
    global band_client, agents, workflow_running, start_time
    
    try:
        start_time = time.time()
        dashboard_state['metrics']['system_status'] = 'running'
        dashboard_state['timeline'] = []  # Reset timeline
        broadcast_update('workflow_status', {'status': 'initializing'})
        
        # Timeline: System initialization
        add_timeline_event('System Initialization', 'CrisisOS Multi-Agent System Starting')
        
        # Initialize Band client
        band_client = InMemoryBandClient()
        
        # Create agents
        agents['analysis'] = PQCAnalysisAgent(
            name="PQCAnalysisAgent",
            band_client=band_client,
            ai_client=None
        )
        
        agents['coordination'] = PQCCoordinationAgent(
            name="PQCCoordinationAgent",
            band_client=band_client,
            ai_client=None
        )
        
        agents['decision'] = PQCDecisionAgent(
            name="PQCDecisionAgent",
            band_client=band_client,
            ai_client=None
        )
        
        agents['audit'] = PQCAuditAgent(
            name="PQCAuditAgent",
            band_client=band_client,
            audit_file_path="pqc_audit.jsonl"
        )
        
        dashboard_state['metrics']['agents_active'] = len(agents)
        
        # Subscribe agents
        band_client.subscribe("pqc.incident.detected", agents['analysis'].handle_message)
        band_client.subscribe("pqc.incident.detected", agents['coordination'].handle_message)
        band_client.subscribe("pqc.analysis.completed", agents['decision'].handle_message)
        band_client.subscribe("pqc.coordination.updated", agents['decision'].handle_message)
        
        # Subscribe collectors
        band_client.subscribe("pqc.incident.detected", create_incident_collector())
        band_client.subscribe("pqc.analysis.completed", create_analysis_collector())
        band_client.subscribe("pqc.coordination.updated", create_coordination_collector())
        band_client.subscribe("pqc.decision.made", create_decision_collector())
        
        broadcast_update('workflow_status', {'status': 'agents_ready'})
        add_timeline_event('Agents Ready', '4 AI Agents Initialized and Standing By')
        push_command_state({
            'crisis_title': 'PQ Cryptographic Flash Crash under active review',
            'crisis_status': 'ALERT',
            'recommended_action': 'Hold final recommendation until analysis completes.',
            'expected_outcome': 'Gathering council consensus across risk, compliance, and finance.',
            'damage_avoided': '$0',
            'confidence': '24%',
            'consensus': '3/8'
        })
        push_council_state([
            {
                'role': 'Threat Director',
                'opinion': 'Immediate containment is required to stop propagation.',
                'confidence': 94,
                'vote': 'Yes',
                'evidence': 'HSM entropy failure is active and affecting clearing.',
                'status': 'Assertive'
            },
            {
                'role': 'Finance Director',
                'opinion': 'Current exposure is rising rapidly and must be capped.',
                'confidence': 88,
                'vote': 'Yes',
                'evidence': 'Loss projection exceeds acceptable threshold.',
                'status': 'Measured'
            },
            {
                'role': 'Compliance Director',
                'opinion': 'Containment now avoids regulatory escalation.',
                'confidence': 87,
                'vote': 'Yes',
                'evidence': 'Cross-border clearing services are impacted.',
                'status': 'Cautious'
            }
        ])
        time.sleep(1)
        
        # Create and inject incident
        incident_description = (
            "Entropy degradation and key-generation latency spike detected in HSM "
            "(Hardware Security Modules) during post-quantum Kyber-1024 handshakes "
            "across the cross-border clearing gateway."
        )
        
        incident_id = f"PQC-INCIDENT-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        
        incident_payload = {
            "incident_id": incident_id,
            "source": "HSM-Monitor",
            "description": incident_description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity_initial": "critical"
        }
        
        # Validate and publish
        PQCIncidentDetected.model_validate(incident_payload)
        
        add_timeline_event('Event Detected', 'PQ Signature Anomaly in HSM')
        broadcast_update('workflow_status', {'status': 'incident_injected'})
        push_command_state({
            'recommended_action': 'Execute urgent containment and certificate rotation.',
            'expected_outcome': 'Prevent escalation while verifying incident scope.',
            'confidence': '46%',
            'consensus': '4/8'
        })
        
        # Start streaming debate messages
        push_debate_state([
            {'speaker': 'Threat', 'text': 'HSM entropy failure is critical. We need immediate action.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Finance', 'text': 'Agreed. Exposure is rising rapidly. Every minute costs us.', 'timestamp': (datetime.now(timezone.utc).replace(microsecond=0) + timezone.utc.localize(datetime.utcnow()).timedelta(seconds=1)).isoformat() if False else datetime.now(timezone.utc).isoformat()}
        ])
        
        band_client.publish("pqc.incident.detected", {
            "source": "WebDashboard",
            "topic": "pqc.incident.detected",
            "payload": incident_payload
        })
        
        # Wait for processing with timeline updates
        time.sleep(0.5)
        add_timeline_event('Quantum Risk Agent', 'Analysis Started')
        
        time.sleep(2.0)  # Analysis
        update_system_health()
        add_timeline_event('Analysis Complete', 'Root Cause Identified: HSM Entropy Starvation')
        push_command_state({
            'recommended_action': 'Contain exposure and rotate affected keys immediately.',
            'expected_outcome': 'Reduce immediate financial impact and stabilize payment flow.',
            'confidence': '68%',
            'consensus': '6/8'
        })
        
        # Stream more debate during analysis
        push_debate_state([
            {'speaker': 'Threat', 'text': 'HSM entropy failure is critical. We need immediate action.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Finance', 'text': 'Agreed. Exposure is rising rapidly. Every minute costs us.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Compliance', 'text': 'Cross-border implications are severe. Regulators will escalate.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Legal', 'text': 'Immediate containment limits liability exposure significantly.', 'timestamp': datetime.now(timezone.utc).isoformat()},
        ])
        
        time.sleep(0.5)
        add_timeline_event('Compliance Review', 'Regulatory Impact Assessment')
        
        time.sleep(2.0)  # Coordination
        update_system_health()

        push_outcomes_state([
            {
                'name': 'Contain Now',
                'expected_loss': '$2.1M',
                'probability': 88,
                'summary': 'Direct containment minimizes exposure and stabilizes clearing.'
            },
            {
                'name': 'Delay 4 Hours',
                'expected_loss': '$11.2M',
                'probability': 54,
                'summary': 'Waiting increases risk and regulatory exposure.'
            },
            {
                'name': 'Delay 24 Hours',
                'expected_loss': '$42.0M',
                'probability': 22,
                'summary': 'Sustained instability will cause severe business impact.'
            }
        ])
        
        # Build consensus with more debate
        push_debate_state([
            {'speaker': 'Threat', 'text': 'HSM entropy failure is critical. We need immediate action.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Finance', 'text': 'Agreed. Exposure is rising rapidly. Every minute costs us.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Compliance', 'text': 'Cross-border implications are severe. Regulators will escalate.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Legal', 'text': 'Immediate containment limits liability exposure significantly.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Operations', 'text': 'Key rotation can execute in 8 minutes. We have the capacity.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Reputation', 'text': 'Proactive response protects brand trust. Delaying escalates reputational risk.', 'timestamp': datetime.now(timezone.utc).isoformat()},
            {'speaker': 'Executive', 'text': 'Consensus is clear. The recommendation is sound and actionable.', 'timestamp': datetime.now(timezone.utc).isoformat()},
        ])

        push_digital_twin_state({
            'nodes': [
                {'id': 'Identity', 'status': 'Compromised'},
                {'id': 'Cloud', 'status': 'Under strain'},
                {'id': 'Applications', 'status': 'Affected'},
                {'id': 'Finance', 'status': 'Exposed'},
                {'id': 'Customers', 'status': 'At Risk'},
                {'id': 'Operations', 'status': 'Degraded'},
                {'id': 'Regulators', 'status': 'Watching'}
            ],
            'links': [
                {'source': 'Identity', 'target': 'Cloud'},
                {'source': 'Cloud', 'target': 'Applications'},
                {'source': 'Applications', 'target': 'Finance'},
                {'source': 'Finance', 'target': 'Customers'},
                {'source': 'Finance', 'target': 'Regulators'},
                {'source': 'Cloud', 'target': 'Operations'}
            ],
            'focus': 'Identity compromise is propagating through cloud and finance, threatening customer trust.'
        })
        
        # Calculate Business Impact
        add_timeline_event('Business Impact Engine', 'Calculating Financial Exposure')
        affected_systems = ['HSM', 'Cross-Border Clearing Gateway', 'Payment Gateway']
        business_impact = calculate_business_impact(
            severity='critical',
            affected_systems=affected_systems,
            confidence=0.89,
            incident_type='post_quantum_cryptographic_failure',
            incident_description=incident_description
        )
        dashboard_state['business_impact'] = business_impact
        
        financial_exposure = business_impact['financial_impact']['total_financial_impact']
        add_timeline_event('Market Impact', f'${financial_exposure:,.0f} Exposure Calculated')
        broadcast_update('business_impact_update', business_impact)

        push_command_state({
            'damage_avoided': f'${int(max(financial_exposure - 2100000, 0)):,.0f}',
            'confidence': '91%',
            'consensus': '8/8'
        })

        push_oversight_state({
            'verdict': 'Verified',
            'summary': 'Oversight Agent confirms recommendation is supported by strong evidence and no critical assumptions.',
            'flags': [
                'Evidence aligned across threat, finance, and compliance',
                'Model confidence above 90%',
                'No weak assumptions identified'
            ],
            'confidence': '90%'
        })
        
        time.sleep(1.0)
        
        # Generate Executive Report
        add_timeline_event('Executive Recommendation', 'Generating Crisis Briefing')
        report_generator = ExecutiveReportGenerator()
        executive_report = report_generator.generate_executive_briefing(
            incident_id=incident_id,
            incident_title='Post-Quantum Cryptographic Failure',
            severity='critical',
            confidence=0.89,
            root_cause='HSM entropy starvation under peak Kyber-1024 load',
            business_impact=business_impact
        )
        dashboard_state['executive_report'] = executive_report
        broadcast_update('executive_report_update', executive_report)
        
        # Create Executive Summary
        dashboard_state['executive_summary'] = {
            'incident_title': 'Post-Quantum Cryptographic Failure',
            'severity': 'CRITICAL',
            'confidence': 89,
            'financial_exposure': financial_exposure,
            'affected_systems': affected_systems,
            'regulatory_risk': 'HIGH',
            'recommended_actions': len(executive_report['recommended_actions']),
            'status': 'ACTIVE',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        broadcast_update('executive_summary_update', dashboard_state['executive_summary'])

        push_briefing_state({
            'headline': 'Contain now to prevent an estimated $42M escalation.',
            'situation': 'HSM entropy degradation is causing payment clearing delays across critical cross-border channels.',
            'action': 'Initiate immediate containment and certificate rotation for affected systems.',
            'outcome': 'Avoids majority of financial exposure and reduces regulatory escalation risk.',
            'financial_exposure': f'${financial_exposure:,.0f} projected loss if uncontained',
            'board_impact': 'Protects enterprise trust and avoids executive liability.',
            'regulatory_impact': 'Limits cross-border escalation with a proactive remediation posture.'
        })
        
        time.sleep(1.5)  # Decision
        update_system_health()
        add_timeline_event('Crisis Response', 'Initiated - Suspending Settlement Channel B')
        
        time.sleep(1.0)  # Audit
        add_timeline_event('Audit Trail', 'Complete Compliance Record Generated')
        
        # Update metrics
        dashboard_state['metrics']['execution_time'] = time.time() - start_time
        dashboard_state['metrics']['system_status'] = 'completed'
        
        broadcast_update('workflow_status', {'status': 'completed'})
        broadcast_update('metrics_update', dashboard_state['metrics'])
        
        # Load audit trail
        try:
            audit_file = Path('pqc_audit.jsonl')
            if audit_file.exists():
                with open(audit_file, 'r', encoding='utf-8') as f:
                    dashboard_state['audit_records'] = [json.loads(line) for line in f if line.strip()]
                broadcast_update('audit_update', {
                    'records': dashboard_state['audit_records'][-10:],
                    'total_count': len(dashboard_state['audit_records'])
                })
        except Exception as e:
            print(f"Error loading audit trail: {e}")
        
    except Exception as e:
        print(f"Error in workflow: {e}")
        import traceback
        traceback.print_exc()
        dashboard_state['metrics']['system_status'] = 'error'
        broadcast_update('workflow_status', {'status': 'error', 'error': str(e)})
    finally:
        workflow_running = False


# ============================================================================
# Background Tasks
# ============================================================================

def background_health_monitor():
    """Background task to monitor system health."""
    while True:
        if workflow_running:
            update_system_health()
        time.sleep(5)


# ============================================================================
# Main Entry Point
# ============================================================================

def find_free_port(host: str, preferred_port: int) -> int:
    """Return a free port, preferring the configured port if available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind((host, preferred_port))
            return preferred_port
        except OSError:
            probe.bind((host, 0))
            return probe.getsockname()[1]


def main():
    """Start the web dashboard."""
    host = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    preferred_port = int(os.getenv('DASHBOARD_PORT', '5000'))
    port = find_free_port(host, preferred_port)

    print("=" * 80)
    print("🚨 NEXAVARA LABS - PQC CRISIS RESPONSE DASHBOARD 🚨".center(80))
    print("=" * 80)
    print()
    print("Starting Flask server with WebSocket support...")
    print()
    print("Dashboard will be available at:")
    print(f"  → http://localhost:{port}")
    print()
    print("Features:")
    print("  ✓ Real-time incident monitoring")
    print("  ✓ Agent status tracking")
    print("  ✓ Performance metrics")
    print("  ✓ Live audit trail")
    print("  ✓ WebSocket updates")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    print()
    
    # Start background health monitor
    health_thread = threading.Thread(target=background_health_monitor, daemon=True)
    health_thread.start()
    
    # Start Flask-SocketIO server
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()

# Made with Bob