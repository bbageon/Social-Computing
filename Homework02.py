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

    plt.figure()
    plt.plot(years, use_server)
    plt.xlabel("Years")
    plt.ylabel("Required server")
    plt.title("Server growth trends")
    plt.grid(True)
    plt.show()

    print(use_server, years)
    print(result)

    # CAGR
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

    plt.figure()
    plt.plot(future_years, future_use_server)
    plt.xlabel("future years")
    plt.ylabel("Prediction use server")
    plt.title("Server growth estimation")
    plt.grid(True)
    plt.xticks(future_years)
    plt.show()
    print(future_use_server)

except Exception as e:
    print("query failed", e)

# exercise 2.2
# Virality: Identify the 3 most viral posts in the history of the platform.
# Select and justify a specific metric or requirements for a post to be considered viral.
# Answer and explain your queries/calculations below.
# You may use SQL and/or Python to perform this task. (4 points)
