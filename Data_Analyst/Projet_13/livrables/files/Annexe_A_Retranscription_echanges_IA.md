# Annexe A — Retranscription intégrale des échanges IA

> Retranscription complète (et non plus condensée en tableau) des échanges avec l'assistant IA (Claude, Anthropic), sur deux volets : l'amélioration des visualisations Plotly, et l'automatisation de la consolidation des données. Le tableau de synthèse du Livrable 4 reste la version résumée ; cette annexe en est la version détaillée, tour par tour.

---

## Partie 1 — Visualisations Plotly

### Échange 1 — Lancement du chantier dataviz

**🧑 Utilisateur** : *donc maintenant je dois améliorer mes data visualisations avec plotly en me servant soit de l'ia soit d'un article ou documentation ?*

**🤖 Assistant** : Confirmation que les deux démarches se combinent : la documentation sert de source justifiée pour les choix (à intégrer à la veille), l'IA aide à écrire le code plus vite mais l'auteur doit comprendre et documenter ce qu'il fait. Pour compter comme preuve de POC, il faut : un graphique converti, une explication de ce que ça change, idéalement une capture avant/après.

Analyse du notebook (recherche des appels `plt.`, `sns.`, `px.`) : la majorité des graphiques (CA, tops/flops, marges) étaient déjà en Plotly Express (`px.bar`, `px.box`). Seule la matrice de corrélation restait en Matplotlib/Seaborn (`sns.heatmap`), présente en triple dans le notebook — candidat retenu pour le POC.

Code proposé :
```python
import plotly.express as px

fig = px.imshow(
    corr,
    text_auto=".2f",          # équivalent de annot=True
    color_continuous_scale="RdBu_r",  # équivalent de cmap='coolwarm'
    zmin=-1, zmax=1,
    title="Matrice de corrélation"
)
fig.update_layout(width=600, height=500)
fig.show()
```

Proposition d'ajouter au document : avant/après, source Plotly, statut.

### Échange 2 — Ajout au livrable

**🧑 Utilisateur** : *ajoute, je vais tester de mon côté*

**🤖 Assistant** : Ajout de la section POC (contexte, code avant/après, impacts identifiés — lecture des valeurs, cohérence des librairies, export, maintenance —, source, statut "à tester").

### Échange 3 — Retour de test et nouvelle demande

**🧑 Utilisateur** : *je ne vois pas une grande différence avec la version matplotlib mais ok pour la cohérence des librairies. En fait, ce que j'aimerais faire, c'est avoir un graphique qui montre la puissance de plotly. Il parait qu'on peut avoir un graphique dynamique qui s'actualise en fonction des filtres un peu comme dans power bi*

**🤖 Assistant** : Présentation de deux options : (a) menu déroulant Plotly natif (`updatemenus`), sans dépendance, fonctionnant directement dans le notebook ; (b) mini-dashboard **Dash**, filtres multiples réellement indépendants mais nécessitant un serveur. Exemple de code pour l'option (a), basé sur `df_merge` avec colonnes `product_type`, `CA`, `total_sales`, `price`, `stock_quantity` :

```python
import plotly.express as px

df_ca_produit = df_merge.groupby(['product_type', 'post_title'], as_index=False)['CA'].sum()

fig = px.bar(
    df_ca_produit,
    x='post_title', y='CA',
    color='product_type',
    title="Chiffre d'affaires par produit"
)

categories = df_ca_produit['product_type'].unique()
buttons = [dict(label="Toutes catégories", method="update",
                 args=[{"visible": [True] * len(fig.data)}])]

for cat in categories:
    visibility = [trace.name == cat for trace in fig.data]
    buttons.append(dict(label=cat, method="update", args=[{"visible": visibility}]))

fig.update_layout(updatemenus=[dict(active=0, buttons=buttons, x=1.15, y=1)])
fig.show()
```

### Échange 4 — Ajout de la marge

**🧑 Utilisateur** : *j'aimerais ajouter la marge sur mes barres, c'est possible ?*

**🤖 Assistant** : Deux options proposées : (a) marge affichée au survol via `hover_data` ; (b) marge encodée en couleur continue (`color_continuous_scale='RdYlGn'`), plus parlante visuellement mais qui remplace l'encodage couleur par catégorie. Précision que `px` ne peut porter qu'une seule information par couleur — pour combiner catégorie et marge, il faudrait passer par `graph_objects`.

### Échange 5 — Vers le barplot empilé

**🧑 Utilisateur** : *en fait, j'aimerais un barplot empilé avec le CA divisé en 2 : cout d'achat / bénéfices*

