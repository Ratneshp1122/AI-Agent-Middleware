from mitmproxy import http
import json
import datetime
import os
import logging
import sys

# Ensure we can import from the sibling detection directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from detection import analyzer
except ImportError:
    # If running with mitmproxy, the path might need adjustment or detection folder might be missing
    analyzer = None
    logging.error("Could not import detection.analyzer")

# Setup logging
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "audit.jsonl")

# Ensure logs directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log_event(event_type, flow: http.HTTPFlow, decision="ALLOW", metadata=None):
    """
    Logs the event to a JSONL file.
    """
    try:
        # Extract basic info
        url = flow.request.pretty_url
        method = flow.request.method
        
        # Try to decode body if present
        request_body = None
        if flow.request.content:
            try:
                request_body = flow.request.content.decode('utf-8')
            except:
                request_body = "[Binary Content]"

        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "url": url,
            "method": method,
            "request_body_preview": request_body[:500] if request_body else None,
            "decision": decision,
            "metadata": metadata or {}
        }
        
        with open(LOG_FILE, "a", encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
            
    except Exception as e:
        logging.error(f"Failed to log event: {e}")

class AIInterceptor:
    def __init__(self):
        print("AIInterceptor loaded...")

    def request(self, flow: http.HTTPFlow):
        """
        Intercepts HTTP requests.
        """
        request_body = ""
        if flow.request.content:
            try:
                request_body = flow.request.content.decode('utf-8', 'ignore')
            except:
                pass
        
        # 1. Detection Analysis
        if analyzer:
            is_threat, reason = analyzer.analyze_text(request_body)
            
            if is_threat:
                print(f"Blocking request: {reason}")
                log_event("request_blocked", flow, decision="BLOCK", metadata={"reason": reason, "full_body": request_body})
                
                # Return 403 Forbidden
                flow.response = http.Response.make(
                    403,
                    b"Request blocked by AI Security Middleware: " + reason.encode(),
                    {"Content-Type": "text/plain"}
                )
                return

        # 2. OPA Policy Check (Optional integration point)
        # logic to call OPA binary would go here

        log_event("request_allowed", flow, decision="ALLOW")

addons = [
    AIInterceptor()
]
