import sys
import os
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def send_order_reminders():
    url = 'http://localhost:8000/graphql/'
    transport = RequestsHTTPTransport(url=url)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query {
      allOrders {
        id
        orderDate
        customer {
          email
        }
      }
    }
    """)

    try:
        result = client.execute(query)
        orders = result.get('allOrders', [])
        cutoff_date = datetime.now() - timedelta(days=7)
        log_entries = []

        for order in orders:
            try:
                order_date_str = order['orderDate']
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

    except Exception as e:
        print(f"Error fetching orders: {e}")

if __name__ == '__main__':
    send_order_reminders()