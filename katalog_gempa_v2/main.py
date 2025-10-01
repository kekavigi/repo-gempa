import sqlite3
from ast import literal_eval
from datetime import datetime
from typing import Any

# import numpy as np
import pandas as pd
from selectolax.parser import HTMLParser

from tqdm import tqdm


class Database:
    def __init__(self, uri: str) -> None:
        # TODO: bikin tabel version di database; jika < program, program raise Error
        # TODO: bikin script migration versi database

        def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict[str, Any]:
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.sql = sqlite3.connect(
            uri,
            uri=True,
            isolation_level=None,
            check_same_thread=False,
        )
        self.sql.autocommit = sqlite3.LEGACY_TRANSACTION_CONTROL
        self.sql.row_factory = dict_factory

        # skema database ini sederhana saja:
        # `text` menyimpan teks HTML repo gempa yang diunduh
        # `min_date` dan `max_date` berisi info rentang waktu gempa yang ada di HTML tersebut
        # `updated` menginfokan kapan terakhir kali text diunduh (karena basis data yang saya
        #     pilih adalah yang 'preliminary', text bisa obselete suatu saat nanti)

        script = """
                PRAGMA journal_mode = wal;
                PRAGMA synchronous = off;
                PRAGMA temp_store = memory;
                PRAGMA mmap_size = 30000000000;
                PRAGMA busy_timeout = 10000;
                PRAGMA wal_autocheckpoint;

                CREATE TABLE IF NOT EXISTS html(
                    id          INTEGER PRIMARY KEY,
                    min_date    TEXT NOT NULL,
                    max_date    TEXT NOT NULL,
                    updated     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    text        TEXT NOT NULL
                    );

                CREATE UNIQUE INDEX IF NOT EXISTS ix_date
                    ON html (min_date, max_date);

                PRAGMA optimize=0x10002;
                """
        with self.sql as conn:
            for stt in script.split(";"):
                conn.execute(stt)

        # shortcut
        self.execute = self.sql.execute

    def save(self, min_date: datetime, max_date: datetime, text: str) -> None:
        min_date = min_date.strftime("%Y-%m-%d")  # type: ignore[assignment]
        max_date = max_date.strftime("%Y-%m-%d")  # type: ignore[assignment]

        assert min_date < max_date

        # pastikan tidak ada data yang overlap
        result = self.sql.execute(
            """
            SELECT min_date, max_date FROM html
            WHERE  ((min_date < :x) AND (:x < max_date))
                OR ((min_date < :y) AND (:y < max_date))
            ORDER BY min_date
            """,
            {"x": min_date, "y": max_date},
        ).fetchall()
        if result:
            print(", ".join(f"[{_['min_date']}, {_['max_date']})" for _ in result))
            raise IndexError("Overlapped range!")

        with self.sql as conn:
            conn.execute(
                """
                INSERT INTO html (min_date, max_date, text) VALUES (?, ?, ?)
                ON CONFLICT (min_date, max_date) DO UPDATE SET
                    text = excluded.text,
                    updated = CURRENT_TIMESTAMP
                """,
                (min_date, max_date, text),
            )

    def extract(self):
        events, sensors = [], []
        for row in tqdm(self.sql.execute("SELECT text FROM html").fetchall()):
            text = row["text"]
            if not text:
                continue

            # Ambil data gempa. Data terletak di tag <script> ketiga dari terakhir.
            the_script = HTMLParser(text).css("script")[-3].text()

            tmp = self._get_values(the_script, "locations")
            if tmp != "null":
                events += literal_eval(tmp)
            tmp = self._get_values(the_script, "sensors")
            if tmp != "null":
                sensors += literal_eval(tmp)

        return self._df_event(events), self._df_sensors(sensors)

    @staticmethod
    def _get_values(text: str, var_name: str):
        return (
            text.split(f"var {var_name} =")[1]
            .replace(r"\/", "/")
            .split(";\n")[0]
            .strip()
        )

    @staticmethod
    def _df_event(raw_list: list) -> pd.DataFrame:
        # fmt: off
        columns = [
            'No', 'eventID', 'datetime', 'latitude', 'longitude', 'magnitude', 'mag_type',
            'depth', 'phasecount', 'azimuth_gap', 'location', 'agency',  'datetimeFM', 'latFM',
            'lonFM', 'magFM', 'magTypeFM', 'depthFM', 'phasecountFM', 'AzGapFM', 'scalarMoment',
            'Mrr', 'Mtt', 'Mpp', 'Mrt', 'Mrp', 'Mtp', 'varianceReduction', 'doubleCouple', 'clvd',
            'strikeNP1', 'dipNP1', 'rakeNP1', 'strikeNP2', 'dipNP2', 'rakeNP2', 'azgapFM', 'misfit',
        ]
        # fmt: on
        df = pd.DataFrame(raw_list, columns=columns)

        # Beberapa perapian kecil:
        # ubah kolom datetime dari string ke objek datetime
        df.datetime = pd.to_datetime(df.datetime)
        # buang kolom 'No' (Nomor)
        df = df.drop(columns=["No"])
        # urutkan data berdasarkan datetime.
        df = df.sort_values(by="datetime").reset_index(drop=True)

        assert len(df) == len(set(df.eventID))
        return df

    @staticmethod
    def _df_sensors(raw_list: list) -> pd.DataFrame:
        # fmt: off
        columns = [
            'col1', 'code', 'latitude', 'longitude',
            'elevation', 'location', 'datetime', 'col2',
        ]
        # fmt: on

        df = pd.DataFrame(raw_list, columns=columns)
        df = df.drop(columns=["col1", "col2"])
        df = df.drop_duplicates()
        return df