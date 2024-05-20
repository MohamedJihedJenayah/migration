genre_query_all = """SELECT
	c.name,
    annee AS "Année",
    mois AS "Mois",
    SUM(value) AS "Total",
    SUM(CASE WHEN genre = 'enfants' THEN value ELSE 0 END) AS "Enfants",
    SUM(CASE WHEN genre = 'femmes' THEN value ELSE 0 END) AS "Femmes",
    SUM(CASE WHEN genre = 'hommes' THEN value ELSE 0 END) AS "Hommes"
FROM
    public.genre G INNER JOIN public.country C ON C.id=G.country_id

GROUP BY
    annee, mois, c.name
ORDER BY
    annee, mois;"""

voyage_query_all = """SELECT
    c.name,
    annee AS "Année",
    mois AS "Mois",
    total AS "Total",
    value AS "Voyages"
FROM
    public.voyage G INNER JOIN public.country C ON C.id=G.country_id
WHERE
	C.code= :country

ORDER BY
    annee, mois;"""


job_query = """SELECT
    c.name,
    annee AS "Année",
    mois AS "Mois",
    SUM(value) AS "Total",
    SUM(CASE WHEN job = 'eleves' THEN value ELSE 0 END) AS "Élèves",
    SUM(CASE WHEN job = 'etudiants' THEN value ELSE 0 END) AS "Étudiants",
    SUM(CASE WHEN job = 'chomeurs' THEN value ELSE 0 END) AS "Chômeurs",
    SUM(CASE WHEN job = 'travailleurs' THEN value ELSE 0 END) AS "Travailleurs"
FROM
    public.job G INNER JOIN public.country C ON C.id=G.country_id
WHERE
	G.country_id= :country
GROUP BY
    annee, mois
ORDER BY
    annee, mois;"""