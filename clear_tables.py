import argparse
import os
from typing import List

from sqlalchemy import create_engine, text
from dotenv import load_dotenv


TABLES = [
    "canteen_records",
    "vehicle_records", 
    "door_records",
]


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-url", default=os.environ.get("DB_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/shitang"))
    parser.add_argument("--table", choices=TABLES + ["all"], default="all")
    parser.add_argument("--yes", action="store_true", help="确认清空数据")
    parser.add_argument("--cascade", action="store_true", help="使用 CASCADE 清空有外键依赖的数据")
    args = parser.parse_args()

    if not args.yes:
        print("[abort] 需要 --yes 确认以清空数据表")
        return

    targets: List[str] = TABLES if args.table == "all" else [args.table]
    engine = create_engine(args.db_url, future=True)
    opt = " CASCADE" if args.cascade else ""
    with engine.begin() as conn:
        for t in targets:
            print(f"[truncate] {t}")
            conn.execute(text(f'TRUNCATE TABLE {t} RESTART IDENTITY{opt};'))
    print("[done] 清空完成")


if __name__ == "__main__":
    main()