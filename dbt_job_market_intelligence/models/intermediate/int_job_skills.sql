SELECT
    j.JOB_ID,
    s.SKILL,
    s.CATEGORY
FROM {{ ref('int_adzuna_jobs_deduplicated') }} j
JOIN {{ ref('skills') }} s
  ON REGEXP_LIKE(
       j.DESCRIPTION,
       '.*\\b(' || s.PATTERN || ')\\b.*',
       'is'
     )