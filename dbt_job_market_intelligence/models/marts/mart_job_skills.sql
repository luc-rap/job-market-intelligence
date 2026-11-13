SELECT
    js.JOB_ID,
    js.SKILL,
    js.CATEGORY,
    j.JOB_TITLE,
    j.COMPANY_NAME,
    j.STATE,
    j.CITY,
    j.POSTED_AT,
    j.SALARY_MIN,
    j.SALARY_MAX,
    j.SALARY_IS_PREDICTED
FROM {{ ref('int_job_skills') }} js
JOIN {{ ref('int_adzuna_jobs_deduplicated') }} j
  ON js.JOB_ID = j.JOB_ID