**🤖 Assistant** : Code fourni, agrégation par `product_type`, calcul de `cout_achat_total` et `benefice_total`, passage au format long via `melt()` puis `px.bar(..., barmode='stack')`.

### Échange 6 — Ajout de la TVA

**🧑 Utilisateur** : *oui je veux bien mais il faudrait ajouter la TVA tel que benef = CA total - prix d'achat - tva*

**🤖 Assistant** : Repérage dans le notebook d'un taux de TVA déjà utilisé (`tva = 0.20`, ligne ~991, avec calcul de `prix_ht`), donc `price` dans `df_merge` est en TTC. Décomposition proposée en 3 parts (coût d'achat, TVA, bénéfice), avec **question explicite** : `purchase_price` est-il HT ou TTC côté fournisseur ? Signalé comme risque de double comptage si mal supposé.

**🧑 Utilisateur** : *non le purchase price est ht la tva s'applique a bootleneck et pas à son fournisseur.*

**🤖 Assistant** : Confirmation que le calcul est donc correct tel quel (`benefice_total = ca_ht_total − cout_achat_total`, les deux en HT), pas de modification nécessaire.

### Échange 7 — Question sur le format des données

**🧑 Utilisateur** : *je ne peux pas faire un diagramme à barres empilées si mes données sont dans des colonnes différentes ?*

**🤖 Assistant** : Si, en passant directement une liste de colonnes à `y=` dans `px.bar` — pas besoin de `melt()` au préalable, `px.bar` effectue cette transformation en interne :

```python
fig = px.bar(
    df_stack,
    x='product_type',
    y=['cout_achat', 'tva', 'benefice'],
    color_discrete_map={'cout_achat': '#EF553B', 'tva': '#FFA15A', 'benefice': '#00CC96'},
    title="Chiffre d'affaires (TTC) par catégorie : coût d'achat / TVA / bénéfice",
    labels={'value': 'Montant (€)', 'product_type': 'Catégorie', 'variable': 'Composante'}
)
```

### Échange 8 — Débogage du code utilisateur

**🧑 Utilisateur** a soumis un bloc de code combinant le calcul TVA, le barplot empilé par colonnes, et un menu de filtre par catégorie, en erreur.

**🤖 Assistant** — diagnostic de deux bugs :
1. Incohérence de noms : colonnes créées avec le suffixe `_total` (`cout_achat_total`) mais appelées sans dans `y=[...]`.
2. Logique de filtre incompatible avec la structure : avec `y=` en liste de colonnes, chaque trace correspond à une **composante** (pas à une catégorie), donc `trace.name == cat` ne matche jamais rien.

Code corrigé fourni, remplaçant dynamiquement `x`/`y` de chaque trace selon la catégorie choisie plutôt que de simplement cacher des traces.

### Échange 9 — Question méthodologique pandas

**🧑 Utilisateur** : *si je fais un sort_values, je dois faire un reset_index ?*

