from kivy.uix.accordion import AccordionItem, Accordion
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty, AliasProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock, mainthread
from kvscrape.buttons import *
import os
import threading
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
    scraper_thread = None

    selectors = ListProperty()

    stop = threading.Event()

    def start_second_thread(self, target_function, *args, **kwargs):
        threading.Thread(target=target_function, args=args, kwargs=kwargs).start()

    def launch(self):
        self.start_second_thread(self._launch)

    def _launch(self):
        self.scraper = NomadDriver(service_folder=os.path.realpath("scraper/resources"))
        self.scraper_online_ = True
        self.scraper.goto("http://books.toscrape.com/")
        return None

    def shutdown(self):
        self.start_second_thread(self._shutdown)

    def _shutdown(self):
        self.scraper.shutdown()
        self.scraper = None
        self.scraper_online_ = False

    def on_scraper_online_(self, *args):
        if self.scraper_online_:
            self.scraper_status = "Scraper: [color={label_color}]Online[/color]".format(label_color=self.GREEN_TEXT)
        else:
            self.scraper_status = "Scraper: [color={label_color}]Offline[/color]".format(label_color=self.RED_TEXT)

    def _preview_elements(self, selector_text, selector_type, callback):
        by = 'css selector'
        results = self.scraper.find_elements(by, selector_text)
        extract_type = getattr(self.scraper, selector_type.upper(), "text")
        results_data = self.scraper.extract_from_elements(results, extract_type)
        callback(results_data)

    def select(self, *args, **kwargs):
        selector = kwargs['selector']
        results = self.scraper.find_element("xpath", selector)
        print(results)

    def refresh_selectors(self):
        selector_copy = list(self.selectors)
        self.selectors = []
        selector_copy.sort(key=lambda x: x.column_num)
        self.selectors = selector_copy

    def selector_popup(self, col_name, kind='edit', *args, **kwargs):
        """
        Handle opening a Popup for creation or editing a selector
        """
        col_num, col_name = col_name.split(": ")
        col_num = int(col_num)
        if kind == 'new':
            popup = SelectorPopup(title=col_name)
            popup.column_num = col_num

        else:
            matched_selector = next((s for s in self.selectors if s.column_num == col_num), None)
            if not matched_selector:
                popup = SelectorPopup(title=col_name)
                popup.column_num = col_num
            else:
                popup = SelectorPopup(title=col_name)
                for k in ['selector_text', 'selector_type', 'column_name', 'column_num']:
                    setattr(popup, k, getattr(matched_selector, k))

        popup.bind(on_dismiss=self.selector_popup_entry)
        popup.open()

    def selector_popup_entry(self, popup, *args, **kwargs):
        """
        Receives a dismissed popup and updates selectors accordingly
        :param popup:
        :return:
        """
        if not popup.was_saved and not popup.was_deleted:
            return

        if popup.was_deleted:
            matched_selector = next((s for s in self.selectors if s.column_num == popup.column_num), None)
            selector_copy = list(self.selectors)
            retained_selectors = [s for s in selector_copy if s.column_num != matched_selector.column_num]
            retained_selectors.sort(key=lambda x: x.column_num)
            # set column_num to reflect index
            for i, rs in enumerate(retained_selectors):
                rs.column_num = i
            self.selectors = []
            self.selectors = retained_selectors

        else:
            matched_selector = next((s for s in self.selectors if s.column_num == popup.column_num), None)

            if not matched_selector:
                selector = Selector(column_num=popup.column_num, column_name=popup.column_name,
                                    selector_text=popup.selector_text, selector_type=popup.selector_type)
                self.selectors.append(selector)
            else:
                for k in ['column_name', 'selector_text', 'selector_type']:
                    setattr(matched_selector, k, getattr(popup, k, ""))
                self.refresh_selectors()

    def preview_popup(self, col_name, *args, **kwargs):
        """
        Handle opening a Popup for previewing results of a selector
        """
        col_num, col_name = col_name.split(": ")
        col_num = int(col_num)

        # Lookup value for this selector
        matched_selector = next((s for s in self.selectors if s.column_num == col_num), None)
        if not matched_selector:
            return

        # Open the popup without results
        # Popup will listen for results to be passed and will handle display

        popup = SelectorPreviewPopup(title=col_name)
        popup.selector_text = matched_selector.selector_text
        popup.column_name = col_name
        popup.open()

        def callback(results):
            popup.results = results

        selector_text = matched_selector.selector_text
        selector_type = matched_selector.selector_type

        self.start_second_thread(target_function=self._preview_elements, selector_text=selector_text,
                                 selector_type=selector_type, callback=callback)


class Selector(object):

    def __init__(self, column_num, column_name, selector_text, selector_type):
        self.column_num = column_num
        self.column_name = column_name
        self.selector_text = selector_text
        self.selector_type = selector_type

    @property
    def value(self):
        return "{}: {}".format(self.column_num, self.column_name)


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

    selector_text = StringProperty()
    selector_type = StringProperty()
    column_name = StringProperty()
    was_saved = BooleanProperty()
    was_deleted = BooleanProperty()

    column_num = -1

    def __init__(self, **kwargs):
        super(SelectorPopup, self).__init__(**kwargs)

    def dismiss_update(self, *largs, **kwargs):
        if 'save' in kwargs:
            self.was_saved = kwargs.pop('save')
        else:
            self.was_saved = False
        if 'delete' in kwargs:
            self.was_deleted = kwargs.pop('delete')
        else:
            self.was_deleted = False
        self.dismiss()


class SelectorPreviewPopup(Popup):

    results = ListProperty()
    selector_text = StringProperty()
    column_name = StringProperty()

    results_box = ObjectProperty()
    results_count = ObjectProperty()


    def __init__(self, **kwargs):
        super(SelectorPreviewPopup, self).__init__(**kwargs)

    def on_results(self, *args):
        if len(self.results) < 1:
            pass
        else:
            self.populate_results()

    def populate_results(self):
        self.results_box.clear_widgets()

        layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for r in self.results:
            l = Label(text=r, font_size=15, size_hint_y=None)
            layout.add_widget(l)
        box = self.results_box
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        box.add_widget(scroll_view)






















