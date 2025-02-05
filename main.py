from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation
from screens import AvatarScreen, QuestScreen, AddQuestScreen
import database

class ToDoApp(MDApp):
    def build(self):
        bottom_nav = MDBottomNavigation()
        quest_screen = QuestScreen()
        avatar_screen = AvatarScreen()
        bottom_nav.add_widget(avatar_screen)
        bottom_nav.add_widget(quest_screen)
        bottom_nav.add_widget(AddQuestScreen(quest_screen, avatar_screen))
        return bottom_nav

if __name__ == '__main__':
    database.setup_database()
    ToDoApp().run()
