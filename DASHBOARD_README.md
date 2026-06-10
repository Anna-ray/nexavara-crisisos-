# 🚀 NEXAVARA LABS - Real-Time PQC Crisis Response Dashboard

## Overview

An impressive, modern web-based dashboard for real-time monitoring of the PQC (Post-Quantum Cryptographic) multi-agent system. Built with Flask, WebSockets, and a stunning dark-themed UI with glassmorphism effects.

![Dashboard Status](https://img.shields.io/badge/status-operational-success)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-3.1+-green)
![WebSocket](https://img.shields.io/badge/websocket-enabled-cyan)

## ✨ Features

### Real-Time Monitoring
- **Live Incident Tracking** - Monitor PQC incidents as they occur
- **Agent Status** - Track all 4 specialized agents in real-time
- **Performance Metrics** - Execution time, message processing, system health
- **Audit Trail** - Complete forensic log with download capability
- **WebSocket Updates** - Instant updates without page refresh

### Visual Design
- **Modern Dark Theme** - Professional dark blue/black gradient background
- **Glassmorphism Effects** - Semi-transparent cards with blur effects
- **Animated Components** - Smooth transitions and progress indicators
- **Color-Coded Severity** - Visual severity levels (Critical/High/Medium/Low)
- **Responsive Layout** - Works on desktop, tablet, and mobile

### Dashboard Cards

1. **🚨 Incident Card**
   - Incident ID and description
   - Severity badge (Level 1-5)
   - Source and financial impact
   - Real-time updates

2. **🔬 Analysis Card**
   - Root cause analysis
   - Confidence score
   - Severity assessment
   - Progress indicator

3. **🏢 Coordination Card**
   - Crisis room status
   - Active channels
   - Team count
   - Stakeholder notifications

4. **🎯 Decision Card**
   - Executive recommendations
   - Priority level (P0/P1/P2)
   - Approval requirements
   - Estimated downtime

5. **📊 Metrics Card**
   - Execution time
   - Active agents (4/4)
   - Messages processed
   - System uptime

6. **📝 Audit Trail Card**
   - Live audit log
   - Record count
   - Refresh capability
   - JSON export

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Installation

1. **Install Dependencies**
   ```powershell
   cd multi-agent
   pip install -r requirements.txt
   ```

   Or install individually:
   ```powershell
   pip install flask flask-socketio flask-cors psutil
   ```

2. **Launch Dashboard**
   
   **Option A: Using PowerShell Script (Recommended)**
   ```powershell
   .\run_dashboard.ps1
   ```

   **Option B: Direct Python**
   ```powershell
   python web_dashboard.py
   ```

3. **Access Dashboard**
   
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## 📖 Usage Guide

### Starting a Workflow

1. **Open Dashboard** - Navigate to `http://localhost:5000`
2. **Wait for Connection** - Green "Connected" indicator appears
3. **Click "Start Workflow"** - Initiates the PQC incident simulation
4. **Watch Real-Time Updates** - All cards update automatically
5. **Review Results** - Check audit trail and metrics

### Dashboard Controls

- **▶️ Start Workflow** - Begin PQC incident processing
- **🔄 Reset** - Reload dashboard and clear state
- **🔄 Refresh Audit** - Reload audit trail from file
- **💾 Download Audit** - Export audit trail as JSON

### Status Indicators

- **🟢 Green Dot** - System operational
- **🟡 Yellow Dot** - Initializing/Processing
- **🔴 Red Dot** - Error state

### Severity Levels

- **Level 5 (Critical)** - Red badge, immediate action required
- **Level 4 (High)** - Orange badge, urgent attention needed
- **Level 3 (Medium)** - Yellow badge, monitor closely
- **Level 2-1 (Low)** - Green badge, routine handling

## 🎨 Visual Design

### Color Scheme

- **Background**: Dark blue/black gradient (`#0a0e1a` to `#0f172a`)
- **Cards**: Semi-transparent with backdrop blur
- **Accent Colors**:
  - Cyan (`#06b6d4`) - Primary accent, links, highlights
  - Blue (`#3b82f6`) - Secondary accent, gradients
  - Green (`#10b981`) - Success states
  - Yellow (`#f59e0b`) - Warnings
  - Red (`#ef4444`) - Critical alerts

### Typography

- **Primary Font**: Inter (Google Fonts)
- **Monospace Font**: JetBrains Mono (for code/IDs)
- **Font Weights**: 300-800 for hierarchy

### Animations

- **Background Pulse** - Subtle animated gradient (20s cycle)
- **Status Pulse** - Pulsing status indicators (2s cycle)
- **Progress Shine** - Animated progress bars
- **Card Hover** - Lift effect with glow
- **Toast Slide** - Notification animations

## 🔧 Technical Architecture

### Backend (Flask)

```
web_dashboard.py
├── Flask Application
├── Flask-SocketIO (WebSocket)
├── REST API Endpoints
│   ├── GET /api/status
│   ├── GET /api/metrics
│   ├── GET /api/audit
│   └── GET /api/health
└── Multi-Agent Integration
    ├── Band Client
    ├── Analysis Agent
    ├── Coordination Agent
    ├── Decision Agent
    └── Audit Agent
```

### Frontend

```
static/
├── dashboard.html (Structure)
├── styles.css (Styling)
└── dashboard.js (Logic)
```

### WebSocket Events

**Client → Server:**
- `connect` - Initial connection
- `request_state` - Request current state
- `start_workflow` - Start PQC workflow

**Server → Client:**
- `connection_status` - Connection confirmation
- `state_update` - Full state update
- `incident_update` - Incident data
- `analysis_update` - Analysis results
- `coordination_update` - Coordination state
- `decision_update` - Decision data
- `metrics_update` - Performance metrics
- `audit_update` - Audit records
- `health_update` - System health
- `workflow_status` - Workflow state changes

## 📊 API Endpoints

### GET /api/status
Returns system status and agent information.

**Response:**
```json
{
  "status": "operational",
  "timestamp": "2026-06-10T12:00:00Z",
  "agents": {
    "total": 4,
    "active": 4
  },
  "workflow_running": false
}
```

### GET /api/metrics
Returns performance metrics.

**Response:**
```json
{
  "execution_time": 9.83,
  "agents_active": 4,
  "messages_processed": 12,
  "system_status": "completed"
}
```

### GET /api/audit
Returns audit trail records.

**Response:**
```json
{
  "records": [...],
  "total_count": 12
}
```

### GET /api/health
Returns system health metrics.

**Response:**
```json
{
  "cpu_usage": 25.0,
  "memory_usage": 45.0,
  "response_time": 0,
  "uptime": 120.5
}
```

## 🎯 Key Features Explained

### Real-Time Updates

The dashboard uses WebSocket (Socket.IO) for bidirectional communication:

1. **Connection** - Client connects on page load
2. **State Sync** - Server sends current state
3. **Live Updates** - Server broadcasts changes
4. **Auto-Reconnect** - Handles disconnections gracefully

### Workflow Execution

When you click "Start Workflow":

1. **Initialization** - Band client and agents created
2. **Subscription** - Agents subscribe to topics
3. **Incident Injection** - PQC incident published
4. **Processing** - Agents process in sequence:
   - Analysis Agent (2.5s)
   - Coordination Agent (2.5s)
   - Decision Agent (2.5s)
   - Audit Agent (1s)
5. **Completion** - Results displayed, audit saved

### Audit Trail

The audit trail provides:

- **Immutable Log** - JSONL format (one record per line)
- **Real-Time Display** - Last 10 records shown
- **Full Export** - Download complete trail as JSON
- **Forensic Quality** - Timestamps, agents, actions

## 🔒 Security Considerations

- **Local Deployment** - Runs on localhost by default
- **No Authentication** - Demo purposes only
- **CORS Enabled** - For development flexibility
- **Secret Key** - Set via environment variable

For production:
- Add authentication (Flask-Login, JWT)
- Enable HTTPS
- Restrict CORS origins
- Use production WSGI server (Gunicorn)

## 🐛 Troubleshooting

### Dashboard Won't Start

**Issue**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```powershell
pip install flask flask-socketio flask-cors psutil
```

### WebSocket Not Connecting

**Issue**: Connection status shows "Disconnected"

**Solution**:
1. Check if server is running
2. Verify port 5000 is not blocked
3. Check browser console for errors
4. Try different browser

### Cards Not Updating

**Issue**: Dashboard loads but cards don't update

**Solution**:
1. Click "Start Workflow" button
2. Check browser console for JavaScript errors
3. Verify WebSocket connection (green dot)
4. Refresh page and try again

### Port Already in Use

**Issue**: `Address already in use`

**Solution**:
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

## 📱 Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+
- ✅ Opera 76+

## 🎓 Learning Resources

### Technologies Used

- **Flask** - Python web framework
- **Socket.IO** - WebSocket library
- **HTML5/CSS3** - Modern web standards
- **JavaScript ES6+** - Client-side logic
- **Google Fonts** - Typography

### Recommended Reading

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Socket.IO Documentation](https://socket.io/docs/)
- [CSS Glassmorphism](https://css.glass/)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

## 🤝 Contributing

This dashboard is part of the NEXAVARA LABS PQC Crisis Response System. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

Part of the NEXAVARA LABS project. See main project LICENSE for details.

## 🙏 Acknowledgments

- **Band Protocol** - Message bus architecture
- **Flask Team** - Excellent web framework
- **Socket.IO** - Real-time communication
- **Google Fonts** - Beautiful typography

## 📞 Support

For issues or questions:

1. Check this README
2. Review troubleshooting section
3. Check browser console for errors
4. Review server logs

---

**Made with ❤️ by Bob**

*NEXAVARA LABS - Advancing Post-Quantum Security*