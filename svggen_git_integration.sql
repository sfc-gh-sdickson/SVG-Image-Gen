-- Streamlit Git Integration via API Integration
USE ROLE ACCOUNTADMIN;
CREATE ROLE IF NOT EXISTS svggen_git_admin;
GRANT CREATE INTEGRATION ON ACCOUNT TO ROLE svggen_git_admin;

USE ROLE svggen_db_owner;
GRANT USAGE ON DATABASE svggen_db TO ROLE svggen_git_admin;
GRANT USAGE ON SCHEMA svggen_db.integrations TO ROLE svggen_git_admin;

USE ROLE svggen_secrets_admin;
GRANT USAGE ON SECRET svggen_git_secret TO ROLE svggen_git_admin;

USE ROLE svggen_git_admin;
USE DATABASE svggen_db;
USE SCHEMA svggen_db.integrations;

CREATE OR REPLACE API INTEGRATION git_api_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/sfc-gh-sdickson/')
  ALLOWED_AUTHENTICATION_SECRETS = (svggen_git_secret)
  ENABLED = TRUE;
