import os
import json
import pandas as pd

# Replicate the logic exactly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "..", "logs", "audit.jsonl")

print(f"Script Location: {os.path.abspath(__file__)}")
print(f"Calculated Log Path: {os.path.abspath(LOG_FILE)}")

if not os.path.exists(LOG_FILE):
    print("❌ Log file does not exist!")
    exit(1)

print("✅ Log file found!")

data = []
try:
    with open(LOG_FILE, "r", encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            try:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error decoding line {line_num}: {e}")
                continue
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

print(f"Loaded {len(data)} rows.")
if data:
    df = pd.DataFrame(data)
    print("DataFrame Head:")
    print(df.head())
    print("\nColumns:", df.columns)
else:
    print("Data is empty.")
