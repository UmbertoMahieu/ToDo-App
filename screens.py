from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from widgets import QuestBox
from kivy.clock import Clock
from dataManager import DataManager


class AvatarScreen(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'avatar'
        self.text = 'Avatar'
        
        #Data
        self.db = DataManager()
        self.avatar = self.db.get_avatar()
        self.categories = self.db.get_categories()
        self.category_experience = self.db.get_avatar_experience_by_category(self.avatar.id)

        scroll_view = ScrollView(size_hint=(1, 1))

        self.layout = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10,
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.avatar_label = MDLabel(
            text=f"{self.avatar.name}",
            halign='center',
            size_hint_y=None,
            height=40
        )
        self.layout.add_widget(self.avatar_label)

        self.level_label = MDLabel(
            text=f"Level : {self.avatar.level}",
            halign='center',
            size_hint_y=None,
            height=15,
            font_style="Caption"
        )
        self.layout.add_widget(self.level_label)

        self.category_bars = {}
        for category in self.categories:
            category_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=40,
                padding=20
            )

            category_label = MDLabel(
                text=category.category_name.capitalize(),
                halign='center',
                size_hint_x=0.4
            )
            category_layout.add_widget(category_label)

            exp_points = self.category_experience.get(category.category_name, 0)

            progress_bar = MDProgressBar(
                value=exp_points,
                max=100,
                size_hint_x=0.6,
                size_hint_y=None,
                height=10
            )
            progress_bar.pos_hint = {'center_y': 0.5}
            category_layout.add_widget(progress_bar)

            self.layout.add_widget(category_layout)
            self.category_bars[category] = progress_bar

        scroll_view.add_widget(self.layout)
        self.add_widget(scroll_view)

    def refresh_avatar_view(self):
        """Refreshes the avatar view UI properly."""
        # Fetch updated avatar data
        self.avatar = self.db.get_avatar()

        # ✅ Update the actual UI elements, not just internal variables
        self.avatar_label.text = f"{self.avatar.name}"
        self.level_label.text = f"Level : {self.avatar.level}"

        # Fetch the updated category experience
        self.category_experience = self.db.get_avatar_experience_by_category(self.avatar.id)
        # ✅ Ensure the progress bars update
        for category in self.categories:
            category_name = category.category_name  # Extract name for comparison
            exp_points = float(self.category_experience.get(category_name, 0))
            print(f"Category name = {category_name}")
            print(f"exp_point = {exp_points}")


            # Find the correct progress bar using category name
            progress_bar = None
            for cat, bar in self.category_bars.items():
                if cat.category_name == category_name:
                    progress_bar = bar
                    break

            if progress_bar:
                category_layout = progress_bar.parent  # Get the parent layout
                category_layout.remove_widget(progress_bar)  # Remove old progress bar

                # Create a new progress bar
                new_bar = MDProgressBar(
                    value=exp_points,
                    max=100,
                    size_hint_x=0.6,
                    size_hint_y=None,
                    height=10
                )
                new_bar.pos_hint = {'center_y': 0.5}

                category_layout.add_widget(new_bar)  # Add new progress bar
                self.category_bars[category] = new_bar  # Update reference


