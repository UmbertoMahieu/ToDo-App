from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from models import DataManager
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout

class AddQuestScreen(MDBottomNavigationItem):
    def __init__(self, quest_screen, avatar_screen, **kwargs):
        super().__init__(**kwargs)
        self.name = 'add'
        self.text = 'Add'
        self.quest_screen = quest_screen
        self.avatar_screen = avatar_screen
        self.db = DataManager()


        ## ELEMENTS
        # Quest input field
        self.quest_input = MDTextField(
            hint_text='Add a quest...'
        )

        # Date picker field
        self.date_input = MDTextField(
            hint_text='Select Date',
            readonly=True)

        # Category input field
        self.category_input = MDTextField(
            hint_text='Select Category',
            readonly=True
        )

        # Experience input field
        self.exp_input = MDTextField(
            hint_text='Enter experience points',
            input_filter='int',
            multiline=False
        )

        # Button to add quest
        self.add_button = MDRaisedButton(
            text='Add',
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={'center_x': 0.5},
            on_release=self.add_quest
        )


        #BUILD
        scroll_view = ScrollView(size_hint=(1, 1))
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.layout.add_widget(self.quest_input)

        self.date_input.bind(focus=self.show_date_picker)
        self.layout.add_widget(self.date_input)

        self.category_input.bind(focus=self.show_category_menu)
        self.layout.add_widget(self.category_input)
        self.category_menu = None # Initialize the category menu (but fill it dynamically later)
        self.populate_category_menu()  # Fetch categories from DB

        self.layout.add_widget(self.exp_input)

        self.layout.add_widget(self.add_button)

        scroll_view.add_widget(self.layout) # Add layout to scroll view and to the screen
        self.add_widget(scroll_view)


    ## LOGIC
    # Fetch categories and add them to the view
    def populate_category_menu(self):
        """Fetch categories from DB and populate dropdown."""
        categories = self.db.get_categories()  # Fetch categories from DB

        menu_items = []
        for category in categories:
            menu_items.append({
                'text': category.category_name,  # Assuming Category model has a `name` attribute
                'on_release': lambda x=category.category_name: self.set_category(x)
            })

        # Initialize the category dropdown menu
        self.category_menu = MDDropdownMenu(
            caller=self.category_input,
            items=menu_items,
            width_mult=4
        )

    # Open the category selection menu dynamically
    def show_category_menu(self, instance, value):
        if value:
            if self.category_menu:
                self.category_menu.open()
            else:
                print("Category menu is not initialized")

    # Set the selected category in the input field and close the menu
    def set_category(self, category):
        self.category_input.text = category
        self.category_menu.dismiss()

    # Open date picker when the date input is focused
    def show_date_picker(self, instance, value):
        if value:
            date_dialog = MDDatePicker()
            date_dialog.bind(on_save=self.on_date_selected)
            date_dialog.open()

    #Set the selected date in the input field
    def on_date_selected(self, instance, value, date_range):
        self.date_input.text = value.strftime('%Y-%m-%d')

    #Save the quest to the database and refresh the quest list
    def add_quest(self, instance):
        quest_text = self.quest_input.text.strip()
        category_text = self.category_input.text if self.category_input.text else 'No category'
        date_text = self.date_input.text if self.date_input.text else None  # Use None if no date
        exp_amount = int(self.exp_input.text) if self.exp_input.text.isdigit() else 0

        if quest_text:
            # Save the quest in the database
            self.db.add_quest(self.avatar_screen.avatar.id, quest_text, category_text, exp_amount, date_text)

            # Refresh quest list dynamically
            self.quest_screen.load_quests()