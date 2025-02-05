from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle

class ColoredBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.color = Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def change_color(self, r, g, b):
        self.color.rgba = (r, g, b, 1)
