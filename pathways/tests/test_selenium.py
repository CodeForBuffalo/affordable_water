from django.test import LiveServerTestCase, TestCase, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Selenium
class PathwaysTestCase(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Chrome('node_modules/chromedriver/lib/chromedriver/chromedriver.exe')
        activate('en')
        super(PathwaysTestCase, self).setUp()
    
    def tearDown(self):
        self.selenium.quit()
        super(PathwaysTestCase, self).tearDown()
    
    def test_home(self):
        selenium = self.selenium
        selenium.get(self.live_server_url)
        elements = selenium.find_elements_by_tag_name('h1')
        self.assertEqual(elements[0].text, _('Apply for assistance in 10 minutes'))