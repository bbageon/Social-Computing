from datetime import datetime
import datetime
import sqlite3
import os
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np

os.system("clear")
con = sqlite3.connect("/Users/bbageon/Downloads/database.sqlite")

# ------ Exercise 2.1 ------
# Growth: This year, we are renting 16 servers to run our social media platform.
# They are soon at 100% capacity, so we need to rent more servers.
# We would like to rent enough to last for 3 more years without upgrades,
# plus 20% capacity for redundancy. We need an estimate of how many servers we need to start renting based on ßpast growth trends. Plot the trend on a graph using Python and include it below. Answer and explain your queries/calculations below. You may use SQL and/or Python to perform this task.
# (Note that the dataset may not end in the current year, please assume that the last data marks today’s date) (3 points)
server_count = 16

try:
    result = pd.read_sql_query(
        """
        select year, sum(event_count) as total_count
            FROM(
                SELECT strftime('%Y', created_at) AS year, COUNT(*) AS event_count
                FROM posts
                GROUP BY strftime('%Y', created_at)
                union all
                SELECT strftime('%Y', p.created_at) AS year, COUNT(*) AS event_count
                FROM reactions r
                JOIN posts p ON r.post_id = p.id
                GROUP BY strftime('%Y', p.created_at)
                union all
                SELECT strftime('%Y', created_at) AS year, COUNT(*) AS event_count
                FROM comments
                GROUP BY strftime('%Y', created_at)
        ) as total_events
        group by year;
    """,
        con,
    )
    use_server = []  # For displaying trends
    future_use_server = []  # For predict future

    years = []
    future_years = []

    total_events = 0

    for i in range(len(result)):
        # for i in result.total_count:
        total_events += result.total_count[i]
        use_server.append(result.total_count[i])
        years.append(result.year[i])

    events_per_server = total_events / server_count

    use_server = [
        math.ceil(sum(use_server[: i + 1]) / events_per_server)
        for i in range(len(use_server))
    ]

    # plt.figure()
    # plt.plot(years, use_server)
    # plt.xlabel("Years")
    # plt.ylabel("Required server")
    # plt.title("Server growth trends")
    # plt.grid(True)
    # plt.show()

    # print(use_server, years)
    # print(result)

    # CAGR
    # https://anderson.ae/article/how-to-calculate-cagr
    first_value = result.total_count.iloc[0]
    last_value = result.total_count.iloc[-1]

    n_years = int(years[-1]) - int(years[0])

    # CAGR calcurating
    cagr = (last_value / first_value) ** (1 / n_years) - 1
    print(f"CAGR: {cagr:.2%} per year")

    future_years = [int(years[-1]) + i for i in range(1, 4)]
    print(future_years)

    prev_value = last_value
    for i in range(len(future_years)):
        next_value = prev_value * (1 + cagr)
        future_use_server.append(math.ceil(int(next_value) / events_per_server * 1.2))
        prev_value = next_value

    # plt.figure()
    # plt.plot(future_years, future_use_server)
    # plt.xlabel("future years")
    # plt.ylabel("Prediction use server")
    # plt.title("Server growth estimation")
    # plt.grid(True)
    # plt.xticks(future_years)
    # plt.show()
    # print(future_use_server)

except Exception as e:
    print("query failed", e)

# exercise 2.2
# Virality: Identify the 3 most viral posts in the history of the platform.
# Select and justify a specific metric or requirements for a post to be considered viral.
# Answer and explain your queries/calculations below.
# You may use SQL and/or Python to perform this task. (4 points)

# viral = (comment_count + reaction_count) / (now - p.created_at)
# julianday() -> Time Between BC 4713-01-01 and now
try:
    result = pd.read_sql_query(
        """SELECT p.id, p.user_id, 
        COUNT(DISTINCT c.id) AS comment_count,
        COUNT(DISTINCT r.id) AS reaction_count,
        (COUNT(DISTINCT c.id) + COUNT(DISTINCT r.id)) * 1.0 /
       ((strftime('%s','now') - strftime('%s', p.created_at)) / 86400.0)  AS total_count
        FROM posts p
        LEFT JOIN comments c ON p.id = c.post_id
        LEFT JOIN reactions r ON p.id = r.post_id
        GROUP BY p.id
        ORDER BY total_count DESC
        LIMIT 3;
        """,
        con,
    )

    # print(result)


except Exception as e:
    print("query failed : ", e)


# exercise 2.3
# Exercise 2.3 Content Lifecycle:
# What is the average time between the publishing of a post and the first engagement it receives?
# What is the average time between the publishing of a post and the last engagement it receives?
# Answer and explain your queries/calculations below.
# You may use SQL and/or Python to perform this task. (4 points)


try:
    result1 = pd.read_sql_query(
        """
        select avg(first_engagement) / 86400.00 as first_avg
        from (
            select p.id,
                        min(strftime('%s', c.created_at) - strftime('%s', p.created_at)) as first_engagement
            from posts p 
            left outer join comments c on p.id = c.post_id
            group by p.id
            having first_engagement is not null and first_engagement > 0
            order by first_engagement
        ) """,
        con,
    )

    print(
        "Avg first engagement:",
        str(datetime.timedelta(seconds=int(result1["first_avg"][0]))),
    )

    result2 = pd.read_sql_query(
        """
        select avg(last_engagement) as last_avg
        from (
            select p.id,
            max(strftime('%s', c.created_at) - strftime('%s', p.created_at)) as last_engagement
            from posts p 
            left outer join comments c on p.id = c.post_id
            group by p.id
            having last_engagement is not null and last_engagement > 0
            order by last_engagement
        ) """,
        con,
    )

    print(
        "Avg last engagement:",
        str(datetime.timedelta(seconds=int(result2["last_avg"][0]))),
    )

except Exception as e:
    print("query failed : ", e)


# exercise 2.4
# Connections: Identify the top 3 user pairs who engage with each other’s content the most.
# Define and describe your metric for engagement.
# Answer and explain your queries/calculations below.
# You may use SQL and/or Python to perform this task. (4 points)

# engagement = reaction + comment

try:
    result = pd.read_sql_query(
        """
        select post_user, engager, sum(engagement) as total_engagement
        from (
            select p.user_id as post_user, c.user_id as engager, count(*) as engagement
            from posts p
            inner join comments c on p.id = c.post_id
            where p.user_id != c.user_id
            group by p.user_id, c.user_id
            
            union ALL
            
            select p.user_id as post_user, r.user_id as engager, count(*) as engagement
            from posts p
            inner join reactions r on p.id = r.post_id
            where p.user_id != r.user_id
            group by p.user_id, r.user_id
        ) sub
        GROUP by post_user, engager
        order by total_engagement desc
        LIMIT 3;    
    """,
        con,
    )

    print(result)

except Exception as e:
    print("query failed : ", e)