**🤖 Assistant** : Pas nécessaire pour Plotly (basé sur les valeurs des colonnes, pas sur l'index). Utile dans d'autres cas : affichage, `.iloc`, calcul de rang. Rappel du piège classique : `sort_values()` renvoie un nouveau DataFrame, il ne modifie pas sur place — il faut réassigner.

### Échange 10 — Vue agrégée avec drill-down (treemap)

**🧑 Utilisateur** : *est il possible d'avoir une vue agrégée des catégories avant de pouvoir rentrer dans le détail ?*

**🤖 Assistant** : Proposition d'un treemap hiérarchique (`px.treemap`), avec `path=[px.Constant("Tous produits"), 'product_type', 'post_title']`, `values='CA'`, `color='benefice_total'`. Alternative sunburst également présentée.

**🧑 Utilisateur** a soumis une erreur : `ValueError: ('None entries cannot have not-None children', ...)`.

**🤖 Assistant** — diagnostic : deux causes possibles, valeurs manquantes (NaN) ou noms de produits dupliqués dans plusieurs catégories, cassant l'identification des nœuds par nom. Solution robuste fournie : génération d'un identifiant composite unique (`product_type + " / " + post_title`) plutôt que de compter sur les noms seuls.

### Échange 11 — Retour au barplot empilé, avec drill-down et tri

**🧑 Utilisateur** : *c'est bon, j'ai résolu le problème. En revanche, je veux garder le graphique à barres empilées mais je veux pouvoir agir sur la hierrarchie product_type / post_title. En clair, je veux une vue initiale avec le 'cout_achat_total', 'tva_total', 'benefice_total' puis pouvoir zoomer sur une catégorie en voyant les produits en détail dans une des catégories. aussi j'aimerais pouvoir trier le graph en focntion d'un des indicateurs*

**🤖 Assistant** : Explication d'une limite technique de Plotly Express/graph_objects seul (sans serveur) : deux menus déroulants indépendants qui interagissent entre eux ne sont pas possibles nativement, chaque option devant être précalculée. Solution proposée : un seul menu combinant toutes les paires (niveau × tri), via `go.Figure` :

```python
import plotly.graph_objects as go

composantes = ['cout_achat_total', 'tva_total', 'benefice_total']
couleurs = {'cout_achat_total': '#EF553B', 'tva_total': '#FFA15A', 'benefice_total': '#00CC96'}

def agreger(df, niveau):
    return df.groupby(niveau, as_index=False)[composantes].sum()

df_cat = agreger(df_merge, 'product_type')
categories = df_merge['product_type'].unique()

fig = go.Figure()
for comp in composantes:
    fig.add_trace(go.Bar(name=comp, x=df_cat['product_type'], y=df_cat[comp], marker_color=couleurs[comp]))
fig.update_layout(barmode='stack', title="CA par catégorie : coût d'achat / TVA / bénéfice")

def make_args(df, x_col, sort_by):
    df_sorted = df.sort_values(sort_by, ascending=False)
    return {"x": [df_sorted[x_col]] * 3, "y": [df_sorted[c] for c in composantes]}

buttons = []
for sort_by in composantes:
    buttons.append(dict(label=f"Toutes catégories — triées par {sort_by}", method="update",
                         args=[make_args(df_cat, 'product_type', sort_by)]))
for cat in categories:
    df_prod = agreger(df_merge[df_merge['product_type'] == cat], 'post_title')
    for sort_by in composantes:
        buttons.append(dict(label=f"{cat} — triée par {sort_by}", method="update",
                             args=[make_args(df_prod, 'post_title', sort_by)]))

fig.update_layout(updatemenus=[dict(active=0, buttons=buttons, x=1.3, y=1, xanchor='left')])
fig.show()
```

Alternative Dash mentionnée pour un vrai croisement de filtres indépendants, proposée comme piste future plutôt qu'implémentée dans l'immédiat.

### Échange 12 — Ergonomie du retour à la vue globale

**🧑 Utilisateur** : *je peux revenir à la vue toutes catégories après avoir 'zoomé' sur une ?*

**🤖 Assistant** : Oui, les options "Toutes catégories" restent en tête de liste dans le même menu déroulant — pas de bouton de retour dédié. Limite ergonomique signalée (18 options au total dans un seul menu, moins intuitif qu'un treemap), avec deux pistes d'amélioration proposées (tri visuel des options, bouton "Vue d'ensemble" dédié).

### Échange 13 — Documentation du POC

**🧑 Utilisateur** : *là c'est pas mal, c'est quoi la suite ?*

**🤖 Assistant** : Récapitulatif de l'état d'avancement, proposition de 3 suites possibles (documenter le POC / script de consolidation / accessibilité), sélection par l'utilisateur : documentation du POC.

Rédaction de la section POC dans le livrable principal : contexte, construction de la donnée, fonctionnalités interactives, code consolidé, impacts identifiés et évalués (tableau avant/après), limite technique identifiée (Dash), source, statut.

### Échange 14 — Capture d'écran et validation

**🧑 Utilisateur** a fourni une capture d'écran du graphique fonctionnel et demandé son intégration.

**🤖 Assistant** : Intégration de la capture dans le document avec légende interprétative (la catégorie Vin concentre l'essentiel du CA, du coût d'achat et du bénéfice), passage du statut à "réalisé et testé".

### Échange 15 — Test d'accessibilité

**🧑 Utilisateur** : *oui, je dois tester quoi ?*

**🤖 Assistant** : Trois tests concrets proposés : simulation de daltonisme (Coblis), contraste texte/fond (WebAIM), navigation clavier du menu déroulant.

**🧑 Utilisateur** a fourni une capture Coblis en simulation protanopie, avec le commentaire *« le pire est en protanopia »*.

**🤖 Assistant** : Confirmation du problème — les 3 composantes se confondent en un ton kaki/olive. Palette de remplacement proposée (Okabe-Ito) : `#0072B2` (bleu), `#E69F00` (orange/ambre), `#009E73` (vert bleuté), reconnue pour rester distinguable en daltonisme.

**🧑 Utilisateur** a fourni une nouvelle capture avec la palette corrigée.

**🤖 Assistant** : Confirmation visuelle de la lisibilité restaurée. Documentation du test dans le livrable (avant/après, palette corrigée, limite non résolue signalée : navigation clavier non testée).

---

## Partie 2 — Automatisation de la consolidation des données

### Échange 1 — Cadrage de la demande

**🧑 Utilisateur** : *ok pour la consolidation des données*

**🤖 Assistant** : Analyse du notebook (recherche des cellules `df_erp`, `df_web`, `df_liaison`, `sku`, `duplic`, `merge(`) pour identifier la logique déjà validée manuellement : nettoyage ERP (prix négatifs supprimés, stocks négatifs corrigés à 0, statut de stock recalculé, exclusion des articles hors vente `onsale_web`), nettoyage web (colonnes utiles sélectionnées, `sku` manquants exclus, filtrage sur `post_type == 'product'`), vérification du fichier de liaison (doublons, `id_web` manquants), fusion en deux temps (`product_id` puis `id_web`).

Constat formulé : le travail de nettoyage est rigoureux mais manuel et linéaire, sans rapport d'anomalies centralisé.

Script livré (`consolidation_donnees.py`), structuré en fonctions :

```python
"""
Script de consolidation des données Bottleneck (ERP + extraction web + liaison).
...
"""

import pandas as pd


def nettoyer_erp(df_erp: pd.DataFrame, rapport: dict) -> pd.DataFrame:
    """Nettoie le fichier ERP : prix/stock négatifs, statut de stock, articles hors vente."""
    n_avant = len(df_erp)
    df_erp = df_erp[~(df_erp['price'] < 0)]
    rapport['erp_prix_negatifs_supprimes'] = n_avant - len(df_erp)

    n_stock_neg = (df_erp['stock_quantity'] < 0).sum()
    df_erp.loc[df_erp['stock_quantity'] < 0, 'stock_quantity'] = 0
    rapport['erp_stocks_negatifs_corriges'] = int(n_stock_neg)

    df_erp['stock_status'] = 'instock'
    df_erp.loc[df_erp['stock_quantity'] < 1, 'stock_status'] = 'outofstock'

    n_avant = len(df_erp)
    df_erp = df_erp[df_erp['onsale_web'] != 0]
    rapport['erp_hors_vente_exclus'] = n_avant - len(df_erp)

    rapport['erp_doublons_product_id'] = int(df_erp.duplicated(subset='product_id').sum())
    return df_erp


def nettoyer_web(df_web: pd.DataFrame, rapport: dict) -> pd.DataFrame:
    """Nettoie l'extraction web : colonnes utiles, sku manquants, type d'entrée 'product'."""
    colonnes_utiles = ['sku', 'tax_status', 'total_sales', 'product_type', 'post_title', 'post_type']
    df_web = df_web[colonnes_utiles]

    n_avant = len(df_web)
    df_web = df_web[~df_web['sku'].isna()]
    rapport['web_sku_manquants_exclus'] = n_avant - len(df_web)
    rapport['web_doublons_sku'] = int(df_web['sku'].duplicated().sum())

    n_avant = len(df_web)
    df_web = df_web[df_web['post_type'] == 'product']
    rapport['web_lignes_non_product_exclues'] = n_avant - len(df_web)

    df_web = df_web.rename(columns={'sku': 'id_web'})
    return df_web


def verifier_liaison(df_liaison: pd.DataFrame, rapport: dict) -> pd.DataFrame:
    """Vérifie l'intégrité du fichier de liaison (clé pivot entre ERP et web)."""
    rapport['liaison_doublons_product_id'] = int(df_liaison['product_id'].duplicated().sum())
    rapport['liaison_doublons_id_web'] = int(df_liaison['id_web'].duplicated(keep=False).sum())
    rapport['liaison_id_web_manquants'] = int(df_liaison['id_web'].isna().sum())
    return df_liaison


def fusionner(df_erp: pd.DataFrame, df_web: pd.DataFrame, df_liaison: pd.DataFrame, rapport: dict) -> pd.DataFrame:
    """Fusionne les 3 sources via les clés product_id et id_web, en journalisant les non-correspondances."""
    manquants_liaison = set(df_liaison['product_id']) - set(df_erp['product_id'])
    manquants_erp = set(df_erp['product_id']) - set(df_liaison['product_id'])
    rapport['product_id_dans_liaison_absents_erp'] = len(manquants_liaison)
    rapport['product_id_dans_erp_absents_liaison'] = len(manquants_erp)

    df_merge = pd.merge(df_erp, df_liaison, on='product_id', how='left')

    manquants_web = set(df_web['id_web']) - set(df_merge['id_web'])
    manquants_merge = set(df_merge['id_web']) - set(df_web['id_web'])
    rapport['id_web_dans_web_absents_merge'] = len(manquants_web)
    rapport['id_web_dans_merge_absents_web'] = len(manquants_merge)

    df_final = pd.merge(df_web, df_merge, on='id_web', how='inner')
    df_final = df_final[['product_id', 'product_type', 'post_title', 'total_sales',
                          'stock_quantity', 'price', 'purchase_price']]

    rapport['lignes_finales_consolidees'] = len(df_final)
    return df_final


def consolider_donnees(chemin_erp: str, chemin_web: str, chemin_liaison: str):
    """
    Point d'entrée principal : charge, nettoie et fusionne les 3 sources de données.
    Retourne : df_final (DataFrame consolidé) et rapport (dict des anomalies détectées).
    """
    rapport = {}
    df_erp = pd.read_excel(chemin_erp)
    df_web = pd.read_excel(chemin_web)
    df_liaison = pd.read_excel(chemin_liaison)

    df_erp = nettoyer_erp(df_erp, rapport)
    df_web = nettoyer_web(df_web, rapport)
    df_liaison = verifier_liaison(df_liaison, rapport)

    df_final = fusionner(df_erp, df_web, df_liaison, rapport)
    return df_final, rapport


def afficher_rapport(rapport: dict) -> None:
    """Affiche un résumé lisible des anomalies détectées, à conserver comme preuve/log."""
    print("=== Rapport de consolidation des données Bottleneck ===")
    for cle, valeur in rapport.items():
        print(f"- {cle.replace('_', ' ')} : {valeur}")


if __name__ == "__main__":
    df_final, rapport = consolider_donnees("erp.xlsx", "web.xlsx", "liaison.xlsx")
    afficher_rapport(rapport)
```

**Point volontairement exclu**, explicité à l'utilisateur : une correction ponctuelle du notebook original (forçage de `onsale_web` sur un `product_id` spécifique, `4200`) n'a pas été reprise, car c'est une correction ad hoc sur une donnée précise, non généralisable — recommandation de la traiter à la source (ERP) plutôt que de la coder en dur, au risque qu'elle s'applique à tort sur de futurs exports où ce produit n'existe plus dans cet état.

### Échange 2 — Prise en main

**🧑 Utilisateur** : *je la voie où ?*

**🤖 Assistant** : Présentation du fichier via l'outil de partage, avec instructions d'usage :

```python
from consolidation_donnees import consolider_donnees, afficher_rapport

df_merge, rapport = consolider_donnees("erp.xlsx", "web.xlsx", "liaison.xlsx")
afficher_rapport(rapport)
```

Précision que les colonnes de sortie (`product_id`, `product_type`, `post_title`, `total_sales`, `stock_quantity`, `price`, `purchase_price`) sont identiques à celles du notebook original, donc le reste des analyses (CA, marges, graphiques Plotly) continue de fonctionner sans modification en aval.

### Échange 3 — Documentation du résultat

**🧑 Utilisateur**, après avoir sélectionné "Documenter le script de consolidation" parmi les suites proposées.

**🤖 Assistant** : Rédaction d'une section dédiée dans le cahier des charges (contexte, réalisation par fonction, tableau d'impacts avant/après, point de vigilance sur la correction ad hoc exclue, statut passé à "réalisé"), et mise à jour du statut correspondant dans le tableau des spécifications fonctionnelles ("à développer" → "réalisé").

### Échange 4 — Intégration au notebook amélioré

**🧑 Utilisateur** a ultérieurement demandé un notebook amélioré appelant directement `consolider_donnees()`.

**🤖 Assistant** : Édition programmatique du notebook original — remplacement des ~105 cellules de chargement/nettoyage/fusion manuel par deux cellules (import de la fonction, appel, affichage du rapport), suppression de la boîte à moustache Matplotlib redondante avec sa version Plotly déjà présente, remplacement des 3 heatmaps Seaborn par leurs équivalents `px.imshow`. Limite signalée : le notebook n'a pas pu être exécuté par l'assistant (fichiers de données `erp.xlsx`, `web.xlsx`, `liaison.xlsx` non fournis), à exécuter et vérifier par l'utilisateur.

---

*Cette retranscription reste une reconstruction fidèle mais rédigée après coup à partir de l'historique de conversation, et non un export technique brut (logs horodatés) — limite assumée cohérente avec celle du tableau de traçabilité IA synthétique (Livrable 4).*
