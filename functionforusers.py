import sqlite3

def authenticate_user(username, password):
    """בודקת אם שם המשתמש והסיסמה קיימים במסד הנתונים ומחזירה את נתוני השחקן אם כן"""
    conn = sqlite3.connect('DATABASE_GAME.db')  # התחברות למסד הנתונים
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE username = ? AND password = ?", (username, password))
    player_data = cursor.fetchone()  # מחזיר את הנתונים של השחקן אם קיים

    conn.close()

    if player_data:
        return True, player_data  # השחקן קיים, מחזירים True ואת המידע שלו
    else:
        return False, None  # השחקן לא קיים

# דוגמה לשימוש:
exists, data = authenticate_user("player1", "securepass123")
if exists:
    print("✅ משתמש קיים! הנתונים שלו:", data)
else:
    print("❌ שם משתמש או סיסמה שגויים")
