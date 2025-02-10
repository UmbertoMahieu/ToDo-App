import logging
import datetime
from models.database import get_session, Avatar, Category, AvatarCategory, Quest

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class DataManager:
    def __init__(self):
        pass

    #return first avatar
    def get_avatar(self):
        with get_session() as session:
            return session.query(Avatar).first()

    #update avatar name
    def update_avatar_name(self, avatar_id, new_name):
        with get_session() as session:
            try:
                avatar = session.query(Avatar).filter_by(id=avatar_id).first()
                if not avatar:
                    logger.error(f"Avatar with ID {avatar_id} not found.")
                    return False
                avatar.name = new_name
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logger.exception(f"Error updating avatar name: {e}")
                return False

    #return all existing quest categories
    def get_categories(self):
        with get_session() as session:
            return session.query(Category).all()

    #return exp by categories for a specific avatar
    def get_avatar_experience_by_category(self, avatar_id):
        with get_session() as session:
            avatar_categories = session.query(AvatarCategory).filter(AvatarCategory.avatar_id == avatar_id).all()
            return {
                avatar_category.category.category_name: avatar_category.exp_points
                for avatar_category in avatar_categories
            }

    #update exp level for a category
    def update_experience(self, quest_id):
        with get_session() as session:
            try:
                # Fetch the quest
                quest = session.query(Quest).filter_by(id=quest_id).first()
                if not quest:
                    logger.error(f"❌ Quest with ID {quest_id} not found.")
                    return

                # Fetch the avatar-category relationship
                avatar_category = session.query(AvatarCategory).filter_by(
                    avatar_id=quest.avatar_id, category_id=quest.category_id
                ).first()

                if not avatar_category:
                    logger.error(
                        f"⚠ AvatarCategory entry not found for Avatar {quest.avatar_id} and Category {quest.category_id}")
                    return

                # Update experience based on quest completion status
                if quest.completed:
                    avatar_category.exp_points += quest.exp_amount
                else:
                    avatar_category.exp_points -= quest.exp_amount

                session.commit()
                logger.info(
                    f"✅ Updated experience: Avatar {quest.avatar_id} - {avatar_category.exp_points} XP in Category {quest.category_id}")

            except Exception as e:
                logger.error(f"⚠ Error updating experience for Quest {quest_id}: {e}")
                session.rollback()

    #update status of completion a quest
    def swap_quest_status(self, quest_id):
        """Toggles the quest's completion status and commits to the DB."""
        with get_session() as session:
            try:
                #fetch the quest
                logger.info(f"🔄 Fetching quest with ID {quest_id}")
                quest = session.query(Quest).filter_by(id=quest_id).first()
                if not quest:
                    logger.error(f"❌ Quest not found.")
                    return None

                #update quest completion
                quest.completed = not quest.completed
                logger.info(f"✅ Updated status: {quest.completed}")
                session.commit()

            except Exception as e:
                session.rollback()
                logger.exception(f"⚠ Error updating quest status for : {e}")
                return None

    #return all quests related to an avatar
    def get_avatar_quests(self, avatar):
        """Fetches all quests for a given avatar."""
        with get_session() as session:
            quests = session.query(Quest).filter_by(avatar_id=avatar.id).all()
            return [
                {
                    "id": quest.id,
                    "quest_name": quest.quest_name,
                    "category_id": quest.category_id,
                    "category_name": quest.category.category_name,
                    "due_date": quest.due_date.strftime('%Y-%m-%d') if quest.due_date else "No date",
                    "exp_amount": quest.exp_amount,
                    "completed": quest.completed
                }
                for quest in quests
            ]

    #create a new quest
    def add_quest(self, avatar_id, title, category_name, exp_amount, due_date=None):
        """Adds a new quest to the database safely."""
        with get_session() as session:
            try:
                #fetch category object
                category = session.query(Category).filter_by(category_name=category_name).first()
                if not category:
                    logger.error(f"Category '{category_name}' not found.")
                    return

                #create and add new object
                new_quest = Quest(
                    avatar_id=avatar_id,
                    quest_name=title,
                    category_id=category.id,
                    due_date=datetime.datetime.strptime(due_date, '%Y-%m-%d') if due_date else None,
                    exp_amount=exp_amount
                )

                session.add(new_quest)
                session.commit()  # 🔥 Ajout de session.commit()

            except Exception as e:
                session.rollback()
                logger.error(f"⚠ Error adding quest '{title}': {e}")

    #remove a quest
    def remove_quest(self, quest_id):
        with get_session() as session:
            try:
                quest = session.query(Quest).filter_by(id=quest_id).first()
                if not quest:
                    logger.error(f"Quest  ID '{quest_id}' not found.")
                    return

                session.delete(quest)
                session.commit()  # 🔥 Ajout de session.commit()

            except Exception as e:
                session.rollback()
                logger.error(f"⚠ Error adding quest : {e}")