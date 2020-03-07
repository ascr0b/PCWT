DROP TABLE IF EXISTS users;

DROP TABLE IF EXISTS projects;

DROP TABLE IF EXISTS hosts;

DROP TABLE IF EXISTS ports;

DROP TABLE IF EXISTS domains;

CREATE TABLE users (
	id integer PRIMARY KEY AUTOINCREMENT,
	username text,
	password text
);

CREATE TABLE projects (
	id text PRIMARY KEY,
	name text,
	owner text
);

CREATE TABLE hosts (
	id text PRIMARY KEY,
	ip text,
	note text,
	style text,
	portsq integer,
	project text,
	FOREIGN KEY (project) REFERENCES projects (id)
);

CREATE TABLE ports (
	id text PRIMARY KEY,
	port text,
	state text,
	service text,
	version text,
	note text,
	host text,
	FOREIGN KEY (host) REFERENCES hosts (id)
);

CREATE TABLE domains (
	id text PRIMARY KEY,
	domain text,
	lvl text,
	ip text,
	note text,
	style text,
	project text,
	FOREIGN KEY (project) REFERENCES projects (id)
);