class QuestScreen(MDBottomNavigationItem):
    def __init__(self,avatar_screen, **kwargs):
        super().__init__(**kwargs)
        self.name = 'quests'
        self.text = 'All Quests'
        self.avatar_screen = avatar_screen

        # Data
        self.db = DataManager()
        self.avatar = self.db.get_avatar()

        # UI
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.quest_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.quest_list.bind(minimum_height=self.quest_list.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.quest_list)
        self.layout.add_widget(scroll_view)

        self.add_widget(self.layout)

        self.load_quests()

    def load_quests(self):
        """Fetch quests from the database and populate the UI."""
        self.quest_list.clear_widgets()  # Clear existing quests
        self.quests = self.db.get_avatar_quests(self.avatar)  # Fetch quests

        for quest in self.quests:
            self.add_quest_ui(quest)

    def add_quest_ui(self, quest_data):
        """Create a UI quest box from a quest dictionary."""
        quest_box = QuestBox(quest_data['id'],orientation='horizontal', size_hint_y=None, height=60, padding=10)

        # Quest info
        quest_label = MDLabel(text=quest_data["quest_name"])
        quest_box.add_widget(quest_label)

        date_label = MDLabel(text=quest_data["due_date"])
        quest_box.add_widget(date_label)

        category_label = MDLabel(text=quest_data["category_name"])
        quest_box.add_widget(category_label)

        exp_label = MDLabel(text=f"EXP: {quest_data['exp_amount']}", theme_text_color="Secondary")
        quest_box.add_widget(exp_label)

        if quest_data["completed"]:
            quest_box.change_color(0, 1, 0)  # Green

        # Quest controls
        v_button = MDIconButton(icon="check-circle", pos_hint={'center_y': 0.5},
                                on_release=lambda instance, box=quest_box: self.change_status(box))
        quest_box.add_widget(v_button)

        delete_button = MDIconButton(icon="delete", pos_hint={'center_y': 0.5},
                                     on_release=lambda instance, box=quest_box: self.remove_quest(box))
        quest_box.add_widget(delete_button)

        self.quest_list.add_widget(quest_box)

    def remove_quest(self, quest_box):
        """Remove a quest box from the UI."""
        self.quest_list.remove_widget(quest_box)
        self.db.swap_quest_status(quest_box.quest_id)
        self.db.update_experience(quest_box.quest_id)
        self.db.remove_quest(quest_box.quest_id)
        self.avatar_screen.refresh_avatar_view()



    def change_status(self, quest_box):
        self.db.swap_quest_status(quest_box.quest_id)
        self.db.update_experience(quest_box.quest_id)
        self.avatar_screen.refresh_avatar_view()
        quest = self.db.get_quest_by_id(quest_box.quest_id)
        if quest:
            # Change color based on new status
            if quest.completed:
                quest_box.change_color(0, 1, 0)  # Green (Completed)
            else:
                quest_box.change_color(1, 1, 1)  # White (Not Completed)



class AddQuestScreen(MDBottomNavigationItem):
    def __init__(self, quest_screen, avatar_screen, **kwargs):
        super().__init__(**kwargs)
        self.name = 'add'
        self.text = 'Add'
        self.quest_screen = quest_screen
        self.avatar_screen = avatar_screen
        self.db = DataManager()


        # ScrollView for dynamic layout
        scroll_view = ScrollView(size_hint=(1, 1))

        # BoxLayout for quest input UI elements
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        # Quest input field
        self.quest_input = MDTextField(hint_text='Add a quest...')
        self.layout.add_widget(self.quest_input)

        # Date picker field (readonly)
        self.date_input = MDTextField(hint_text='Select Date', readonly=True)
        self.date_input.bind(focus=self.show_date_picker)  # Open date picker when focused
        self.layout.add_widget(self.date_input)

        # Category input field (readonly)
        self.category_input = MDTextField(hint_text='Select Category', readonly=True)
        self.category_input.bind(focus=self.show_category_menu)  # Open category dropdown when focused
        self.layout.add_widget(self.category_input)

        # Dropdown menu for categories
        self.category_menu = MDDropdownMenu(
            caller=self.category_input,
            items=[
                {'text': 'wisdom', 'on_release': lambda x='wisdom': self.set_category(x)},
                {'text': 'constitution', 'on_release': lambda x='constitution': self.set_category(x)},
                {'text': 'reflexion', 'on_release': lambda x='reflexion': self.set_category(x)},
                {'text': 'family', 'on_release': lambda x='family': self.set_category(x)},
            ],
            width_mult=4
        )

        # Experience input field (integer)
        self.exp_input = MDTextField(
            hint_text='Enter experience points',
            input_filter='int',
            multiline=False
        )
        self.layout.add_widget(self.exp_input)


        # Button to add quest
        add_button = MDRaisedButton(
            text='Add',
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={'center_x': 0.5},
            on_release=self.add_quest  # Call add_quest method
        )
        self.layout.add_widget(add_button)

        # Add layout to scroll view and to the screen
        scroll_view.add_widget(self.layout)
        self.add_widget(scroll_view)

    def show_date_picker(self, instance, value):
        if value:
            date_dialog = MDDatePicker()
            date_dialog.bind(on_save=self.on_date_selected)
            date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        self.date_input.text = value.strftime('%Y-%m-%d')

    def show_category_menu(self, instance, value):
        if value:
            self.category_menu.open()

    def set_category(self, category):
        self.category_input.text = category
        self.category_menu.dismiss()

    def add_quest(self, instance):
        quest_text = self.quest_input.text.strip()
        category_text = self.category_input.text if self.category_input.text else 'No category'
        date_text = self.date_input.text if self.date_input.text else None  # Use None if no date
        exp_amount = int(self.exp_input.text)

        if quest_text:
            # Save the quest in the database
            self.db.add_quest(self.avatar_screen.avatar.id, quest_text, category_text, exp_amount, date_text)

            # Refresh quest list dynamically
            self.quest_screen.load_quests()
