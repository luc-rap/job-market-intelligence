WITH ranked_jobs AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY JOB_ID
            ORDER BY LOADED_AT DESC
        ) AS RN
    FROM {{ ref('stg_adzuna_jobs') }}
)
SELECT * EXCLUDE (RN)
FROM ranked_jobs
WHERE RN = 1