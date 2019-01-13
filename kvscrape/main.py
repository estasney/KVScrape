from kivy.app import App
from kivy.config import Config
from copy import deepcopy
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, ListProperty, NumericProperty, DictProperty
from kivy.clock import Clock
from datetime import datetime
from buttons import RedButton, GreenButton, RoundedButton


from kvscrape.scraper import NomadDriver

import threading

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')


class ScreenManagement(ScreenManager):
    pass


class SplashScreen(Screen):
    pass


class FormItem(BoxLayout):

    field_name = StringProperty()
    field_role = StringProperty()
    field_value = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FormItemSpinner(BoxLayout):

    field_name = StringProperty()
    field_role = StringProperty()
    field_value = StringProperty()
    field_options = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MyActionView(Screen):

    index = NumericProperty()
    available_options = ObjectProperty()
    action = StringProperty()
    target = StringProperty()
    facets = ListProperty()

    action2fields = {'Click': [{'cname': FormItem, 'field_name': 'CSS Selector', 'field_role': 'target'}],
                     'Extract': [{'cname': FormItem, 'field_name': 'CSS Selector', 'field_role': 'target'},
                                 {'cname': FormItemSpinner, 'field_name': 'Extract', 'field_role': 'options',
                                 'field_options': ['URL', 'Text']}]
                     }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_parent(self, *args):
        # if facets are available draw them
        if len(self.facets) < 1:
            return
        facets = deepcopy(self.facets)
        for facet in facets:
            facet_cls = facet.pop('cname')
            item = facet_cls(**facet)
            self.available_options.add_widget(item)

    def display_options(self, selected, *args):
        self.available_options.clear_widgets()
        # Get the appropriate fields
        fields = deepcopy(self.action2fields.get(selected))
        if not fields:
            return
        for f in fields:
            field_cls = f.pop('cname')
            item = field_cls(**f)
            self.available_options.add_widget(item)

    def go_actions(self, selected, *args):
        # compile values from displayed facets
        target = next((x for x in self.available_options.children if x.field_role == 'target'), None)
        if not target:
            target = ''
        else:
            target = target.field_value

        def get_field_data(child):
            keys = ['field_name', 'field_role', 'field_value']
            return {k: getattr(child, k, None) for k in keys}

        data = list(map(get_field_data, self.available_options.children))
        data = {'index': self.index, 'action': selected, 'target': target, 'facets': data}
        print(data)
        self.manager.get_screen('actions').new_data(data)
        self.manager.transition.direction = 'right'
        self.manager.current = 'actions'


class ActionItem(BoxLayout):

    index = NumericProperty()
    action_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Actions(Screen):

    data = ListProperty()
    action_layout = ObjectProperty()

    def on_data(self, *args):
        self.action_layout.clear_widgets()
        for i, d in enumerate(self.data):
            w = ActionItem(action_text=d.get('action'), index=i)
            self.action_layout.add_widget(w)

    def new_data(self, data, *args):
        current_data = self.data
        self.data = []
        new_data_index = data['index']
        current_data[new_data_index] = data
        self.data = current_data


    def edit_action(self, index, *args, **kwargs):
        action_data = self.data[index]
        name = 'action{}'.format(index)

        if self.manager.has_screen(name):
            self.manager.remove_widget(self.manager.get_screen(name))

        # create a view from the data

        view = MyActionView(
            name=name,
            index=index,
            action=action_data['action'],
            target=action_data['target'],
            facets=action_data['facets']
        )

        self.manager.add_widget(view)
        view.display_options("Click")
        self.manager.transition.direction = 'left'
        self.manager.current = view.name

    def add_action(self, *args, **kwargs):
        self.data.append({'index': len(self.data), 'action': '', 'target': '', 'facets': []})
        self.edit_action(index=len(self.data) - 1)



class ScraperApp(App):

    APP_NAME = "Scraper"
    APP_VERSION_ = 1
    APP_VERSION = "v{}".format(APP_VERSION_)
    APP_ICON_PATH = os.path.realpath("resources/images/logo.png")
    GREEN_TEXT = "#21fc0d"
    RED_TEXT = "#fe420f"

    clock_time = StringProperty()
    resource_dir = StringProperty()
    scraper_online_ = BooleanProperty(False)
    scraper_status = StringProperty("Scraper: [color={label_color}]Offline[/color]".format(label_color=RED_TEXT))

    def get_time(self, *args, **kwargs):
        self.clock_time = datetime.strftime(datetime.now(), "%I:%M:%S %p")

    def on_scraper_online_(self, *args):
        if self.scraper_online_:
            self.scraper_status = "Scraper: [color={label_color}]Online[/color]".format(label_color=self.GREEN_TEXT)
        else:
            self.scraper_status = "Scraper: [color={label_color}]Offline[/color]".format(label_color=self.RED_TEXT)

    def build(self):
        self.actions = Actions()
        self.actions.data = []
        self.get_time()
        Clock.schedule_interval(self.get_time, 0.1)


if __name__ == "__main__":

    ScraperApp().run()