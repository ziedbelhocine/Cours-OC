1. Nombre total d’appartements vendus au 1er semestre 2020.

SELECT 
COUNT(vente.id) AS nb_ventes
FROM vente
JOIN bien ON vente.id_bien = bien.id
WHERE date >= '2020-01-01' AND date <= '2020-06-30'
AND bien.type_local = 'Appartement' ;

2. Le nombre de ventes d’appartement par région pour le 1er semestre
2020.

SELECT 
COUNT(vente.id) AS nb_ventes,
region.nom AS region
FROM vente 
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
JOIN region ON departement.id_region = region.id
WHERE date >= '2020-01-01' AND date <= '2020-06-30'
AND bien.type_local = 'Appartement'
group BY region.nom
ORDER BY nb_ventes DESC;

3. Proportion des ventes d’appartements par le nombre de pièces.

SELECT
bien.nb_pieces AS nb_pieces,
ROUND(COUNT(CASE WHEN bien.type_local = 'Appartement' THEN 1 END) *100.00 / COUNT(vente.id), 2) AS proportion_appartements_pourc
FROM
vente
JOIN bien ON vente.id_bien = bien.id
GROUP BY
bien.nb_pieces
ORDER BY
bien.nb_pieces DESC

SELECT 
  ROUND(appartement.nb_ventes * 100.0 / tous_types.nb_ventes, 2)  AS proportion_appartements_pourc,
  appartement.nb_ventes AS nb_ventes_appartement,
  tous_types.nb_ventes AS nb_ventes_tous_types,
  appartement.nb_pieces AS nb_pieces
FROM
  ( SELECT 
        COUNT(vente.id) AS nb_ventes,
        bien.nb_pieces AS nb_pieces
    FROM vente 
    JOIN bien ON vente.id_bien = bien.id
    WHERE bien.type_local = 'Appartement'
    GROUP BY bien.nb_pieces
  ) AS appartement
JOIN
  ( SELECT 
        COUNT(vente.id) AS nb_ventes,
        bien.nb_pieces AS nb_pieces
    FROM vente 
    JOIN bien ON vente.id_bien = bien.id
    GROUP BY bien.nb_pieces
  ) AS tous_types ON appartement.nb_pieces = tous_types.nb_pieces
ORDER BY proportion_appartements_pourc DESC;


4. Liste des 10 départements où le prix du mètre carré est le plus élevé.

SELECT
ROUND(AVG(vente.valeur/bien.surface_carrez), 2) AS prix_m2,
departement.nom AS departement
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
GROUP BY departement.nom
ORDER BY prix_m2 DESC LIMIT 10;

SELECT 
ROUND(SUM(vente.valeur)/ SUM(bien.surface_carrez)) AS prix_m2,
departement.nom AS departement
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
WHERE vente.valeur != ''
AND bien.surface_carrez != 0
GROUP BY departement.nom
ORDER BY 
    prix_m2 DESC LIMIT 10;

5. Prix moyen du mètre carré d’une maison en Île-de-France.

SELECT
region.nom AS region,
ROUND(AVG(vente.valeur / bien.surface_carrez), 2) AS prix_moyen_m2_maison
FROM
vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
JOIN region ON departement.id_region = region.id
WHERE
region.nom = 'Ile-de-France'
AND bien.type_local = 'Maison'
AND vente.valeur != ''
AND bien.surface_carrez != 0
GROUP BY region.nom;

SELECT 
region.nom AS region,
ROUND(SUM(vente.valeur) / SUM(bien.surface_carrez)) AS prix_moyen_m2_maison
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
JOIN region ON departement.id_region = region.id
WHERE region.nom = 'Ile-de-France'
AND bien.type_local = 'Maison'
AND vente.valeur != ''
AND bien.surface_carrez != 0
GROUP BY region.nom;


6. Liste des 10 appartements les plus chers avec la région et le nombre
de mètres carrés.

SELECT 
valeur,
bien.surface_carrez,
region.nom
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
JOIN region ON departement.id_region = region.id
WHERE vente.valeur != ''
ORDER BY
valeur DESC LIMIT 10;

7. Taux d’évolution du nombre de ventes entre le premier et le second
trimestre de 2020.

SELECT 
ROUND((deuxieme_trimestre.nb_ventes - premier_trimestre.nb_ventes)*100.0 / premier_trimestre.nb_ventes, 2)  AS taux_evolution_en_pourcent
FROM
  ( SELECT 
        COUNT(vente.id) AS nb_ventes
        FROM vente 
        WHERE date < '2020-04-01')
    AS premier_trimestre,
  ( SELECT 
        COUNT(vente.id) AS nb_ventes
        FROM vente 
        WHERE date >= '2020-04-01')
    AS deuxieme_trimestre


8. Le classement des régions par rapport au prix au mètre carré des
appartement de plus de 4 pièces.

SELECT 
region.nom AS region,
ROUND(AVG(vente.valeur / bien.surface_carrez), 2) AS prix_moyen_m2_appartement
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
JOIN region ON departement.id_region = region.id
WHERE bien.nb_pieces > 4
AND bien.type_local = 'Appartement'
AND vente.valeur != ''
AND bien.surface_carrez != 0
GROUP BY region.nom
ORDER BY prix_moyen_m2_appartement DESC;

SELECT 
region.nom AS region,
ROUND(SUM(vente.valeur) / SUM(bien.surface_carrez), 2) AS prix_moyen_m2_appartement
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
JOIN region ON departement.id_region = region.id
WHERE bien.nb_pieces > 4
AND bien.type_local = 'Appartement'
GROUP BY region.nom
ORDER BY prix_moyen_m2_appartement DESC;

