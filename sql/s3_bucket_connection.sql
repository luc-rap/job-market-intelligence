--- This is the 'proper' way
SELECT CURRENT_ACCOUNT(),
       CURRENT_REGION(),
       CURRENT_ROLE();

-- job-market-intelligence-raw-lr is a private bucket -> hence https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration 
-- drop storage integration s3_bucket_integration

CREATE STORAGE INTEGRATION s3_bucket_integration_v2
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::176169048874:role/snowflake_role_access'
  STORAGE_ALLOWED_LOCATIONS = ('s3://job-market-intelligence-raw-lr/adzuna/')

DESC INTEGRATION s3_bucket_integration_v2

-- GRANT CREATE STAGE ON SCHEMA public TO ROLE myrole;

-- GRANT USAGE ON INTEGRATION s3_bucket_integration TO ROLE myrole;

CREATE DATABASE IF NOT EXISTS JOB_MARKET_INTELLIGENCE;
CREATE SCHEMA IF NOT EXISTS JOB_MARKET_INTELLIGENCE.RAW;

USE DATABASE JOB_MARKET_INTELLIGENCE;
USE SCHEMA RAW;

-- SHOW STORAGE INTEGRATIONS;

CREATE OR REPLACE FILE FORMAT ADZUNA_JSON_FORMAT
    TYPE = JSON
    STRIP_OUTER_ARRAY = FALSE;

CREATE OR REPLACE STAGE ADZUNA_STAGE
    URL = 's3://job-market-intelligence-raw-lr/adzuna/'
    STORAGE_INTEGRATION = S3_BUCKET_INTEGRATION_V2
    FILE_FORMAT = ADZUNA_JSON_FORMAT;

SELECT SYSTEM$VALIDATE_STORAGE_INTEGRATION(
    'S3_BUCKET_INTEGRATION_V2',
    's3://job-market-intelligence-raw-lr/adzuna/',
    'validate_all.txt',
    'all'
);

LIST @ADZUNA_STAGE;

-- Throws error at this moment

