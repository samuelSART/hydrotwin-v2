--
-- Hydrotwin: CHS & ODC databases initialization
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

\set db_admin `echo "\"$POSTGRES_USER\""`
\set chs_db `echo "\"$CHS_DB_NAME\""`
\set chs_db_pass `echo "'$CHS_DB_PASSWORD'"`
\set odc_db `echo "\"$ODC_DB_NAME\""`
\set odc_db_pass `echo "'$ODC_DB_PASSWORD'"`

CREATE USER :chs_db WITH PASSWORD :chs_db_pass;
CREATE USER :odc_db WITH PASSWORD :odc_db_pass;
ALTER USER :odc_db SUPERUSER;

DROP DATABASE IF EXISTS :chs_db;
DROP DATABASE IF EXISTS :odc_db;

CREATE DATABASE :chs_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';
CREATE DATABASE :odc_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';

ALTER DATABASE :chs_db OWNER TO :db_admin;
GRANT ALL ON DATABASE :chs_db TO :chs_db;
ALTER DATABASE :odc_db OWNER TO :db_admin;
GRANT ALL ON DATABASE :odc_db TO :odc_db;


\connect :chs_db

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: aquifer; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.aquifer (
    code character varying NOT NULL,
    superposition character varying
);


ALTER TABLE public.aquifer OWNER TO :db_admin;

--
-- Name: control_point; Type: TABLE; Schema: public; Owner: db_admin
--

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


ALTER TABLE public.control_point OWNER TO :db_admin;

--
-- Name: demand_unit; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.demand_unit (
    code character varying NOT NULL,
    type character varying NOT NULL,
    geometry public.geometry,
    name character varying,
    surface numeric
);


ALTER TABLE public.demand_unit OWNER TO :db_admin;

--
-- Name: demand_water_relation; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.demand_water_relation (
    water_body character varying NOT NULL,
    demand_unit character varying NOT NULL
);


ALTER TABLE public.demand_water_relation OWNER TO :db_admin;

--
-- Name: environmental_flow; Type: TABLE; Schema: public; Owner: admin
--

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


ALTER TABLE public.environmental_flow OWNER TO :db_admin;

--
-- Name: dam; Type: TABLE; Schema: public; Owner: db_admin
--

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

ALTER TABLE public.dam OWNER TO :db_admin;

--
-- Name: measurement_point; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.measurement_point (
    code character varying NOT NULL,
    control_point character varying,
    denomination character varying NOT NULL,
    location public.geometry NOT NULL,
    description character varying NOT NULL,
    typology character varying
);


ALTER TABLE public.measurement_point OWNER TO :db_admin;

--
-- Name: superficial; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.superficial (
    code character varying NOT NULL,
    eumspfcod character varying NOT NULL
);


ALTER TABLE public.superficial OWNER TO :db_admin;

--
-- Name: underground; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.underground (
    code character varying NOT NULL,
    eumsbtcod character varying
);


ALTER TABLE public.underground OWNER TO :db_admin;

--
-- Name: variable; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.variable (
    code character varying NOT NULL,
    measurement_point character varying NOT NULL,
    typology character varying NOT NULL,
    description character varying NOT NULL
);


ALTER TABLE public.variable OWNER TO :db_admin;

--
-- Name: water_body; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.water_body (
    code character varying NOT NULL,
    type character varying NOT NULL,
    geometry public.geometry,
    name character varying NOT NULL,
    category character varying NOT NULL,
    generator_flow numeric
);


ALTER TABLE public.water_body OWNER TO :db_admin;

--
-- Name: water_body_relation; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.water_body_relation (
    water_body_1 character varying NOT NULL,
    water_body_2 character varying NOT NULL
);


ALTER TABLE public.water_body_relation OWNER TO :db_admin;

--
-- Name: crop; Type: TABLE; Schema: public; Owner: admin
--

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


ALTER TABLE public.crop OWNER TO :db_admin;

--
-- Name: system_unit; Type: TABLE; Schema: public; Owner: db_admin
--

