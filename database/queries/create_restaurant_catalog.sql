CREATE TABLE restaurant_catalog
(id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
description TEXT,
category TEXT,
price REAL,
is_vegetarian INTEGER,
is_gluten_free INTEGER,
is_spicy INTEGER,
calories INTEGER)