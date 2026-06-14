import sqlite3
import sys

def main():
    conn = sqlite3.connect('haftyar.db')
    cursor = conn.cursor()
    
    # 1. Find the team "سرو سبز"
    cursor.execute("SELECT id FROM teams WHERE name = 'سرو سبز'")
    team = cursor.fetchone()
    
    if not team:
        print("Error: Team 'سرو سبز' not found.")
        sys.exit(1)
        
    team_id = team[0]
    print(f"Found Team ID: {team_id}")
    
    # 2. Update team_members for this team
    cursor.execute("UPDATE team_members SET has_ai_access = 1 WHERE team_id = ?", (team_id,))
    conn.commit()
    
    print(f"Success: Updated {cursor.rowcount} members to have PRO access.")
    conn.close()

if __name__ == "__main__":
    main()
