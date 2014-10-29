from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from main.models import *
from billing.models import PackageTransaction
import submission.models as sm
from django.contrib.auth.models import User, Group
import datetime
import pytz
import sys

SERVER = 'http://testserver'


def load_unauthenticated_redirect(self, url):
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 302)  # redirect to login page


def load_unauthenticated_redirect_location(self, url):
    redirect = '/?next='
    resp = self.client.get(url)
    self.assertEqual(resp['Location'],
                         SERVER + redirect + url)  # login page


def load_200(self, url):
    self.client.login(username='nathan', password='13ceecos')
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 200)


def load_302(self, url):
    self.client.login(username='nathan', password='13ceecos')
    resp = self.client.get(url)
    self.assertEqual(resp.status_code, 302)


def load_404(self, url):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


def log_in(self):
    self.client.login(username='nathan', password='13ceecos')


class HomeViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)  # no redirect for home
        load_200(self, url)


class UserListViewTest(TestCase):
    fixtures = ['test_data.json']

    def test_load_unauthenticated_redirect(self):
        resp = self.client.get('/user/list/')
        self.assertEqual(resp.status_code, 302)  # redirect to login page

    def test_load_unauthenticated_redirect_location(self):
        url = '/user/list/'
        redirect = '/?next='
        resp = self.client.get(url)
        self.assertEqual(resp['Location'],
                         SERVER + redirect + url)  # login page

    def test_load(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.get('/user/list/')
        self.assertEqual(resp.status_code, 200)


class UserDetailViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/user/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_post_blank(self):
        url = '/user/1/'
        log_in(self)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        url = '/user/1/'
        log_in(self)
        resp = self.client.post(url, {
            'username': 'test',
            'password': 'test',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'Tester',
            'is_active': True
             })
        self.assertEqual(resp.status_code, 302)


class UserCreateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/user/create/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        user_count = User.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'username': 'test',
            'password': 'test',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'Tester',
            'is_active': True
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(User.objects.count(), user_count + 1)

'''
class GroupListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/group/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class GroupDetailViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/group/1/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        group_count = Group.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test'
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Group.objects.count(), group_count)


class GroupCreateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/group/create/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        group_count = Group.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test'
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Group.objects.count(), group_count + 1)
'''


class TankListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/tank/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class TankUpdateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/tank/update/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class TankDeleteViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/tank/delete/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_delete(self):
        url = '/tank/delete/1/'
        tank_count = Tank.objects.count()
        log_in(self)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/tank/list/')
        self.assertEqual(Tank.objects.count(), tank_count - 1)


class TankCreateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/tank/create/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        tank_count = Tank.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': "Test Tank",
            'volume': 6000,
            'location': 1,
            'active': True
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Tank.objects.count(), tank_count + 1)


class LocationListViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/location/list/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)


class LocationUpdateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/location/update/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class LocationDeleteViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/location/delete/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class LocationCreateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/location/create/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_create(self):
        url = '/location/create/'
        location_count = Location.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'test',
            'active': True
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/location/list/')
        self.assertEqual(Location.objects.count(), location_count + 1)


class BevTypeListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/bevtype/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class BevTypeUpdateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/bevtype/update/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class BevTypeDeleteViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/bevtype/delete/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class BevTypeCreateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/bevtype/create/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_create(self):
        url = '/bevtype/create/'
        bevtype_count = BevType.objects.count()
        producttype_count = ProductType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'bt-name': 'test',
            'bt-prefix': 'TS',
            'bt-active': True,
            'bt-create_product_type': False
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/bevtype/list/')
        self.assertEqual(BevType.objects.count(), bevtype_count + 1)
        self.assertEqual(ProductType.objects.count(), producttype_count)

    def test_create_with_product_type(self):
        url = '/bevtype/create/'
        bevtype_count = BevType.objects.count()
        producttype_count = ProductType.objects.count()
        ec = sm.ExciseCategory.objects.get(name='Beer')
        log_in(self)
        resp = self.client.post(url, {
            'bt-name': 'test',
            'bt-prefix': 'TS',
            'bt-active': True,
            'bt-create_product_type': True,
            'pt-alcohol': 5.3,
            'pt-colour': '#999',
            'pt-excise_category': ec.id
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/bevtype/list/')
        self.assertEqual(BevType.objects.count(), bevtype_count + 1)
        self.assertEqual(ProductType.objects.count(), producttype_count + 1)

    def test_create_no_product_info(self):
        url = '/bevtype/create/'
        bevtype_count = BevType.objects.count()
        producttype_count = ProductType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'bt-name': 'test',
            'bt-prefix': 'TS',
            'bt-active': True,
            'bt-create_product_type': True
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(BevType.objects.count(), bevtype_count)
        self.assertEqual(ProductType.objects.count(), producttype_count)


class ProductTypeListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/producttype/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class ProductTypeUpdateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/producttype/update/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class ProductTypeDeleteViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/producttype/delete/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class ProductTypeCreateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/producttype/create/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_create(self):
        url = '/producttype/create/'
        producttype_count = ProductType.objects.count()
        productbevtype_count = ProductBevType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'test',
            'prefix': 'TS',
            'alcohol': 5.0,
            'colour': '#cccccc',
            'active': True,
            'excise_category': 1,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-id': 1,
            'form-0-proportion': 100
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/producttype/list/')
        self.assertEqual(ProductType.objects.count(), producttype_count + 1)
        self.assertEqual(ProductBevType.objects.count(),
                         productbevtype_count + 1)


class PackageTypeListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/packagetype/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class PackageTypeCreateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/packagetype/create/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_create(self):
        url = '/packagetype/create/'
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'test',
            'volume': 30,
            'variable_size': False,
            'active': True
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/packagetype/list/')
        self.assertEqual(PackageType.objects.count(), packagetype_count + 1)

    def test_create_same_name(self):
        url = '/packagetype/create/'
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg',
            'volume': 30,
            'variable_size': False,
            'active': True
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PackageType.objects.count(), packagetype_count)

    def test_create_negative_volume(self):
        url = '/packagetype/create/'
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg Negative',
            'volume': -30,
            'variable_size': False,
            'active': True
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PackageType.objects.count(), packagetype_count)

    def test_create_zero_volume(self):
        url = '/packagetype/create/'
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg 0 Vol',
            'volume': 0,
            'variable_size': False,
            'active': True
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PackageType.objects.count(), packagetype_count)

    def test_create_volume_variable(self):
        url = '/packagetype/create/'
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Tank with Vol',
            'volume': 30,
            'variable_size': True,
            'active': True
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/packagetype/list/')
        self.assertEqual(PackageType.objects.count(), packagetype_count + 1)
        tank = PackageType.objects.get(name='Tank with Vol')
        self.assertEqual(tank.volume, None)

    def test_create_no_volume_variable(self):
        url = '/packagetype/create/'
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg No Vol',
            'volume': '',
            'variable_size': True,
            'active': True
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(PackageType.objects.count(), packagetype_count + 1)

    def test_create_no_volume_not_variable(self):
        url = '/packagetype/create/'
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg No Vol not variable',
            'volume': '',
            'variable_size': False,
            'active': True
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PackageType.objects.count(), packagetype_count)


class PackageTypeUpdateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        self.package = PackageType.objects.get(name='50L Keg')

    def test_loading(self):
        url = '/packagetype/update/{}/'.format(self.package.id)
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_update(self):
        url = '/packagetype/update/{}/'.format(self.package.id)
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': '25L Keg',
            'volume': 25,
            'variable_size': False,
            'active': True
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/packagetype/list/')
        self.assertEqual(PackageType.objects.count(), packagetype_count)

    def test_update_same_name(self):
        url = '/packagetype/update/{}/'.format(self.package.id)
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': '50L Keg',
            'volume': 50,
            'variable_size': False,
            'active': False
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/packagetype/list/')
        self.assertEqual(PackageType.objects.count(), packagetype_count)

    def test_update_negative_volume(self):
        url = '/packagetype/update/{}/'.format(self.package.id)
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg Negative',
            'volume': -30,
            'variable_size': False,
            'active': True
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PackageType.objects.count(), packagetype_count)

    def test_update_zero_volume(self):
        url = '/packagetype/update/{}/'.format(self.package.id)
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg 0 Vol',
            'volume': 0,
            'variable_size': False,
            'active': True
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PackageType.objects.count(), packagetype_count)

    def test_update_volume_variable(self):
        url = '/packagetype/update/{}/'.format(self.package.id)
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg Vol',
            'volume': 30,
            'variable_size': True,
            'active': True
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/packagetype/list/')
        self.assertEqual(PackageType.objects.count(), packagetype_count)
        tank = PackageType.objects.get(name='Keg Vol')
        self.assertEqual(tank.volume, None)

    def test_update_no_volume_variable(self):
        url = '/packagetype/update/{}/'.format(self.package.id)
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg No Vol',
            'volume': '',
            'variable_size': True,
            'active': True
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(PackageType.objects.count(), packagetype_count)

    def test_update_no_volume_not_variable(self):
        url = '/packagetype/update/{}/'.format(self.package.id)
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.post(url, {
            'name': 'Keg No Vol not variable',
            'volume': '',
            'variable_size': False,
            'active': True
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PackageType.objects.count(), packagetype_count)


class PackageTypeDeleteViewTest(TransactionTestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        self.package = PackageType.objects.get(name='50L Keg')

    def test_loading(self):
        url = '/packagetype/delete/{}/'.format(self.package.id)
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_delete(self):
        url = '/packagetype/delete/{}/'.format(self.package.id)
        packagetype_count = PackageType.objects.count()
        log_in(self)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PackageType.objects.count(), packagetype_count)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/packagetype/list/')
        self.assertEqual(PackageType.objects.count(), packagetype_count - 1)

    def test_delete_used(self):
        log_in(self)
        resp = self.client.post('/brew/create/',
            {'create_date': '01/01/2014',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1200,
             'bev_type': 1})
        self.assertEqual(resp.status_code, 302)
        resp = self.client.post('/package/create/',
            {'create_date': '01/01/2014',
             'bev_tank': BevTank.objects.get(tank__id=1).id,
             'item_count': 14,
             'package_type': self.package.id,
             'empty': True,
             'notes': 'create',
             })
        self.assertEqual(resp.status_code, 302)
        url = '/packagetype/delete/{}/'.format(self.package.id)
        packagetype_count = PackageType.objects.count()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PackageType.objects.count(), packagetype_count)


class SalesItemListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/sales_item/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class SalesItemCreateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/sales_item/create/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_create(self):
        sales_item_count = om.SalesItem.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test',
            'active': True,
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-TOTAL_FORMS': 1,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count + 1)

    def test_create_same_name(self):
        sales_item_count = om.SalesItem.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test',
            'active': True,
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-TOTAL_FORMS': 1,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count + 1)
        resp = self.client.post(self.url, {
            'name': 'test',
            'active': True,
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-TOTAL_FORMS': 1,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count + 1)

    def test_create_with_unit(self):
        sales_item_count = om.SalesItem.objects.count()
        sales_item_unit_count = om.SalesItemUnit.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test',
            'active': True,
            'salesitemunit_set-0-name': 'test unit',
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-TOTAL_FORMS': 1,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count + 1)
        self.assertEqual(om.SalesItem.objects.count(),
            sales_item_unit_count + 1)

    def test_create_with_unit_same_name(self):
        sales_item_count = om.SalesItem.objects.count()
        sales_item_unit_count = om.SalesItemUnit.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test',
            'active': True,
            'salesitemunit_set-0-id': None,
            'salesitemunit_set-0-sales_item': None,
            'salesitemunit_set-0-name': 'test unit',
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-1-id': None,
            'salesitemunit_set-1-sales_item': None,
            'salesitemunit_set-1-name': 'test unit',
            'salesitemunit_set-1-active': True,
            'salesitemunit_set-TOTAL_FORMS': 2,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count)
        self.assertEqual(om.SalesItem.objects.count(), sales_item_unit_count)


class SalesItemUpdateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        log_in(self)
        self.client.post('/sales_item/create/', {
            'name': 'test',
            'active': True,
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-TOTAL_FORMS': 1,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.client.logout()
        self.sales_item = om.SalesItem.objects.get()
        self.url = '/sales_item/update/{}/'.format(self.sales_item.id)

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_update(self):
        sales_item_count = om.SalesItem.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test2',
            'active': True,
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-TOTAL_FORMS': 1,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count)
        self.assertEqual(om.SalesItem.objects.get().name, 'test2')
        self.assertEqual(om.SalesItem.objects.get().active, True)

    def test_update_same_name(self):
        sales_item_count = om.SalesItem.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test',
            'active': False,
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-TOTAL_FORMS': 1,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count)
        self.assertEqual(om.SalesItem.objects.get().name, 'test')
        self.assertEqual(om.SalesItem.objects.get().active, False)

    def test_update_add_units(self):
        sales_item_count = om.SalesItem.objects.count()
        sales_item_unit_count = om.SalesItemUnit.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test2',
            'active': True,
            'salesitemunit_set-0-name': 'test unit',
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-1-name': 'test unit 2',
            'salesitemunit_set-1-active': True,
            'salesitemunit_set-TOTAL_FORMS': 2,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count)
        self.assertEqual(om.SalesItemUnit.objects.count(),
            sales_item_unit_count + 2)
        self.assertEqual(om.SalesItem.objects.get().name, 'test2')
        self.assertEqual(om.SalesItem.objects.get().active, True)

    def test_update_change_units(self):
        log_in(self)
        self.client.post(self.url, {
            'name': 'test2',
            'active': True,
            'salesitemunit_set-0-name': 'test unit',
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-1-name': 'test unit 2',
            'salesitemunit_set-1-active': True,
            'salesitemunit_set-TOTAL_FORMS': 2,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        sui1 = om.SalesItemUnit.objects.get(name='test unit')
        sui2 = om.SalesItemUnit.objects.get(name='test unit 2')
        sales_item_count = om.SalesItem.objects.count()
        sales_item_unit_count = om.SalesItemUnit.objects.count()
        resp = self.client.post(self.url, {
            'name': 'test2',
            'active': True,
            'salesitemunit_set-0-id': sui1.pk,
            'salesitemunit_set-0-sales_order': om.SalesItem.objects.get().pk,
            'salesitemunit_set-0-name': 'test unit',
            'salesitemunit_set-0-active': False,
            'salesitemunit_set-1-id': sui2.pk,
            'salesitemunit_set-1-sales_order': om.SalesItem.objects.get().pk,
            'salesitemunit_set-1-name': 'test unit 3',
            'salesitemunit_set-1-active': True,
            'salesitemunit_set-TOTAL_FORMS': 2,
            'salesitemunit_set-INITIAL_FORMS': 2
            })
        sui1 = om.SalesItemUnit.objects.get(name='test unit')
        sui2 = om.SalesItemUnit.objects.get(active=True)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count)
        self.assertEqual(om.SalesItemUnit.objects.count(),
            sales_item_unit_count)
        self.assertEqual(sui1.active, False)
        self.assertEqual(sui2.name, 'test unit 3')
        self.assertEqual(om.SalesItem.objects.get().name, 'test2')
        self.assertEqual(om.SalesItem.objects.get().active, True)

    def test_update_delete_units(self):
        log_in(self)
        self.client.post(self.url, {
            'name': 'test2',
            'active': True,
            'salesitemunit_set-0-name': 'test unit',
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-1-name': 'test unit 2',
            'salesitemunit_set-1-active': True,
            'salesitemunit_set-TOTAL_FORMS': 2,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        sui1 = om.SalesItemUnit.objects.get(name='test unit')
        sui2 = om.SalesItemUnit.objects.get(name='test unit 2')
        sales_item_count = om.SalesItem.objects.count()
        sales_item_unit_count = om.SalesItemUnit.objects.count()
        resp = self.client.post(self.url, {
            'name': 'test2',
            'active': True,
            'salesitemunit_set-0-id': sui1.pk,
            'salesitemunit_set-0-sales_order': om.SalesItem.objects.get().pk,
            'salesitemunit_set-0-name': 'test unit',
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-1-id': sui2.pk,
            'salesitemunit_set-1-sales_order': om.SalesItem.objects.get().pk,
            'salesitemunit_set-1-name': 'test unit 2',
            'salesitemunit_set-1-active': True,
            'salesitemunit_set-1-DELETE': True,
            'salesitemunit_set-TOTAL_FORMS': 2,
            'salesitemunit_set-INITIAL_FORMS': 2
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count)
        self.assertEqual(om.SalesItemUnit.objects.count(),
            sales_item_unit_count - 1)
        resp = self.client.post(self.url, {
            'name': 'test2',
            'active': True,
            'salesitemunit_set-0-id': sui1.pk,
            'salesitemunit_set-0-sales_order': om.SalesItem.objects.get().pk,
            'salesitemunit_set-0-name': 'test unit',
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-0-DELETE': True,
            'salesitemunit_set-TOTAL_FORMS': 1,
            'salesitemunit_set-INITIAL_FORMS': 1
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count)
        self.assertEqual(om.SalesItemUnit.objects.count(),
            sales_item_unit_count - 2)


class SalesItemDeleteViewTest(TransactionTestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        log_in(self)
        self.client.post('/sales_item/create/', {
            'name': 'test',
            'active': True,
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-TOTAL_FORMS': 1,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        self.client.logout()
        self.sales_item = om.SalesItem.objects.get()
        self.url = '/sales_item/delete/{}/'.format(self.sales_item.id)

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_delete(self):
        sales_item_count = om.SalesItem.objects.count()
        log_in(self)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count - 1)

    def test_delete_with_units(self):
        log_in(self)
        resp = self.client.post('/sales_item/update/{}/'.format(self.sales_item.id), {
            'name': 'test',
            'active': True,
            'salesitemunit_set-0-name': 'test unit',
            'salesitemunit_set-0-active': True,
            'salesitemunit_set-1-name': 'test unit 2',
            'salesitemunit_set-1-active': True,
            'salesitemunit_set-TOTAL_FORMS': 2,
            'salesitemunit_set-INITIAL_FORMS': 0
            })
        sales_item_count = om.SalesItem.objects.count()
        sales_item_unit_count = om.SalesItemUnit.objects.count()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/sales_item/list/')
        self.assertEqual(om.SalesItem.objects.count(), sales_item_count - 1)
        self.assertEqual(om.SalesItemUnit.objects.count(),
            sales_item_unit_count - 2)

#     def test_delete_used(self):
#         log_in(self)
#         resp = self.client.post('/brew/create/',
#             {'create_date': '01/01/2014',
#              'product_type': 1,
#              'yeast': 222,
#              'starting_density': 1.042,
#              'dest_tank': 1,
#              'dest_volume': 1200,
#              'bev_type': 1})
#         self.assertEqual(resp.status_code, 302)
#         resp = self.client.post('/package/create/',
#             {'create_date': '01/01/2014',
#              'bev_tank': BevTank.objects.get(tank__id=1).id,
#              'item_count': 14,
#              'package_type': self.package.id,
#              'empty': True,
#              'notes': 'create',
#              })
#         self.assertEqual(resp.status_code, 302)
#         url = '/packagetype/delete/{}/'.format(self.package.id)
#         packagetype_count = PackageType.objects.count()
#         resp = self.client.get(url)
#         self.assertEqual(resp.status_code, 200)
#         self.assertEqual(PackageType.objects.count(), packagetype_count)


class BrewReportViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/brew/report/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class BrewCreateViewTest(TestCase):
    fixtures = ['test_data.json']

    def test_load_unauthenticated_redirect(self):
        resp = self.client.get('/brew/create/')
        self.assertEqual(resp.status_code, 302)  # redirect to login page

    def test_load_unauthenticated_redirect_location(self):
        url = '/brew/create/'
        redirect = '/?next='
        resp = self.client.get(url)
        self.assertEqual(resp['Location'],
                         SERVER + redirect + url)  # login page

    def test_load(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.get('/brew/create/')
        self.assertEqual(resp.status_code, 200)

    def test_create_brew(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)
        resp = self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)

    def test_long_sg(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)
        resp = self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)

    def test_5_digit_sg(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)
        resp = self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)

    def test_convert_vol(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)
        resp = self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)

    def test_blend(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        bid = Brew.objects.all()[0].id
        resp = self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 2,
             'dest_volume': 10,
             'bev_type': 1,
             'blend_with': bid})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 2)

"""
class BrewCreateFromEventViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)
        resp = self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        self.client.logout()

    def test_loading(self):
        eid = Event.objects.all()[0].id
        url = '/brew/create/' + str(eid) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)"""


class BrewDetailViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        self.client.logout()

    def test_loading(self):
        bid = Brew.objects.all()[0].id
        url = '/brew/' + str(bid) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class BrewListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/brew/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class BrewEditViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/brew/edit/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_edit(self):
        self.client.login(username='nathan', password='13ceecos')
        brew = Brew.objects.all()[0]
        bev_chunk = BevChunk.objects.get(brew=brew)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 1)
        url = '/brew/edit/' + str(brew.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2013-01-04',
            'bev_type': 1,
            'product_type': 1,
            'malt': 'Pale Ale',
            'hops': 'Cascade',
            'yeast': 'WY2124',
            'density': brew.starting_density,
            'dest_tank': bev_chunk.cur_tank.tank.id,
            'blend_with': '',
            'dest_volume': 2000.0})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 1)
        brew = Brew.objects.all()[0]
        bev_chunk = BevChunk.objects.get(brew=brew)
        self.assertEqual(brew.create_date, datetime.date(2013, 1, 4))
        self.assertEqual(brew.bev_type, BevType.objects.get(pk=1))
        self.assertEqual(bev_chunk.cur_tank.product_type,
            ProductType.objects.get(pk=1))
        self.assertEqual(brew.malt, 'Pale Ale')
        self.assertEqual(brew.hops, 'Cascade')
        self.assertEqual(brew.yeast, 'WY2124')
        self.assertEqual(bev_chunk.cur_tank.empty_date, None)
        self.assertEqual(bev_chunk.volume, 2000)
        event = Event.objects.get(event_type__name='Brew')
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 3, 11, 0, tzinfo=pytz.utc))
        measurements = Measurement.objects.all()
        for m in measurements:
            self.assertEqual(m.measurement_date, datetime.date(2013, 1, 4))

    def test_edit_with_package(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        brew = Brew.objects.all()[0]
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        url = '/brew/edit/' + str(brew.id) + '/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('LG1 can not be modified', resp.content)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)

    def test_edit_with_transfer(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        brew = Brew.objects.all()[0]
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        url = '/brew/edit/' + str(brew.id) + '/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('LG1 can not be modified', resp.content)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)


class BrewDeleteViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/brew/delete/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_delete(self):
        url = '/brew/delete/1/'
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 1)
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post(url)
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)

    def test_delete_blend(self):
        url = '/brew/delete/1/'
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 1)
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.042,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_with_transfer(self):
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)

    def test_delete_with_blend_transfer(self):
        """
        Brew, then brew on top, then transfer the blend.
        Delete the first brew, deletes the transfer,
        must leave the second brew
        The mev tank OG Measurement should update to the second brew OG
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.050)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_with_blend_transfer_2(self):
        """
        Brew, then transfer, then brew on top.
        Delete the first brew, deletes the transfer,
        must leave the second brew
        The bev tank OG Measurement should update to the second brew OG
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '02/01/2013',
            'cur_tank': 1,
            'dest_volume': 200,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.050)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_with_blend_transfer_3(self):
        """
        Brew, then brew on top, then transfer the blend.
        Delete the second brew, deletes the transfer,
        must leave the first brew
        The bev tank OG Measurement should remain the same
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_with_blend_transfer_4(self):
        """
        Brew, then transfer, then brew on top.
        Delete the second brew, does not delete the transfer,
        must leave the first brew
        The bev tank OG Measurement should not change
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '02/01/2013',
            'cur_tank': 1,
            'dest_volume': 200,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(
            Measurement.objects.filter(
                measurement_type__name='Density',
                ).earliest('id').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)

    def test_delete_with_transfer_transfer(self):
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        # First transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        # Transfer the transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': mm.BevTank.objects.latest('id').pk,
            'dest_volume': 200,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_transfer_transfer(self):
        """
        Brew, then brew on top, then transfer the blend.
        Transfer the transfer, must not delete anything.
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        # Transfer the transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '04/01/2013',
            'cur_tank': mm.BevTank.objects.latest('id').pk,
            'dest_volume': 200,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post(url)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)

    def test_delete_with_blend_transfer_transfer_2(self):
        """
        Brew, then transfer, then brew on top.
        Transfer the transfer, must not delete anything.
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '02/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        # Transfer the transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '04/01/2013',
            'cur_tank': mm.BevTank.objects.latest('id').pk,
            'dest_volume': 200,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post(url)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)

    def test_delete_with_blend_transfer_transfer_3(self):
        """
        Brew, then transfer, then brew on top.
        Transfer the transfer, must not delete anything.
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        # Transfer the transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '04/01/2013',
            'cur_tank': mm.BevTank.objects.latest('id').pk,
            'dest_volume': 200,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post(url)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)

    def test_delete_with_blend_transfer_transfer_4(self):
        """
        Brew, then transfer, then brew on top.
        Transfer the transfer
        Delete the second brew, does not delete the transfers,
        must leave the first brew
        The bev tank OG Measurement should not change
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '02/01/2013',
            'cur_tank': 1,
            'dest_volume': 200,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        # Transfer the transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '04/01/2013',
            'cur_tank': mm.BevTank.objects.latest('id').pk,
            'dest_volume': 200,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(
            Measurement.objects.filter(
                measurement_type__name='Density',
                ).earliest('id').value, 1.042)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_transfer_package(self):
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        # First transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        # Package the transfer
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': mm.BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Package.objects.count(), 1)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Package.objects.count(), 1)

    def test_delete_with_blend_transfer_package(self):
        """
        Brew, then brew on top, then transfer the blend.
        Package the transfer, must not delete anything.
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        # Package the transfer
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': mm.BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post(url)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 4)

    def test_delete_with_blend_transfer_package_2(self):
        """
        Brew, then transfer, then brew on top.
        Package the transfer, must not delete anything.
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '02/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        # Package the transfer
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': mm.BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post(url)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 4)

    def test_delete_with_blend_transfer_package_3(self):
        """
        Brew, then transfer, then brew on top.
        Package the transfer, must not delete anything.
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        # Package the transfer
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': mm.BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post(url)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 4)

    def test_delete_with_blend_transfer_package_4(self):
        """
        Brew, then transfer, then brew on top.
        Package the transfer
        Delete the second brew, does not delete the transfer and package,
        must leave the first brew
        The bev tank OG Measurement should not change
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '02/01/2013',
            'cur_tank': 1,
            'dest_volume': 200,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        # Package the transfer
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': mm.BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(
            Measurement.objects.filter(
                measurement_type__name='Density',
                ).earliest('id').value, 1.042)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_package(self):
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Package.objects.count(), 0)

    def test_delete_with_blend_package(self):
        """
        Brew, then brew on top, then package the blend.
        Delete the first brew, deletes the package,
        must leave the second brew
        The bev tank OG Measurement should update to the second brew OG
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.050)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_with_blend_package_2(self):
        """
        Brew, then package, then brew on top.
        Delete the first brew, deletes the package,
        must leave the second brew
        The bev tank OG Measurement should update to the second brew OG
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.050)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_with_blend_package_3(self):
        """
        Brew, then brew on top, then package the blend.
        Delete the second brew, deletes the package,
        must leave the first brew
        The bev tank OG Measurement should remain the same
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_with_blend_package_4(self):
        """
        Brew, then package, then brew on top.
        Delete the second brew, does not delete the package,
        must leave the first brew
        The bev tank OG Measurement should not change
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.filter(
                measurement_type__name='Density',
                ).earliest('id').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)

    def test_delete_with_package_checkout(self):
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 0)
        self.assertEqual(CheckOutBevChunk.objects.count(), 0)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)

    def test_delete_with_blend_package_checkout(self):
        """
        Brew, then brew on top, then package the blend.
        Check out the package, must not delete
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_package_checkout_2(self):
        """
        Brew, then package, then checkout, then brew on top.
        Must not delete anything
        """
        url = '/brew/delete/1/'
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_package_checkout_3(self):
        """
        Brew, then brew on top, then package the blend.
        Checkout the package.
        Must not delete anything
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_package_checkout_4(self):
        """
        Brew, then package, then checkout, then brew on top.
        Delete the second brew, does not delete the package,
        must leave the first brew
        The bev tank OG Measurement should not change
        """
        url = '/brew/delete/2/'
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(
            Measurement.objects.get(
                measurement_type__name='Density').value, 1.042)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': 1,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(
            Measurement.objects.filter(
                measurement_type__name='Density',
                ).earliest('id').value, 1.042)
        self.assertEqual(Event.objects.count(), 2)


class BrewScheduleViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/brew/schedule/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class BrewScheduleWithDateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/brew/schedule/2013-1-1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class EventTypeListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/event_type/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class EventTypeCreateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/event_type/create/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        eventtype_count = EventType.objects.count()
        log_in(self)
        resp = self.client.post(self.url, {
            'name': 'test',
            'active': True,
            'BackGroundColor': '#123123',
            'TextColor': '#000',
            'BorderColor': '#999'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(EventType.objects.count(), eventtype_count + 1)


class EventTypeUpdateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/event_type/update/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class EventTypeDeleteViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/event_type/delete/1/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class ProcessCreateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/process/create/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        process_count = Process.objects.count()
        resp = self.client.post(self.url, {
            'create_date': '01/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'type': ProcessType.objects.all()[0].id
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Process.objects.count(), process_count + 1)


class ProcessCreateWithEventViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        localtz = pytz.timezone(settings.TIME_ZONE)
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        event = Event(title='test',
                      start=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      end=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      event_type=EventType.objects.get(name='Process'),
                      scheduled=True)
        event.save()
        self.client.logout()

    def test_loading(self):
        url = '/process/create/' + str(Event.objects.all()[0].id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class ProcessDetailViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        localtz = pytz.timezone(settings.TIME_ZONE)
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        event = Event(title='test',
                      start=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      end=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      event_type=EventType.objects.get(name='Process'),
                      scheduled=True)
        process = Process(create_date=datetime.datetime(
                          2013, 1, 2, 0, 0, 0, 0, localtz),
                          bev_tank=BevTank.objects.all()[0],
                          type=ProcessType.objects.all()[0],
                          active=True)
        event.save()
        process.save()
        self.client.logout()

    def test_loading(self):
        url = '/process/' + str(Process.objects.all()[0].id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class ProcessScheduleWithDateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/process/schedule/2013-1-1/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        event_count = Event.objects.count()
        resp = self.client.post(self.url, {
            'date': '01/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'process_type': ProcessType.objects.all()[0].id
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Event.objects.count(), event_count + 1)


class TaskScheduleViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/task/schedule/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class TaskScheduleWithDateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/task/schedule/2013-1-1/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        event_count = Event.objects.count()
        resp = self.client.post(self.url, {
            'date': '01/01/2013',
            'task_type': TaskType.objects.all()[0].id
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Event.objects.count(), event_count + 1)


class ScheduleViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/schedule/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_302(self, url)


class TransferTest(TestCase):
    fixtures = ['test_data.json']

    def test_loading(self):
        url = '/transfer/create/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_thorough(self):
        '''
        brew x 2
        xfer
        xfer into same tank
        xfer to another tank
        change volume
        delete
        '''
        localtz = pytz.timezone(settings.TIME_ZONE)
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Transfer.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(TransferBevChunk.objects.count(), 0)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2014',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1200,
             'bev_type': 1})
        self.client.post('/brew/create/',
            {'create_date': '01/01/2014',
             'product_type': 2,
             'yeast': 222,
             'starting_density': 1.050,
             'dest_tank': 2,
             'dest_volume': 1000,
             'bev_type': 2})
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 2)
        bc = BevChunk.objects.get(cur_tank__tank__id=1)
        self.assertEqual(bc.volume, 1200)
        bc = BevChunk.objects.get(cur_tank__tank__id=2)
        self.assertEqual(bc.volume, 1000)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(TransferBevChunk.objects.count(), 0)
        self.assertEqual(WasteBevChunk.objects.count(), 0)

        resp = self.client.post('/transfer/create/',
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=1).id,
             'dest_volume': 500,
             'dest_tank': 3,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 3)
        bc = BevChunk.objects.get(cur_tank__tank__id=3)
        self.assertEqual(bc.volume, 500)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        tbc = TransferBevChunk.objects.get(bev_chunk__cur_tank__tank__id=1)
        self.assertEqual(tbc.volume, 500)
        self.assertEqual(WasteBevChunk.objects.count(), 0)

        resp = self.client.post('/transfer/create/',
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=2).id,
             'dest_volume': 900,
             'dest_tank': 3,
             'product_type': 1,
             'blend_with': BevTank.objects.get(tank__id=3).id,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(BevChunk.objects.count(), 4)
        bc = BevChunk.objects.get(src_tank__tank__id=2)
        self.assertEqual(bc.volume, 900)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        tbc = TransferBevChunk.objects.get(bev_chunk__cur_tank__tank__id=2)
        self.assertEqual(tbc.volume, 900)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=2)
        self.assertEqual(wbc.volume, 100)

        resp = self.client.post('/transfer/create/',
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=3).id,
             'dest_volume': 700,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 6)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=1)
        self.assertEqual(bc.volume, 250)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=2)
        self.assertEqual(bc.volume, 450)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 4)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=1)
        self.assertEqual(tbc.volume, 250)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=2)
        self.assertEqual(tbc.volume, 450)
        self.assertEqual(WasteBevChunk.objects.count(), 3)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(wbc.volume, 250)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(wbc.volume, 450)

        transfer = Transfer.objects.get(bevchunk=bc)
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url, {
            'transfer_date': '01/01/2014',
            'cur_tank': BevTank.objects.get(tank__id=3).id,
            'dest_volume': 1050,  # Changed
            'dest_tank': 4,
            'product_type': 1,
            'empty': True,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 6)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=1)
        self.assertEqual(bc.volume, 375)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=2)
        self.assertEqual(bc.volume, 675)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 4)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=1)
        self.assertEqual(tbc.volume, 375)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=2)
        self.assertEqual(tbc.volume, 675)
        self.assertEqual(WasteBevChunk.objects.count(), 3)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(wbc.volume, 125)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(wbc.volume, 225)

        transfer = Transfer.objects.get(bevchunk=bc)
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url, {
            'transfer_date': '01/01/2014',
            'cur_tank': BevTank.objects.get(tank__id=3).id,
            'dest_volume': 700,  # Changed
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,  # Changed
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 6)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=1)
        self.assertEqual(bc.volume, 250)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=2)
        self.assertEqual(bc.volume, 450)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 4)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=1)
        self.assertEqual(tbc.volume, 250)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=2)
        self.assertEqual(tbc.volume, 450)
        self.assertEqual(WasteBevChunk.objects.count(), 1)

        transfer = Transfer.objects.get(bevchunk=bc)
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url, {
            'transfer_date': '01/01/2014',
            'cur_tank': BevTank.objects.get(tank__id=3).id,
            'dest_volume': 280,  # Changed
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 6)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=1)
        self.assertEqual(bc.volume, 100)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=2)
        self.assertEqual(bc.volume, 180)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 4)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=1)
        self.assertEqual(tbc.volume, 100)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=2)
        self.assertEqual(tbc.volume, 180)
        self.assertEqual(WasteBevChunk.objects.count(), 1)

        transfer = Transfer.objects.get(bevchunk=bc)
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url, {
            'transfer_date': '02/01/2014',  # Changed
            'cur_tank': BevTank.objects.get(tank__id=3).id,
            'dest_volume': 560,  # Changed
            'dest_tank': 4,
            'product_type': 1,
            'empty': True,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 6)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=1)
        self.assertEqual(bc.volume, 200)
        bc = BevChunk.objects.get(src_tank__tank__id=3,
            parent__src_tank__tank__id=2)
        self.assertEqual(bc.volume, 360)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 4)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=1)
        self.assertEqual(tbc.volume, 200)
        tbc = TransferBevChunk.objects.get(bev_chunk__src_tank__tank__id=2)
        self.assertEqual(tbc.volume, 360)
        self.assertEqual(WasteBevChunk.objects.count(), 3)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(wbc.volume, 300)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(wbc.volume, 540)

        url = '/transfer/delete/' + str(transfer.id) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(BevChunk.objects.count(), 4)
        bc = BevChunk.objects.filter(src_tank__tank__id=3,
            parent__src_tank__tank__id=1)
        self.assertEqual(bc.count(), 0)
        bc = BevChunk.objects.filter(src_tank__tank__id=3,
            parent__src_tank__tank__id=2)
        self.assertEqual(bc.count(), 0)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        tbc = TransferBevChunk.objects.filter(bev_chunk__src_tank__tank__id=1)
        self.assertEqual(tbc.count(), 0)
        tbc = TransferBevChunk.objects.filter(bev_chunk__src_tank__tank__id=2)
        self.assertEqual(tbc.count(), 0)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        wbc = WasteBevChunk.objects.filter(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(wbc.count(), 0)
        wbc = WasteBevChunk.objects.filter(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(wbc.count(), 0)

        resp = self.client.post('/transfer/create/',
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=1).id,
             'dest_volume': 500,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 5)
        bc = BevChunk.objects.get(cur_tank__tank__id=4)
        self.assertEqual(bc.volume, 500)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 3)
        tbc = TransferBevChunk.objects.get(
            transfer__bevchunk__cur_tank__tank__id=4)
        self.assertEqual(tbc.volume, 500)
        self.assertEqual(WasteBevChunk.objects.count(), 2)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=1,
            bev_chunk__parent__cur_tank__tank__id=None)
        self.assertEqual(wbc.volume, 200)

        transfer = Transfer.objects.get(bevchunk=bc)

        resp = self.client.post('/transfer/edit/{}/'.format(transfer.id),
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=1).id,
             'dest_volume': 600,  # Changed
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 5)
        bc = BevChunk.objects.get(cur_tank__tank__id=4)
        self.assertEqual(bc.volume, 600)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 3)
        tbc = TransferBevChunk.objects.get(
            transfer__bevchunk__cur_tank__tank__id=4)
        self.assertEqual(tbc.volume, 600)
        self.assertEqual(WasteBevChunk.objects.count(), 2)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=1,
            bev_chunk__parent__cur_tank__tank__id=None)
        self.assertEqual(wbc.volume, 100)

        resp = self.client.post('/transfer/edit/{}/'.format(transfer.id),
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=1).id,
             'dest_volume': 650,  # Changed
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,  # Changed
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 5)
        bc = BevChunk.objects.get(cur_tank__tank__id=4)
        self.assertEqual(bc.volume, 650)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 3)
        tbc = TransferBevChunk.objects.get(
            transfer__bevchunk__cur_tank__tank__id=4)
        self.assertEqual(tbc.volume, 650)
        self.assertEqual(WasteBevChunk.objects.count(), 1)

        resp = self.client.post('/transfer/edit/{}/'.format(transfer.id),
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=1).id,
             'dest_volume': 450,  # Changed
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 5)
        bc = BevChunk.objects.get(cur_tank__tank__id=4)
        self.assertEqual(bc.volume, 450)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 3)
        tbc = TransferBevChunk.objects.get(
            transfer__bevchunk__cur_tank__tank__id=4)
        self.assertEqual(tbc.volume, 450)
        self.assertEqual(WasteBevChunk.objects.count(), 1)

        resp = self.client.post('/transfer/edit/{}/'.format(transfer.id),
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=1).id,
             'dest_volume': 700,  # Changed
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,  # Changed
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(BevChunk.objects.count(), 5)
        bc = BevChunk.objects.get(cur_tank__tank__id=4)
        self.assertEqual(bc.volume, 700)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(TransferBevChunk.objects.count(), 3)
        tbc = TransferBevChunk.objects.get(
            transfer__bevchunk__cur_tank__tank__id=4)
        self.assertEqual(tbc.volume, 700)
        self.assertEqual(WasteBevChunk.objects.count(), 2)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=1,
            bev_chunk__parent__cur_tank__tank__id=None)
        self.assertEqual(wbc.volume, 0)

        url = '/transfer/delete/' + str(transfer.id) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(BevChunk.objects.count(), 4)
        bc = BevChunk.objects.filter(src_tank__tank__id=3,
            parent__src_tank__tank__id=1)
        self.assertEqual(bc.count(), 0)
        bc = BevChunk.objects.filter(src_tank__tank__id=3,
            parent__src_tank__tank__id=2)
        self.assertEqual(bc.count(), 0)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        tbc = TransferBevChunk.objects.filter(bev_chunk__src_tank__tank__id=1)
        self.assertEqual(tbc.count(), 0)
        tbc = TransferBevChunk.objects.filter(bev_chunk__src_tank__tank__id=2)
        self.assertEqual(tbc.count(), 0)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        wbc = WasteBevChunk.objects.filter(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(wbc.count(), 0)
        wbc = WasteBevChunk.objects.filter(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(wbc.count(), 0)
        wbc = WasteBevChunk.objects.filter(bev_chunk__cur_tank__tank__id=1,
            bev_chunk__parent__cur_tank__tank__id=None)
        self.assertEqual(wbc.count(), 0)

        self.client.logout()


class TransferCreateWithEventViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        localtz = pytz.timezone(settings.TIME_ZONE)
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        event = Event(title='test',
                      start=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      end=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      event_type=EventType.objects.get(name='Transfer'),
                      scheduled=True)
        event.save()
        self.client.logout()

    def test_loading(self):
        url = '/transfer/create/' + str(Event.objects.all()[0].id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class TransferDetailViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        localtz = pytz.timezone(settings.TIME_ZONE)
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        event = Event(title='test',
                      start=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      end=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      event_type=EventType.objects.get(name='Process'),
                      scheduled=True)
        event.save()
        resp = self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': BevTank.objects.all()[0].id,
             'dest_volume': 950,
             'dest_tank': 2,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.client.logout()

    def test_loading(self):
        url = '/transfer/' + str(Transfer.objects.all()[0].id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class TransferScheduleWithDateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/transfer/schedule/2013-1-1/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        event_count = Event.objects.count()
        resp = self.client.post(self.url, {
            'date': '01/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'dest_tank': Tank.objects.all()[0].id
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Event.objects.count(), event_count + 1)


class TransferEditViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        self.client.logout()
        transfer = Transfer.objects.all()[0]
        url = '/transfer/edit/' + str(transfer.id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_edit_with_early_date(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        transfer = Transfer.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url, {
            'transfer_date': '03/01/2012',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(transfer.get_transfer_date(),
            datetime.date(2013, 01, 03))

    def test_edit_non_empty_to_non_empty(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url,
            {'transfer_date': '02/01/2013',
             'cur_tank': 1,
             'dest_volume': 900,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(transfer.get_transfer_date(),
            datetime.date(2013, 1, 2))
        self.assertEqual(transfer.get_dest_bevtank().product_type.id, 1)
        self.assertEqual(transfer.get_src_tank().empty_date, None)
        self.assertEqual(transfer.get_volume(), 900)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 1, 11, 0, tzinfo=pytz.utc))
        measurements = Measurement.objects.filter(
            bev_tank=transfer.get_dest_bevtank())
        for m in measurements:
            self.assertEqual(m.measurement_date, datetime.date(2013, 1, 2))

    def test_edit_non_empty_to_empty(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url,
            {'transfer_date': '02/01/2013',
             'cur_tank': 1,
             'dest_volume': 900,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 5)
        self.assertEqual(Event.objects.count(), 2)
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        measurement = Measurement.objects.get(measurement_type__name="Volume",
            value=0.0)
        self.assertEqual(transfer.get_transfer_date(),
            datetime.date(2013, 1, 2))
        self.assertEqual(transfer.get_dest_bevtank().product_type.id, 1)
        self.assertEqual(transfer.get_src_tank().empty_date,
            datetime.date(2013, 1, 2))
        self.assertEqual(transfer.get_volume(), 900)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 1, 11, 0, tzinfo=pytz.utc))
        self.assertEqual(measurement.measurement_date,
            datetime.date(2013, 1, 2))
        measurements = Measurement.objects.filter(
            bev_tank=transfer.get_dest_bevtank())
        for m in measurements:
            self.assertEqual(m.measurement_date, datetime.date(2013, 1, 2))

    def test_edit_empty_to_empty(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 5)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url,
            {'transfer_date': '02/01/2013',
             'cur_tank': 1,
             'dest_volume': 900,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 5)
        self.assertEqual(Event.objects.count(), 2)
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        measurement = Measurement.objects.get(measurement_type__name="Volume",
            value=0.0)
        self.assertEqual(transfer.get_transfer_date(),
            datetime.date(2013, 1, 2))
        self.assertEqual(transfer.get_dest_bevtank().product_type.id, 1)
        self.assertEqual(transfer.get_src_tank().empty_date,
            datetime.date(2013, 1, 2))
        self.assertEqual(transfer.get_volume(), 900)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 1, 11, 0, tzinfo=pytz.utc))
        self.assertEqual(measurement.measurement_date,
            datetime.date(2013, 1, 2))
        measurements = Measurement.objects.filter(
            bev_tank=transfer.get_dest_bevtank())
        for m in measurements:
            self.assertEqual(m.measurement_date, datetime.date(2013, 1, 2))

    def test_edit_empty_to_non_empty(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 5)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url,
            {'transfer_date': '02/01/2013',
             'cur_tank': 1,
             'dest_volume': 900,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(transfer.get_transfer_date(),
            datetime.date(2013, 1, 2))
        self.assertEqual(transfer.get_dest_bevtank().product_type.id, 1)
        self.assertEqual(transfer.get_src_tank().empty_date, None)
        self.assertEqual(transfer.get_volume(), 900)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 1, 11, 0, tzinfo=pytz.utc))
        measurements = Measurement.objects.filter(
            bev_tank=transfer.get_dest_bevtank())
        for m in measurements:
            self.assertEqual(m.measurement_date, datetime.date(2013, 1, 2))

    def test_edit_non_empty_to_non_empty_same_date(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
            })
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(
            event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url, {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 900,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(
            transfer.get_transfer_date(),
            datetime.date(2013, 1, 3))
        self.assertEqual(transfer.get_dest_bevtank().product_type.id, 1)
        self.assertEqual(transfer.get_src_tank().empty_date, None)
        self.assertEqual(transfer.get_volume(), 900)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        measurements = Measurement.objects.filter(
            bev_tank=transfer.get_dest_bevtank())
        for m in measurements:
            self.assertEqual(m.measurement_date, datetime.date(2013, 1, 3))

    def test_edit_non_empty_to_empty_same_date(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url,
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 900,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 5)
        self.assertEqual(Event.objects.count(), 2)
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        measurement = Measurement.objects.get(measurement_type__name="Volume",
            value=0.0)
        self.assertEqual(transfer.get_transfer_date(),
            datetime.date(2013, 1, 3))
        self.assertEqual(transfer.get_dest_bevtank().product_type.id, 1)
        self.assertEqual(transfer.get_src_tank().empty_date,
            datetime.date(2013, 1, 3))
        self.assertEqual(transfer.get_volume(), 900)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        self.assertEqual(measurement.measurement_date,
            datetime.date(2013, 1, 3))
        measurements = Measurement.objects.filter(
            bev_tank=transfer.get_dest_bevtank())
        for m in measurements:
            self.assertEqual(m.measurement_date, datetime.date(2013, 1, 3))

    def test_edit_empty_to_empty_same_date(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 5)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url,
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 900,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 5)
        self.assertEqual(Event.objects.count(), 2)
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        measurement = Measurement.objects.get(measurement_type__name="Volume",
            value=0.0)
        self.assertEqual(transfer.get_transfer_date(),
            datetime.date(2013, 1, 3))
        self.assertEqual(transfer.get_dest_bevtank().product_type.id, 1)
        self.assertEqual(transfer.get_src_tank().empty_date,
            datetime.date(2013, 1, 3))
        self.assertEqual(transfer.get_volume(), 900)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        self.assertEqual(measurement.measurement_date,
            datetime.date(2013, 1, 3))
        measurements = Measurement.objects.filter(
            bev_tank=transfer.get_dest_bevtank())
        for m in measurements:
            self.assertEqual(m.measurement_date, datetime.date(2013, 1, 3))

    def test_edit_empty_to_non_empty_same_date(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': True,
             })
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 5)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        url = '/transfer/edit/' + str(transfer.id) + '/'
        resp = self.client.post(url,
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 900,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)
        transfer = Transfer.objects.all()[0]
        event = Event.objects.get(event_type__name='Transfer')
        self.assertEqual(transfer.get_transfer_date(),
            datetime.date(2013, 1, 3))
        self.assertEqual(transfer.get_src_tank().empty_date, None)
        self.assertEqual(transfer.get_volume(), 900)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        measurements = Measurement.objects.filter(
            bev_tank=transfer.get_dest_bevtank())
        for m in measurements:
            self.assertEqual(m.measurement_date, datetime.date(2013, 1, 3))

    def test_edit_with_package(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        brew = Brew.objects.all()[0]
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)
        url = '/brew/edit/' + str(brew.id) + '/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('LG1 can not be modified', resp.content)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 3)

    def test_edit_with_transfer(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': 1,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        cur_tank = BevChunk.objects.filter(src_tank__isnull=False)[0].cur_tank
        resp = self.client.post('/transfer/create/',
            {'transfer_date': '04/01/2013',
             'cur_tank': cur_tank.id,
             'dest_volume': 950,
             'dest_tank': 4,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        brew = Brew.objects.all()[0]
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        url = '/brew/edit/' + str(brew.id) + '/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('LG1 can not be modified', resp.content)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)


class TransferDeleteViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()
        # Add in a second brew which we can use for the blend tests
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/', {
            'create_date': '02/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1
            })
        self.client.logout()

    def test_delete(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': True,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        st = BevTank.objects.get(pk=1)
        self.assertEqual(st.empty_date, datetime.date(2013, 1, 3))
        self.assertEqual(Measurement.objects.count(), 7)
        self.assertEqual(Event.objects.count(), 3)
        pk = Transfer.objects.all()[0].id
        url = '/transfer/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Transfer.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(TransferBevChunk.objects.count(), 0)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        st = BevTank.objects.get(pk=1)
        self.assertEqual(st.empty_date, None)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Event.objects.count(), 2)

    def test_delete_blend(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 400,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
            })
        self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 500,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': mm.BevTank.objects.latest('id').pk,
            'empty': True,
            })
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(mm.BevTank.objects.latest('id').name, 'LG1+LG1')
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        st = BevTank.objects.get(pk=1)
        self.assertEqual(st.empty_date, datetime.date(2013, 1, 3))
        self.assertEqual(Measurement.objects.count(), 7)
        self.assertEqual(Event.objects.count(), 4)
        pk = Transfer.objects.latest('id').id
        url = '/transfer/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(mm.BevTank.objects.latest('id').name, 'LG1')
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        st = BevTank.objects.get(pk=1)
        self.assertEqual(st.empty_date, None)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_transfer(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '04/01/2013',
            'cur_tank': 2,
            'dest_volume': 900,
            'dest_tank': 1,
            'product_type': 1,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 4)
        pk = Transfer.objects.get(bevchunk__create_date='2013-01-03').id
        url = '/transfer/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevChunk.objects.count(), 3)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_package(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        resp = self.client.post('/package/create/', {
            'create_date': '04/01/2013',
            'bev_tank': 3,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        self.assertEqual(Package.objects.count(), 1)
        pk = Transfer.objects.get(bevchunk__create_date='2013-01-03').id
        url = '/transfer/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 0)
        self.assertEqual(Package.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 2)

    def test_delete_with_blend_transfer(self):
        """
        Transfer, then transfer on top, then transfer the blend.
        Delete the first transfer, deletes the blend transfer,
        must leave the second transfer
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_transfer_2(self):
        """
        Transfer, then transer, then transfer on top of first.
        Delete the first transfer, deletes the next transfer,
        must leave the second transfer
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_transfer_3(self):
        """
        Transfer, then transfer on top, then transfer the blend.
        Delete the second transfer, deletes the blend transfer,
        must leave the first transfer
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_transfer_4(self):
        """
        Transfer, then transfer, then transfer on top of first.
        Delete the second transfer, does not delete the next transfer,
        must leave the first transfer
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 4)

    def test_delete_with_transfer_transfer(self):
        self.client.login(username='nathan', password='13ceecos')
        # First transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        # Transfer the transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': mm.BevTank.objects.latest('id').pk,
            'dest_volume': 200,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        # Transfer the transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': mm.BevTank.objects.latest('id').pk,
            'dest_volume': 200,
            'dest_tank': 2,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 5)

    def test_delete_with_blend_transfer_transfer(self):
        """
        Transfer, then transfer on top, then transfer the blend.
        Transfer that, try and delete first transfer.
        Must not delete anything.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': BevTank.objects.latest('id').pk,
            'dest_volume': 950,
            'dest_tank': 1,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Transfer.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Transfer.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)

    def test_delete_with_blend_transfer_transfer_2(self):
        """
        Transfer, then transfer, then transfer on top of first.
        Transfer the transfer try and delete the first transfer.
        Must not delete anything.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': BevTank.objects.latest('id').pk,
            'dest_volume': 950,
            'dest_tank': 1,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)

    def test_delete_with_blend_transfer_transfer_3(self):
        """
        Transfer, then transfer on top, then transfer the blend.
        Transfer that, try and delete second transfer.
        Must not delete anything.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': BevTank.objects.latest('id').pk,
            'dest_volume': 950,
            'dest_tank': 1,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Transfer.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Transfer.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)

    def test_delete_with_blend_transfer_transfer_4(self):
        """
        Transfer, then transfer, then transfer on top of first.
        Transfer the transfer delete the second transfer.
        Must only delete second transfer.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': BevTank.objects.latest('id').pk,
            'dest_volume': 950,
            'dest_tank': 1,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 5)

    def test_delete_with_transfer_package(self):
        self.client.login(username='nathan', password='13ceecos')
        # First transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        # Second transfer
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': BevTank.objects.latest('id').pk,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 4)
        # Package the transfer
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': mm.BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        self.assertEqual(Package.objects.count(), 1)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        self.assertEqual(Package.objects.count(), 1)

    def test_delete_with_blend_transfer_package(self):
        """
        Transfer, then transfer on top, then transfer the blend.
        Package that, try and delete first transfer.
        Must not delete anything.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 6)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 6)

    def test_delete_with_blend_transfer_package_2(self):
        """
        Transfer, then transfer, then transfer on top of first.
        Package the transfer try and delete the first transfer.
        Must not delete anything.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': BevTank.objects.latest('id').pk,
            'dest_volume': 950,
            'dest_tank': 1,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)

    def test_delete_with_blend_transfer_package_3(self):
        """
        Transfer, then transfer on top, then transfer the blend.
        Package that, try and delete second transfer.
        Must not delete anything.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 6)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 6)

    def test_delete_with_blend_transfer_package_4(self):
        """
        Transfer, then transfer, then transfer on top of first.
        Package the transfer delete the second transfer.
        Must only delete second transfer.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 3,
            'dest_volume': 950,
            'dest_tank': 3,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 4)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Measurement.objects.count(), 8)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': BevTank.objects.latest('id').pk,
            'dest_volume': 950,
            'dest_tank': 1,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Transfer.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 7)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 5)
        self.assertEqual(Measurement.objects.count(), 10)
        self.assertEqual(Event.objects.count(), 6)

    def test_delete_with_blend_package(self):
        """
        Transfer, then transfer on top, then package the blend.
        Delete the first transfer, deletes the blend package,
        must leave the second transfer
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 0)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_package_2(self):
        """
        Transfer, then package, then transfer on top of first.
        Delete the first transfer, deletes the package,
        must leave the second transfer
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_package_3(self):
        """
        Transfer, then transfer on top, then package the blend.
        Delete the second transfer, deletes the blend package,
        must leave the first transfer
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)

    def test_delete_with_blend_package_4(self):
        """
        Transfer, then package, then transfer on top of first.
        Delete the second transfer, does not delete the package,
        must leave the first transfer
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)

    def test_delete_with_package_checkout(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        url = '/package/delete/{}/'.format(Package.objects.latest('id').pk)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 0)
        self.assertEqual(CheckOutBevChunk.objects.count(), 0)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)

    def test_delete_with_blend_package_checkout(self):
        """
        Transfer, then transfer on top, then package the blend.
        Check out that, try and delete first transfer.
        Must not delete anything.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 2)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)

    def test_delete_with_blend_package_checkout_2(self):
        """
        Transfer, then package, then transfer on top.
        Check out that, try and delete first transfer.
        Must not delete anything.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)

    def test_delete_with_blend_package_checkout_3(self):
        """
        Transfer, then transfer on top, then package the blend.
        Check out that, try and delete second transfer.
        Must not delete anything.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 2)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)

    def test_delete_with_blend_package_checkout_4(self):
        """
        Transfer, then package, then transfer on top of first.
        Checkj out the package delete the second transfer.
        Must only delete second transfer.
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 1,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'empty': False,
        })
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 3)
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.latest('id').pk,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 4,
            'exempt': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        resp = self.client.post('/transfer/create/', {
            'transfer_date': '03/01/2013',
            'cur_tank': 2,
            'dest_volume': 950,
            'dest_tank': 4,
            'product_type': 1,
            'blend_with': 3,
            'empty': False,
        })
        url = '/transfer/delete/{}/'.format(Transfer.objects.latest('id').pk)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/transfer/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 5)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(Measurement.objects.count(), 6)
        self.assertEqual(Event.objects.count(), 4)


class PackageViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/package/create/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_thorough(self):
        '''
        brew x 2
        xfer
        xfer into same tank
        package empty
        change volume empty
        change volume not empty
        change volume not empty
        change date empty
        delete
        '''
        localtz = pytz.timezone(settings.TIME_ZONE)
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Transfer.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 0)
        self.assertEqual(TransferBevChunk.objects.count(), 0)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2014',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1200,
             'bev_type': 1})
        self.client.post('/brew/create/',
            {'create_date': '01/01/2014',
             'product_type': 2,
             'yeast': 222,
             'starting_density': 1.050,
             'dest_tank': 2,
             'dest_volume': 1000,
             'bev_type': 2})
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 2)
        bc = BevChunk.objects.get(cur_tank__tank__id=1)
        self.assertEqual(bc.volume, 1200)
        bc = BevChunk.objects.get(cur_tank__tank__id=2)
        self.assertEqual(bc.volume, 1000)
        self.assertEqual(BevTank.objects.count(), 2)
        self.assertEqual(TransferBevChunk.objects.count(), 0)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(PackageTransaction.objects.count(), 0)

        resp = self.client.post('/transfer/create/',
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=1).id,
             'dest_volume': 500,
             'dest_tank': 3,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 3)
        bc = BevChunk.objects.get(cur_tank__tank__id=3)
        self.assertEqual(bc.volume, 500)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 1)
        tbc = TransferBevChunk.objects.get(bev_chunk__cur_tank__tank__id=1)
        self.assertEqual(tbc.volume, 500)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(PackageTransaction.objects.count(), 0)

        resp = self.client.post('/transfer/create/',
            {'transfer_date': '01/01/2014',
             'cur_tank': BevTank.objects.get(tank__id=2).id,
             'dest_volume': 900,
             'dest_tank': 3,
             'product_type': 1,
             'blend_with': BevTank.objects.get(tank__id=3).id,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 0)
        self.assertEqual(PackageBevChunk.objects.count(), 0)
        self.assertEqual(BevChunk.objects.count(), 4)
        bc = BevChunk.objects.get(src_tank__tank__id=2)
        self.assertEqual(bc.volume, 900)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        tbc = TransferBevChunk.objects.get(bev_chunk__cur_tank__tank__id=2)
        self.assertEqual(tbc.volume, 900)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=2)
        self.assertEqual(wbc.volume, 100)
        self.assertEqual(PackageTransaction.objects.count(), 0)

        resp = self.client.post('/package/create/',
            {'create_date': '01/01/2014',
             'bev_tank': BevTank.objects.get(tank__id=3).id,
             'item_count': 35,
             'package_type': 7,
             'empty': True,
             'notes': 'create',
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 700)
        self.assertEqual(PackageBevChunk.objects.count(), 2)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(pbc.volume, 250)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(pbc.volume, 450)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 3)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(wbc.volume, 250)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(wbc.volume, 450)
        self.assertEqual(PackageTransaction.objects.count(), 1)
        pt = PackageTransaction.objects.get()
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, 700)
        self.assertEqual(pt.tank, 'FV3')
        self.assertEqual(pt.name, 'LG1+ST2')
        self.assertEqual(pt.notes, 'create')
        self.assertEqual(pt.package_type, '20L Bag')
        self.assertEqual(pt.transaction_type, 'Create')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 1))

        package = Package.objects.get()
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url,
            {'create_date': '01/01/2014',
             'bev_tank': BevTank.objects.get(tank__id=3).id,
             'item_count': 35,  # changed
             'package_type': 6,
             'empty': True,
             'notes': 'update1',
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 1050)
        self.assertEqual(PackageBevChunk.objects.count(), 2)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(pbc.volume, 375)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(pbc.volume, 675)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 3)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(wbc.volume, 125)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(wbc.volume, 225)
        self.assertEqual(PackageTransaction.objects.count(), 2)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, 350)
        self.assertEqual(pt.tank, 'FV3')
        self.assertEqual(pt.name, 'LG1+ST2')
        self.assertEqual(pt.notes, 'update1')
        self.assertEqual(pt.package_type, '30L Keg')
        self.assertEqual(pt.transaction_type, 'Update')

        package = Package.objects.get()
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url,
            {'create_date': '01/01/2014',
             'bev_tank': BevTank.objects.get(tank__id=3).id,
             'item_count': 56,  # changed
             'package_type': 7,  # changed
             'empty': False,  # changed
             'notes': 'update2',  # changed
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 1120)
        self.assertEqual(PackageBevChunk.objects.count(), 2)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(pbc.volume, 400)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(pbc.volume, 720)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(PackageTransaction.objects.count(), 3)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, 70)
        self.assertEqual(pt.tank, 'FV3')
        self.assertEqual(pt.name, 'LG1+ST2')
        self.assertEqual(pt.notes, 'update2')
        self.assertEqual(pt.package_type, '20L Bag')
        self.assertEqual(pt.transaction_type, 'Update')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 1))

        package = Package.objects.get()
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url,
            {'create_date': '01/01/2014',
             'bev_tank': BevTank.objects.get(tank__id=3).id,
             'item_count': 7,  # changed
             'package_type': 5,  # changed
             'empty': False,
             'notes': 'update3',
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 350)
        self.assertEqual(PackageBevChunk.objects.count(), 2)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(pbc.volume, 125)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(pbc.volume, 225)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(PackageTransaction.objects.count(), 4)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, -770)
        self.assertEqual(pt.tank, 'FV3')
        self.assertEqual(pt.name, 'LG1+ST2')
        self.assertEqual(pt.notes, 'update3')
        self.assertEqual(pt.package_type, '50L Keg')
        self.assertEqual(pt.transaction_type, 'Update')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 1))

        package = Package.objects.get()
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url,
            {'create_date': '02/01/2014',  # changed
             'bev_tank': BevTank.objects.get(tank__id=3).id,
             'item_count': 14,  # changed
             'package_type': 5,  # changed
             'empty': True,  # changed
             'notes': 'update4'
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 700)
        self.assertEqual(PackageBevChunk.objects.count(), 2)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(pbc.volume, 250)
        pbc = PackageBevChunk.objects.get(
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(pbc.volume, 450)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 3)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(wbc.volume, 250)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(wbc.volume, 450)
        self.assertEqual(PackageTransaction.objects.count(), 5)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(
            tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, 350)
        self.assertEqual(pt.tank, 'FV3')
        self.assertEqual(pt.name, 'LG1+ST2')
        self.assertEqual(pt.notes, 'update4')
        self.assertEqual(pt.package_type, '50L Keg')
        self.assertEqual(pt.transaction_type, 'Update')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 2))

        url = '/package/delete/' + str(p.id) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(BevChunk.objects.count(), 4)
        bc = BevChunk.objects.filter(src_tank__tank__id=3,
            parent__src_tank__tank__id=1)
        self.assertEqual(bc.count(), 0)
        bc = BevChunk.objects.filter(src_tank__tank__id=3,
            parent__src_tank__tank__id=2)
        self.assertEqual(bc.count(), 0)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        tbc = TransferBevChunk.objects.filter(bev_chunk__src_tank__tank__id=1)
        self.assertEqual(tbc.count(), 0)
        tbc = TransferBevChunk.objects.filter(bev_chunk__src_tank__tank__id=2)
        self.assertEqual(tbc.count(), 0)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        wbc = WasteBevChunk.objects.filter(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=1)
        self.assertEqual(wbc.count(), 0)
        wbc = WasteBevChunk.objects.filter(bev_chunk__cur_tank__tank__id=3,
            bev_chunk__parent__cur_tank__tank__id=2)
        self.assertEqual(wbc.count(), 0)
        self.assertEqual(PackageTransaction.objects.count(), 6)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, -700)
        self.assertEqual(pt.tank, 'FV3')
        self.assertEqual(pt.name, 'LG1+ST2')
        self.assertEqual(pt.notes, 'update4')
        self.assertEqual(pt.package_type, '50L Keg')
        self.assertEqual(pt.transaction_type, 'Delete')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 2))

        # Now test single bevchunk packages
        resp = self.client.post('/package/create/',
            {'create_date': '01/01/2014',
             'bev_tank': BevTank.objects.get(tank__id=1).id,
             'item_count': 20,
             'package_type': 7,
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 400)
        self.assertEqual(PackageBevChunk.objects.count(), 1)
        pbc = PackageBevChunk.objects.get()
        self.assertEqual(pbc.volume, 400)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 2)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=1,
            bev_chunk__parent__cur_tank__tank__id=None)
        self.assertEqual(wbc.volume, 300)
        self.assertEqual(PackageTransaction.objects.count(), 7)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, 400)
        self.assertEqual(pt.tank, 'FV1')
        self.assertEqual(pt.name, 'LG1')
        self.assertEqual(pt.notes, '')
        self.assertEqual(pt.package_type, '20L Bag')
        self.assertEqual(pt.transaction_type, 'Create')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 1))

        package = Package.objects.get()
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url,
            {'create_date': '01/01/2014',
             'bev_tank': BevTank.objects.get(tank__id=3).id,
             'item_count': 10,  # changed
             'package_type': 5,  # changed
             'empty': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 500)
        self.assertEqual(PackageBevChunk.objects.count(), 1)
        pbc = PackageBevChunk.objects.get()
        self.assertEqual(pbc.volume, 500)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 2)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=1,
            bev_chunk__parent__cur_tank__tank__id=None)
        self.assertEqual(wbc.volume, 200)
        self.assertEqual(PackageTransaction.objects.count(), 8)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, 100)
        self.assertEqual(pt.tank, 'FV1')
        self.assertEqual(pt.name, 'LG1')
        self.assertEqual(pt.notes, '')
        self.assertEqual(pt.package_type, '50L Keg')
        self.assertEqual(pt.transaction_type, 'Update')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 1))

        package = Package.objects.get()
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url,
            {'create_date': '01/01/2014',
             'bev_tank': BevTank.objects.get(tank__id=3).id,
             'item_count': 20,  # changed
             'package_type': 6,
             'empty': False,  # changed
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 600)
        self.assertEqual(PackageBevChunk.objects.count(), 1)
        pbc = PackageBevChunk.objects.get()
        self.assertEqual(pbc.volume, 600)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(PackageTransaction.objects.count(), 9)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, 100)
        self.assertEqual(pt.tank, 'FV1')
        self.assertEqual(pt.name, 'LG1')
        self.assertEqual(pt.notes, '')
        self.assertEqual(pt.package_type, '30L Keg')
        self.assertEqual(pt.transaction_type, 'Update')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 1))

        package = Package.objects.get()
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url,
            {'create_date': '01/01/2014',
             'bev_tank': BevTank.objects.get(tank__id=1).id,
             'item_count': 11,  # changed
             'package_type': 5,  # changed
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 550)
        self.assertEqual(PackageBevChunk.objects.count(), 1)
        pbc = PackageBevChunk.objects.get()
        self.assertEqual(pbc.volume, 550)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(PackageTransaction.objects.count(), 10)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, -50)
        self.assertEqual(pt.tank, 'FV1')
        self.assertEqual(pt.name, 'LG1')
        self.assertEqual(pt.notes, '')
        self.assertEqual(pt.package_type, '50L Keg')
        self.assertEqual(pt.transaction_type, 'Update')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 1))

        package = Package.objects.get()
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url,
            {'create_date': '02/01/2014',  # changed
             'bev_tank': BevTank.objects.get(tank__id=3).id,
             'item_count': 14,  # changed
             'package_type': 5,  # changed
             'empty': True,  # changed
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(Transfer.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        p = Package.objects.get()
        self.assertEqual(p.volume, 700)
        self.assertEqual(PackageBevChunk.objects.count(), 1)
        pbc = PackageBevChunk.objects.get()
        self.assertEqual(pbc.volume, 700)
        self.assertEqual(BevChunk.objects.count(), 4)
        self.assertEqual(BevTank.objects.count(), 3)
        self.assertEqual(TransferBevChunk.objects.count(), 2)
        self.assertEqual(WasteBevChunk.objects.count(), 2)
        wbc = WasteBevChunk.objects.get(bev_chunk__cur_tank__tank__id=1,
            bev_chunk__parent__cur_tank__tank__id=None)
        self.assertEqual(wbc.volume, 0)
        self.assertEqual(PackageTransaction.objects.count(), 11)
        pt = PackageTransaction.objects.latest('id')
        self.assertEqual(pt.package_id, p.id)
        self.assertTrue(pt.datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(pt.user_id, 1)
        self.assertEqual(pt.user_name, 'nathan')
        self.assertEqual(pt.volume, 150)
        self.assertEqual(pt.tank, 'FV1')
        self.assertEqual(pt.name, 'LG1')
        self.assertEqual(pt.notes, '')
        self.assertEqual(pt.package_type, '50L Keg')
        self.assertEqual(pt.transaction_type, 'Update')
        self.assertEqual(pt.billed, None)
        self.assertEqual(pt.package_date, datetime.date(2014, 1, 2))

        self.client.logout()


class PackageWithEventViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        localtz = pytz.timezone(settings.TIME_ZONE)
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        event = Event(title='test',
                      start=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      end=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      event_type=EventType.objects.get(name='Package'),
                      scheduled=True)
        event.save()
        self.client.logout()

    def test_loading(self):
        url = '/package/create/' + str(Event.objects.all()[0].id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class PackageDetailViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        localtz = pytz.timezone(settings.TIME_ZONE)
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        event = Event(title='test',
                      start=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      end=datetime.datetime(2013, 1, 2, 0, 0, 0, 0, localtz),
                      event_type=EventType.objects.get(name='Package'),
                      scheduled=True)
        event.save()
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.client.logout()

    def test_loading(self):
        url = '/package/' + str(Package.objects.all()[0].id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class PackageEditViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_edit_non_empty_to_empty(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        package = Package.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(PackageBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2013-01-04',
            'bev_tank': BevTank.objects.all()[0].id,
            'empty': True,
            'package_type': PackageType.objects.get(name='Tank').id,
            'item_count': 300.0})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(PackageBevChunk.objects.count(), 1)
        self.assertEqual(WasteBevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 3)
        self.assertEqual(Event.objects.count(), 2)
        package = Package.objects.all()[0]
        event = Event.objects.get(event_type__name='Package')
        measurement = Measurement.objects.get(measurement_type__name="Volume",
            value=0.0)
        self.assertEqual(package.package_type,
            PackageType.objects.get(name='Tank'))
        self.assertEqual(package.create_date, datetime.date(2013, 1, 4))
        self.assertEqual(package.volume, 300)
        self.assertEqual(package.bev_tank.empty_date,
            datetime.date(2013, 1, 4))
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 3, 11, 0, tzinfo=pytz.utc))
        self.assertEqual(measurement.measurement_date,
            datetime.date(2013, 1, 4))

    def test_edit_empty_to_empty(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': True,
             })
        package = Package.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 3)
        self.assertEqual(Event.objects.count(), 2)
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2013-01-04',
            'bev_tank': BevTank.objects.all()[0].id,
            'empty': True,
            'package_type': PackageType.objects.get(name='Tank').id,
            'item_count': 300.0})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 3)
        self.assertEqual(Event.objects.count(), 2)
        package = Package.objects.all()[0]
        event = Event.objects.get(event_type__name='Package')
        self.assertEqual(package.package_type,
            PackageType.objects.get(name='Tank'))
        self.assertEqual(package.create_date, datetime.date(2013, 1, 4))
        self.assertEqual(package.volume, 300)
        self.assertEqual(package.bev_tank.empty_date,
            datetime.date(2013, 1, 4))
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 3, 11, 0, tzinfo=pytz.utc))
        m = Measurement.objects.get(value=0.0, measurement_type__name='Volume')
        self.assertEqual(m.measurement_date, datetime.date(2013, 1, 4))

    def test_edit_empty_to_non_empty(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': True,
             })
        package = Package.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 3)
        self.assertEqual(Event.objects.count(), 2)
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2013-01-04',
            'bev_tank': BevTank.objects.all()[0].id,
            'empty': False,
            'package_type': PackageType.objects.get(name='Tank').id,
            'item_count': 300.0})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        package = Package.objects.all()[0]
        event = Event.objects.get(event_type__name='Package')
        self.assertEqual(package.package_type,
            PackageType.objects.get(name='Tank'))
        self.assertEqual(package.create_date, datetime.date(2013, 1, 4))
        self.assertEqual(package.volume, 300)
        self.assertEqual(package.bev_tank.empty_date, None)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 3, 11, 0, tzinfo=pytz.utc))
        m = Measurement.objects.filter(value=0.0,
            measurement_type__name='Volume')
        self.assertEqual(m.count(), 0)

    def test_edit_non_empty_to_non_empty(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        package = Package.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2013-01-04',
            'bev_tank': BevTank.objects.all()[0].id,
            'empty': False,
            'package_type': PackageType.objects.get(name='Tank').id,
            'item_count': 300.0})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        package = Package.objects.all()[0]
        event = Event.objects.get(event_type__name='Package')
        self.assertEqual(package.package_type,
            PackageType.objects.get(name='Tank'))
        self.assertEqual(package.create_date, datetime.date(2013, 1, 4))
        self.assertEqual(package.volume, 300)
        self.assertEqual(package.bev_tank.empty_date, None)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 3, 11, 0, tzinfo=pytz.utc))
        m = Measurement.objects.filter(value=0.0,
            measurement_type__name='Volume')
        self.assertEqual(m.count(), 0)

    def test_edit_non_empty_to_empty_same_date(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        package = Package.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2013-01-03',
            'bev_tank': BevTank.objects.all()[0].id,
            'empty': True,
            'package_type': PackageType.objects.get(name='Tank').id,
            'item_count': 300.0})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 3)
        self.assertEqual(Event.objects.count(), 2)
        package = Package.objects.all()[0]
        event = Event.objects.get(event_type__name='Package')
        measurement = Measurement.objects.get(measurement_type__name="Volume",
            value=0.0)
        self.assertEqual(package.package_type,
            PackageType.objects.get(name='Tank'))
        self.assertEqual(package.create_date, datetime.date(2013, 1, 3))
        self.assertEqual(package.volume, 300)
        self.assertEqual(package.bev_tank.empty_date,
            datetime.date(2013, 1, 3))
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        self.assertEqual(measurement.measurement_date,
            datetime.date(2013, 1, 3))

    def test_edit_empty_to_empty_same_date(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': True,
             })
        package = Package.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 3)
        self.assertEqual(Event.objects.count(), 2)
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2013-01-03',
            'bev_tank': BevTank.objects.all()[0].id,
            'empty': True,
            'package_type': PackageType.objects.get(name='Tank').id,
            'item_count': 300.0})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 3)
        self.assertEqual(Event.objects.count(), 2)
        package = Package.objects.all()[0]
        event = Event.objects.get(event_type__name='Package')
        self.assertEqual(package.package_type,
            PackageType.objects.get(name='Tank'))
        self.assertEqual(package.create_date, datetime.date(2013, 1, 3))
        self.assertEqual(package.volume, 300)
        self.assertEqual(package.bev_tank.empty_date,
            datetime.date(2013, 1, 3))
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        m = Measurement.objects.get(value=0.0, measurement_type__name='Volume')
        self.assertEqual(m.measurement_date, datetime.date(2013, 1, 3))

    def test_edit_empty_to_non_empty_same_date(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': True,
             })
        package = Package.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 3)
        self.assertEqual(Event.objects.count(), 2)
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2013-01-03',
            'bev_tank': BevTank.objects.all()[0].id,
            'empty': False,
            'package_type': PackageType.objects.get(name='Tank').id,
            'item_count': 300.0})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        package = Package.objects.all()[0]
        event = Event.objects.get(event_type__name='Package')
        self.assertEqual(package.package_type,
            PackageType.objects.get(name='Tank'))
        self.assertEqual(package.create_date, datetime.date(2013, 1, 3))
        self.assertEqual(package.volume, 300)
        self.assertEqual(package.bev_tank.empty_date, None)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        m = Measurement.objects.filter(value=0.0,
            measurement_type__name='Volume')
        self.assertEqual(m.count(), 0)

    def test_edit_non_empty_to_non_empty_same_date(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        package = Package.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2013-01-03',
            'bev_tank': BevTank.objects.all()[0].id,
            'empty': False,
            'package_type': PackageType.objects.get(name='Tank').id,
            'item_count': 300.0})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        package = Package.objects.all()[0]
        event = Event.objects.get(event_type__name='Package')
        self.assertEqual(package.package_type,
            PackageType.objects.get(name='Tank'))
        self.assertEqual(package.create_date, datetime.date(2013, 1, 3))
        self.assertEqual(package.volume, 300)
        self.assertEqual(package.bev_tank.empty_date, None)
        self.assertEqual(event.start,
            datetime.datetime(2013, 1, 2, 11, 0, tzinfo=pytz.utc))
        m = Measurement.objects.filter(value=0.0,
            measurement_type__name='Volume')
        self.assertEqual(m.count(), 0)

    def test_edit_with_submission(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        resp = self.client.post('/submission/create/2013-01-01/2013-01-31/')
        pk = Submission.objects.all()[0].id
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/submission/' +
            str(pk) + '/')
        pk = Package.objects.all()[0].id
        url = '/package/edit/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

    def test_edit_with_early_date(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        package = Package.objects.all()[0]
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        url = '/package/edit/' + str(package.id) + '/'
        resp = self.client.post(url, {
            'create_date': '2012-12-31',
            'bev_tank': BevTank.objects.all()[0].id,
            'empty': True,
            'package_type': PackageType.objects.get(name='Tank').id,
            'item_count': 300.0})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(package.create_date, datetime.date(2013, 01, 03))


class PackageDeleteViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_delete(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        pk = Package.objects.all()[0].id
        url = '/package/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp['Location'], SERVER + '/package/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Package.objects.count(), 0)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_with_checkout(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 2,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/checkout/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        pk = Package.objects.all()[0].id
        url = '/package/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)

    def test_delete_with_checkout_package(self):
        """
        package twice from the same tank. Delete checked out package
        Must not delete anything
        """
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.earliest('id').id,
            'item_count': 2,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/checkout/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 2)
        pk = Package.objects.earliest('id').id
        url = '/package/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 2)

    def test_delete_with_checkout_package_2(self):
        """
        package twice from the same tank. Delete non-checked out package
        Must delete only that package
        """
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.earliest('id').id,
            'item_count': 2,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/checkout/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 2)
        pk = Package.objects.latest('id').id
        url = '/package/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)

    def test_delete_with_checkout_blend(self):
        """
        Create blend, package, checkout, then try and delete package
        Must not delete anything
        """
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 2,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/checkout/list/')
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevChunk.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)
        pk = Package.objects.all()[0].id
        url = '/package/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevChunk.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 2)
        self.assertEqual(Package.objects.count(), 1)

    def test_delete_with_checkout_blend_2(self):
        """
        Package, checkout, blend then try and delete package
        Must not delete anything
        """
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/', {
            'create_date': '03/01/2013',
            'bev_tank': BevTank.objects.all()[0].id,
            'package_type': 5,
            'item_count': 4,
            'empty': False,
            })
        resp = self.client.post('/checkout/create/', {
            'create_date': '04/01/2013',
            'package': Package.objects.all()[0].id,
            'item_count': 2,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/checkout/list/')
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(BevChunk.objects.count(), 1)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)
        pk = Package.objects.all()[0].id
        resp = self.client.post('/brew/create/', {
            'create_date': '03/01/2013',
            'product_type': 1,
            'yeast': 222,
            'starting_density': 1.050,
            'dest_tank': 1,
            'dest_volume': 1000,
            'bev_type': 1,
            'blend_with': 1
            })
        self.assertEqual(resp['Location'], SERVER + '/brew/list/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        url = '/package/delete/' + str(pk) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Brew.objects.count(), 2)
        self.assertEqual(BevChunk.objects.count(), 2)
        self.assertEqual(BevTank.objects.count(), 1)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Submission.objects.count(), 0)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(Package.objects.count(), 1)


class PackageScheduleViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/package/schedule/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)
        load_200(self, url)


