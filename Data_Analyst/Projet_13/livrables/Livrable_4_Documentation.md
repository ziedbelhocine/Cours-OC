# Bottleneck — Amélioration du livrable Projet 6

> README de projet — analyse et fiabilisation des données de stock et de vente Bottleneck, augmentée par l'IA.

## Sommaire

- [Contexte](#contexte)
- [Traçabilité des essais IA](#traçabilité-des-essais-ia)
- [Justifications techniques](#justifications-techniques)
- [Limites & biais](#limites--biais)
- [Reproductibilité](#reproductibilité)
- [Synthèse recruteur/client](#synthèse-recruteurclient)
- [Structure du dépôt](#structure-du-dépôt)

---

## Contexte

Projet mené pour Bottleneck, marchand de vin, à la demande de Nicolas (responsable des ventes). Objectif : rapprocher et fiabiliser les données issues de 3 sources hétérogènes (ERP, extraction web, table de liaison), identifier les erreurs de données, et produire une analyse exploitable pour le comité de direction (CODIR). Détail complet du besoin et du périmètre : livrable 2.

---

## Traçabilité des essais IA

**Outil utilisé** : Claude (Anthropic), en dialogue itératif — génération de code, comparaison de variantes, diagnostic d'erreurs, recherche documentaire sourcée.

**Principe appliqué** : chaque amélioration a été obtenue par itération et vérification, pas en acceptant la première proposition. Cinq essais significatifs ont été tracés :

| # | Besoin exprimé | Variantes comparées | Décision retenue | Écarté et pourquoi |
|---|---|---|---|---|
| 1 | Homogénéiser les librairies de dataviz | `px.imshow` (Plotly) vs `sns.heatmap` (Seaborn) | `px.imshow` | Seaborn écarté : gain d'interactivité jugé supérieur au coût de migration |
| 2 | Graphique filtrable dynamiquement | Menu déroulant Plotly natif vs mini-dashboard Dash | Menu déroulant natif | Dash écarté pour cette itération : complexité disproportionnée pour un usage notebook ; conservé comme piste future |
| 3 | Empiler 3 composantes financières sur un barplot | `melt()` puis traçage vs colonnes passées directement à `y=` | Colonnes directes | `melt()` écarté : redondant, `px.bar` transforme déjà les données en interne |
| 4 | Vérifier l'accessibilité du graphique empilé | Palette rouge/orange/vert vs palette Okabe-Ito | Palette Okabe-Ito | Palette initiale écartée : confirmée illisible en protanopie par un test réel (Coblis), pas seulement présumée problématique |
| 5 | Calculer le bénéfice en tenant compte de la TVA | Hypothèse `purchase_price` en TTC vs confirmation HT par le commanditaire | Calcul HT validé | Hypothèse TTC non appliquée sans vérification métier explicite |

**Limite assumée** : ce tableau a été reconstitué a posteriori à partir de l'historique des échanges, plutôt que consigné en temps réel dans un journal dédié au fil du développement.

---

## Justifications techniques

| Choix | Justification |
|---|---|
| **Clé de jointure** : `product_id` (ERP ↔ liaison) puis `id_web` (liaison ↔ web) | Seule paire de clés disponible entre les 3 systèmes ; toute jointure directe ERP↔web est impossible, les identifiants ne correspondant pas nativement |
| **Preprocessing** : exclusion des lignes à `sku` manquant, `price` négatif, `onsale_web = 0` | Ces lignes sont soit inexploitables pour la jointure, soit correspondent à des erreurs de saisie ou des produits hors vente, non pertinents pour l'analyse commerciale |
| **Correction du stock négatif à 0 plutôt que suppression** | Le stock négatif est une erreur de saisie évidente (physiquement impossible), mais la ligne produit reste valide pour les autres indicateurs (CA, marge) — suppression injustifiée |
| **Métrique de détection d'outliers** : IQR retenu en complément du z-score | Le z-score suppose une distribution normale, non vérifiée sur la variable prix ; l'IQR ne fait pas cette hypothèse (cf. livrable 1) |
| **Seuil de TVA** : 20% | Taux standard applicable aux boissons alcoolisées en France, cohérent avec le calcul déjà présent dans le notebook initial |
| **Palette de couleurs** : Okabe-Ito (`#0072B2`, `#E69F00`, `#009E73`) | Palette conçue pour rester distinguable en daltonisme, validée par test réel plutôt que choisie par défaut |

---

## Limites & biais

**Ce qui peut casser** :
- Le script de consolidation suppose une structure de colonnes stable entre exports ERP/web mensuels ; un changement de nommage de colonne côté source casserait le script sans erreur explicite si la colonne manquante n'est pas contrôlée en amont.
- Le calcul de TVA à taux fixe (20%) ne gère pas une éventuelle diversité de taux selon les catégories de produits (ex. taux réduits) si Bottleneck en introduisait à l'avenir.

**Ce qui reste incertain** :
- La méthode IQR n'a pas été comparée à un test statistique plus poussé (chi², piste identifiée mais non expérimentée — cf. livrable 1).
- `ydata-profiling` a été comparé sur documentation mais jamais testé concrètement sur `df_merge` (cf. livrable 1, limite assumée).
- La navigation clavier du menu déroulant Plotly n'a pas été testée (limite technique connue des menus Plotly natifs, non vérifiée empiriquement ici).

**Risques d'interprétation** :
- Le graphique empilé (coût d'achat / TVA / bénéfice) agrège par catégorie ou produit selon la vue choisie ; une lecture rapide sans changer de vue peut masquer des disparités au sein d'une catégorie dominante (ex. Vin).
- L'analyse porte sur un instantané mensuel unique (31 octobre) : aucune tendance ni saisonnalité ne peut être déduite de ce seul mois.

---

## Reproductibilité

**Environnement** :
```
Python 3.12
pandas >= 2.x (testé avec la version 3.0.5, notes de version consultées le 04/08/2026)
plotly (plotly.express, plotly.graph_objects)
numpy
seaborn, matplotlib (conservés pour les exports figés)
```

**Structure du dépôt / notebook** :
```
├── notebook_bottleneck.ipynb        # Notebook initial (P6) + analyses complétées
├── consolidation_donnees.py         # Script de consolidation ERP + web + liaison
├── Livrable_1_Veille_technologique.md
├── Livrable_2_Besoin_metier_et_cahier_des_charges.md
├── Livrable_3_Organisation_du_projet.md
├── Livrable_4_Documentation.md      # Ce document
└── annexes/
    ├── kanban_notion.png
    ├── poc_barplot_empile.png
    ├── test_accessibilite_daltonisme.png
    └── Annexe_A_Retranscription_echanges_IA.md   # Retranscription détaillée des échanges IA (plots + consolidation)
```

**Instructions d'exécution** :
```python
from consolidation_donnees import consolider_donnees, afficher_rapport

df_merge, rapport = consolider_donnees("erp.xlsx", "web.xlsx", "liaison.xlsx")
afficher_rapport(rapport)
```
Le reste des analyses (CA, marges, graphiques Plotly) s'exécute directement dans le notebook à partir de `df_merge`.

**Seeds / aléatoire** : aucune opération aléatoire n'intervient dans ce projet (pas de modélisation, d'échantillonnage aléatoire ni de simulation) — la reproductibilité ne dépend donc d'aucun seed à fixer.

---

## Synthèse recruteur/client

**Résultats** : consolidation fiabilisée de 3 sources de données hétérogènes, avec un rapport d'anomalies systématique (doublons, `sku` manquants, clés non appariées) ; au moins 8 erreurs de données identifiées et documentées, conformément à la demande initiale du commanditaire. Production d'indicateurs de pilotage (CA, marge, rotation de stock, tops/flops) et de deux POC de visualisation interactive validés par un test d'accessibilité réel.

**Impact** : le projet transforme une analyse ponctuelle et manuelle en un processus partiellement automatisé et documenté, réduisant le risque d'erreur silencieuse lors des futurs rapprochements de données mensuels. Les graphiques interactifs livrés permettent une exploration autonome par des utilisateurs non techniques, réduisant la dépendance à l'analyste pour chaque nouvelle question business.

**Recommandations** :
1. Mettre en place un dictionnaire de données partagé entre l'ERP et le site web pour réduire durablement les erreurs de jointure.
2. Industrialiser le POC dataviz en un vrai dashboard Dash pour permettre des filtres croisés (catégorie et tri combinés), au-delà de la limite actuelle des menus Plotly natifs.
3. Tester `ydata-profiling` en amont du script métier pour accélérer l'exploration initiale sur de futurs jeux de données.

**Prochaines étapes** :
- Reconduire le script de consolidation sur les extractions des mois suivants pour valider sa robustesse dans la durée.
- Tester la piste stats non explorée (chi²) pour renforcer l'axe interprétabilité de la veille.
- Vérifier la navigation clavier des composants interactifs avant tout déploiement élargi.
