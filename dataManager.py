from database import get_session, Avatar, Category, AvatarCategory, Quest
import datetime

class DataManager:
    def __init__(self):
        pass

    def get_avatar(self):
        session = get_session()
        avatar = session.query(Avatar).first()
        session.close()
        return avatar

    def get_categories(self):
        session = get_session()
        categories = session.query(Category).all()
        session.close()
        return categories

    def get_avatar_categories(self, avatar_id):
        session = get_session()
        avatar_categories = session.query(AvatarCategory).filter(AvatarCategory.avatar_id == avatar_id).all()
        session.close()
        return avatar_categories

    def get_avatar_experience_by_category(self, avatar_id):
        session = get_session()
        avatar_categories = session.query(AvatarCategory).filter(AvatarCategory.avatar_id == avatar_id).all()

        category_experience = {
            avatar_category.category.category_name: avatar_category.exp_points
            for avatar_category in avatar_categories
        }

        session.close()
        return category_experience

    def update_experience(self, avatar_id, category_name, new_exp_points):
        session = get_session()
        category = session.query(Category).filter(Category.category_name == category_name).first()
        avatar_category = session.query(AvatarCategory).filter(
            AvatarCategory.avatar_id == avatar_id,
            AvatarCategory.category_id == category.id
        ).first()

        if avatar_category:
            avatar_category.exp_points = new_exp_points
            session.commit()
        session.close()

    def get_avatar_quests(self, avatar):
        session = get_session()
        Quests = session.query(Quest).filter(Quest.avatar_id == avatar.id).all()

        quest_list = [
            {
                "id": Quest.id,
                "title": Quest.quest_name,
                "category": Quest.category.category_name,
                "due_date": Quest.due_date.strftime('%Y-%m-%d') if Quest.due_date else "No date",
                "exp_amount" : Quest.exp_amount,
                "completed" : Quest.completed
            }
            for Quest in Quests
        ]

        session.close()
        return quest_list

    def add_quest(self, avatar_id, title, category_name, exp_amount, due_date=None):
        """Adds a new quest to the database."""
        session = get_session()

        # Find the category by name
        category = session.query(Category).filter(Category.category_name == category_name).first()
        if not category:
            print(f"Category '{category_name}' not found.")
            session.close()
            return

        # Create new quest
        new_quest = Quest(
            avatar_id=avatar_id,
            quest_name=title,
            category_id=category.id,
            due_date=datetime.datetime.strptime(due_date, '%Y-%m-%d') if due_date else None,
            exp_amount=exp_amount
        )

        # Save quest to the database
        session.add(new_quest)
        session.commit()
        session.close()

