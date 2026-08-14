"""
Script de consolidation des données Bottleneck (ERP + extraction web + liaison).

Reprend et automatise la logique de nettoyage/fusion validée manuellement dans le
notebook initial (Projet 6), en l'encapsulant dans une fonction réutilisable qui
journalise les anomalies détectées et corrigées à chaque exécution.

Usage :
    df_final, rapport = consolider_donnees("erp.xlsx", "web.xlsx", "liaison.xlsx")
"""

import pandas as pd


def nettoyer_erp(df_erp: pd.DataFrame, rapport: dict) -> pd.DataFrame:
    """Nettoie le fichier ERP : prix/stock négatifs, statut de stock, articles hors vente."""
    n_avant = len(df_erp)

    # Prix négatifs (erreur de saisie) -> lignes supprimées
    df_erp = df_erp[~(df_erp['price'] < 0)]
    rapport['erp_prix_negatifs_supprimes'] = n_avant - len(df_erp)

    # Stock négatif (erreur de saisie) -> ramené à 0
    n_stock_neg = (df_erp['stock_quantity'] < 0).sum()
    df_erp.loc[df_erp['stock_quantity'] < 0, 'stock_quantity'] = 0
    rapport['erp_stocks_negatifs_corriges'] = int(n_stock_neg)

    # Recalcul du statut de stock à partir de la quantité (source de vérité)
    df_erp['stock_status'] = 'instock'
    df_erp.loc[df_erp['stock_quantity'] < 1, 'stock_status'] = 'outofstock'

    # Articles explicitement hors vente sur le site web
    n_avant = len(df_erp)
    df_erp = df_erp[df_erp['onsale_web'] != 0]
    rapport['erp_hors_vente_exclus'] = n_avant - len(df_erp)

    # Doublons sur product_id (clé attendue unique) -> comptés puis supprimés (on garde la première occurrence)
    rapport['erp_doublons_product_id'] = int(df_erp.duplicated(subset='product_id').sum())
    df_erp = df_erp.drop_duplicates(subset='product_id', keep='first')

    return df_erp


def nettoyer_web(df_web: pd.DataFrame, rapport: dict) -> pd.DataFrame:
    """Nettoie l'extraction web : colonnes utiles, sku manquants, type d'entrée 'product'."""
    colonnes_utiles = ['sku', 'tax_status', 'total_sales', 'product_type', 'post_title', 'post_type']
    df_web = df_web[colonnes_utiles]

    # sku manquant -> ligne inexploitable pour la jointure, on l'exclut
    n_avant = len(df_web)
    df_web = df_web[~df_web['sku'].isna()]
    rapport['web_sku_manquants_exclus'] = n_avant - len(df_web)

    # On ne garde que les entrées de type 'product' (exclut les 'attachment', pièces jointes)
    n_avant = len(df_web)
    df_web = df_web[df_web['post_type'] == 'product']
    rapport['web_lignes_non_product_exclues'] = n_avant - len(df_web)

    # product_type manquant (ex. bons cadeaux, sans catégorie assignable) -> ligne exclue
    n_avant = len(df_web)
    df_web = df_web[df_web['product_type'].notna()]
    rapport['web_product_type_manquant_exclus'] = n_avant - len(df_web)

    # Doublons sur sku -> comptés puis supprimés (on garde la première occurrence)
    # Dédupliqué ICI, après les filtres post_type/product_type : une pièce jointe partageant
    # le même sku qu'un produit ne doit jamais "gagner" la déduplication à la place du produit.
    rapport['web_doublons_sku'] = int(df_web['sku'].duplicated().sum())
    df_web = df_web.drop_duplicates(subset='sku', keep='first')

    df_web = df_web.rename(columns={'sku': 'id_web'})
    return df_web


def verifier_liaison(df_liaison: pd.DataFrame, rapport: dict) -> pd.DataFrame:
    """Vérifie l'intégrité du fichier de liaison (clé pivot entre ERP et web).

    Contrairement à nettoyer_erp/nettoyer_web, cette fonction ne supprime volontairement
    aucun doublon : un doublon sur la table de liaison peut signaler un vrai problème de
    mapping (ex. un product_id associé à 2 id_web différents) qui mérite une vérification
    humaine plutôt qu'une correction automatique silencieuse.
    """
    rapport['liaison_doublons_product_id'] = int(df_liaison['product_id'].duplicated().sum())
    # .dropna() avant duplicated() : sinon plusieurs id_web manquants (NaN) se comptent comme
    # "dupliqués entre eux", ce qui gonfle artificiellement ce chiffre avec des lignes déjà
    # comptées séparément dans liaison_id_web_manquants.
    rapport['liaison_doublons_id_web'] = int(df_liaison['id_web'].dropna().duplicated(keep=False).sum())
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

    Retourne :
        df_final : DataFrame consolidé, prêt pour l'analyse (CA, marge, etc.)
        rapport  : dict listant les anomalies détectées et corrigées à cette exécution
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
