# Project Overview

This is the foundational prototype for an AI Governance Layer designed to intercept and monitor API calls made by and to AI agents. The system acts as a reverse proxy that provides security controls for agentic AI workflows.

## Primary Goal
Build a working interception layer that logs all AI agent API traffic and implements basic security controls to prevent prompt injection attacks.

## What This Prototype Does

The Weekend 1 prototype establishes the core infrastructure:

- **HTTP/HTTPS Reverse Proxy**: Intercepts all traffic between AI agents and LLM APIs (OpenAI, Anthropic, etc.)
- **Request/Response Logging**: Captures detailed audit trails of all agent interactions
- **Basic Pattern Matching**: Detects known prompt injection patterns using regex-based rules
- **Policy Enforcement**: Implements simple allow/deny rules based on content analysis
- **Real-time Dashboard**: Visualizes blocked vs. allowed requests

## Architecture

```
AI Agent Application
        |
        | HTTPS Request
        v
+------------------+
| Governance Layer |
|   (This System)  |
+------------------+
        |
        | 1. Log Request
        | 2. Pattern Match
        | 3. Policy Check
        |
    [ALLOW/DENY]
        |
        v
   LLM API Provider
   (OpenAI/Anthropic)
        |
        | Response
        v
+------------------+
| Governance Layer |
+------------------+
        |
        v
  AI Agent Application
```

## Directory Structure
*(Note: Current structure implemented in prototype)*

```
governance-layer/
├── interceptor.py         # Main proxy interceptor (mitmproxy addon)
├── detection/
│   └── analyzer.py        # Injection detection rules
├── policy/
│   └── blocking.rego      # OPA Policy
├── logs/
│   └── audit.jsonl        # Request/response logs
├── dashboard/
│   ├── app.py             # Streamlit dashboard
│   └── debug_read.py      # Debug utility
├── verification/
│   └── test_proxy.py      # Test suite
└── readme.md
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- mitmproxy

### Setup

```bash
# Clone the repository
git clone https://github.com/Ratneshp1122/AI-Agent-Middleware
cd AI-Agent-Middleware

# Install dependencies
pip install mitmproxy streamlit plotly pandas

# (Optional) Generate self-signed certificates if not using mitmproxy's default
```

## Usage

### Starting the Proxy

```bash
# Start the governance layer proxy
mitmdump -s interceptor.py -p 8080
```
The proxy will listen on `http://127.0.0.1:8080`

### Starting the Dashboard

```bash
# In another terminal, start the dashboard
cd dashboard
streamlit run app.py
```
Open your browser to the URL shown (usually `http://localhost:8501`).

### Configuring Your AI Agent

Point your AI agent to use the governance layer as a proxy.

**Example: Using with OpenAI Python client**

```python
import os
os.environ["HTTP_PROXY"] = "http://127.0.0.1:8080"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:8080"

# Now requests will go through the proxy (ensure SSL verification is handled if using self-signed certs)
```

## Security Features

### Prompt Injection Detection

The system detects common injection patterns:

- **Direct Injection Patterns**: "Ignore previous instructions", "System prompt extraction"
- **Indirect Injection Patterns**: Delimiter attacks

### Policy Rules

Basic OPA-style policies to block specific keywords (e.g., SQL Injection terms like `SELECT`, `DROP`).

## Logging and Audit Trail

All requests are logged in structured JSON format in `logs/audit.jsonl`:

```json
{
  "timestamp": "2026-02-08T14:32:15.123Z",
  "event_type": "request_blocked",
  "url": "http://example.com/api",
  "method": "POST",
  "decision": "BLOCK",
  "metadata": {
    "reason": "SQL Keyword detected: SELECT"
  }
}
```

## Testing

Run the verification script to test the proxy:

```bash
python verification/test_proxy.py
```

## Contributing

This is a research prototype. Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request