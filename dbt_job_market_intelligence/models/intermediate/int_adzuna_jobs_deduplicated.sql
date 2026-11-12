WITH ranked_jobs AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY JOB_ID
            ORDER BY LOADED_AT DESC
        ) AS RN
    FROM STG_ADZUNA_JOBS
)
SELECT *
FROM ranked_jobs
WHERE RN = 1