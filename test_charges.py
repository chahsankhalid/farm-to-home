from recharge import get_customer
import json

print(json.dumps(get_customer(236000361), indent=2))