-- Query 1: Full county risk ranking with health and social context
SELECT
    c.county_name,
    r.risk_rank,
    r.composite_risk_score,
    h.diabetes_rate,
    h.obesity_rate,
    h.hypertension_rate,
    s.svi_score,
    s.poverty_rate,
    r.primary_risk_driver
FROM counties c
JOIN health_indicators h ON c.fips = h.fips
JOIN social_vulnerability s ON c.fips = s.fips
JOIN risk_scores r ON c.fips = r.fips
ORDER BY r.risk_rank;


-- Query 2: Top 10 highest-risk counties
SELECT
    c.county_name,
    r.composite_risk_score,
    r.risk_rank,
    r.primary_risk_driver,
    s.poverty_rate,
    s.svi_score
FROM counties c
JOIN risk_scores r ON c.fips = r.fips
JOIN social_vulnerability s ON c.fips = s.fips
ORDER BY r.risk_rank
LIMIT 10;


-- Query 3: Counties where both health burden and social vulnerability are high
-- These are the counties that need the most urgent intervention
SELECT
    c.county_name,
    c.population,
    r.composite_risk_score,
    h.diabetes_rate,
    h.obesity_rate,
    s.poverty_rate,
    s.svi_score,
    r.primary_risk_driver
FROM counties c
JOIN health_indicators h ON c.fips = h.fips
JOIN social_vulnerability s ON c.fips = s.fips
JOIN risk_scores r ON c.fips = r.fips
WHERE r.high_risk_flag = 1
ORDER BY r.composite_risk_score DESC;


-- Query 4: Correlation view between poverty and diabetes across all counties
-- Shows how economic deprivation maps to chronic disease burden
SELECT
    c.county_name,
    s.poverty_rate,
    h.diabetes_rate,
    h.obesity_rate,
    s.uninsured_rate,
    r.composite_risk_score
FROM counties c
JOIN health_indicators h ON c.fips = h.fips
JOIN social_vulnerability s ON c.fips = s.fips
JOIN risk_scores r ON c.fips = r.fips
ORDER BY s.poverty_rate DESC;


-- Query 5: Average health indicators grouped by SVI quartile
-- Shows how health outcomes worsen as social vulnerability increases
SELECT
    CASE
        WHEN s.svi_score >= 0.75 THEN 'High vulnerability (Q4)'
        WHEN s.svi_score >= 0.50 THEN 'Medium-high (Q3)'
        WHEN s.svi_score >= 0.25 THEN 'Medium-low (Q2)'
        ELSE 'Low vulnerability (Q1)'
    END AS vulnerability_tier,
    COUNT(*) AS county_count,
    ROUND(AVG(h.diabetes_rate), 2)     AS avg_diabetes,
    ROUND(AVG(h.obesity_rate), 2)      AS avg_obesity,
    ROUND(AVG(h.hypertension_rate), 2) AS avg_hypertension,
    ROUND(AVG(s.poverty_rate), 2)      AS avg_poverty
FROM counties c
JOIN health_indicators h ON c.fips = h.fips
JOIN social_vulnerability s ON c.fips = s.fips
GROUP BY vulnerability_tier
ORDER BY AVG(s.svi_score) DESC;


-- Query 6: Primary risk driver distribution across all counties
SELECT
    primary_risk_driver,
    COUNT(*) AS county_count,
    ROUND(AVG(composite_risk_score), 4) AS avg_risk_score
FROM risk_scores
GROUP BY primary_risk_driver
ORDER BY county_count DESC;