class PackageScheduleWithDateViewTest(TestCase):
    fixtures = ['test_data.json']
    url = '/package/schedule/2013-1-1/'

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        load_unauthenticated_redirect(self, self.url)
        load_unauthenticated_redirect_location(self, self.url)
        load_200(self, self.url)

    def test_post_blank(self):
        log_in(self)
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        event_count = Event.objects.count()
        resp = self.client.post(self.url, {
            'date': '01/01/2013',
            'bev_tank': BevTank.objects.all()[0].id
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Event.objects.count(), event_count + 1)


class CheckOutListViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/checkout/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class CheckOutViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/checkout/create/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

    def test_checkout(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Package.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 0)
        self.assertEqual(CheckOutBevChunk.objects.count(), 0)
        self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        resp = self.client.post('/checkout/create/',
            {'create_date': '04/01/2013',
             'package': Package.objects.all()[0].id,
             'item_count': 4,
             'exempt': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(CheckOut.objects.filter(exempt=True).count(), 0)
        self.assertEqual(CheckOut.objects.filter(exempt=False).count(), 1)

    def test_checkout_exempt(self):
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Package.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 0)
        self.assertEqual(CheckOutBevChunk.objects.count(), 0)
        self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        resp = self.client.post('/checkout/create/',
            {'create_date': '04/01/2013',
             'package': Package.objects.all()[0].id,
             'item_count': 4,
             'exempt': True,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(CheckOut.objects.filter(exempt=True).count(), 1)
        self.assertEqual(CheckOut.objects.filter(exempt=False).count(), 0)


class CheckOutEditViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_edit(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        resp = self.client.post('/checkout/create/',
            {'create_date': '04/01/2013',
             'package': Package.objects.all()[0].id,
             'item_count': 4,
             'exempt': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(CheckOut.objects.filter(exempt=True).count(), 0)
        self.assertEqual(CheckOut.objects.filter(exempt=False).count(), 1)
        coid = CheckOut.objects.all()[0].pk
        url = '/checkout/edit/' + str(coid) + '/'
        resp = self.client.post(url,
            {'create_date': '05/01/2013',
             'package': Package.objects.all()[0].id,
             'item_count': 2,
             'exempt': True,
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/checkout/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(CheckOut.objects.filter(exempt=True).count(), 1)
        self.assertEqual(CheckOut.objects.filter(exempt=False).count(), 0)
        self.assertEqual(CheckOut.objects.all()[0].create_date,
            datetime.date(2013, 01, 05))
        self.assertEqual(CheckOut.objects.all()[0].volume, 100)

    def test_edit_submission(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        resp = self.client.post('/checkout/create/',
            {'create_date': '04/01/2013',
             'package': Package.objects.all()[0].id,
             'item_count': 4,
             'exempt': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Submission.objects.count(), 0)
        resp = self.client.post('/submission/create/2013-01-01/2013-01-31/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Submission.objects.count(), 1)
        co = CheckOut.objects.all()[0]
        s = Submission.objects.all()[0]
        self.assertEqual(co.submission, s)
        url = '/checkout/edit/' + str(co.id) + '/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("can not be modified", resp.content)


class CheckOutDeleteViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_delete(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        resp = self.client.post('/checkout/create/',
            {'create_date': '04/01/2013',
             'package': Package.objects.all()[0].id,
             'item_count': 4,
             'exempt': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 1)
        self.assertEqual(CheckOutBevChunk.objects.count(), 1)
        self.assertEqual(CheckOut.objects.filter(exempt=True).count(), 0)
        self.assertEqual(CheckOut.objects.filter(exempt=False).count(), 1)
        coid = CheckOut.objects.all()[0].pk
        url = '/checkout/delete/' + str(coid) + '/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/checkout/list/')
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 0)
        self.assertEqual(CheckOutBevChunk.objects.count(), 0)

    def test_delete_submission(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        resp = self.client.post('/checkout/create/',
            {'create_date': '04/01/2013',
             'package': Package.objects.all()[0].id,
             'item_count': 4,
             'exempt': False,
             })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Submission.objects.count(), 0)
        resp = self.client.post('/submission/create/2013-01-01/2013-01-31/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Submission.objects.count(), 1)
        co = CheckOut.objects.all()[0]
        s = Submission.objects.all()[0]
        self.assertEqual(co.submission, s)
        url = '/checkout/delete/' + str(co.id) + '/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("can not be deleted", resp.content)


class MeasurementListViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/measurement/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class MeasurementViewTest(TestCase):
    fixtures = ['test_data.json']

    def test_add_density(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        resp2 = self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 2,
             'value': 1.0312})
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), 4)
        am = Measurement.objects.filter(
            measurement_type=3).order_by('-measurement_date')
        self.assertEqual(round(am[0].value, 6), 1.534400)

    def test_add_set_temperature(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        resp2 = self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 4,
             'value': 16.1})
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), 3)

    def test_add_actual_temperature(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        resp2 = self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 5,
             'value': 610})
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), 3)

    def test_add_alcohol(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        resp2 = self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 3,
             'value': 2.3})
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), 3)

    def test_add_volume(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        resp2 = self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 1,
             'value': 1000})
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), 3)

    def test_add_o2(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        resp2 = self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 7,
             'value': 0.182})
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), 3)

    def test_add_co2(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        resp2 = self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 6,
             'value': 2.42})
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), 3)

    def test_add_pressure(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        resp2 = self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 8,
             'value': 102})
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), 3)


class MeasurementDetailViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def test_loading(self):
        url = '/measurement/' + str(Measurement.objects.all()[0].id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class MeasurementEditViewTest(TestCase):
    fixtures = ['test_data.json']

    def test_edit_density(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        bt = BevTank.objects.all()[0].id
        self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 2,
             'value': 1.0312})
        m_count = Measurement.objects.count()
        m = Measurement.objects.get(value=1.0312).pk
        resp = self.client.post('/measurement/edit/{0}/'.format(m),
            {'value': 1.040})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), m_count)
        self.assertEqual(Measurement.objects.get(pk=m).value, 1.040)
        self.assertEqual(round(Measurement.objects.get(parent__pk=m).value, 6),
            round((1.0424 - 1.040) * 137, 6))

    def test_edit_density_transfer(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        bt = BevTank.objects.all()[0].id

        self.client.post('/measurement/',
            {'measurement_date': '01/01/2013',
             'bev_tank': bt,
             'measurement_type': 2,
             'value': 1.034})
        m0 = Measurement.objects.get(value=1.034, bev_tank=bt).pk

        self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 2,
             'value': 1.0312})

        resp = self.client.post('/transfer/create/',
            {'transfer_date': '03/01/2013',
             'cur_tank': bt,
             'dest_volume': 950,
             'dest_tank': 2,
             'product_type': 1,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)

        self.client.post('/measurement/',
            {'measurement_date': '05/01/2013',
             'bev_tank': bt,
             'measurement_type': 2,
             'value': 1.014})
        m2 = Measurement.objects.get(value=1.014, bev_tank=bt).pk

        m_count = Measurement.objects.count()
        m = Measurement.objects.get(value=1.0312, bev_tank=bt).pk
        bt2 = BevTank.objects.get(tank__pk=2)
        self.assertEqual(round(Measurement.objects.get(
            measurement_type__name='Alcohol', bev_tank=bt2).value, 6),
            round((1.0424 - 1.0312) * 137, 6))
        self.assertEqual(Measurement.objects.get(
            measurement_type__name='Density', bev_tank=bt2).value, 1.0312)

        resp = self.client.post('/measurement/edit/{0}/'.format(m),
            {'value': 1.040})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Measurement.objects.count(), m_count)
        self.assertEqual(Measurement.objects.get(pk=m).value, 1.0312)
        self.assertEqual(round(Measurement.objects.get(parent__pk=m,
            bev_tank=bt).value, 6),
            round((1.0424 - 1.0312) * 137, 6))
        self.assertEqual(round(Measurement.objects.get(
            measurement_type__name='Alcohol', bev_tank=bt2).value, 6),
            round((1.0424 - 1.0312) * 137, 6))
        self.assertEqual(Measurement.objects.get(
            measurement_type__name='Density', bev_tank=bt2).value, 1.0312)

        resp = self.client.post('/measurement/edit/{0}/'.format(m0),
            {'value': 1.036})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Measurement.objects.get(pk=m0).value, 1.034)

        resp = self.client.post('/measurement/edit/{0}/'.format(m2),
            {'value': 1.013})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), m_count)
        self.assertEqual(Measurement.objects.get(pk=m2).value, 1.013)
        self.assertEqual(
            round(Measurement.objects.get(parent__pk=m2).value, 6),
            round((1.0424 - 1.013) * 137, 6))

    def test_edit_density_package(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        bt = BevTank.objects.all()[0].id

        self.client.post('/measurement/',
            {'measurement_date': '01/01/2013',
             'bev_tank': bt,
             'measurement_type': 2,
             'value': 1.034})
        m0 = Measurement.objects.get(value=1.034, bev_tank=bt).pk

        self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 2,
             'value': 1.0312})

        resp = self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': bt,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        self.assertEqual(resp.status_code, 302)

        self.client.post('/measurement/',
            {'measurement_date': '05/01/2013',
             'bev_tank': bt,
             'measurement_type': 2,
             'value': 1.014})
        m2 = Measurement.objects.get(value=1.014, bev_tank=bt).pk

        m_count = Measurement.objects.count()
        m = Measurement.objects.get(value=1.0312, bev_tank=bt).pk

        resp = self.client.post('/measurement/edit/{0}/'.format(m),
            {'value': 1.040})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Measurement.objects.count(), m_count)
        self.assertEqual(Measurement.objects.get(pk=m).value, 1.0312)
        self.assertEqual(round(Measurement.objects.get(parent__pk=m,
            bev_tank=bt).value, 6),
            round((1.0424 - 1.0312) * 137, 6))

        resp = self.client.post('/measurement/edit/{0}/'.format(m0),
            {'value': 1.036})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Measurement.objects.get(pk=m0).value, 1.034)

        resp = self.client.post('/measurement/edit/{0}/'.format(m2),
            {'value': 1.013})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), m_count)
        self.assertEqual(Measurement.objects.get(pk=m2).value, 1.013)
        self.assertEqual(
            round(Measurement.objects.get(parent__pk=m2).value, 6),
            round((1.0424 - 1.013) * 137, 6))

    def test_edit_alcohol(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 3,
             'value': 2.3})
        m_count = Measurement.objects.count()
        m = Measurement.objects.get(value=2.3).pk
        resp = self.client.post('/measurement/edit/{0}/'.format(m),
            {'value': 2.6})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), m_count)
        self.assertEqual(Measurement.objects.get(pk=m).value, 2.6)

    def test_edit_volume(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.0424,
             'dest_tank': 1,
             'dest_volume': 10,
             'bev_type': 1})
        self.assertEqual(Measurement.objects.count(), 2)
        bt = BevTank.objects.all()[0].id
        self.client.post('/measurement/',
            {'measurement_date': '02/01/2013',
             'bev_tank': bt,
             'measurement_type': 1,
             'value': 1000})
        m_count = Measurement.objects.count()
        m = Measurement.objects.get(value=1000).pk
        resp = self.client.post('/measurement/edit/{0}/'.format(m),
            {'value': 900})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/measurement/list/')
        self.assertEqual(Measurement.objects.count(), m_count)
        self.assertEqual(Measurement.objects.get(pk=m).value, 900)


class StatusEditViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/bev_tank/status/' + str(BevTank.objects.all()[0].id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class BevTankDetailViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.assertEqual(Process.objects.count(), 0)
        self.assertEqual(Brew.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)
        self.client.post('/brew/create/',
            {'create_date': '01/01/2013',
             'product_type': 1,
             'yeast': 222,
             'starting_density': 1.042,
             'dest_tank': 1,
             'dest_volume': 1000,
             'bev_type': 1})
        self.client.logout()

    def test_loading(self):
        url = '/bev_tank/' + str(BevTank.objects.all()[0].id) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class BevTankListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/tank_list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class SettingsViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/settings/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class SubmissionListViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/submission/list/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class SubmissionCreateViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/submission/create/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class SubmissionCompleteViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        url = '/submission/create/2013-01-01/2013-01-31/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)


class SubmissionSubmitViewTest(TestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    def setUp(self):
        self.client = Client()

    def test_loading(self):
        self.client.login(username='nathan', password='13ceecos')
        resp = self.client.post('/submission/create/2013-01-01/2013-01-31/')
        self.assertEqual(Submission.objects.count(), 1)
        sid = Submission.objects.all()[0].id
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], SERVER + '/submission/'
                         + str(sid) + '/')

    def test_exempt(self):
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/package/create/',
            {'create_date': '03/01/2013',
             'bev_tank': BevTank.objects.all()[0].id,
             'package_type': 5,
             'item_count': 4,
             'empty': False,
             })
        self.client.post('/checkout/create/',
            {'create_date': '04/01/2013',
             'package': Package.objects.all()[0].id,
             'item_count': 2,
             'exempt': False,
             })
        self.client.post('/checkout/create/',
            {'create_date': '05/01/2013',
             'package': Package.objects.all()[0].id,
             'item_count': 1,
             'exempt': True,
             })
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(Brew.objects.count(), 1)
        self.assertEqual(CheckOut.objects.count(), 2)
        self.assertEqual(CheckOutBevChunk.objects.count(), 2)
        self.assertEqual(CheckOut.objects.filter(exempt=True).count(), 1)
        self.assertEqual(CheckOut.objects.filter(exempt=False).count(), 1)
        resp = self.client.post('/submission/create/2013-01-01/2013-01-31/')
        self.assertEqual(Submission.objects.count(), 1)
        sid = Submission.objects.all()[0].id
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp['Location'], SERVER + '/submission/' + str(sid) + '/')
        resp = self.client.get(
            SERVER + '/submission/' + str(sid) + '/')
        self.assertIn('<td class="total">100.0', resp.content)


class SubmissionDetailViewTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='nathan', password='13ceecos')
        self.client.post('/submission/create/2013-01-01/2013-01-31/')
        self.client.logout()

    def test_loading(self):
        sid = Submission.objects.all()[0].id
        url = '/submission/' + str(sid) + '/'
        load_unauthenticated_redirect(self, url)
        load_unauthenticated_redirect_location(self, url)
        load_200(self, url)

from orders.tests import *


