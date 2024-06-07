import sqlite3
from config import DB_FILE

print()
print(DB_FILE)
connection = sqlite3.connect(DB_FILE)
connection.close()