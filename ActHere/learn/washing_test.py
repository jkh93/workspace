from django.test import TestCase

SERVER = 'http://testserver'


class WashTest(TestCase):
    fixtures = ['test_data.json']

    def test_add_wash_step(self):
        pass

