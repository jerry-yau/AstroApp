CREATE TABLE contact (id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT,
    email TEXT NOT NULL,
    purpose TEXT NOT NULL,
    message TEXT NOT NULL,
    promo INTEGER NOT NULL
);

CREATE TABLE accounts (id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    city TEXT DEFAULT London
);

CREATE TABLE bookmarks (id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    target_name TEXT NOT NULL,
    RA REAL,
    Dec REAL,
    notes TEXT,
    FOREIGN KEY (user_id)
        REFERENCES accounts (id)
);