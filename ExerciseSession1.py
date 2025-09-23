import sqlite3
import pandas as pd
import os
from datetime import date, datetime

# cur = con.cursor()
# cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
# result = cur.fetchall()
# print(result)
# print(len(result))

# for i in result:
#     table_name = i[0]
#     # print(table_name)
#     cur.execute(f"SELECT * FROM {table_name} LIMIT 5;")
#     rows = cur.fetchall()

#     print(table_name)
#     print(rows)
#     print(" ")

os.system("clear")
con = sqlite3.connect("/Users/bbageon/Downloads/database.sqlite")

# ---------------Exercise1 ---------------------------------

tablenames_df = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table';", con
)
# print(tablenames_df)

for table in tablenames_df.name:
    tablerows_df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5;", con)
    # print(table)
    # print(tablerows_df)
    # print(" ")

# -----------------Exercise 2-------------------
tablerows2_df = pd.read_sql_query(
    "SELECT location, count(id) as user_count from users where location IS NOT NULL and location != ' ' group by location order by 2 DESC Limit 5;",
    con,
)
# print(tablerows2_df)

# -----------------Exercise 3 -------------------
# today = date.today()
today = datetime.now()

tablerows3_df = pd.read_sql_query("SELECT birthdate from users", con)
tablerows3_df["birthdate"] = pd.to_datetime(tablerows3_df["birthdate"])
print(tablerows3_df)


def calcurate_age(birthday):
    if (today.month, today.day) < (birthday.month, birthday.day):  # Before Birthday
        return today.year - birthday.year - 1
    else:  # After Birthday
        return today.year - birthday.year


# ------Use "apply" ---------
# tablerows3_df["age"] = tablerows3_df["birthdate"].apply(calcurate_age)
# ------Use "loof" ---------
ages = []
for temp in tablerows3_df["birthdate"]:
    ages.append(calcurate_age(temp))

tablerows3_df["age"] = ages

print("Avg age : ", tablerows3_df["age"].mean())  # Average
print("Max age : ", tablerows3_df["age"].max())  # Max
print("Min age : ", tablerows3_df["age"].min())  # Min
print(" ")


# ---------- Exercise 4 -----------------
tablerows4_df = pd.read_sql_query(
    "SELECT  id, count(followed_id) as follower_number from follows join users on id = followed_id group by id order by follower_number DESC LIMIT 5;",
    con,
)
print(tablerows4_df)

# ---------- Exercise 5 ------------------
tablerows5_df = pd.read_sql_query(
    """
    select max(latest)  as latest_time from (
    select MAX(created_at) as latest from users 
    union
    select MAX(created_at) from posts
    union
    select MAX(created_at) from comments
    ) AS t1
""",
    con,
)


def Cal_time_different(latest_time):
    return today - latest_time
    # return today - latest_time if today > latest_time else latest_time - today


tablerows5_df["latest_time"] = pd.to_datetime(tablerows5_df["latest_time"])
tablerows5_df["today"] = today
tablerows5_df["time_different"] = tablerows5_df["latest_time"].apply(Cal_time_different)
# print(tablerows5_df)

time_different = tablerows5_df["time_different"]
# SQLite don't support date calcurating
different = int(time_different.dt.total_seconds().iloc[0])

try:
    con.execute(
        # strfttime -> Data/time to String format
        "Update users SET created_at = datetime(strftime('%s', created_at) + ?, 'unixepoch')",
        (different,),
        # sqlite3 expects a sequence value for params
    )
    con.execute(
        "Update comments SET created_at = datetime(strftime('%s', created_at) + ?, 'unixepoch')",
        (different,),
    )
    con.execute(
        "Update posts SET created_at = datetime(strftime('%s', created_at) + ?, 'unixepoch')",
        (different,),
    )
except:
    print("Update fail")

exit()
con.close()
