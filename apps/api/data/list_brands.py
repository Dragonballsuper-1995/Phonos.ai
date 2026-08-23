import sqlite3

def main():
    conn = sqlite3.connect('C:/Users/sujal/Documents/Projects/Phonos.ai/apps/api/data/phonos_ai.db')
    cursor = conn.cursor()
    cursor.execute('SELECT brand, COUNT(*) FROM phones GROUP BY brand ORDER BY brand COLLATE NOCASE')
    results = cursor.fetchall()
    
    print(f"Total distinct brands: {len(results)}")
    print("----------------------------------------")
    for brand, count in results:
        print(f"{brand} ({count} phones)")

if __name__ == '__main__':
    main()
