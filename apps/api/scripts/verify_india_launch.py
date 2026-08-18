import sqlite3
import time
import os
import argparse
import re
from groq import Groq
from ddgs import DDGS
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'fone_master.db')

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def search_web(query):
    try:
        results = DDGS().text(query, max_results=1)
        return " ".join([r.get('body', '') for r in results])
    except Exception as e:
        return ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-key', required=True, help="Groq API Key")
    parser.add_argument('--year-start', type=int, default=2024, help="Start year to verify")
    args = parser.parse_args()

    client = Groq(api_key=args.api_key)
    conn = setup_db()
    cursor = conn.cursor()

    brands = ["Samsung", "Apple", "Xiaomi", "Vivo", "Oppo", "Realme", "OnePlus", "iQOO", "Motorola", "Nothing", "Google", "Asus", "Poco", "Honor", "Infinix", "Tecno"]
    placeholders = ','.join(['?'] * len(brands))
    
    # We only verify phones that haven't been verified yet
    query = f"SELECT rowid, brand, name FROM phones WHERE launch_year >= ? AND price_numeric IS NOT NULL AND brand COLLATE NOCASE IN ({placeholders}) AND (ai_verified = 0 OR ai_verified IS NULL) ORDER BY launch_year DESC"
    cursor.execute(query, [args.year_start] + brands)
    rows = cursor.fetchall()

    print(f"Found {len(rows)} phones to verify (Year >= {args.year_start}). Batching in chunks of 10...")
    
    updated_count = 0
    chunk_size = 10
    
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i+chunk_size]
        print(f"\nProcessing batch {i//chunk_size + 1}/{(len(rows) + chunk_size - 1)//chunk_size} (Phones {i+1} to {min(i+chunk_size, len(rows))})")
        
        prompt_parts = [
            "For each of the following smartphones, determine if it has been officially launched and is currently available for purchase in India.",
            "Reply with exactly one word for each ID (YES, NO, or UNRELEASED), formatted exactly as 'ID: RESULT' on each line.",
            "- YES (if officially launched in India)",
            "- NO (if China-exclusive, global-only, or not officially released in India)",
            "- UNRELEASED (if it is rumored, upcoming, or not yet released anywhere)\n"
        ]
        
        for idx, row in enumerate(chunk):
            rowid, brand, name = row
            # Clean duplicate brand prefix in name if present
            clean_name = name.strip()
            if clean_name.lower().startswith(brand.lower()):
                brand_len = len(brand)
                if len(clean_name) > brand_len and clean_name[brand_len] in (' ', '-', '/'):
                    clean_name = clean_name[brand_len:].strip()
                elif len(clean_name) == brand_len:
                    clean_name = ""
            
            phone_name = f"{brand} {clean_name}" if clean_name else brand
            print(f"  Searching DDGS for: {phone_name}")
            search_query = f"Is {phone_name} officially launched and available in India?"
            search_results = search_web(search_query)
            
            prompt_parts.append(f"ID {rowid} ({phone_name}):")
            prompt_parts.append(f"Search Results: {search_results}\n")
            
            time.sleep(1) # Delay to prevent DDGS rate limits
            
        prompt = "\n".join(prompt_parts)
        
        success = False
        retries = 5
        while not success and retries > 0:
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=150
                )
                
                result_text = response.choices[0].message.content.strip()
                lines = result_text.split('\n')
                
                for line in lines:
                    line = line.strip().upper()
                    if ":" in line:
                        parts = line.split(":")
                        try:
                            # Use regex to find the numeric ID in the left part
                            match = re.search(r'(?:ID\s*)?(\d+)', parts[0])
                            if not match:
                                raise ValueError(f"Could not extract numeric ID from '{parts[0]}'")
                            r_id = int(match.group(1))
                            res = parts[1].strip()
                            
                            status = 1 if "YES" in res else 0
                            
                            cursor.execute("UPDATE phones SET released_in_india = ?, ai_verified = 1 WHERE rowid = ?", (status, r_id))
                            updated_count += 1
                            print(f"  Updated ID {r_id} -> {status} ({res})")
                        except Exception as e:
                            print(f"  Failed to parse line '{line}': {e}")
                
                conn.commit()
                success = True
                
                # Sleep between batches to respect Groq limits
                time.sleep(5)
                
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "rate limit" in err_msg.lower() or "rate_limit" in err_msg.lower():
                    print("  Rate limit hit. Waiting 30 seconds before retry...", flush=True)
                    time.sleep(30)
                    retries -= 1
                else:
                    print(f"  Error: {e}")
                    print("  Waiting 10 seconds before retry...")
                    time.sleep(10)
                    retries -= 1
        
        if not success:
            print(f"  Failed to verify batch after multiple retries. Skipping this batch to continue with the next ones.")
                    
    print(f"\nVerification complete. Updated {updated_count} phones.")
    conn.close()

if __name__ == "__main__":
    main()
