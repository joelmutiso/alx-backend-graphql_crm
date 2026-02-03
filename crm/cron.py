from datetime import datetime

def log_crm_heartbeat():
    # Get current time in the specific format: DD/MM/YYYY-HH:MM:SS
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Construct the message
    message = f"{timestamp} CRM is alive\n"
    
    # Append to the log file (mode 'a' for append)
    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write(message)