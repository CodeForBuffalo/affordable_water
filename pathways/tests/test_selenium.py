from django.test import LiveServerTestCase
from django.urls import reverse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

chrome_options = Options()
chrome_options.headless = True
if (os.getenv('TRAVIS_CHROME_PATH') == None):
    chrome_driver = "node_modules/chromedriver/lib/chromedriver/chromedriver.exe"
else:
    chrome_driver = "/home/travis/chromedriver/chromedriver"

class PathwaysTestCase(LiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
        activate('en')
        self.driver.implicitly_wait(10)
        super(PathwaysTestCase, self).setUp()

    def tearDown(self):
        self.driver.quit()
        super(PathwaysTestCase, self).tearDown()

    def test_home(self):
        self.driver.get(f"{self.live_server_url}")
        self.assertIn('GetBuffaloWater', self.driver.title)
        