import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
    "mysql+pymysql://root:voc_root@localhost:3306/vocdata",
    echo=False
)

ddl_statements = [
    '''
    CREATE TABLE IF NOT EXISTS dim_gemeindetyp (
        gemeindetyp_id   INT AUTO_INCREMENT PRIMARY KEY,
        gemeindetyp_code VARCHAR(50) UNIQUE,
        gemeindetyp_bez  VARCHAR(100)
    );
    ''',
    '''
    CREATE TABLE IF NOT EXISTS dim_sprachregion (
        sprachregion_id   INT AUTO_INCREMENT PRIMARY KEY,
        sprachregion_code VARCHAR(50) UNIQUE,
        sprachregion_bez  VARCHAR(100)
    );
    ''',
    '''
    CREATE TABLE IF NOT EXISTS dim_kanton (
        kanton_id   INT AUTO_INCREMENT PRIMARY KEY,
        kanton_code CHAR(2) UNIQUE,
        kanton_bez  VARCHAR(100)
    );
    '''
]

with engine.begin() as con:
    for ddl in ddl_statements:
        con.execute(text(ddl))

print("✔ Drei leere Dimensionstabellen angelegt.")
