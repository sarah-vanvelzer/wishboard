import time

import psycopg

from app.agent import find_gifts
from app.db import DATABASE_URL

TOP_N = 6
MIN_GIFTABILITY = 5


def main():
    with psycopg.connect(DATABASE_URL) as conn:
        themes = conn.execute(
            # Drops low giftability themes (e.g., quotes)
            "SELECT id, name, reason FROM themes "
            "WHERE giftability >= %s ORDER BY score DESC LIMIT %s",
            (MIN_GIFTABILITY, TOP_N),
        ).fetchall()

    # Unpacks each database row into three variables
    for theme_id, name, reason in themes:
        print(f"\n=== {name} ===")
        _, gifts = find_gifts(name, reason)
        with psycopg.connect(DATABASE_URL) as conn:
            # Rerunning replaces a theme's gifts (instead of duplicates)
            conn.execute("DELETE FROM gifts WHERE theme_id = %s", (theme_id,))
            for g in gifts:
                conn.execute(
                    "INSERT INTO gifts (theme_id, name, why, link, source) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (theme_id, g["name"], g["why"], g["link"], g["source"]),
                )
        for g in gifts:
            print(f"- {g['name']}: {g['link']}")
        time.sleep(5)


if __name__ == "__main__":
    main()