import pandas as pd
import joblib

# On importe notre modèle déjà entrainé pour ne pas le relancer à chaque test de billet.
model_rf = joblib.load('model_rf.joblib')  

def demander_valeur(nom_variable):
    valeur = None
    while valeur is None:
        try:
            valeur = float(input(f"Entrez {nom_variable} du billet en mm au format xxx.xx: "))
        except ValueError:
            print(f"HEY! '{valeur}' n'est pas un nombre décimal")
    return valeur

diagonal = demander_valeur("la diagonale")
height_left = demander_valeur("la hauteur gauche")
height_right = demander_valeur("la hauteur droite")
margin_low = demander_valeur("la marge basse")
margin_up = demander_valeur("la marge haute")
length = demander_valeur("la longueur")

nouveau_billet = pd.DataFrame([{
'diagonal': diagonal,
'height_left': height_left,
'height_right': height_right,
'margin_low': margin_low,
'margin_up': margin_up,
'length': length
}])

# Récupération de la prédiction et probabilité
pred_rf = model_rf.predict(nouveau_billet)[0]
proba_rf = model_rf.predict_proba(nouveau_billet)[0]

print(f"\n--- Analyse du billet ---")
if pred_rf:
    print(f"✅ billet VALIDE (confiance : {proba_rf[1]*100:.1f}%)")
else:
    print(f"❌ FAUX billet (confiance : {proba_rf[0]*100:.1f}%)")