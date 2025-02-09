from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivy.clock import Clock
from models import DataManager
from kivy.uix.widget import Widget
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
from kivy.uix.boxlayout import BoxLayout


class AvatarScreen(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'avatar'
        self.text = 'Avatar'

        # Data
        self.db = DataManager()
        self.avatar = self.db.get_avatar()
        self.categories = self.db.get_categories()
        self.category_experience = self.db.get_avatar_experience_by_category(self.avatar.id)

        # UI Widgets
        self.layout = BoxLayout(
            orientation='vertical',
            padding=[10, 40, 10, 10],
            spacing=10,
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.avatar_label = MDLabel(
            text=f"{self.avatar.name}",
            halign='center',
            size_hint_y=1
        )
        self.avatar_label.bind(on_touch_down=self.on_name_double_tap)

        self.level_label = MDLabel(
            text=f"Level : {self.avatar.level}",
            halign='center',
            size_hint_y=None,
            height=15,
            font_style="Caption"
        )

        # View building
        scroll_view = ScrollView(size_hint=(1, 1))
        self.name_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10, size_hint_x=0.5,
                                  pos_hint={'center_x': 0.5})
        self.name_box.add_widget(self.avatar_label)
        self.layout.add_widget(self.name_box)
        self.layout.add_widget(self.level_label)
        self.layout.add_widget(Widget(size_hint=(None, None), size=(1, 20)))  # Spacer
        self.create_categories_UI()  # Dynamic elements stored inside the functions
        scroll_view.add_widget(self.layout)
        self.add_widget(scroll_view)

    # Create the categories widgets and progress bars
    def create_categories_UI(self):
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
                size_hint_x=0.33
            )
            category_layout.add_widget(category_label)

            exp_points = self.category_experience.get(category.category_name, 0)

            progress_bar = MDProgressBar(
                value=exp_points,
                max=100,
                size_hint_x=0.65,
                size_hint_y=None,
                height=10
            )

            progress_bar.pos_hint = {'center_y': 0.5}
            category_layout.add_widget(progress_bar)
            spacer = Widget(size_hint_x=0.25)  # Spacer
            category_layout.add_widget(spacer)

            # Add the category_layout to the main one of the view
            self.layout.add_widget(category_layout)
            self.category_bars[category] = progress_bar

    def on_name_double_tap(self, instance, touch):
        """Detect double tap and switch to text field for editing."""
        if instance.collide_point(*touch.pos):  # Check if touch is inside label
            if touch.is_double_tap:
                self.enable_name_edit()

    def enable_name_edit(self):
        """Replace the avatar label with an editable text field."""
        # Remove the label from the name box
        self.name_box.remove_widget(self.avatar_label)

        # Create an MDTextField pre-filled with the current name
        self.name_edit = MDTextField(
            text=self.avatar.name,
            multiline=False,
            size_hint_y=None,  # Disable automatic height adjustment
            height=40,  # Set height explicitly to match the layout
            halign="center",  # Center text
            background_color=(1, 1, 1, 0),  # Transparent background (optional)
            foreground_color=(0, 0, 0, 1),  # Set text color to black
            padding=[10, 10]  # Add some padding to make it look cleaner
        )
        # Bind the focus event so that when focus is lost, we update the name
        self.name_edit.bind(focus=self.on_name_focus)

        # Insert the text field at the beginning of the name_box
        self.name_box.add_widget(self.name_edit)
        Clock.schedule_once(self.set_focus, 0.1)

    def set_focus(self, dt):
        """Set the focus to the text input after it is rendered."""
        if hasattr(self, 'name_edit'):
            self.name_edit.focus = True

    def on_name_focus(self, instance, value):
        """When the text field loses focus, update the avatar name."""
        if not value:  # Focus lost
            new_name = instance.text.strip()
            if new_name and new_name != self.avatar.name:
                # Update the DB
                success = self.db.update_avatar_name(self.avatar.id, new_name)
                if success:
                    # Update internal data and refresh UI
                    self.avatar.name = new_name
                    self.avatar_label.text = new_name

            # Remove the text field and re-add the label
            self.name_box.remove_widget(self.name_edit)
            self.name_box.add_widget(self.avatar_label)
            # Optionally, force a UI refresh:
            Clock.schedule_once(lambda dt: self.avatar_label.canvas.ask_update())

    def refresh_avatar_view(self):
        """Refreshes the avatar view UI properly."""
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
