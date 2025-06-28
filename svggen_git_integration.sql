--
-- IMPORTANT: Snowflake's grant/ownership rules are designed to protect the platform and Snowflake's liability, not to protect your business or users. These rules can cause compliance/IT to expand their authority by accident. The business owns the business—do not cede control to bean-counters, lawyers, or compliance by default. Understand the difference between platform safety and business authority.
--
-- Streamlit Git Integration via API Integration
-- This script creates the Git API integration for GitHub access
-- Run as ACCOUNTADMIN (you have full privileges)

-- Step 1: Create database and schema
CREATE DATABASE IF NOT EXISTS svggen_db;
USE DATABASE svggen_db;
CREATE SCHEMA IF NOT EXISTS integrations;

-- Step 2: Create secret for GitHub token
CREATE SECRET IF NOT EXISTS svggen_git_secret
  TYPE = GENERIC_STRING
  SECRET_STRING = 'your_github_token_here';  -- Replace with actual GitHub token

-- Step 3: Create API integration for GitHub
USE SCHEMA svggen_db.integrations;

CREATE OR REPLACE API INTEGRATION git_api_integration
  API_PROVIDER = custom_api_provider
  API_ALLOWED_PREFIXES = ('https://api.github.com/')
  ALLOWED_AUTHENTICATION_SECRETS = (svggen_git_secret)
  ENABLED = TRUE;

-- Step 4: Grant usage to current role
GRANT USAGE ON INTEGRATION git_api_integration TO ROLE ACCOUNTADMIN;

-- Step 5: Verify the integration was created
SHOW API INTEGRATIONS LIKE 'git_api_integration';
