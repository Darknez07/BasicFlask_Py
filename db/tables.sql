Create Table log_date(
    Id integer primary key autoincrement,
    entry_date date NOT NULL
);

Create TABLE food(
    Id INTEGER PRIMARY KEY autoincrement,
    name text not NULL,
    protien INTEGER NOT NULL,
    carbohydrate integer not null,
    fat INTEGER not null,
    calories INTEGER not null
);

Create TABLE food_date(
    food_id INTEGER not null,
    log_date_id INTEGER not null,
    primary KEY(food_id, log_date_id)
);