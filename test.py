import sys
print("Python Path:")
for path in sys.path:
    print(path)

try:
    from utils.db import get_db_connection
    print("Import successful!")
except ImportError as e:
    print(f"Import failed: {e}")