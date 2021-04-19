create table if not exists drinks (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    quantity        INTEGER,
    selling_price   REAL,
    purchase_price  REAL
);
create table if not exists operation (
    date            TEXT,
    operation       TEXT,
    id_drink        INTEGER,
    name_drink      TEXT,
    amount          INTEGER,
    price           REAL
);