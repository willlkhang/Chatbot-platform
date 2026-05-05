--init tables for docker database
CREATE SCHEMA IF NOT EXISTS db_user;
CREATE SCHEMA IF NOT EXISTS db_chat;
CREATE SCHEMA IF NOT EXISTS db_personalization;


GRANT ALL ON SCHEMA db_user TO postgres;
GRANT ALL ON SCHEMA db_chat TO postgres;
GRANT ALL ON SCHEMA db_personalization TO postgres;