CREATE TABLE public.system_unit (
    zone character varying NOT NULL,
    name character varying NOT NULL,
    geometry public.geometry,
    ha numeric
);


ALTER TABLE public.system_unit OWNER TO :db_admin;


--
-- Data for Name: aquifer; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.aquifer (code, superposition) FROM '/docker-entrypoint-initdb.d/aquifer.dat';

--
-- Data for Name: control_point; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.control_point (code, denomination, municipality, province, typology, description, water_body, location) FROM '/docker-entrypoint-initdb.d/control_point.dat';

--
-- Data for Name: demand_unit; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.demand_unit (code, type, geometry, name, surface) FROM '/docker-entrypoint-initdb.d/demand_unit.dat';

--
-- Data for Name: demand_water_relation; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.demand_water_relation (water_body, demand_unit) FROM '/docker-entrypoint-initdb.d/demand_water_relation.dat';

--
-- Data for Name: environmental_flow; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.environmental_flow (variable, typology, water_body, oct_dic, ene_mar, abr_jun, jul_sep, sistema, masa_estrategica, oct_dic_seq, ene_mar_seq, abr_jun_seq, jul_sep_seq) FROM '/docker-entrypoint-initdb.d/environmental_flow.dat';

--
-- Data for Name: dam; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.dam (water_body, variable, typology, max_oct_dic, max_ene_mar, max_abr_jun, max_jul_sep, min_oct_dic, min_ene_mar, min_abr_jun, min_jul_sep) FROM '/docker-entrypoint-initdb.d/dam.dat';

--
-- Data for Name: measurement_point; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.measurement_point (code, control_point, denomination, location, description, typology) FROM '/docker-entrypoint-initdb.d/measurement_point.dat';

--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM '/docker-entrypoint-initdb.d/spatial_ref_sys.dat';

--
-- Data for Name: superficial; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.superficial (code, eumspfcod) FROM '/docker-entrypoint-initdb.d/superficial.dat';

--
-- Data for Name: underground; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.underground (code, eumsbtcod) FROM '/docker-entrypoint-initdb.d/underground.dat';

--
-- Data for Name: variable; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.variable (code, measurement_point, typology, description) FROM '/docker-entrypoint-initdb.d/variable.dat';

--
-- Data for Name: water_body; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.water_body (code, type, geometry, name, category, generator_flow) FROM '/docker-entrypoint-initdb.d/water_body.dat';

--
-- Data for Name: water_body_relation; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.water_body_relation (water_body_1, water_body_2) FROM '/docker-entrypoint-initdb.d/water_body_relation.dat';

--
-- Data for Name: crop; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.crop (demand_unit_code, cereales_invierno, arroz, cereales_primavera, tuberculos, horticolas_protegido, horticolas_libre, citricos, frutales_fruto_carnoso, almendro, vinedo_vino, vinedo_mesa, olivar, total) FROM '/docker-entrypoint-initdb.d/crop.dat';


--
-- Data for Name: system_unit; Type: TABLE DATA; Schema: public; Owner: db_admin
--

COPY public.system_unit (zone, name, geometry, ha) FROM '/docker-entrypoint-initdb.d/system_unit.dat';


--
-- Name: aquifer aquifer_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.aquifer
    ADD CONSTRAINT aquifer_pkey PRIMARY KEY (code);

--
-- Name: demand_unit code; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.demand_unit
    ADD CONSTRAINT code UNIQUE (code);

--
-- Name: control_point control_point_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.control_point
    ADD CONSTRAINT control_point_pkey PRIMARY KEY (code);

--
-- Name: demand_unit demand_unit_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.demand_unit
    ADD CONSTRAINT demand_unit_pkey PRIMARY KEY (code);

--
-- Name: demand_water_relation demand_water_relation_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.demand_water_relation
    ADD CONSTRAINT demand_water_relation_pkey PRIMARY KEY (water_body, demand_unit);

--
-- Name: measurement_point measurement_point_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.measurement_point
    ADD CONSTRAINT measurement_point_pkey PRIMARY KEY (code);

