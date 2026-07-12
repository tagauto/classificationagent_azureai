import re
line = 'Amount Due: $1250.00'
pattern = r'amount due[:\s]+\$?([0-9,]+(?:\.\d{1,2})?)'
m = re.search(pattern, line, re.IGNORECASE)
print(m.group(1) if m else None)
