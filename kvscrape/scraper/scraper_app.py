from kivy.uix.accordion import AccordionItem, Accordion
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kvscrape.buttons import *
import os
from kivy.lang import Builder
from kivy.app import App
from .scraper import NomadDriver

Builder.load_file('scraper/scraper_app.kv')
GREEN_TEXT = "#21fc0d"
RED_TEXT = "#fe420f"


class ScraperScreen(Screen):

    GREEN_TEXT = "#21fc0d"
    RED_TEXT = "#fe420f"

    scraper_actions = ObjectProperty()
    scraper_actions_scraper = ObjectProperty()
    scraper_actions_selector = ObjectProperty()
    scraper_status_bar = ObjectProperty()

    scraper_online_ = BooleanProperty(False)
    scraper_status = StringProperty("Scraper: [color={label_color}]Offline[/color]".format(label_color=RED_TEXT))

    scraper = None

    selectors = ListProperty()

    def launch(self):
        self.scraper = NomadDriver(service_folder=os.path.realpath("scraper/resources"))
        self.scraper_online_ = True

    def shutdown(self):
        self.scraper.shutdown()
        self.scraper = None
        self.scraper_online_ = False

    def on_scraper_online_(self, *args):
        if self.scraper_online_:
            self.scraper_status = "Scraper: [color={label_color}]Online[/color]".format(label_color=self.GREEN_TEXT)
        else:
            self.scraper_status = "Scraper: [color={label_color}]Offline[/color]".format(label_color=self.RED_TEXT)

    def preview(self, *args, **kwargs):
        selector = kwargs['selector']
        results = self.scraper.find_elements("xpath", selector)
        for r in results:
            print(r.get_attribute('href'))

    def select(self, *args, **kwargs):
        selector = kwargs['selector']
        results = self.scraper.find_element("xpath", selector)
        print(results)

    def popup_entry(self, widget, *args, **kwargs):
        selector = SelectorColumn(column_name=widget.column_name, selector_text=widget.selector_text,
                                  selector_type=widget.selector_type)
        self.selectors.append(selector)


    def selector_popup(self, col_name, *args, **kwargs):
        popup = SelectorPopup(title=col_name)
        popup.bind(on_dismiss=self.popup_entry)
        popup.open()


class SelectorColumn(object):

    def __init__(self, column_name, selector_text, selector_type):
        self.column_name = column_name
        self.selector_text = selector_text
        self.selector_type = selector_type

    @property
    def value(self):
        if self.column_name and self.column_name != "":
            return self.column_name
        else:
            return self.selector_text


class ScreenNav(BoxLayout):
    pass


class ScraperActions(Accordion):
    pass


class ScraperStatusBar(BoxLayout):

    # Register callback with ScraperScreen
    # Pass ScraperScreen.scraper_actions.scraper_status

    status_label = ObjectProperty()


class ScraperView(AccordionItem):

    TITLE = "Scraper"

    button1 = ObjectProperty()
    button2 = ObjectProperty()
    scraper_root = ObjectProperty()


class SelectorView(AccordionItem):

    TITLE = "Selector"

    def get_scraper(self):
        return App.get_running_app().scraper

class SelectorPopup(Popup):
    pass


















