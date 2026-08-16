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

Voir annexes des échanges avec Claude et GitHub Copilot
---

## Justifications techniques

| Choix | Justification |
|---|---|
| **Clé de jointure** : `product_id` (ERP ↔ liaison) puis `id_web` (liaison ↔ web) | Seule paire de clés disponible entre les 3 systèmes ; toute jointure directe ERP↔web est impossible, les identifiants ne correspondant pas nativement |
| **Preprocessing** : exclusion des lignes à `sku` manquant, `price` négatif, `onsale_web = 0` | Ces lignes sont soit inexploitables pour la jointure, soit correspondent à des erreurs de saisie ou des produits hors vente, non pertinents pour l'analyse commerciale |
| **Correction du stock négatif à 0 plutôt que suppression** | Le stock négatif est une erreur de saisie évidente (physiquement impossible), mais la ligne produit reste valide pour les autres indicateurs (CA, marge) — suppression injustifiée |
| **Métrique de détection d'outliers** : IQR retenu en complément du z-score | Le z-score suppose une distribution normale, non vérifiée sur la variable prix ; l'IQR ne fait pas cette hypothèse |
| **Seuil de TVA** : 20% | Taux standard applicable aux boissons alcoolisées en France, cohérent avec le calcul déjà présent dans le notebook initial |
| **Palette de couleurs** : Okabe-Ito (`#0072B2`, `#E69F00`, `#009E73`) | Palette conçue pour rester distinguable en daltonisme, validée par test réel plutôt que choisie par défaut |

**Preuve du test d'accessibilité** : simulation de vision daltonienne (protanopie) via [Coblis — Color Blindness Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/) sur le graphique Plotly retenu (cf. livrable 1, section 4.1).

| Avant correction (protanopie simulée) | Après correction (palette Okabe-Ito) |


*Avant correction, les 3 composantes (coût d'achat, TVA, bénéfice) se confondent en un ton kaki/olive. Après correction, elles restent nettement distinguables par tous.*

---

## Limites & biais

**Ce qui peut casser** :

- Le script de consolidation suppose une structure de colonnes stable entre exports ERP/web mensuels ; un changement de nommage de colonne côté source casserait le script sans erreur explicite si la colonne manquante n'est pas contrôlée en amont.
- Le calcul de TVA à taux fixe (20%) ne gère pas une éventuelle diversité de taux selon les catégories de produits (ex. taux réduits) si Bottleneck en introduisait à l'avenir.

**Ce qui reste incertain** :

- Le filtrage combiné (catégorie *et* tri, sélectionnables indépendamment) n'a été résolu ni en Plotly (nécessiterait Dash) ni testé en Altair au-delà d'un seul filtre (cf. livrable 1, section 4.1).

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


---

## Synthèse recruteur/client

**Résultats** : consolidation fiabilisée de 3 sources de données hétérogènes, avec un rapport d'anomalies systématique (doublons, `sku` manquants, clés non appariées) ; **9 types d'erreurs de données identifiés et documentés** sur exécution réelle, dépassant l'attente initiale du commanditaire ("au moins 8"). Production d'indicateurs de pilotage (CA, marge, rotation de stock, tops/flops) et d'un POC de visualisation interactive validé par un test d'accessibilité réel, retenu après comparaison testée face à une alternative (Altair). Script de consolidation validé par comparaison croisée avec une seconde IA (GitHub Copilot), les deux convergeant vers un résultat strictement identique.

**Impact** : le projet transforme une analyse ponctuelle et manuelle en un processus partiellement automatisé et documenté, réduisant le risque d'erreur silencieuse lors des futurs rapprochements de données mensuels. Les graphiques interactifs livrés permettent une exploration autonome par des utilisateurs non techniques, réduisant la dépendance à l'analyste pour chaque nouvelle question business.

**Recommandations** :

1. Mettre en place un dictionnaire de données partagé entre l'ERP et le site web pour réduire durablement les erreurs de jointure.
2. Industrialiser le POC dataviz en un vrai dashboard Dash pour permettre des filtres croisés (catégorie et tri combinés), au-delà de la limite actuelle des menus Plotly natifs.
3. Maintenir la pratique de comparaison systématique entre assistants IA sur les prochaines évolutions du script, plutôt que de se reposer sur la sortie d'un seul outil sans vérification croisée.

**Prochaines étapes** :

- Reconduire le script de consolidation sur les extractions des mois suivants pour valider sa robustesse dans la durée.
