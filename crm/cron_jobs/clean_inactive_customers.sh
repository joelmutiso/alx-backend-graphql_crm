#!/bin/bash

# Navigate to the project root (assuming script is in crm/cron_jobs/)
cd "$(dirname "$0")/../.."

# Run Python code inside the Django shell
output=$(python3 manage.py shell <<EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Calculate the cutoff date (1 year ago)
one_year_ago = timezone.now() - timedelta(days=365)

# Logic: Delete customers who do NOT have any orders created after the cutoff date
# .exclude(orders__created_at__gte=one_year_ago) finds customers with no recent orders
count, _ = Customer.objects.exclude(orders__created_at__gte=one_year_ago).delete()

print(count)
EOF
)

# Log the result with a timestamp
echo "$(date): Deleted $output customers" >> /tmp/customer_cleanup_log.txt