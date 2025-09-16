import sqlite3
import pandas as pd
import os

# ------ Exercise 1.1 ------
os.system('clear')
con = sqlite3.connect("/Users/bbageon/Downloads/database.sqlite")

tablenames_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", con)
# print(tablenames_df)

for table in tablenames_df.name:
    tablerows_df = pd.read_sql_query(f"SELECT * FROM {table};", con)
    rows_num = pd.read_sql_query(f"SELECT COUNT(*) as rowNum FROM {table}", con)
    print(table)
    print(tablerows_df)
    print("rows : " , rows_num["rowNum"].iloc[0])
    print(" ")

    colinfo_df = pd.read_sql_query(f"PRAGMA table_info({table});", con)
    print("Columns info:")
    print(colinfo_df)

# ------ Exercise 1.2 ------

try:
    result = pd.read_sql_query(
        """ select count(*)
        from users
        where id not in (select user_id from posts) 
        and id not in (select user_id from reactions)"""
    ,con)

    print(result)
except Exception as e:
    print("Query failed", e)


# ------ Exercise 1.3 ------

try:
    result = pd.read_sql_query(
        """SELECT u.id, u.username,
        SUM(
        (select count(*) from reactions r where p.id = r.post_id)+
        (select count(*) from comments c where p.id = c.post_id)
        )  as Engagement,
        100.0 * SUM(
        (SELECT COUNT(*) FROM reactions r WHERE r.post_id = p.id) +
        (SELECT COUNT(*) FROM comments  c WHERE c.post_id = p.id))/
        NULLIF((SELECT COUNT(*) FROM follows f WHERE f.followed_id = u.id),0
        ) AS ER_Post
        FROM users u INNER JOIN posts p ON u.id = p.user_id
        GROUP by u.id
        order by ER_Post desc
        LIMIT 5;
        """
    ,con)
    print(result)
except Exception as e:
    print("Query failed", e)


# ------ Exercise 1.4 ------ 

try:
    result = pd.read_sql_query(
        """select user_id, content, count(*)
        from (
        select user_id, content from comments
        union ALL
        select user_id, content from posts 
        )
        GROUP by user_id, content
        HAVING count(*) >= 3"""
    ,con)
    print(result)
except Exception as e:
    print("Query failed", e)
