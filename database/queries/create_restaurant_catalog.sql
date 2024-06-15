CREATE TABLE IF NOT EXISTS restaurant_catalog
(id INTEGER PRIMARY KEY IDENTITY(1,1),
name TEXT NOT NULL,
description TEXT,
category TEXT,
price REAL,
is_vegetarian INTEGER,
is_gluten_free INTEGER,
is_spicy INTEGER,
calories INTEGER)