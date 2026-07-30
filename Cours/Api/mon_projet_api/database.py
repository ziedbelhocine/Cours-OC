from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. L'adresse de notre base de données.
# SQLite va stocker toutes les données dans un fichier nommé "sql_app.db".
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. Le moteur de connexion. C'est lui qui sait parler à SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Obligatoire spécifiquement pour SQLite avec FastAPI
)

# 3. La "fabrique" de sessions. 
# Une session, c'est comme une conversation ouverte avec la base de données.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. La classe de base pour nos futurs modèles.
Base = declarative_base()

# 5. La fonction pour ouvrir/fermer la session.
def get_db():
    db = SessionLocal() # On ouvre une connexion
    try:
        yield db        # On la donne temporairement à la route qui en a besoin
    finally:
        db.close()      # Une fois la requête finie, ON FERME LA CONNEXION (très important !)