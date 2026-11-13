WITH raw_documents AS (

    SELECT
        RAW_DATA,
        SOURCE_FILE,
        LOADED_AT
    FROM {{ source('adzuna', 'raw_adzuna_jobs') }} -- each row in the raw table represents one JSON document, containing array of jobs

),

flattened_jobs AS (

    SELECT
        f.VALUE AS JOB,
        r.SOURCE_FILE,
        r.LOADED_AT,
        f.INDEX AS JOB_POSITION
    FROM raw_documents r,
    LATERAL FLATTEN(INPUT => r.RAW_DATA) f -- expands json array so that each job becomes its own row

)

SELECT -- extracts individual json attributes and converts them into regular SQL columns
    JOB:adref::VARCHAR AS ADREF,
    JOB:id::VARCHAR AS JOB_ID,
    JOB:title::VARCHAR AS JOB_TITLE,
    JOB:company.display_name::VARCHAR AS COMPANY_NAME,
    JOB:location.display_name::VARCHAR AS LOCATION,
    JOB:location.area[0]::VARCHAR AS COUNTRY,
    JOB:location.area[1]::VARCHAR AS STATE,
    JOB:location.area[2]::VARCHAR AS COUNTY,
    JOB:location.area[3]::VARCHAR AS CITY,
    JOB:latitude::FLOAT AS LATITUDE,
    JOB:longitude::FLOAT AS LONGITUDE,
    JOB:category.label::VARCHAR AS CATEGORY,
    JOB:salary_min::NUMBER(12,2) AS SALARY_MIN,
    JOB:salary_max::NUMBER(12,2) AS SALARY_MAX,
    JOB:redirect_url::VARCHAR AS REDIRECT_URL,
    JOB:description::VARCHAR AS DESCRIPTION,
    TRY_TO_TIMESTAMP_NTZ(JOB:created::VARCHAR) AS POSTED_AT,
    SOURCE_FILE,
    LOADED_AT,
    JOB_POSITION

FROM flattened_jobs