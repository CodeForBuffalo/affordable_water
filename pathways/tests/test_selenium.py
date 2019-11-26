from django.test import LiveServerTestCase
from django.urls import reverse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
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
        self.driver.set_page_load_timeout(10)
        super(PathwaysTestCase, self).setUp()

    def tearDown(self):
        self.driver.quit()
        super(PathwaysTestCase, self).tearDown()

    def test_home_title(self):
        self.driver.get(f"{self.live_server_url}")
        self.assertIn('GetBuffaloWater', self.driver.title)

    def test_apply_now(self):
        self.driver.get(self.live_server_url)
        self.driver.find_element_by_link_text('Apply now').click()
        h1 = self.driver.find_element_by_class_name('form-card__title')
        self.assertEqual('Here\'s how Affordable Water works.', h1.text)

        self.driver.get(self.live_server_url)
        self.driver.find_element_by_link_text('Apply now').send_keys(Keys.ENTER)
        h1 = self.driver.find_element_by_class_name('form-card__title')
        self.assertEqual('Here\'s how Affordable Water works.', h1.text)
        