9. Liste des communes ayant eu au moins 50 ventes au 1er trimestre

SELECT 
commune.code_dep_code_com,
commune.nom,
COUNT(vente.id) AS nb_ventes
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
WHERE vente.date < '2020-04-01'
GROUP BY commune.code_dep_code_com
HAVING COUNT(vente.id) >= 50
ORDER BY nb_ventes DESC;

10. Différence en pourcentage du prix au mètre carré entre un
appartement de 2 pièces et un appartement de 3 pièces.

SELECT
ROUND(((t3.prix_moyen - t2.prix_moyen) / t2.prix_moyen) * 100, 2) AS difference_pourcentage
FROM
(SELECT
ROUND(AVG(vente.valeur / bien.surface_carrez), 2) AS prix_moyen
FROM vente
JOIN bien ON vente.id_bien = bien.id
WHERE bien.type_local = 'Appartement'
AND bien.nb_pieces = 2) AS t2,
(SELECT
ROUND(AVG(vente.valeur / bien.surface_carrez), 2) AS prix_moyen
FROM vente
JOIN bien ON vente.id_bien = bien.id
WHERE bien.type_local = 'Appartement'
AND bien.nb_pieces = 3) AS t3;


11. Les moyennes de valeurs foncières pour le top 3 des communes des
départements 6, 13, 33, 59 et 69.

SELECT
id,
departement,
commune,
moyenne_valeur
FROM
(SELECT
departement.id AS id,
departement.nom AS departement,
commune.nom AS commune,
ROUND(AVG(valeur), 2) AS moyenne_valeur
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
WHERE departement.id = '6'
GROUP BY departement.id,
commune.nom
ORDER BY moyenne_valeur DESC
LIMIT 3)
UNION
SELECT
id,
departement,
commune,
moyenne_valeur
FROM
(SELECT
departement.id AS id,
departement.nom AS departement,
commune.nom AS commune,
ROUND(AVG(valeur), 2) AS moyenne_valeur
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
WHERE departement.id = '13'
GROUP BY departement.id,
commune.nom
ORDER BY moyenne_valeur DESC
LIMIT 3)
UNION
SELECT
id,
departement,
commune,
moyenne_valeur
FROM
(SELECT
departement.id AS id,
departement.nom AS departement,
commune.nom AS commune,
ROUND(AVG(valeur), 2) AS moyenne_valeur
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
WHERE departement.id = '33'
GROUP BY departement.id,
commune.nom
ORDER BY moyenne_valeur DESC
LIMIT 3)
UNION
SELECT
id,
departement,
commune,
moyenne_valeur
FROM
(SELECT
departement.id AS id,
departement.nom AS departement,
commune.nom AS commune,
ROUND(AVG(valeur), 2) AS moyenne_valeur
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
WHERE departement.id = '59'
GROUP BY departement.id,
commune.nom
ORDER BY moyenne_valeur DESC
LIMIT 3)
UNION
SELECT
id,
departement,
commune,
moyenne_valeur
FROM
(SELECT
departement.id AS id,
departement.nom AS departement,
commune.nom AS commune,
ROUND(AVG(valeur), 2) AS moyenne_valeur
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
JOIN departement ON commune.id_dep = departement.id
WHERE departement.id = '69'
GROUP BY departement.id,
commune.nom
ORDER BY moyenne_valeur DESC
LIMIT 3)
ORDER BY moyenne_valeur ;


WITH classement AS (
    SELECT 
        departement.id,
        departement.nom AS departement,
        commune.nom AS commune,
        ROUND(AVG(valeur), 2) AS moyenne_valeur,
        COUNT(vente.id) AS nb_ventes,
        ROW_NUMBER() OVER (
            PARTITION BY departement.id 
            ORDER BY COUNT(vente.id) DESC
        ) as rang
    FROM vente
    JOIN bien ON vente.id_bien = bien.id
    JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
    JOIN departement ON commune.id_dep = departement.id
    WHERE departement.id IN ('6', '13', '33', '59', '69')
    GROUP BY departement.id, commune.nom
)
SELECT departement, commune, moyenne_valeur, nb_ventes, rang
FROM classement
WHERE rang <= 3
ORDER BY departement, rang;

WITH classement AS (
    SELECT 
        departement.id,
        departement.nom AS departement,
        commune.nom AS commune,
        ROUND(AVG(valeur), 2) AS moyenne_valeur,
        ROW_NUMBER() OVER (
            PARTITION BY departement.id 
            ORDER BY ROUND(AVG(valeur), 2) DESC
        ) as rang
    FROM vente
    JOIN bien ON vente.id_bien = bien.id
    JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
    JOIN departement ON commune.id_dep = departement.id
    WHERE departement.id IN ('6', '13', '33', '59', '69')
    GROUP BY departement.id, commune.nom
)
SELECT departement, commune, moyenne_valeur, rang
FROM classement
WHERE rang <= 3
ORDER BY departement, rang;

12. Les 20 communes avec le plus de transactions pour 1000 habitants
pour les communes qui dépassent les 10 000 habitants.

SELECT 
commune.code_dep_code_com,
commune.nom as commune,
ROUND(COUNT(vente.id) / (commune.population/1000.00), 2) AS transactions_pour_1000_hab
FROM vente
JOIN bien ON vente.id_bien = bien.id
JOIN commune ON bien.code_dep_code_com = commune.code_dep_code_com
WHERE commune.population >= 10000
GROUP BY commune.code_dep_code_com
ORDER BY transactions_pour_1000_hab DESC LIMIT 20;
