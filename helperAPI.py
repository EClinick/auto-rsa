# Nelson Dane
# Helper functions and classes
# to share between scripts

import asyncio
import textwrap
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType


class Brokerage:
    def __init__(self, name):
        self.name = name  # Name of brokerage
        self.account_numbers = {}  # Dictionary of account names and numbers
        self.loggedInObjects = []  # List of logged in objects

    def add_account_number(self, name, number):
        if name in self.account_numbers:
            self.account_numbers[name].append(number)
        else:
            self.account_numbers[name] = [number]

    def get_account_numbers(self, name):
        return self.account_numbers[name]

    def __str__(self):
        return textwrap.dedent(
            f"""
            Brokerage: {self.name}
            Account Numbers: {self.account_numbers}
            Logged In Objects: {self.loggedInObjects}
        """
        )


def type_slowly(element, string, delay=0.3):
    # Type slower
    for character in string:
        element.send_keys(character)
        sleep(delay)


def check_if_page_loaded(driver):
    # Check if page is loaded
    readystate = driver.execute_script("return document.readyState;")
    return readystate == "complete"


def getDriver(DOCKER=False):
    # Init webdriver options
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    if DOCKER:
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        # Docker uses specific chromedriver installed via apt
        driver = webdriver.Chrome(
            service=ChromiumService("/usr/bin/chromedriver"),
            options=options,
        )
    else:
        driver = webdriver.Chrome(
            service=ChromiumService(
                ChromeDriverManager(
                    chrome_type=ChromeType.CHROMIUM, cache_valid_range=30
                ).install()
            ),
            options=options,
        )
    driver.maximize_window()
    return driver


def killDriver(brokerObj):
    # Kill all drivers
    for driver in brokerObj.loggedInObjects:
        print(f"Killed Selenium driver {brokerObj.loggedInObjects.index(driver) + 1}")
        driver.close()
        driver.quit()


def printAndDiscord(message, ctx=None, loop=None):
    # Print message
    print(message)
    # Send message to Discord
    if ctx is not None and loop is not None:
        sleep(0.5)
        asyncio.run_coroutine_threadsafe(ctx.send(message), loop)
