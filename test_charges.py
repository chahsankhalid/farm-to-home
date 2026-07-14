from recharge import get_charges
import json

charge = get_charges()["charges"][0]

print(json.dumps(charge, indent=2))