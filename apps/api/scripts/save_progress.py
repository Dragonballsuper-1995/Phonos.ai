import sqlite3
import re
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'fone_master.db')
LOG_PATH = r"C:\Users\sujal\.gemini\antigravity-cli\brain\cd6941ad-b51f-4bc0-8be4-3f7f8d4dc917\.system_generated\tasks\task-379.log"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create column if not exists
    try:
        cursor.execute("ALTER TABLE phones ADD COLUMN ai_verified INTEGER DEFAULT 0")
        print("Added ai_verified column.")
    except sqlite3.OperationalError:
        print("ai_verified column already exists.")

    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        log_content = f.read()
        
    # Regex to find "Updated ID 1234"
    matches = re.findall(r'Updated ID (\d+)', log_content)
    
    print(f"Found {len(matches)} updated IDs in the log.")
    
    for rowid in matches:
        cursor.execute("UPDATE phones SET ai_verified = 1 WHERE rowid = ?", (rowid,))
        
    conn.commit()
    print("Database updated with ai_verified statuses.")
    conn.close()

if __name__ == "__main__":
    main()
