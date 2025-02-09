from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# Déclaration de la base
Base = declarative_base()

# Définition des modèles
class Avatar(Base):
    __tablename__ = "avatar"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)

    quests = relationship("Quest", back_populates="avatar", cascade="all, delete")
    categories = relationship("AvatarCategory", back_populates="avatar", cascade="all, delete")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False, unique=True)


class Quest(Base):
    __tablename__ = "quests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    avatar_id = Column(Integer, ForeignKey("avatar.id"), nullable=False)
    quest_name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    completed = Column(Boolean, default=False)
    exp_amount = Column(Integer, default=0)
    due_date = Column(Date, nullable=True)  # New column for the due date

    avatar = relationship("Avatar", back_populates="quests")
    category = relationship("Category")


class AvatarCategory(Base):
    __tablename__ = "avatar_category"
    avatar_id = Column(Integer, ForeignKey("avatar.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
    exp_points = Column(Integer, default=0)

    avatar = relationship("Avatar", back_populates="categories")
    category = relationship("Category")


# Connexion à la base de données
DATABASE_URL = "sqlite:///app-db.db"
engine = create_engine(DATABASE_URL, echo=True)

# Création des tables si elles n'existent pas déjà
Base.metadata.create_all(engine)

# Création de la session
Session = sessionmaker(bind=engine)


# Fonction pour obtenir une session
def get_session():
    session = Session()
    return session


# Fonction pour ajouter un avatar par défaut "Unknow"
def add_default_avatar():
    session = get_session()

    existing_avatar = session.query(Avatar).all()
    if not existing_avatar:
        new_avatar = Avatar(name="Unknow", level=0, experience=0)

        session.add(new_avatar)
        session.commit()
    session.close()


# Fonction pour ajouter des catégories par défaut
def add_default_categories():
    session = get_session()

    existing_categories = session.query(Category).all()
    if not existing_categories:
        default_categories = ["wisdom", "constitution", "reflexion", "family"]
        categories_to_add = [Category(category_name=category) for category in default_categories]

        session.add_all(categories_to_add)
        session.commit()
    session.close()


# Fonction pour ajouter des relations avatar-catégorie par défaut
def add_avatar_categories():
    session = get_session()
    avatar = session.query(Avatar).first()

    if avatar:
        categories = session.query(Category).all()
        for category in categories:
            existing_relation = session.query(AvatarCategory).filter(AvatarCategory.avatar_id == avatar.id,
                                                                     AvatarCategory.category_id == category.id).first()
            if not existing_relation:
                avatar_category = AvatarCategory(avatar_id=avatar.id, category_id=category.id, exp_points=0)
                session.add(avatar_category)

        session.commit()

    session.close()


# Fonction de setup initial pour la base de données
def setup_database():
    # Création des tables
    Base.metadata.create_all(engine)
    # Ajout des données par défaut
    add_default_avatar()
    add_default_categories()
    add_avatar_categories()

