import os
import argparse
import re
import logging
from typing import List, Dict, Any, Tuple

from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy import Integer, Date, DateTime, Text
from dotenv import load_dotenv

try:
    from openpyxl import load_workbook
    from openpyxl.utils.datetime import from_excel
    OPENPYXL_AVAILABLE = True
except Exception:
    OPENPYXL_AVAILABLE = False





def _canon(s: str) -> str:
    s = (s or "").strip()
    s = s.replace("（", "(").replace("）", ")")
    s = s.replace(" ", "")
    return s


def read_xlsx(path: str, header_row: int = 1, target_table: str = None) -> List[Tuple[str, List[Dict[str, Any]], List[str]]]:
    if not OPENPYXL_AVAILABLE:
        return []
    wb = load_workbook(path, data_only=True, read_only=True)
    if target_table is None:
        base = os.path.basename(path)
        name, _ = os.path.splitext(base)
        target_table = determine_table_by_filename(name)
    excel_mappings: Dict[str, str] = {}
    target_fields: List[str] = []
    if target_table and target_table in TABLES:
        excel_mappings = TABLES[target_table]["excel_mappings"]
        target_fields = list(excel_mappings.values())
    results: List[Tuple[str, List[Dict[str, Any]], List[str]]] = []
    for ws in wb.worksheets:
        use_header_row = header_row
        hdr_cells = ws[use_header_row]
        headers: List[str] = [str(cell.value) if cell.value is not None else f"col_{idx}" for idx, cell in enumerate(hdr_cells, start=1)]
        canon_map: Dict[str, str] = { _canon(h): h for h in headers }
        header_map: Dict[str, str] = {}
        for src, tgt in excel_mappings.items():
            ch = _canon(src)
            header_map[tgt] = canon_map.get(ch, src)
        rows: List[Dict[str, Any]] = []
        for row in ws.iter_rows(min_row=use_header_row + 1):
            raw_row: Dict[str, Any] = {}
            for i, cell in enumerate(row):
                key = headers[i] if i < len(headers) else f"col_{i+1}"
                val = cell.value
                if getattr(cell, "is_date", False) and isinstance(val, (int, float)):
                    raw_row[key] = from_excel(val)
                else:
                    raw_row[key] = val
            if header_map:
                record: Dict[str, Any] = {}
                for tgt in target_fields:
                    hk = header_map.get(tgt, tgt)
                    record[tgt] = raw_row.get(hk)
                rows.append(record)
            else:
                rows.append(raw_row)
        returned_headers = target_fields if header_map else headers
        results.append((ws.title, rows, returned_headers))
    return results


TABLES = {
    "canteen_records": {
        "columns": {
            "id": Integer,
            "record_date": DateTime(timezone=True),
            "name": Text,
            "type": Text,
        },
        "excel_mappings": {
            "消费时间": "record_date",
            "姓名": "name",
            "餐别": "type",
        },
    },
    "vehicle_records": {
        "columns": {
            "id": Integer,
            "record_date": DateTime(timezone=True),
            "name": Text,
            "type": Text,
        },
        "excel_mappings": {
            "打卡时间": "record_date",
            "姓名": "name",
            "打卡类型": "type",
        },
    },
    "door_records": {
        "columns": {
            "id": Integer,
            "record_date": DateTime(timezone=True),
            "name": Text,
            "type": Text,
        },
        "excel_mappings": {
            "事件时间": "record_date",
            "人员姓名": "name",
            "控制器": "type",
        },
    },
}


def ensure_table(metadata: MetaData, table_name: str, columns: Dict[str, Any]) -> Table:
    try:
        return Table(table_name, metadata, autoload_with=metadata.bind)
    except Exception:
        cols = [Column(cn, ct, quote=True) for cn, ct in columns.items()]
        cols.append(Column("created_at", DateTime(timezone=True), server_default="now()", quote=True))
        tbl = Table(table_name, metadata, *cols)
        metadata.create_all(metadata.bind, tables=[tbl])
        return tbl


def _simple_insert(engine, metadata: MetaData, path: str, excel_header_row: int, target_table: str, verbose: bool) -> None:
    results = read_xlsx(path, header_row=excel_header_row, target_table=target_table)
    if not results:
        return
    schema = TABLES[target_table]["columns"]
    tbl = ensure_table(metadata, target_table, schema)
    for sheet_name, rows, headers in results:
        if verbose:
            logging.info(f"导入 {os.path.basename(path)}[{sheet_name}] -> {target_table}, 行数={len(rows)}")
        insert_rows: List[Dict[str, Any]] = []
        for r in rows:
            insert_rows.append(r)
        if insert_rows:
            with engine.begin() as conn:
                conn.execute(tbl.insert(), insert_rows)


def determine_table_by_filename(filename: str) -> str:
    fname = filename.lower()
    if "consumelog" in fname:
        return "canteen_records"
    if "打卡明细数据" in fname:
        return "vehicle_records"
    if "dooreventinfo" in fname:
        return "door_records"
    return None


def import_canteen_excel(engine, metadata: MetaData, path: str, excel_header_row: int = 1, verbose: bool = False) -> None:
    _simple_insert(engine, metadata, path, excel_header_row, "canteen_records", verbose)


def import_vehicle_excel(engine, metadata: MetaData, path: str, excel_header_row: int = 1, verbose: bool = False) -> None:
    _simple_insert(engine, metadata, path, excel_header_row, "vehicle_records", verbose)


def import_personnel_excel(engine, metadata: MetaData, path: str, excel_header_row: int = 1, verbose: bool = False) -> None:
    _simple_insert(engine, metadata, path, excel_header_row, "door_records", verbose)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=os.environ.get("DATA_DIR", "./data"))
    parser.add_argument("--import-dir", default=os.environ.get("IMPORT_DIR", "import/"))
    parser.add_argument("--db-url", default=os.environ.get("DB_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/shitang"))
    parser.add_argument("--excel-header-row", type=int, default=int(os.environ.get("EXCEL_HEADER_ROW", "1")))
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--table", choices=["canteen_records", "vehicle_records", "door_records"], nargs="*")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    engine = create_engine(args.db_url, future=True)
    metadata = MetaData()
    metadata.bind = engine

    base_dir = os.path.join(args.data_dir, args.import_dir)
    processed = 0

    for root, _, files in os.walk(base_dir):
        for f in files:
            if not f.lower().endswith((".xlsx", ".xlsm")):
                continue
            file_path = os.path.join(root, f)
            name, _ = os.path.splitext(f)
            target_table = determine_table_by_filename(name)
            if target_table is None:
                if args.verbose:
                    logging.warning(f"跳过未知类型文件: {file_path}")
                continue
            if args.table and target_table not in args.table:
                continue
            if target_table == "canteen_records":
                import_canteen_excel(engine, metadata, file_path, args.excel_header_row, args.verbose)
            elif target_table == "vehicle_records":
                import_vehicle_excel(engine, metadata, file_path, args.excel_header_row, args.verbose)
            elif target_table == "door_records":
                import_personnel_excel(engine, metadata, file_path, args.excel_header_row, args.verbose)
            processed += 1

    if args.verbose:
        logging.info(f"导入完成，处理文件数: {processed}")


if __name__ == "__main__":
    main()
