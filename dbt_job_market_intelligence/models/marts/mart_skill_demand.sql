WITH totals AS (
    SELECT COUNT(DISTINCT JOB_ID) AS TOTAL_JOBS
    FROM {{ ref('int_adzuna_jobs_deduplicated') }}
),

skill_counts AS (
    SELECT
        SKILL,
        CATEGORY,
        COUNT(DISTINCT JOB_ID) AS JOBS_MENTIONING
    FROM {{ ref('int_job_skills') }}
    GROUP BY SKILL, CATEGORY
)

SELECT
    s.SKILL,
    s.CATEGORY,
    s.JOBS_MENTIONING,
    t.TOTAL_JOBS,
    ROUND(100 * s.JOBS_MENTIONING / t.TOTAL_JOBS, 1) AS PCT_OF_JOBS
FROM skill_counts s
CROSS JOIN totals t