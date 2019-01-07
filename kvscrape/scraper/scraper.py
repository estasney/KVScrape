from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import platform
import glob
import os
import re


from selenium.webdriver.common.by import By


"""
Custom Exceptions
"""


class ElementNotFound(Exception):

    def __init__(self, message, url):

        super().__init__(message)

        self.url = url


class UnsupportedOS(Exception):

    def __init__(self):
        message = "Chromedriver version for {} not found".format(platform.system())
        super().__init__(message)



"""
Custom Selenium Waits
"""


class NomadDriver(object):

    TEXT = 'innerText'
    URL = 'href'

    def __init__(self, service_folder):
        self.service_folder = os.path.realpath(service_folder)
        self.service_path = self.select_chromedriver(self.service_folder)
        self.driver = self.start_driver()
        self.wait = WebDriverWait(self.driver, 20)


    @property
    def driver_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_extension("scraper/resources/selector_gadget.crx")
        return chrome_options

    @property
    def page_source(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    def select_chromedriver(self, service_folder):
        system_os = platform.system().lower()
        available_chromedrivers = glob.glob("{service_folder}{sep}chromedriver*".format(service_folder=service_folder,
                                                                                        sep=os.path.sep))
        selected_driver = next((driver for driver in available_chromedrivers if system_os in driver), None)
        if not selected_driver:
            raise UnsupportedOS
        return selected_driver

    def find_element(self, by, value):
        try:
            elements = self.driver.find_element(by, value)
        except:
            return None
        return elements

    def find_elements(self, by, value):
        try:
            elements = self.driver.find_elements(by, value)
        except:
            return None
        return elements

    def extract_from_elements(self, elements, attribute):
        if attribute == 'text':
            attribute = "innerText"
        if not elements:
            return None
        results = []

        for e in elements:
            results.append(e.get_attribute(attribute))
        return results

    def start_driver(self):
        return webdriver.Chrome(executable_path=self.service_path, chrome_options=self.driver_options)

    def validate_url(self, url):
        if re.match(r"((http)s?://)", url):
            return url
        else:
            return "https://{}".format(url)

    def goto(self, url):
        url = self.validate_url(url)
        self.driver.get(url)



    def maximize_window(self):
        if self.driver:
            self.driver.maximize_window()

    def shutdown(self):
        if self.driver:
            try:
                self.driver.close()
                self.driver.quit()
            except WebDriverException:
                pass


