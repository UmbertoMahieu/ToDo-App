from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from models import DataManager
from kivymd.uix.list import TwoLineAvatarIconListItem, MDList, IconLeftWidget, IconRightWidget
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout

class QuestScreen(MDBottomNavigationItem):
    def __init__(self, avatar_screen, **kwargs):
        super().__init__(**kwargs)
        self.name = 'quests'
        self.text = 'All Quests'
        self.avatar_screen = avatar_screen

        # Data
        self.db = DataManager()
        self.avatar = self.db.get_avatar()
        self.quests = []

        # Layout
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Search Field
        self.search_field = MDTextField(
            hint_text="Search quests...",
            size_hint_x=1,
            on_text_validate=self.load_quests,
            mode= "round",
            height= "15dp"

        )
        self.search_field.bind(text=self.load_quests)

        # Top Bar
        self.sort_button = MDIconButton(icon="sort", on_release=self.open_sort_menu, size_hint=(None, None),pos_hint={'center_x': 0.5, 'center_y': 0.5 })
        self.top_bar = BoxLayout(size_hint_y=None, height=50)
        self.top_bar.add_widget(self.search_field)
        self.top_bar.add_widget(self.sort_button)
        self.layout.add_widget(self.top_bar)

        # Scrollable List
        self.scroll_view = ScrollView()
        self.list_container = MDList()
        self.scroll_view.add_widget(self.list_container)
        self.layout.add_widget(self.scroll_view)
        self.add_widget(self.layout)

        # Sorting Menu
        self.sort_menu = MDDropdownMenu(
            caller=self.sort_button,
            items=[
                {"text": "Sort by Due Date", "on_release": lambda: self.sort_quests("due_date")},
                {"text": "Sort by Experience", "on_release": lambda: self.sort_quests("exp_amount")},
            ],
            width_mult=4,
        )

        # Load data
        self.load_quests()

    # Fetch quests from the database and populate the list
    def load_quests(self, *args):
        self.list_container.clear_widgets()  # Clear existing list items
        search_text = self.search_field.text.lower()
        self.quests = self.db.get_avatar_quests(self.avatar)  # Fetch quests

        filtered_quests = [
            q for q in self.quests
            if search_text in q['quest_name'].lower() or search_text in q['category_name'].lower()
        ]

        for quest in filtered_quests:
            quest_id = quest["id"]
            completed = quest.get("completed", False)

            quest_item = TwoLineAvatarIconListItem(
                text=quest['quest_name'],
                secondary_text=f"[size=14sp]{quest['category_name']} | {quest['due_date']} | {quest['exp_amount']} XP[/size]"
            )

            # Validate Button
            validate_icon = IconLeftWidget(
                icon="check-circle",
                theme_text_color="Custom",
                text_color=get_color_from_hex("#4CAF50") if completed else get_color_from_hex("#000000"),
                on_release=lambda x, qid=quest_id: self.toggle_validate_quest(x, qid)
            )
            quest_item.add_widget(validate_icon)

            # Delete Button
            delete_icon = IconRightWidget(icon="trash-can",
                                          on_release=lambda x, qid=quest_id: self.confirm_delete_quest(qid))
            quest_item.add_widget(delete_icon)

            self.list_container.add_widget(quest_item)

    # Toggle quest validation status
    def toggle_validate_quest(self, widget, quest_id):
        self.db.swap_quest_status(quest_id)
        self.db.update_experience(quest_id)
        self.avatar_screen.refresh_avatar_view()

        # Toggle button color
        widget.text_color = get_color_from_hex("#000000") if widget.text_color == get_color_from_hex(
            "#4CAF50") else get_color_from_hex("#4CAF50")

        self.load_quests()

    # Show confirmation dialog before deleting a quest
    def confirm_delete_quest(self, quest_id):
        self.dialog = MDDialog(
            title="Delete Quest?",
            text="Are you sure you want to delete this quest?",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Delete", on_release=lambda x: self.delete_quest(quest_id)),
            ],
        )
        self.dialog.open()

    def delete_quest(self, quest_id):
        """Remove quest and update UI."""
        self.db.remove_quest(quest_id)
        self.avatar_screen.refresh_avatar_view()
        self.load_quests()
        self.dialog.dismiss()

    def open_sort_menu(self, instance):
        """Open the sorting dropdown menu."""
        self.sort_menu.open()

    def sort_quests(self, key):
        """Sort quests based on the selected key."""
        self.quests.sort(key=lambda x: x[key])
        self.load_quests()
        self.sort_menu.dismiss()
