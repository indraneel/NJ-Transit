-- table for stations

CREATE TABLE IF NOT EXISTS stations (
	station_id SERIAL PRIMARY KEY,
	station_abbr VARCHAR(2) NOT NULL,
	station_name VARCHAR(100) NOT NULL,
	train_row_id INTEGER REFERENCES trains(id)

);

-- table for trains

CREATE TABLE IF NOT EXISTS trains (
	id SERIAL PRIMARY KEY,
	sched_dep_date TIMESTAMP NOT NULL,
	track SMALLINT,
	line VARCHAR(10) NOT NULL,
	train_line VARCHAR(50) NOT NULL,
	train_number VARCHAR(10) NOT NULL,
	status VARCHAR(50),
	sec_late SMALLINT,
	gps_lat SMALLINT,
	gps_lon SMALLINT,
	gps_time TIMESTAMP,
	station_id INTEGER REFERENCES stations(station_id),
);