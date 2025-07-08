--
-- IMPORTANT: Snowflake's grant/ownership rules are designed to protect the platform and Snowflake's liability, not to protect your business or users. These rules can cause compliance/IT to expand their authority by accident. The business owns the business—do not cede control to bean-counters, lawyers, or compliance by default. Understand the difference between platform safety and business authority.
--
-- Streamlit Git Integration via API Integration
-- This script creates the Git API integration for GitHub access
-- Run as ACCOUNTADMIN (you have full privileges)
-- TEMPLATE: Replace placeholders with your actual values

-- Step 1: Create database and schema
CREATE DATABASE IF NOT EXISTS svggen_db;
USE DATABASE svggen_db;
CREATE SCHEMA IF NOT EXISTS integrations;

-- Step 2: Drop the existing secret to ensure correct type, then create it
-- REPLACE: 'your_github_username' with your actual GitHub username
-- REPLACE: 'your_github_token_here' with your actual GitHub Personal Access Token
DROP SECRET IF EXISTS svggen_git_secret;
CREATE OR REPLACE SECRET svggen_git_secret
  TYPE = PASSWORD
  USERNAME = 'your_github_username'
  PASSWORD = 'your_github_token_here';

-- Step 3: Create API integration for GitHub
USE SCHEMA svggen_db.integrations;

-- REPLACE: 'https://github.com/your_username/' with your actual GitHub URL pattern
CREATE OR REPLACE API INTEGRATION git_api_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/your_username/')
  ALLOWED_AUTHENTICATION_SECRETS = (svggen_git_secret)
  ENABLED = TRUE;

-- Step 4: Create Git repository clone
-- REPLACE: 'https://github.com/your_username/your-repo.git' with your actual repository URL
CREATE OR REPLACE GIT REPOSITORY svg_image_gen
  API_INTEGRATION = git_api_integration
  GIT_CREDENTIALS = svggen_git_secret
  ORIGIN = 'https://github.com/your_username/your-repo.git';

-- Step 5: Grant necessary privileges
GRANT USAGE ON DATABASE svggen_db TO ROLE ACCOUNTADMIN;
GRANT USAGE ON SCHEMA svggen_db.integrations TO ROLE ACCOUNTADMIN;
GRANT USAGE ON SECRET svggen_git_secret TO ROLE ACCOUNTADMIN;
GRANT USAGE ON INTEGRATION git_api_integration TO ROLE ACCOUNTADMIN;
GRANT READ ON GIT REPOSITORY svg_image_gen TO ROLE ACCOUNTADMIN;

-- Step 6: Verify the integration was created
SHOW API INTEGRATIONS LIKE 'git_api_integration';
SHOW GIT REPOSITORIES LIKE 'svg_image_gen';
