genre_query = """SELECT
    annee AS "Année",
    mois AS "Mois",
    SUM(value) AS "Total",
    SUM(CASE WHEN genre = 'enfants' THEN value ELSE 0 END) AS "Enfants",
    SUM(CASE WHEN genre = 'femmes' THEN value ELSE 0 END) AS "Femmes",
    SUM(CASE WHEN genre = 'hommes' THEN value ELSE 0 END) AS "Hommes"
FROM
    public.genre G INNER JOIN public.country C ON C.id=G.country_id
WHERE
	C.code= :country
GROUP BY
    annee, mois
ORDER BY
    annee, mois;"""

etat_query = """SELECT
    annee AS "Année",
    mois AS "Mois",
    SUM(CASE WHEN etat = 'morts' THEN value ELSE 0 END) AS "morts",
    SUM(CASE WHEN etat = 'migrants_interceptes' THEN value ELSE 0 END) AS "migrants_interceptes",
    SUM(CASE WHEN etat = 'personnes_arrivees' THEN value ELSE 0 END) AS "personnes_arrivees"
FROM
    public.etatmigrant G INNER JOIN public.country C ON C.id=G.country_id
WHERE
	C.code= :country
GROUP BY
    annee, mois
ORDER BY
    annee, mois;"""


def get_migration_moyen_query(migration_moyens):
    base_query = """
    SELECT 
        annee AS "Année", 
        mois AS "Mois", 
        total AS "Total",
        SUM(value) AS "voyages",
    """
    case_statements = ""
    for moyen_name in migration_moyens:
        case_statements += f"    SUM(CASE WHEN moyen = '{moyen_name}' THEN value ELSE 0 END) AS \"{moyen_name}\",\n"

    # Remove the trailing comma from the last CASE statement
    case_statements = case_statements.rstrip(",\n")

    # Finish the query
    final_query = base_query + case_statements + """
    FROM public.migration_moyen MM INNER JOIN public.country C ON C.id=MM.country_id
    WHERE
    C.code= :country
    GROUP BY annee, mois, total
    ORDER BY annee, mois;
    """

    return final_query


def get_population_query(migration_moyens):
    base_query = """
    SELECT 
        city AS "Region", 
    """
    case_statements = ""
    for moyen_name in migration_moyens:
        case_statements += f"    SUM(CASE WHEN annee = '{moyen_name}' THEN value ELSE 0 END) AS \"{moyen_name}\",\n"

    # Remove the trailing comma from the last CASE statement
    case_statements = case_statements.rstrip(",\n")

    # Finish the query
    final_query = base_query + case_statements + """
    FROM public.population PO INNER JOIN public.country C ON C.id=PO.country_id
    WHERE
    C.code= :country
    GROUP BY city
    ORDER BY city;
    """

    return final_query


voyage_query = """SELECT
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

# job_query = """SELECT
#     annee AS "Année",
#     mois AS "Mois",
#     SUM(value) AS "Total",
#     SUM(CASE WHEN job = 'eleves' THEN value ELSE 0 END) AS "Élèves",
#     SUM(CASE WHEN job = 'etudiants' THEN value ELSE 0 END) AS "Étudiants",
#     SUM(CASE WHEN job = 'chomeurs' THEN value ELSE 0 END) AS "Chômeurs",
#     SUM(CASE WHEN job = 'travailleurs' THEN value ELSE 0 END) AS "Travailleurs"
# FROM
#     public.job G INNER JOIN public.country C ON C.id=G.country_id
# WHERE
# 	C.code= :country
# GROUP BY
#     annee, mois
# ORDER BY
#     annee, mois;"""

job_query = """SELECT
    annee AS "Année",
    mois AS "Mois",
    SUM(value) AS "Total",
    SUM(CASE WHEN job = 'eleves' THEN value ELSE 0 END) AS "Élèves",
    SUM(CASE WHEN job = 'etudiants' THEN value ELSE 0 END) AS "Étudiants",
    SUM(CASE WHEN job = 'chomeurs' THEN value ELSE 0 END) AS "Chômeurs",
    SUM(CASE WHEN job = 'travailleurs' THEN value ELSE 0 END) AS "Travailleurs"
FROM
    public.job G 
WHERE
	G.country_id= :country
GROUP BY
    annee, mois
ORDER BY
    annee, mois;"""


def get_intercepter_query(migration_moyens):
    base_query = """
    SELECT 
        annee AS "Année", 
        total AS "Total",
    """
    case_statements = ""
    for moyen_name in migration_moyens:
        case_statements += f"    SUM(CASE WHEN city = '{moyen_name}' THEN value ELSE 0 END) AS \"{moyen_name}\",\n"

    # Remove the trailing comma from the last CASE statement
    case_statements = case_statements.rstrip(",\n")

    # Finish the query
    final_query = base_query + case_statements + """
    FROM public.intercepter MM INNER JOIN public.country C ON C.id=MM.country_id
    WHERE
    C.code= :country

    GROUP BY annee, total
    ORDER BY annee;
    """

    return final_query