#!/bin/bash
set -e

## Postgres DB ##
#################

backup_rdb() {
	echo "Backing up ${DB_TYPE^^} db..."
	BACKUP_FILE="${DB_TYPE}db_$(date +%Y%m%dT%H%M%Z).bak"
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "mkdir -p /backup/ && pg_dump -U \$POSTGRES_USER -d \$${DB_TYPE^^}_DB_NAME > /backup/$BACKUP_FILE"
	DATA_FOLDER="$(grep -oP "^DATA_FOLDER=\K.*" "$ENV_FILE")"
	mkdir -p "${DATA_FOLDER:-.}"/backups/RDB/
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" cp rdb:/backup/$BACKUP_FILE "${DATA_FOLDER:-.}"/backups/RDB/
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb rm -rf /backup/$BACKUP_FILE
}

restore_rdb(){
	echo "Restoring ${DB_TYPE^^} db..."
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "mkdir -p /restore/"
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" cp "$RESTORE_PATH" rdb:/restore/
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "dropdb -U \$POSTGRES_USER \$${DB_TYPE^^}_DB_NAME && 
		createdb -U \$POSTGRES_USER \$${DB_TYPE^^}_DB_NAME && psql -U \$POSTGRES_USER -d \$${DB_TYPE^^}_DB_NAME < /restore/$(basename $RESTORE_PATH)"
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb rm -rf /restore/*
}

# CHS database
init_chsdb() {
	echo -e "Initializing CHS DB:"
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -v ON_ERROR_STOP=1 --username=\$POSTGRES_USER <<-EOSQL
		SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '\$CHS_DB_NAME' AND pid <> pg_backend_pid();
		DROP DATABASE IF EXISTS \$CHS_DB_NAME;
		CREATE DATABASE \$CHS_DB_NAME WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';
		DROP USER IF EXISTS \$CHS_DB_NAME;
		CREATE USER \$CHS_DB_NAME WITH ENCRYPTED PASSWORD '\$CHS_DB_PASSWORD';
		GRANT ALL ON DATABASE \$CHS_DB_NAME TO \$CHS_DB_NAME;
		\connect \$CHS_DB_NAME;
		CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;
		COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';
		SET default_tablespace = '';
		SET default_with_oids = false;
		CREATE TABLE public.aquifer (
			code character varying NOT NULL,
			superposition character varying
		);
		ALTER TABLE public.aquifer OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.control_point (
			code character varying NOT NULL,
			denomination character varying NOT NULL,
			municipality character varying NOT NULL,
			province character varying NOT NULL,
			typology character varying NOT NULL,
			description character varying,
			water_body character varying,
			location public.geometry
		);
		ALTER TABLE public.control_point OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.demand_unit (
			code character varying NOT NULL,
			type character varying NOT NULL,
			geometry public.geometry,
			name character varying,
			surface numeric
		);
		ALTER TABLE public.demand_unit OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.demand_water_relation (
			water_body character varying NOT NULL,
			demand_unit character varying NOT NULL
		);
		ALTER TABLE public.demand_water_relation OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.measurement_point (
			code character varying NOT NULL,
			control_point character varying,
			denomination character varying NOT NULL,
			location public.geometry NOT NULL,
			description character varying NOT NULL,
			typology character varying
		);
		ALTER TABLE public.measurement_point OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.environmental_flow (
			variable character varying NOT NULL,
			typology character varying NOT NULL,
			water_body character varying NOT NULL,
			oct_dic numeric,
			ene_mar numeric,
			abr_jun numeric,
			jul_sep numeric,
			sistema smallint,
			masa_estrategica boolean NOT NULL,
			oct_dic_seq numeric,
			ene_mar_seq numeric,
			abr_jun_seq numeric,
			jul_sep_seq numeric
		);
		ALTER TABLE public.environmental_flow OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.dam (
			water_body character varying NOT NULL,
			variable character varying NOT NULL,
			typology character varying NOT NULL,
			max_oct_dic numeric,
			max_ene_mar numeric,
			max_abr_jun numeric,
			max_jul_sep numeric,
			min_oct_dic numeric,
			min_ene_mar numeric,
			min_abr_jun numeric,
			min_jul_sep numeric
		);
		ALTER TABLE public.dam OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.superficial (
			code character varying NOT NULL,
			eumspfcod character varying NOT NULL
		);
		ALTER TABLE public.superficial OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.underground (
			code character varying NOT NULL,
			eumsbtcod character varying
		);
		ALTER TABLE public.underground OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.variable (
			code character varying NOT NULL,
			measurement_point character varying,
			typology character varying NOT NULL,
			description character varying NOT NULL
		);
		ALTER TABLE public.variable OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.water_body (
			code character varying NOT NULL,
			type character varying NOT NULL,
			geometry public.geometry,
			name character varying NOT NULL,
			category character varying NOT NULL,
			generator_flow numeric
		);
		ALTER TABLE public.water_body OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.water_body_relation (
			water_body_1 character varying NOT NULL,
			water_body_2 character varying NOT NULL
		);
		ALTER TABLE public.water_body_relation OWNER TO \"\$POSTGRES_USER\";
		CREATE TABLE public.crop (
			demand_unit_code character varying,
			cereales_invierno numeric,
			arroz numeric,
			cereales_primavera numeric,
			tuberculos numeric,
			horticolas_protegido numeric,
			horticolas_libre numeric,
			citricos numeric,
			frutales_fruto_carnoso numeric,
			almendro numeric,
			vinedo_vino numeric,
			vinedo_mesa numeric,
			olivar numeric,
			total numeric
		);
		ALTER TABLE public.crop OWNER TO \"\$POSTGRES_USER\";
		
		CREATE TABLE public.system_unit (
			zone character varying NOT NULL,
			name character varying NOT NULL,
			geometry public.geometry,
			ha numeric
		);
		ALTER TABLE public.system_unit OWNER TO \"\$POSTGRES_USER\";
		GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"\$POSTGRES_USER\";
	EOSQL"
	echo -e "Injecting data to CHS DB:"
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.aquifer (code, superposition) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/aquifer.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.control_point (code, denomination, municipality, province, typology, description, water_body, location) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/control_point.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.demand_unit (code, type, geometry, name, surface) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/demand_unit.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.demand_water_relation (water_body, demand_unit) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/demand_water_relation.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.environmental_flow (variable, typology, water_body, oct_dic, ene_mar, abr_jun, jul_sep, sistema, masa_estrategica, oct_dic_seq, ene_mar_seq, abr_jun_seq, jul_sep_seq) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/environmental_flow.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.dam (water_body, variable, typology, max_oct_dic, max_ene_mar, max_abr_jun, max_jul_sep, min_oct_dic, min_ene_mar, min_abr_jun, min_jul_sep) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/dam.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.measurement_point (code, control_point, denomination, location, description, typology) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/measurement_point.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/spatial_ref_sys.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.superficial (code, eumspfcod) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/superficial.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.underground (code, eumsbtcod) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/underground.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.variable (code, measurement_point, typology, description) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/variable.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.water_body (code, type, geometry, name, category, generator_flow) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/water_body.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.water_body_relation (water_body_1, water_body_2) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/water_body_relation.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.crop (demand_unit_code, cereales_invierno, arroz, cereales_primavera, tuberculos, horticolas_protegido, horticolas_libre, citricos, frutales_fruto_carnoso, almendro, vinedo_vino, vinedo_mesa, olivar, total) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/crop.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 -c \"COPY public.system_unit (zone, name, geometry, ha) FROM STDIN;\"" < ./backend/database/docker-entrypoint-initdb.d/system_unit.dat
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -U \$POSTGRES_USER -d \$CHS_DB_NAME -v ON_ERROR_STOP=1 <<-EOSQL
		ALTER TABLE ONLY public.aquifer ADD CONSTRAINT aquifer_pkey PRIMARY KEY (code);
		ALTER TABLE ONLY public.demand_unit ADD CONSTRAINT code UNIQUE (code);
		ALTER TABLE ONLY public.control_point ADD CONSTRAINT control_point_pkey PRIMARY KEY (code);
		ALTER TABLE ONLY public.demand_unit ADD CONSTRAINT demand_unit_pkey PRIMARY KEY (code);
		ALTER TABLE ONLY public.demand_water_relation ADD CONSTRAINT demand_water_relation_pkey PRIMARY KEY (water_body, demand_unit);
		ALTER TABLE ONLY public.measurement_point ADD CONSTRAINT measurement_point_pkey PRIMARY KEY (code);
		ALTER TABLE ONLY public.superficial ADD CONSTRAINT superficial_pkey PRIMARY KEY (code);
		ALTER TABLE ONLY public.underground ADD CONSTRAINT underground_pkey PRIMARY KEY (code);
		ALTER TABLE ONLY public.variable ADD CONSTRAINT variable_pkey PRIMARY KEY (code, typology);
		ALTER TABLE ONLY public.water_body ADD CONSTRAINT water_body_pkey PRIMARY KEY (code);
		ALTER TABLE ONLY public.water_body_relation
			ADD CONSTRAINT water_body_relation_pkey PRIMARY KEY (water_body_1, water_body_2);
		ALTER TABLE ONLY public.system_unit ADD CONSTRAINT system_unit_pkey PRIMARY KEY (zone);
		ALTER TABLE ONLY public.aquifer
			ADD CONSTRAINT aquifer_fkey FOREIGN KEY (code) REFERENCES public.water_body(code) NOT VALID;
		ALTER TABLE ONLY public.control_point
			ADD CONSTRAINT control_point_fkey FOREIGN KEY (water_body) REFERENCES public.water_body(code);
		ALTER TABLE ONLY public.demand_water_relation
			ADD CONSTRAINT demand_fkey FOREIGN KEY (demand_unit) REFERENCES public.demand_unit(code) NOT VALID;
		ALTER TABLE ONLY public.measurement_point
			ADD CONSTRAINT measurement_point_fkey FOREIGN KEY (control_point) REFERENCES public.control_point(code) NOT VALID;
		ALTER TABLE ONLY public.superficial
			ADD CONSTRAINT superficial_fkey FOREIGN KEY (code) REFERENCES public.water_body(code) NOT VALID;
		ALTER TABLE ONLY public.underground
			ADD CONSTRAINT underground_fkey FOREIGN KEY (code) REFERENCES public.water_body(code) NOT VALID;
		ALTER TABLE ONLY public.variable
			ADD CONSTRAINT variable_fkey FOREIGN KEY (measurement_point) REFERENCES public.measurement_point(code);
		ALTER TABLE ONLY public.environmental_flow
			ADD CONSTRAINT variable_fkey FOREIGN KEY (variable, typology) REFERENCES public.variable(code, typology) NOT VALID;
		ALTER TABLE ONLY public.dam
			ADD CONSTRAINT dam_variable_fkey FOREIGN KEY (variable, typology) REFERENCES public.variable(code, typology);
		ALTER TABLE ONLY public.water_body_relation
			ADD CONSTRAINT water_body_1_fkey FOREIGN KEY (water_body_1) REFERENCES public.water_body(code) NOT VALID;
		ALTER TABLE ONLY public.water_body_relation
			ADD CONSTRAINT water_body_2_fkey FOREIGN KEY (water_body_2) REFERENCES public.water_body(code) NOT VALID;
		ALTER TABLE ONLY public.environmental_flow
			ADD CONSTRAINT water_body_fkey FOREIGN KEY (water_body) REFERENCES public.water_body(code) NOT VALID;
		ALTER TABLE ONLY public.dam
			ADD CONSTRAINT dam_water_body_fkey FOREIGN KEY (water_body) REFERENCES public.water_body(code);
		ALTER TABLE ONLY public.demand_water_relation
			ADD CONSTRAINT water_fkey FOREIGN KEY (water_body) REFERENCES public.water_body(code) NOT VALID;
		ALTER TABLE ONLY public.crop
			ADD CONSTRAINT fkey_crop_demand_unit FOREIGN KEY (demand_unit_code) REFERENCES public.demand_unit(code);
		GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \$CHS_DB_NAME;
	EOSQL"
}

# ODC database
init_odcdb() {
	echo -e "Initializing ODC DB:"
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T rdb sh -c "psql -v ON_ERROR_STOP=1 --username=\$POSTGRES_USER <<-EOSQL
		SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '\$ODC_DB_NAME' AND pid <> pg_backend_pid();
		DROP DATABASE IF EXISTS \$ODC_DB_NAME;
		CREATE DATABASE \$ODC_DB_NAME WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';
		DROP USER IF EXISTS \$ODC_DB_NAME;
		CREATE USER \$ODC_DB_NAME WITH ENCRYPTED PASSWORD '\$ODC_DB_PASSWORD';
		ALTER USER \$ODC_DB_NAME SUPERUSER;
		GRANT ALL ON DATABASE \$ODC_DB_NAME TO \$ODC_DB_NAME;
	EOSQL"
}

## INFLUX DB ##
###############
init_tdb() {
	echo -e "Initializing TDB:"

	# Get Influx admin token
	INFLUXDB_ADMIN_TOKEN=$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c 'influx auth list \
		--user $DOCKER_INFLUXDB_INIT_USERNAME \
		--hide-headers | cut -f 3')
	
	# Create SAIH raw data bucket
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c "influx bucket create \
		--org \$DOCKER_INFLUXDB_INIT_ORG \
		--name ${SAIH_BUCKET:-SAIH}_raw \
		--token $INFLUXDB_ADMIN_TOKEN"
	
	# Create simulations bucket
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c "influx bucket create \
		--org \$DOCKER_INFLUXDB_INIT_ORG \
		--name ${SIMUL_BUCKET:-SIMUL} \
		--token $INFLUXDB_ADMIN_TOKEN"
	
	# Create RW token on org buckets
	echo -e "InfluxDB token:"
	INFLUXDB_V2_TOKEN=$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c "influx auth create \
		--org \$DOCKER_INFLUXDB_INIT_ORG \
		--description 'RW buckets' \
		--read-buckets \
		--write-buckets \
		--token $INFLUXDB_ADMIN_TOKEN")
	echo "$INFLUXDB_V2_TOKEN"
}

backup_tdb() {
	# Get Influx admin token
	INFLUXDB_ADMIN_TOKEN=$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c 'influx auth list \
		--user $DOCKER_INFLUXDB_INIT_USERNAME \
		--hide-headers | cut -f 3')
	
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c "mkdir -p /backup/ && influx backup \
		--token $INFLUXDB_ADMIN_TOKEN \
		/backup/"
	
	DATA_FOLDER="$(grep -oP "^DATA_FOLDER=\K.*" "$ENV_FILE")"
	date="$(date +%Y%m%dT%H%M%Z)"
	mkdir -p "${DATA_FOLDER:-.}"/backups/TDB/"$date"
	
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" cp tdb:/backup/ "${DATA_FOLDER:-.}"/backups/TDB/"$date"/
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb rm -rf /backup/*
}

restore_tdb() {
	# Get Influx admin token
	INFLUXDB_ADMIN_TOKEN=$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c 'influx auth list \
		--user $DOCKER_INFLUXDB_INIT_USERNAME \
		--hide-headers | cut -f 3')
	
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c "mkdir -p /restore/"
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" cp "$RESTORE_PATH"/* tdb:/restore/
	
	# SAIH_BUCKET="$(grep -oP "^SAIH_BUCKET=\K.*" "$ENV_FILE")"
	# SIMUL_BUCKET="$(grep -oP "^SIMUL_BUCKET=\K.*" "$ENV_FILE")"
	# docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c \
	# 	"influx bucket delete ${SAIH_BUCKET:-SAIH} --token $INFLUXDB_ADMIN_TOKEN && \
	# 	influx bucket delete ${SIMUL_BUCKET:-SIMUL} --token $INFLUXDB_ADMIN_TOKEN"
	
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb sh -c "influx restore --full \
		--token $INFLUXDB_ADMIN_TOKEN \
		/restore/"
	
	docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T tdb rm -rf /restore/*
}

# The command line help #
display_help() {
	echo -e "\n Usage: $(basename $0) [option...]"
	echo
	echo "	-f, --compose-file	specify a compose file to use (default: docker-compose.yml)"
	echo "	-e, --env-file		specify an .env file to use (default: .env)"
	echo "	init {chs|odc|tdb}	initialize CHS, ODC or TDB database"
	echo "	backup {chs|odc|tdb}	backup CHS, ODC or TDB database"
	echo "	restore {chs|odc|tdb} {file|folder path}	restore CHS, ODC or TDB database from file/folder"
	echo "	-h,   --help		this help"
}

# Check if parameters options are given on the commandline #
check_params() {
	while [[ $1 ]]; do
		case "$1" in
			-f | --compose-file)
				shift
				COMPOSE_FILE="$1"
				;;
			-e | --env-file)
				shift
				ENV_FILE="$1"
				;;
			init)
				CMD=init
				shift
				DB_TYPE="$1"
				;;
			backup)
				CMD=backup
				shift
				DB_TYPE="$1"
				;;
			restore)
				CMD=restore
				shift
				DB_TYPE="$1"
				shift
				RESTORE_PATH="$1"
				;;
			-h | --help)
				display_help
				exit 0
				;;
			*)
				echo "${1} is not a valid parameter"
				display_help && exit 1
				;;
		esac
		shift
	done
}

check_files() {
	if [ -z "$ENV_FILE" ]; then
		ENV_FILE=".env"
	fi
	if [ -z "$COMPOSE_FILE" ]; then
		if [ ! -f docker-compose.yml ]; then
			echo "A compose file is needed!"
			display_help && exit 1
		else
			COMPOSE_FILE="docker-compose.yml"
		fi
	fi
}

ops_launcher() {
	case "$DB_TYPE" in
		chs | CHS | odc | ODC)
			CMD="${CMD}_rdb"
			;;
		tdb | TDB)
			CMD="${CMD}_tdb"
			;;
		*)
			echo "${DB_TYPE} is not a valid database option"
			display_help && exit 1
			;;
	esac
	eval "$CMD"
}


## INIT ##

ENV_FILE=""
COMPOSE_FILE=""

# Look for passed parameters
if [ "$#" -gt 0 ]; then
	check_params "$@"
	check_files
	ops_launcher
else
	display_help
fi
