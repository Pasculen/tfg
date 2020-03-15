-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS evidence;


CREATE TABLE evidence (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	body TEXT NOT NULL UNIQUE
);
