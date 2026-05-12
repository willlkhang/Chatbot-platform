import sqlite3
from pathlib import Path
p = Path(r"c:\All University Materials\Project\ICT304-project\ai\ai_tools\classifier_app\databases\data\resources.db")
conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute('SELECT id, topic, resource FROM resources')
rows = cur.fetchall()
for r in rows[:200]:
    print(r)
print('TOTAL:', len(rows))
conn.close()
