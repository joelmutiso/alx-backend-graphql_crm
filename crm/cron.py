from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    try:
        transport = RequestsHTTPTransport(url='http://localhost:8000/graphql/')
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql('query { hello }')
        client.execute(query)
        
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        message = f"{timestamp} CRM is alive\n"
        
        with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
            f.write(message)
    except Exception:
        pass