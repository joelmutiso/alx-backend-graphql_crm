import requests
from datetime import datetime, timedelta

def send_order_reminders():
    url = 'http://localhost:8000/graphql/'
    
    query = """
    query {
      allOrders {
        id
        orderDate
        customer {
          email
        }
      }
    }
    """
    
    try:
        response = requests.post(url, json={'query': query})
        if response.status_code == 200:
            data = response.json()
            orders = data.get('data', {}).get('allOrders', [])
            
            # Filter for orders from the last 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            log_entries = []
            
            for order in orders:
                try:
                    order_date_str = order['orderDate']
                    # Handle typical ISO date formats
                    if 'T' in order_date_str:
                         order_date = datetime.strptime(order_date_str.split('T')[0], '%Y-%m-%d')
                    else:
                         order_date = datetime.strptime(order_date_str, '%Y-%m-%d')
                         
                    if order_date >= cutoff_date:
                        customer_email = order['customer']['email']
                        order_id = order['id']
                        timestamp = datetime.now().isoformat()
                        log_entries.append(f"{timestamp}: Reminder for Order {order_id} sent to {customer_email}")
                except (ValueError, TypeError):
                    continue

            if log_entries:
                with open('/tmp/order_reminders_log.txt', 'a') as f:
                    for entry in log_entries:
                        f.write(entry + '\n')
            
            print("Order reminders processed!")
        else:
            print(f"Failed to fetch orders: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to localhost:8000. Is the server running?")

if __name__ == '__main__':
    send_order_reminders()