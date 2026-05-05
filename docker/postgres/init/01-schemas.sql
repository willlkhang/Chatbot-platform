-- Create schemas required by the Spring Boot services.
-- Hibernate (ddl-auto=update) creates tables but NOT schemas, so we need
-- these to exist before any service tries to write.
--
-- This script only runs on first init of an empty data volume. To re-run,
-- destroy the volume:
--     docker compose down -v
--     docker compose up -d

CREATE SCHEMA IF NOT EXISTS db_user;
CREATE SCHEMA IF NOT EXISTS db_chat;
CREATE SCHEMA IF NOT EXISTS db_personalization;

-- Optional: be explicit about owner/privileges. The default user (postgres)
-- already owns these via the CREATE above, but make it readable.
GRANT ALL ON SCHEMA db_user TO postgres;
GRANT ALL ON SCHEMA db_chat TO postgres;
GRANT ALL ON SCHEMA db_personalization TO postgres;
