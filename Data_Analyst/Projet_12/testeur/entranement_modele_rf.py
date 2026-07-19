import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# On charge nos données, on supprime les NaN et on définit X et y.
df = pd.read_csv('billets.csv', sep=';')
df = df.dropna().reset_index(drop=True)
X = df[['margin_low', 'margin_up', 'length']]
y = df['is_genuine']

# Entraînement des modèles sur le jeu complet avec les paramètres de GridSearch
model_rf = RandomForestClassifier(max_depth=7, min_samples_split=4, n_estimators=100, random_state=42)
model_rf.fit(X, y)

# Enregistrement du modèle dans un fichier
joblib.dump(model_rf, 'model_rf.joblib')
print("Modèle entraîné et sauvegardé.")