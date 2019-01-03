from kivy.app import App
from kivy.config import Config
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.clock import Clock
from datetime import datetime
from kvscrape.buttons import *
from scraper import ScraperView, SelectorView
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')


class SplashScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

class MainApp(App):

    APP_NAME = "Scraper"
    APP_VERSION_ = 1
    APP_VERSION = "v{}".format(APP_VERSION_)
    APP_ICON_PATH = os.path.realpath("resources/images/logo.png")

    clock_time = StringProperty()
    resource_dir = StringProperty()





    def get_time(self, *args, **kwargs):
        self.clock_time = datetime.strftime(datetime.now(), "%I:%M:%S %p")

    def on_scraper_status(self, *args, **kwargs):
        if self.scraper_status == 'Online':
            self.scraper_status_color = self.GREEN_TEXT
        else:
            self.scraper_status_color = self.RED_TEXT
        self.switch_accordion()


    def app_update(self, *args, **kwargs):
        for k, v in kwargs.items():
            print(k, v)
            setattr(self, k, v)

    def build(self):
        self.get_time()
        Clock.schedule_interval(self.get_time, 0.1)




if __name__ == "__main__":

    MainApp().run()
