from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation
from screens import AvatarScreen, QuestScreen, AddQuestScreen
from models import database as db

class ToDoApp(MDApp):
    def build(self):
        bottom_nav = MDBottomNavigation()
        avatar_screen = AvatarScreen()
        quest_screen = QuestScreen(avatar_screen)
        bottom_nav.add_widget(avatar_screen)
        bottom_nav.add_widget(quest_screen)
        bottom_nav.add_widget(AddQuestScreen(quest_screen, avatar_screen))
        return bottom_nav

if __name__ == '__main__':
    db.setup_database()
    ToDoApp().run()
