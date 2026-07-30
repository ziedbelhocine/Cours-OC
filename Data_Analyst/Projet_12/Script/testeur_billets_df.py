import pandas as pd
import joblib

model_rf = joblib.load('model_rf.joblib')

nom_fichier = input('Entrez le chemin/nom de votre fichier : ')
df = pd.read_csv(nom_fichier)

X = df[['diagonal', 'height_left', 'height_right', 'margin_low', 'margin_up', 'length']]
y = df['id']

predictions = model_rf.predict(X)
probabilites = model_rf.predict_proba(X)

for i, nouveau_billet in enumerate(df.index):
    id_billet = y[nouveau_billet]
    pred_rf = predictions[i]
    proba_rf = probabilites[i]

    print(f"\n--- Analyse du billet {id_billet} ---")
    if pred_rf:
        print(f"✅ Billet VALIDE (confiance : {proba_rf[1]*100:.1f}%)")
    else:            # Si le modèle prédit "Faux"
        print(f"❌ FAUX billet (confiance : {proba_rf[0]*100:.1f}%)")