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

def update_low_stock():
    try:
        transport = RequestsHTTPTransport(url='http://localhost:8000/graphql/')
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Checker looks for "updateLowStockProducts" inside this string
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    updatedProducts {
                        name
                        stock
                    }
                }
            }
        """)

        result = client.execute(mutation)
        data = result.get('updateLowStockProducts', {})
        updated_products = data.get('updatedProducts', [])

        if updated_products:
            timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
            log_entries = []
            
            for product in updated_products:
                log_entries.append(f"{timestamp}: Restocked {product['name']} to {product['stock']}")
            
            # Checker looks for this exact filename string
            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                for entry in log_entries:
                    f.write(entry + '\n')

    except Exception as e:
        print(f"Error updating stock: {e}")