--
-- Name: superficial superficial_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.superficial
    ADD CONSTRAINT superficial_pkey PRIMARY KEY (code);

--
-- Name: underground underground_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.underground
    ADD CONSTRAINT underground_pkey PRIMARY KEY (code);

--
-- Name: variable variable_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.variable
    ADD CONSTRAINT variable_pkey PRIMARY KEY (code, typology);

--
-- Name: water_body water_body_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.water_body
    ADD CONSTRAINT water_body_pkey PRIMARY KEY (code);

--
-- Name: water_body_relation water_body_relation_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.water_body_relation
    ADD CONSTRAINT water_body_relation_pkey PRIMARY KEY (water_body_1, water_body_2);

--
-- Name: system_unit system_unit_pkey; Type: CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.system_unit
    ADD CONSTRAINT system_unit_pkey PRIMARY KEY (zone);



--
-- Name: aquifer aquifer_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.aquifer
    ADD CONSTRAINT aquifer_fkey FOREIGN KEY (code) REFERENCES public.water_body(code) NOT VALID;

--
-- Name: control_point control_point_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.control_point
    ADD CONSTRAINT control_point_fkey FOREIGN KEY (water_body) REFERENCES public.water_body(code) NOT VALID;

--
-- Name: demand_water_relation demand_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.demand_water_relation
    ADD CONSTRAINT demand_fkey FOREIGN KEY (demand_unit) REFERENCES public.demand_unit(code) NOT VALID;

--
-- Name: measurement_point measurement_point_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.measurement_point
    ADD CONSTRAINT measurement_point_fkey FOREIGN KEY (control_point) REFERENCES public.control_point(code) NOT VALID;

--
-- Name: superficial superficial_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.superficial
    ADD CONSTRAINT superficial_fkey FOREIGN KEY (code) REFERENCES public.water_body(code) NOT VALID;

--
-- Name: underground underground_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.underground
    ADD CONSTRAINT underground_fkey FOREIGN KEY (code) REFERENCES public.water_body(code) NOT VALID;

--
-- Name: variable variable_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.variable
    ADD CONSTRAINT variable_fkey FOREIGN KEY (measurement_point) REFERENCES public.measurement_point(code) NOT VALID;

--
-- Name: environmental_flow variable_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.environmental_flow
    ADD CONSTRAINT variable_fkey FOREIGN KEY (variable, typology) REFERENCES public.variable(code, typology) NOT VALID;

--
-- Name: dam dam_variable_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.dam
    ADD CONSTRAINT dam_variable_fkey FOREIGN KEY (variable, typology) REFERENCES public.variable(code, typology);

--
-- Name: water_body_relation water_body_1_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.water_body_relation
    ADD CONSTRAINT water_body_1_fkey FOREIGN KEY (water_body_1) REFERENCES public.water_body(code) NOT VALID;

--
-- Name: water_body_relation water_body_2_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.water_body_relation
    ADD CONSTRAINT water_body_2_fkey FOREIGN KEY (water_body_2) REFERENCES public.water_body(code) NOT VALID;

--
-- Name: environmental_flow water_body_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.environmental_flow
    ADD CONSTRAINT water_body_fkey FOREIGN KEY (water_body) REFERENCES public.water_body(code) NOT VALID;

--
-- Name: dam dam_water_body_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.dam
    ADD CONSTRAINT dam_water_body_fkey FOREIGN KEY (water_body) REFERENCES public.water_body(code);

--
-- Name: demand_water_relation water_fkey; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.demand_water_relation
    ADD CONSTRAINT water_fkey FOREIGN KEY (water_body) REFERENCES public.water_body(code) NOT VALID;

--
-- Name: crop fkey_crop_demand_unit; Type: FK CONSTRAINT; Schema: public; Owner: db_admin
--

ALTER TABLE ONLY public.crop
    ADD CONSTRAINT fkey_crop_demand_unit FOREIGN KEY (demand_unit_code) REFERENCES public.demand_unit(code);

--
-- Name: DATABASE chs_db; Type: ACL; Schema: -; Owner: db_admin
--

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO :chs_db;

