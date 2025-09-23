import sqlite3
import pandas as pd
import os
from datetime import date, datetime

os.system('clear')
con = sqlite3.connect("/Users/bbageon/Downloads/database.sqlite")
try:
    result = pd.read_sql_query("""
        select reactionUser, rp.postUser
from (
	(select reactionUser, postUser
	from (
		select p.user_id as postUser, r.user_id as reactionUser, count(*)
		from posts p 
		inner join reactions r on p.id = r.post_id
		group by reactionUser, postUser
		having count(*) >= 5
	)) as rp
left outer join
	(select commentUser, postUser
	from (
		select p.user_id as postUser, c.user_id as commentUser
		from posts p 
		inner join comments c on p.id = c.post_id
		group by commentUser, postUser
	)) as cp 
	on rp.reactionUser = cp.commentUser and rp.postUser  = cp.postUser
	)
	where commentUser is null
    """)
except Exception as e:
    print("query failed", e)

