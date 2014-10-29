# coding: utf-8
import writer.views as wrv
from django.http import HttpResponseRedirect, HttpResponse
import main.models as mm
import main.forms as mf
import main.tables as mt
import submission.models as sm
import orders.models as om
import orders.forms as of
import orders.tables as ot
from django.shortcuts import render_to_response, render
from django.template import RequestContext
#from magnitude import *
from django.core import serializers
from django.db.models import Max, Q, ProtectedError, Sum
from django_tables2 import RequestConfig
from decimal import Decimal
from django.conf import settings
from django.forms.formsets import formset_factory
from datetime import date, time, datetime, timedelta
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from time import mktime
from django.contrib.sites.models import get_current_site
import pytz
import inspect
from django.db.models.loading import get_model
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.generic import (
    DetailView, CreateView, UpdateView, DeleteView, ListView)
from django_tables2.views import SingleTableView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import User, Group
from django.utils.safestring import mark_safe
from django.forms.models import modelform_factory
import logging


logger = logging.getLogger(__name__)


def class_view_decorator(function_decorator):
    """Convert a function based decorator into a class based decorator usable
    on class based Views.

    Can't subclass the `View` as it breaks inheritance (super in particular),
    so we monkey-patch instead.
    """

    def simple_decorator(View):
        View.dispatch = method_decorator(function_decorator)(View.dispatch)
        return View

    return simple_decorator


def home(request):
    if request.user.is_authenticated():
        settings = mm.Setting.objects.get(site=get_current_site(request))
        view = settings.calendar_view.value
        return render(
            request, 'home.html', {
                'view': view, 'nav1': 'home',
                'nav2': inspect.stack()[0][3]})
    else:
        return login(request)


@login_required
def user_list(request):
    create = reverse(user_create)
    create_text = 'Create New User'
    list_class = "User"
    list_app = "main"
    table = mt.UserTable(User.objects.filter(is_staff=False))
    table.exclude = ('id', 'password', 'is_staff', 'is_superuser',
                     'date_joined')
    RequestConfig(request, paginate=False).configure(table)
    return render(request, 'record_list.html', {
        'table': table, 'nav1': 'admin',
        'nav2': inspect.stack()[0][3], 'create': create,
        'create_text': create_text, 'list_class': list_class,
        'list_app': list_app,
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def user_detail(request, pk):
    if pk:
        instance = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = mf.UserProfileForm(request.POST, instance=instance)
        if pk:
            u = User.objects.get(id=pk)
            # User can't edit their own status
            if u != request.user:
                own_profile = False
            else:
                own_profile = True
        else:
            u = User()
        if form.is_valid():
            if u != request.user:
                u.is_active = form.cleaned_data['is_active']
            u.username = form.cleaned_data['username']
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.email = form.cleaned_data['email']
            u.save()

            return HttpResponseRedirect(reverse('home'))
    else:
        form = mf.UserProfileForm()
        u = User.objects.get(id=pk)
        if u == request.user:
            own_profile = True
        else:
            own_profile = False
        form.fields['username'].initial = u.username
        form.fields['first_name'].initial = u.first_name
        form.fields['last_name'].initial = u.last_name
        form.fields['email'].initial = u.email
        form.fields['is_active'].initial = u.is_active
    return render_to_response('user_profile.html',
        {'form': form, 'nav1': 'user_tools', 'nav2': inspect.stack()[0][3],
        'self': own_profile},
        context_instance=RequestContext(request))


@login_required
def user_create(request):
    if request.method == 'POST':
        form = mf.UserCreateForm(request.POST)
        if form.is_valid():
            u = User.objects.create_user(form.cleaned_data['username'],
                                         form.cleaned_data['email'],
                                         form.cleaned_data['password'])
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.is_active = form.cleaned_data['is_active']
            u.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse('user_create'))
            else:
                return HttpResponseRedirect(reverse('user_list'))
    else:
        form = mf.UserCreateForm()
    return render(request, 'user_create.html', {'form': form, 'nav1': 'admin',
        'nav2': inspect.stack()[0][3]})


@login_required
def group_list(request):
    table = mt.GroupTable(Group.objects.all())
    RequestConfig(request, paginate=False).configure(table)
    return render(request, 'group_list.html',
        {'table': table, 'nav1': 'admin', 'nav2': inspect.stack()[0][3],
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def group_detail(request, pk):
    if pk:
        instance = get_object_or_404(Group, pk=pk)
    else:
        instance = None
    if request.method == 'POST':
        form = mf.GroupProfileForm(request.POST, instance=instance)
        if form.is_valid():
            if pk:
                g = Group.objects.get(id=pk)
            else:
                g = Group()
            g.name = form.cleaned_data['name']
            g.save()

            return HttpResponseRedirect(reverse('group_list'))
    else:
        if pk:
            g = Group.objects.get(id=pk)
            form = mf.GroupProfileForm(instance=g)
        else:
            form = mf.GroupProfileForm()
    return render_to_response('group_profile.html',
        {'form': form, 'nav1': 'admin', 'nav2': inspect.stack()[0][3]},
        context_instance=RequestContext(request))


@login_required
def tank_detail(request, name):
    tank = mm.Tank.objects.get(name=name)
    json = serializers.serialize('json', [tank], extras=('tank_status',))
    return HttpResponse(json, mimetype="application/json")


@login_required
def tank_list(request):
    list_class = "Tank"
    list_app = "main"
    table = mt.TankTable(mm.Tank.objects.filter(hide=False))
    table.order_by = 'position'
    table.exclude = 'position'
    RequestConfig(request, paginate=False).configure(table)
    records = mm.Tank.objects.all().order_by('position')
    create = reverse(tank_create)
    create_text = 'Create New Tank'
    return render(request, 'record_list.html', {'table': table,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3],
        'list_class': list_class, 'records': records, 'create': create,
        'list_app': list_app,
        'create_text': create_text,
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def tank_create(request, pk):
    if request.method == 'POST':
        form = mf.CreateTankForm(request.POST)
        if form.is_valid():
            tid = form.cleaned_data['id']
            try:
                t = mm.Tank.objects.get(id=tid)
            except:
                t = mm.Tank()
            n = form.cleaned_data['name']
#            v = convert_to_base(float(form.cleaned_data['volume']),
#                                form.cleaned_data['volume_UOM'].mag_symbol,
#                                'volume')
            v = form.cleaned_data['volume']
            l = form.cleaned_data['location']
            a = form.cleaned_data['active']
            max_pos = mm.Tank.objects.all().aggregate(p=Max('position'))

            t.name = n
            t.location = l
            t.volume = v
            t.active = a
            if not t.position:
                if max_pos['p']:
                    t.position = max_pos['p'] + 1
                else:
                    t.position = 1
            t.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse('tank_create'))
            else:
                return HttpResponseRedirect(reverse('tank_list'))
    else:
        form = mf.CreateTankForm()
        if pk:
            default_vol_unit = mm.Unit.objects.filter(
                type=settings.VOLUME_UNIT_TYPE).get(default=True)
            base_vol_unit = mm.Unit.objects.get(pk=settings.BASE_UNIT.get(
                settings.VOLUME_UNIT_TYPE))
            t = mm.Tank.objects.get(id=pk)
            v = mt.convert_to_default(
                t.volume, base_vol_unit, default_vol_unit)
            form.fields['id'].initial = t.id
            form.fields['name'].initial = t.name
            form.fields['location'].initial = t.location
            form.fields['volume'].initial = v
            form.fields['active'].initial = t.active

    return render(request, 'tank_create.html', {'form': form, 'nav1': 'admin',
        'nav2': inspect.stack()[0][3]},
        context_instance=RequestContext(request))


@login_required
@transaction.commit_manually
def tank_delete(request, pk):
    tank = get_object_or_404(mm.Tank, id=pk)
    error = False
    message = ''
    if request.method == 'POST':
        try:
            tank.delete()
            transaction.commit()  # after user POSTs, commit the delete
            return HttpResponseRedirect(reverse('tank_list'))
        except ProtectedError, e:
            message = e
            error = True
    try:  # test to see if a delete throws a protected error
        tank.delete()
    except ProtectedError, e:
        message = e
        error = True
    transaction.rollback()  # rollback regardless as user hasn't confirmed
    return render(request, 'record_delete.html', {
        'record': tank, 'nav1': 'admin', 'nav2': inspect.stack()[0][3],
        'error': error, 'message': mark_safe(message)},
        context_instance=RequestContext(request))


@login_required
def location_list(request):
    list_class = "Location"
    list_app = "main"
    table = mt.LocationTable(mm.Location.objects.all())
    table.order_by = 'position'
    table.exclude = 'position'
    RequestConfig(request, paginate=False).configure(table)
    records = mm.Location.objects.all().order_by('position')
    create = reverse(location_create)
    create_text = 'Create New Location'
    return render(request, 'record_list.html', {
        'table': table,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3],
        'list_class': list_class, 'records': records,
        'list_app': list_app,
        'create': create, 'create_text': create_text,
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def location_create(request, pk):
    if request.method == 'POST':
        form = mf.CreateLocationForm(request.POST)
        if form.is_valid():
            lid = form.cleaned_data['id']
            try:
                l = mm.Location.objects.get(id=lid)
            except:
                l = mm.Location()
            n = form.cleaned_data['name']
            a = form.cleaned_data['active']
            max_pos = mm.Location.objects.all().aggregate(p=Max('position'))

            l.name = n
            l.active = a
            if not l.position:
                if max_pos['p']:
                    l.position = max_pos['p'] + 1
                else:
                    l.position = 1
            l.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse('location_create'))
            else:
                return HttpResponseRedirect(reverse('location_list'))
    else:
        form = mf.CreateLocationForm()
        if pk:
            l = get_object_or_404(mm.Location, id=pk)
            form.fields['id'].initial = l.id
            form.fields['name'].initial = l.name
            form.fields['active'].initial = l.active

    return render(request, 'location_create.html', {'form': form,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3]},
        context_instance=RequestContext(request))


@login_required
@transaction.commit_manually
def location_delete(request, pk):
    location = get_object_or_404(mm.Location, id=pk)
    error = False
    message = ''
    if request.method == 'POST':
        try:
            location.delete()
            transaction.commit()  # after user POSTs, commit the delete
            return HttpResponseRedirect(reverse('location_list'))
        except ProtectedError, e:
            message = e
            error = True
    try:  # test to see if a delete throws a protected error
        location.delete()
    except ProtectedError, e:
        message = e
        error = True
    transaction.rollback()  # rollback regardless as user hasn't confirmed
    return render(request, 'record_delete.html',  {
        'record': location, 'nav1': 'admin', 'nav2': inspect.stack()[0][3],
        'error': error, 'message': mark_safe(message)},
        context_instance=RequestContext(request))


@login_required
def bevtype_list(request):
    list_class = "BevType"
    list_app = "main"
    table = mt.BevTypeTable(mm.BevType.objects.filter(hide=False))
    table.order_by = 'position'
    table.exclude = 'position'
    RequestConfig(request, paginate=False).configure(table)
    records = mm.BevType.objects.all().order_by('position')
    create = reverse(bevtype_create)
    create_text = 'Create New Brew Type'
    return render(request, 'record_list.html', {'table': table,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3],
        'list_class': list_class, 'records': records,
        'list_app': list_app,
        'create': create, 'create_text': create_text,
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def bevtype_create(request, pk):
    if request.method == 'POST':
        form = mf.CreateBevTypeForm(request.POST, prefix="bt")
        if pk:
            form2 = None
        else:
            form2 = mf.CreateProductTypeForm(request.POST, prefix="pt",
                bev_type_form=True)
        if form.is_valid():
            try:
                bt = mm.BevType.objects.get(id=pk)
            except:
                bt = mm.BevType()
            n = form.cleaned_data['name']
            p = form.cleaned_data['prefix']
            i = form.cleaned_data['initial']
            a = form.cleaned_data['active']
            max_pos = mm.BevType.objects.all().aggregate(p=Max('position'))

            bt.name = n
            bt.prefix = p
            if i:
                bt.initial = i
            bt.active = a
            if not bt.position:
                if max_pos['p']:
                    bt.position = max_pos['p'] + 1
                else:
                    bt.position = 1
            if form.cleaned_data['create_product_type']:
                if form2.is_valid():
                    bt.save()
                    max_pos = mm.ProductType.objects.all().aggregate(
                        p=Max('position'))
                    pt = mm.ProductType()
                    pt.name = n
                    pt.prefix = p
                    pt.alcohol = form2.cleaned_data['alcohol']
                    pt.excise_category = form2.cleaned_data['excise_category']
                    pt.colour = form2.cleaned_data['colour']
                    pt.active = a
                    if not pt.position:
                        if max_pos['p']:
                            pt.position = max_pos['p'] + 1
                        else:
                            pt.position = 1
                    pt.save()

                    try:
                        pbt = mm.ProductBevType.objects.get(Q(product_type=pt)
                                                         & Q(bev_type=bt))
                    except:
                        pbt = mm.ProductBevType()

                    pbt.product_type = pt
                    pbt.bev_type = bt
                    pbt.proportion = 1
                    pbt.save()
                    if 'Repeat' in request.POST:
                        return HttpResponseRedirect(reverse('bevtype_create'))
                    else:
                        return HttpResponseRedirect(reverse('bevtype_list'))
            else:
                bt.save()
                if 'Repeat' in request.POST:
                    return HttpResponseRedirect(reverse('bevtype_create'))
                else:
                    return HttpResponseRedirect(reverse('bevtype_list'))
    else:
        if pk:
            bt = get_object_or_404(mm.BevType, id=pk)
            form = mf.CreateBevTypeForm(instance=bt, prefix="bt")
            form2 = None
        else:
            form = mf.CreateBevTypeForm(prefix="bt")
            form2 = mf.CreateProductTypeForm(prefix="pt", bev_type_form=True)

    return render(request, 'bevtype_create.html', {'form': form,
        'form2': form2, 'nav1': 'admin', 'nav2': inspect.stack()[0][3]},
        context_instance=RequestContext(request))


@login_required
@transaction.commit_manually
def bevtype_delete(request, pk):
    bevtype = get_object_or_404(mm.BevType, id=pk)
    error = False
    message = ''
    if request.method == 'POST':
        try:
            bevtype.delete()
            transaction.commit()  # after user POSTs, commit the delete
            return HttpResponseRedirect(reverse('bevtype_list'))
        except ProtectedError, e:
            message = e
            error = True
    try:  # test to see if a delete throws a protected error
        bevtype.delete()
    except ProtectedError, e:
        message = e
        error = True
    transaction.rollback()  # rollback regardless as user hasn't confirmed
    return render(request, 'record_delete.html', {
        'record': bevtype,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3], 'error': error,
        'message': mark_safe(message)},
        context_instance=RequestContext(request))


@login_required
def producttype_list(request):
    list_class = "ProductType"
    list_app = "main"
    table = mt.ProductTypeTable(mm.ProductType.objects.filter(hide=False))
    table.order_by = 'position'
    table.exclude = 'position'
    RequestConfig(request, paginate=False).configure(table)
    records = mm.ProductType.objects.all().order_by('position')
    create = reverse(producttype_create)
    create_text = 'Create New Product Type'
    return render(request, 'record_list.html', {
        'table': table,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3],
        'list_class': list_class, 'records': records,
        'list_app': list_app,
        'create': create, 'create_text': create_text,
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def producttype_create(request, pk):
    bevtypes = mm.BevType.objects.order_by('position')
    bevtype_count = bevtypes.count()
    BevTypeFormSet = formset_factory(
        mf.BevTypeForm, formset=mf.BaseBevTypeFormSet, extra=bevtype_count)
    formset = BevTypeFormSet()
    for i, fs in enumerate(formset):
        fs.fields['proportion'].label = bevtypes[i].name
        fs.fields['id'].initial = bevtypes[i].id

    if request.method == 'POST':
        form = mf.CreateProductTypeForm(request.POST)
        formset = BevTypeFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            ptid = form.cleaned_data['id']
            max_pos = mm.ProductType.objects.all().aggregate(p=Max('position'))
            try:
                pt = mm.ProductType.objects.get(id=ptid)
            except:
                pt = mm.ProductType()
            pt.name = form.cleaned_data['name']
            pt.prefix = form.cleaned_data['prefix']
            pt.alcohol = form.cleaned_data['alcohol']
            pt.excise_category = form.cleaned_data['excise_category']
            pt.colour = form.cleaned_data['colour']
            pt.active = form.cleaned_data['active']
            if not pt.position:
                if max_pos['p']:
                    pt.position = max_pos['p'] + 1
                else:
                    pt.position = 1
            pt.save()

            for fm in formset:
                p = fm.cleaned_data['proportion'] / 100
                bt = mm.BevType.objects.get(pk=fm.cleaned_data['id'])

                try:
                    pbt = mm.ProductBevType.objects.get(
                        Q(product_type=pt) & Q(bev_type=bt))
                    pbt.product_type = pt
                    pbt.bev_type = bt
                    pbt.proportion = p
                    pbt.save()
                except:
                    if p:
                        pbt = mm.ProductBevType()
                        pbt.product_type = pt
                        pbt.bev_type = bt
                        pbt.proportion = p
                        pbt.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse('producttype_create'))
            else:
                return HttpResponseRedirect(reverse('producttype_list'))
    else:
        form = mf.CreateProductTypeForm()
        if pk:
            pt = get_object_or_404(mm.ProductType, id=pk)
            form.fields['id'].initial = pt.id
            form.fields['name'].initial = pt.name
            form.fields['prefix'].initial = pt.prefix
            form.fields['alcohol'].initial = pt.alcohol
            form.fields['excise_category'].initial = pt.excise_category
            form.fields['colour'].initial = pt.colour

            for i, fs in enumerate(formset):
                try:
                    pbt = (mm.ProductBevType.objects.get(
                        Q(bev_type=bevtypes[i].id) & Q(product_type=pt)))
                    fs.fields['proportion'].initial = pbt.proportion * 100
                except:
                    fs.fields['proportion'].initial = 0.0

    return render_to_response('producttype_create.html', {'form': form,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3], 'formset': formset},
        context_instance=RequestContext(request))


@login_required
@transaction.commit_manually
def producttype_delete(request, pk):
    producttype = get_object_or_404(mm.ProductType, id=pk)
    error = False
    message = ''
    if request.method == 'POST':
        try:
            producttype.delete()
            transaction.commit()  # after user POSTs, commit the delete
            return HttpResponseRedirect(reverse('producttype_list'))
        except ProtectedError, e:
            message = e
            error = True
    try:  # test to see if a delete throws a protected error
        producttype.delete()
    except ProtectedError, e:
        message = e
        error = True
    transaction.rollback()  # rollback regardless as user hasn't confirmed
    return render(request, 'record_delete.html', {
        'record': producttype,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3], 'error': error,
        'message': mark_safe(message)},
        context_instance=RequestContext(request))


@class_view_decorator(login_required)
class PackageTypeListView(SingleTableView):
    model = mm.PackageType
    table_class = mt.PackageTypeTable
    table_pagination = False
    template_name = 'record_list.html'

    def get_context_data(self, **kwargs):
        context = super(PackageTypeListView, self).get_context_data(**kwargs)
        context['list_class'] = 'PackageType'
        context['list_app'] = 'main'
        context['create'] = reverse('packagetype_create')
        context['create_text'] = 'Create PackageType'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['pagination'] = mt.get_pagination(unlimited=True)
        return context

    def get_queryset(self):
        '''
        We only want to see non-legacy PackageTypes
        '''
        qs = super(PackageTypeListView, self).get_queryset()
        return qs.filter(legacy=False)


@class_view_decorator(login_required)
class PackageTypeCreateView(CreateView):
    model = mm.PackageType
    form_class = mf.CreatePackageTypeForm
    template_name = 'main/package_type_create_form.html'
    success_url = reverse_lazy('packagetype_list')

    def get_context_data(self, **kwargs):
        context = super(PackageTypeCreateView, self).get_context_data(**kwargs)
        context['model_text'] = 'Package Type'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        return context


@class_view_decorator(login_required)
class PackageTypeUpdateView(UpdateView):
    model = mm.PackageType
    form_class = mf.CreatePackageTypeForm
    template_name = 'main/package_type_create_form.html'
    success_url = reverse_lazy('packagetype_list')

    def get_context_data(self, **kwargs):
        context = super(PackageTypeUpdateView, self).get_context_data(**kwargs)
        context['model_text'] = 'Package Type'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        return context


@class_view_decorator(login_required)
class PackageTypeDeleteView(DeleteView):
    model = mm.PackageType
    template_name = 'record_delete.html'
    success_url = reverse_lazy('packagetype_list')

    def get_context_data(self, **kwargs):
        context = super(PackageTypeDeleteView, self).get_context_data(**kwargs)
        context['model_text'] = 'Package Type'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        return context

    @transaction.commit_manually
    def get(self, request, *args, **kwargs):
        """
        Check for protected error
        """
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        try:
            self.object.delete()
            transaction.rollback()
            return self.render_to_response(context)
        except ProtectedError:
            context = self.get_context_data()
            context['error'] = ('This package type has been used. ' +
                'Edit the package type and change Active to False.')
            context['object'] = self.object
        transaction.rollback()
        return self.render_to_response(context)

    def delete(self, request, *args, **kwargs):
        """
        Handle Protected Error
        """
        self.object = self.get_object()
        try:
            self.object.delete()
        except ProtectedError, e:
            context = self.get_context_data()
            context['error'] = e
            return self.render_to_response(context)
        return HttpResponseRedirect(self.get_success_url())


@login_required
def brew_report(request):
    table = mt.BrewTable(mm.Brew.objects.filter(hide=False))
    list_class = 'Brew'
    list_app = "main"
    table.order_by = '-create_date'
    RequestConfig(request, paginate=False).configure(table)
    return render(request, 'record_list.html', {'table': table,
        'nav1': 'reports', 'nav2': inspect.stack()[0][3],
        'list_class': list_class,
        'list_app': list_app,
        'pagination': mt.get_pagination()})


@login_required
def brew_create(request, event, pk, detail=False):
    if pk:
        edit = True
    else:
        edit = False
    if request.method == 'POST':
        form = mf.CreateBrewForm(request.POST, edit_form=edit)
        if form.is_valid():
            # den = (convert_to_base(float(
            #     form.cleaned_data['starting_density']),
            #     form.cleaned_data['starting_density_UOM'].mag_symbol,
            #     'density'))

            cd = form.cleaned_data['create_date']
            bt = form.cleaned_data['bev_type']

            if pk:
                brew = mm.Brew.objects.get(pk=pk)
                old_create_date = brew.create_date
            else:
                brew = mm.Brew()
                den = form.cleaned_data['starting_density']
                brew.starting_density = den
            brew.create_date = cd
            brew.bev_type = bt
            brew.malt = form.cleaned_data['malt']
            brew.hops = form.cleaned_data['hops']
            brew.yeast = form.cleaned_data['yeast']
            if not pk:
                brew.batch_no = get_next_batch_number(brew.bev_type)
            brew.save()

            if pk:
                pass
            else:
                b = form.cleaned_data['blend_with']
                d = form.cleaned_data['create_date']
                dt = form.cleaned_data['dest_tank']
                n = brew.bev_type.prefix + str(brew.batch_no)
                pt = form.cleaned_data['product_type']
                s = mm.BevTankStatus(pk=1)

                dbt = return_bev_tank(b, d, dt, n, pt, s)

            if pk:
                bt = mm.BevTank.objects.get(
                    bevtank_cur_tank__brew=brew,
                    bevtank_cur_tank__src_tank__isnull=True)
                bc = mm.BevChunk.objects.get(
                    cur_tank=bt, src_tank__isnull=True, brew=brew)
            else:
                bc = mm.BevChunk()
                bc.starting_density = den
                bc.brew = brew
                bc.cur_tank = dbt
            bc.create_date = form.cleaned_data['create_date']
            bc.src_tank = None
#            bc.volume = convert_to_base(float(
#                                form.cleaned_data['dest_volume']),
#                                form.cleaned_data['dest_volume_UOM'].
#                                mag_symbol, 'volume')
            bc.volume = form.cleaned_data['dest_volume']
            bc.save()

            if pk:
                dm = mm.Measurement.objects.get(
                    measurement_type__name='Density', bev_tank=bt,
                    measurement_date=old_create_date)
                dm.measurement_date = form.cleaned_data['create_date']
                dm.save()
                da = mm.Measurement.objects.get(
                    measurement_type__name='Alcohol', bev_tank=bt,
                    measurement_date=old_create_date)
                da.measurement_date = form.cleaned_data['create_date']
                da.save()
            else:
                # only create OG measurement if NOT blending into existing tank
                if not b:
                    m = mm.Measurement()
                    m.measurement_type = mm.MeasurementType.objects.get(
                        name="Density")
                    m.measurement_date = d
                    m.bev_tank = dbt
                    m.value = den
                    m.user = None
                    m.parent = None
                    m.save()
                    m.calculate_alcohol(d)

            if pk:
                e = mm.Event.objects.get(brew=brew)
            else:
                e = mm.Event()
                e.brew = brew
                e.url = '/brew/' + str(brew.id)
                e.event_type = mm.EventType.objects.get(name="Brew")
                e.editable = False
                e.scheduled = False
            e.title = 'Brew: ' + str(brew.bev_type)
            e.start = brew.create_date
            e.end = brew.create_date
            e.record_id = brew.id
            e.save()

            if event:
                se = mm.Event.objects.get(pk=event)
                se.delete()  # delete scheduled event now it has been completed

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(brew_create))
            else:
                return HttpResponseRedirect(reverse(brew_list))
    else:
        if event:
            e = mm.Event.objects.get(pk=event)
            date = e.start.astimezone(pytz.timezone(settings.TIME_ZONE))
            form = mf.CreateBrewForm(initial={'create_date': date,
                'bev_type': e.bev_type})
        else:
            if pk:
                b = get_object_or_404(mm.Brew, id=pk)
                if not detail:
                    pqs = mm.Package.objects.filter(
                        bev_tank__bevtank_cur_tank__brew=b)
                    tqs = mm.Transfer.objects.filter(bevchunk__brew=b)
                    error = ''
                    if pqs:
                        pstr = ''
                        for p in pqs:
                            pstr += str(p) + ' '
                        error += (str(b) + ' has been packaged. If you wish to' +
                            ' edit it, delete the following first: ' + pstr)
                    if tqs:
                        tstr = ''
                        for t in tqs:
                            # TODO: Investigate possibility of this getting
                            #       multiple objects
                            bt = mm.BevTank.objects.get(
                                bevtank_cur_tank__transfer=t)
                            tstr += str(bt) + ' '
                        error += (str(b) + ' has been transferred. If you wish' +
                            ' to edit it, delete the following first: ' + tstr)
                    if error:
                        logger.info(
                            "Unable to Edit Brew: {}".format(error),
                            extra={'request': request})
                        return render(request, 'record_edit_error.html',
                            {'nav1': 'production', 'nav2': inspect.stack()[0][3],
                            'record': b, 'error': error},
                            context_instance=RequestContext(request))
                #TODO: need to change when multiple bevtanks is implemented
                bt = mm.BevTank.objects.get(bevtank_cur_tank__brew=b,
                    bevtank_cur_tank__src_tank__isnull=True)
                bc = mm.BevChunk.objects.get(
                    cur_tank=bt, src_tank__isnull=True, brew=b)
                data = {'create_date': b.create_date,
                        'bev_type': b.bev_type,
                        # need to change when multiple bevtanks is implemented
                        'product_type': bt.product_type,
                        'malt': b.malt,
                        'hops': b.hops,
                        'yeast': b.yeast,
                        'dest_volume': bc.volume,
                        'starting_density': b.starting_density,
                        'dest_tank': bt.tank}
                form = mf.CreateBrewForm(edit_form=edit, initial=data)
            else:
                form = mf.CreateBrewForm(edit_form=edit)
    return render_to_response('brew_create.html', {'form': form,
        'nav1': 'production', 'nav2': inspect.stack()[0][3], 'edit': edit,
        'detail': detail}, context_instance=RequestContext(request))


@login_required
def brew_list(request):
    list_class = 'Brew'
    list_app = "main"
    table = mt.BrewListTable(mm.Brew.objects.filter(hide=False))
    table.order_by = '-create_date'
    RequestConfig(request, paginate=False).configure(table)
    create = reverse(brew_create)
    create_text = 'Create Brew'
    return render(request, 'record_list.html', {'table': table,
        'nav1': 'production', 'nav2': inspect.stack()[0][3],
        'list_class': list_class, 'create': create,
        'list_app': list_app,
        'create_text': create_text,
        'pagination': mt.get_pagination()})


@login_required
def brew_detail(request, pk):
    form = mf.BrewBevTankForm()
    brew = get_object_or_404(mm.Brew, id=pk)
    bev_tanks = (mm.BevTank.objects.filter(bevtank_cur_tank__brew=brew,
        bevtank_cur_tank__src_tank__isnull=True))
    form.fields['bev_tank_field'].queryset = bev_tanks
    bev_tank_id = bev_tanks[0].pk
    mtqs = mm.Measurement.objects.raw('''select id, measurement_type_id,
        "value" from main_measurement m left join (select measurement_type_id
        as mtid, max(measurement_date) as md from main_measurement t2
        where bev_tank_id = %s group by measurement_type_id) m2
        on m.measurement_type_id = m2.mtid
        and m.measurement_date = m2.md
        where bev_tank_id = %s and md is not null''',
        [bev_tank_id, bev_tank_id])  # TODO: ajax
    dm = mm.MeasurementType.objects.get(name="Density")
    stm = mm.MeasurementType.objects.get(name="Set Temperature")
    atm = mm.MeasurementType.objects.get(name="Actual Temperature")
    measurements = mm.Measurement.objects.filter(
        Q(measurement_type=dm) | Q(measurement_type=atm)
        | Q(measurement_type=stm), bev_tank=bev_tanks[0].pk)  # TODO: ajax here
    table = mt.MeasurementTable(measurements)
    table.order_by = 'measurement_date'
    table.exclude = 'id', 'bev_tank', 'parent', 'user', 'notes'
    # Due to bug with css had to use paginate=False here
    RequestConfig(request, paginate=False).configure(table)

    return render(request, 'brew_detail.html', {'form': form,
        'nav1': 'production', 'nav2': inspect.stack()[0][3],
        'measurements': mtqs, 'brew': brew,
        'bev_tanks': bev_tanks, 'table': table, 'bev_tank': bev_tanks[0].pk,
        'pagination': mt.get_pagination()})


@class_view_decorator(login_required)
class BrewDetailView(DetailView):
    model = mm.Brew

    def get_brew_summary(self):
        brew = self.get_object()
        summary = {}
        vol_brewed = mm.BevChunk.objects.filter(brew=brew,
            parent__isnull=True).aggregate(Sum('volume'))['volume__sum']
        summary['vol_brewed'] = vol_brewed
        vol_packaged = mm.PackageBevChunk.objects.filter(
            bev_chunk__brew=brew).aggregate(Sum('volume'))['volume__sum']
        vol_checked_out = mm.CheckOutBevChunk.objects.filter(
            bev_chunk__brew=brew).aggregate(Sum('volume'))['volume__sum']
        vol_waste = mm.WasteBevChunk.objects.filter(
            bev_chunk__brew=brew).aggregate(Sum('volume'))['volume__sum']
        if vol_packaged is None:
            vol_packaged = 0
        if vol_checked_out is None:
            vol_checked_out = 0
        if vol_waste is None:
            vol_waste = 0
        vol_packaged_on_site = vol_packaged - vol_checked_out
        vol_in_tank = vol_brewed - vol_packaged - vol_waste
        summary['vol_packaged_on_site'] = vol_packaged_on_site
        # This assumes vol brewed is not zero
        summary['pc_packaged_on_site'] = (vol_packaged_on_site * 100 /
            vol_brewed)
        summary['vol_checked_out'] = vol_checked_out
        summary['pc_checked_out'] = vol_checked_out * 100 / vol_brewed
        summary['vol_waste'] = vol_waste
        summary['pc_waste'] = vol_waste * 100 / vol_brewed
        summary['vol_in_tank'] = vol_in_tank
        summary['pc_in_tank'] = vol_in_tank * 100 / vol_brewed

        return summary

    def get_brew_data(self):
        """
        Constructs a list of transfers, packages and checkouts recursively.
        Produces a simple list for the template to render
        """

        def get_children(bev_chunk):
            data = []
            p = package_bev_chunks.filter(bev_chunk=bev_chunk).order_by(
                'bev_chunk__create_date')
            if package_bev_chunks:
                data.append("in")
                for pa in p:
                    data.append(pa)
                    c = checkout_bev_chunks.filter(
                        checkout__package=pa.package, bev_chunk=pa.bev_chunk
                        ).order_by('bev_chunk__create_date')
                    if c:
                        data.append("in")
                        for ch in c:
                            data.append(ch)
                        data.append("out")
                data.append("out")
            for o in bev_chunks.filter(parent=bev_chunk):
                data.append("in")
                data.append(o)
                data.extend(get_children(o))
                data.append("out")
            return data

        data = []
        brew = self.get_object()
        bev_chunks = mm.BevChunk.objects.filter(brew=brew)
        package_bev_chunks = mm.PackageBevChunk.objects.filter(
            bev_chunk__in=bev_chunks)
        checkout_bev_chunks = mm.CheckOutBevChunk.objects.filter(
            bev_chunk__in=bev_chunks)
        for o in bev_chunks.filter(src_tank__isnull=True):
            data.append(o)
            data.extend(get_children(o))

        return data

    def get_context_data(self, **kwargs):

        def add_bev_tank(bt, bts, p, c):
            data = [bt]
            packages = p.filter(bev_tank=bt)
            if packages:
                data.append("in")
                for pa in packages:
                    data.append(pa)
                    checkouts = c.filter(package=pa)
                    if checkouts:
                        data.append("in")
                        for ch in checkouts:
                            data.append(ch)
                        data.append("out")
                data.append("out")
            bev_tanks = bts.filter(bevtank_cur_tank__src_tank=bt)
            if bev_tanks:
                data.append("in")
                for bt in bev_tanks:
                    data.extend(add_bev_tank(bt, bts, p, c))
                data.append("out")
            return data

        bev_tanks = mm.BevTank.objects.filter(
            bevtank_cur_tank__brew=self.object).distinct()
        initial_bev_tanks = bev_tanks.filter(
            bevtank_cur_tank__src_tank__isnull=True)
        packages = mm.Package.objects.filter(bev_tank__in=bev_tanks)
        checkouts = mm.CheckOut.objects.filter(package__in=packages)
        data = []
        for ibt in initial_bev_tanks:
            data.extend(add_bev_tank(ibt, bev_tanks, packages, checkouts))

        context = super(BrewDetailView, self).get_context_data(**kwargs)
        context['nav1'] = 'production'
        context['nav2'] = type(self).__name__
        context['data'] = self.get_brew_data()
        context['summary'] = self.get_brew_summary()
        context['title_text'] = 'Brew Detail'
        return context


@login_required
def brew_delete(request, pk):
    brew = get_object_or_404(mm.Brew, id=pk)
    can_delete, message = brew.can_delete()
    error = not can_delete
    if not can_delete:
        logger.info(
            "Unable to Delete Brew: {}".format(message),
            extra={'request': request})
        return render(request, 'record_delete.html', {
            'record': brew, 'error': error, 'message': mark_safe(message),
            'nav1': "production",
            'nav2': inspect.stack()[0][3]},
            context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
            try:
                brew.delete(user=request.user)
                return HttpResponseRedirect(reverse('brew_list'))
            except ProtectedError, e:
                message = e
                logger.warning(
                    "Unable to Delete Brew: {}".format(message),
                    extra={'request': request})
                error = True
        return render(
            request, 'record_delete.html', {
                'record': brew,
                'nav1': 'production',
                'nav2': inspect.stack()[0][3],
                'error': error,
                'message': mark_safe(message)},
            context_instance=RequestContext(request))


@login_required
def brew_schedule(request, date):
    if request.method == 'POST':
        form = mf.ScheduleBrewForm(request.POST)
        if form.is_valid():
            bev_type = form.cleaned_data['bev_type']
            d = form.cleaned_data['date']

            e = mm.Event()
            e.title = 'Brew: ' + str(bev_type)
            e.event_type = mm.EventType.objects.get(name="Brew")
            e.bev_type = bev_type
            e.editable = True
            e.scheduled = True
            e.start = d
            e.end = d
            e.save()
            e.url = reverse('brew_create_with_event', args=(e.id,))
            e.save()
            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(brew_schedule))
            else:
                return HttpResponseRedirect('/')
    else:
        form = mf.ScheduleBrewForm(initial={'date': date})
    return render_to_response('brew_schedule.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3],
        'form': form}, context_instance=RequestContext(request))


@login_required
def event_type_list(request):
    list_class = "Event"
    list_app = "main"
    table = mt.EventTypeTable(mm.EventType.objects.all())
    table.order_by = 'position'
    table.exclude = 'position'
    RequestConfig(request, paginate=False).configure(table)
    records = mm.EventType.objects.all().order_by('position')
    create = reverse(event_type_create)
    create_text = ''  # 'Create New Event Type'
    return render(request, 'record_list.html', {'table': table,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3],
        'list_class': list_class, 'records': records,
        'list_app': list_app,
        'create': create, 'create_text': create_text,
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def event_type_create(request, pk):
    if pk:
        instance = get_object_or_404(mm.EventType, pk=pk)
    else:
        instance = None
    if request.method == 'POST':
        form = mf.CreateEventTypeForm(request.POST, instance=instance)
        if form.is_valid():
            et = form.instance
            et.name = form.cleaned_data['name']
            et.active = True  # form.cleaned_data['active']
            et.color = form.cleaned_data['color']
            et.borderColor = form.cleaned_data['borderColor']
            et.backgroundColor = form.cleaned_data['backgroundColor']
            et.textColor = form.cleaned_data['textColor']
            et.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse('event_type_create'))
            else:
                return HttpResponseRedirect(reverse('event_type_list'))
    else:
        if pk:
            et = mm.EventType.objects.get(id=pk)
            form = mf.CreateEventTypeForm(instance=et)
        else:
            form = mf.CreateEventTypeForm()

    return render(request, 'event_type_create.html', {'form': form,
        'nav1': 'admin', 'nav2': inspect.stack()[0][3]},
        context_instance=RequestContext(request))


@login_required
@transaction.commit_manually
def event_type_delete(request, pk):
    event_type = get_object_or_404(mm.EventType, id=pk)
    error = False
    message = ''
    if request.method == 'POST':
        try:
            event_type.delete()
            transaction.commit()  # after user POSTs, commit the delete
            return HttpResponseRedirect(reverse('event_type_list'))
        except ProtectedError, e:
            error = True
            message = e
    try:  # test to see if a delete throws a protected error
        event_type.delete()
    except ProtectedError, e:
        error = True
        message = e
    transaction.rollback()  # rollback regardless as user hasn't confirmed
    return render(request, 'record_delete.html', {
        'nav1': 'admin', 'nav2': inspect.stack()[0][3],
        'record': event_type, 'error': error, 'message': mark_safe(message)},
        context_instance=RequestContext(request))


@login_required
def process_type_create(request, name):
    if name:
        instance = get_object_or_404(mm.ProcessType, name=name)
    else:
        instance = mm.ProcessType()
    if request.method == 'POST':
        form = mf.CreateProcessTypeForm(request.POST, instance=instance)
        if form.is_valid():
            pt = form.instance
            pt.name = form.cleaned_data['name']
            pt.active = form.cleaned_data['active']
            pt.save()
            return HttpResponseRedirect(reverse('home'))
    elif request.method == 'GET':
        data = {}
        pt = mm.ProcessType.objects.get(name=request.GET['name'])
        data['name'] = pt.name
        data['active'] = pt.active
        return HttpResponse(json.dumps(data), mimetype="applicaton/json")


@login_required
def task_type_create(request, name):
    if name:
        instance = get_object_or_404(mm.TaskType, name=name)
    else:
        instance = None
    if request.method == 'POST':
        form = mf.CreateTaskTypeForm(request.POST, instance=instance)
        if form.is_valid():
            tt = form.instance
            tt.name = form.cleaned_data['name']
            tt.active = form.cleaned_data['active']
            tt.save()

            return HttpResponseRedirect(reverse('home'))
    elif request.method == 'GET':
        data = {}
        tt = mm.TaskType.objects.get(name=request.GET['name'])
        data['name'] = tt.name
        data['active'] = tt.active
        return HttpResponse(json.dumps(data), mimetype="applicaton/json")


@class_view_decorator(login_required)
class SalesItemListView(SingleTableView):
    model = om.SalesItem
    table_class = ot.SalesItemTable
    table_pagination = False
    template_name = 'record_list.html'

    def get_context_data(self, **kwargs):
        context = super(SalesItemListView, self).get_context_data(**kwargs)
        context['list_class'] = 'SalesItem'
        context['list_app'] = 'orders'
        context['create'] = reverse('sales_item_create')
        context['create_text'] = 'Create Sales Item'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['pagination'] = mt.get_pagination(unlimited=True)
        return context


@class_view_decorator(login_required)
class SalesItemCreateView(CreateView):
    form_class = of.SalesItemForm
    model = om.SalesItem
    template_name = 'main/sales_item_create_form.html'
    default_referrer = reverse_lazy('sales_item_list')

    def get_referrer_url(self):
        return self.request.GET.get(
            'referrer', self.default_referrer)

    def get_success_url(self):
        return self.get_referrer_url()

    def get_context_data(self, **kwargs):
        context = super(SalesItemCreateView, self).get_context_data(**kwargs)
        context['model_text'] = 'Sales Item'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['referrer'] = self.get_referrer_url()
        if 'formset' not in kwargs:
            context['formset'] = of.SalesItemUnitFormSet()
        return context

    def post(self, request, *args, **kwargs):
        """
        Override this to call formset.is_valid()
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.formset = of.SalesItemUnitFormSet(self.request.POST)
        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        si = form.save()
        for fs in self.formset:
            if fs.has_changed() and not fs.cleaned_data['DELETE']:
                siu = fs.save(commit=False)
                siu.sales_item = si
                siu.save()
        return super(SalesItemCreateView, self).form_valid(form)

    def form_invalid(self, form):
        """
        Override this to render formset as well as form
        """
        return self.render_to_response(self.get_context_data(
            form=form, formset=self.formset))


@class_view_decorator(login_required)
class SalesItemUpdateView(UpdateView):
    form_class = of.SalesItemForm
    model = om.SalesItem
    template_name = 'main/sales_item_create_form.html'
    default_referrer = reverse_lazy('sales_item_list')

    def get_referrer_url(self):
        return self.request.GET.get(
            'referrer', self.default_referrer)

    def get_success_url(self):
        return self.get_referrer_url()

    def get_context_data(self, **kwargs):
        context = super(SalesItemUpdateView, self).get_context_data(**kwargs)
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['model_text'] = 'Sales Item'
        context['referrer'] = self.get_referrer_url()
        if 'formset' not in kwargs:
            context['formset'] = of.SalesItemUnitFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        """
        Override this to call formset.is_valid()
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.formset = of.SalesItemUnitFormSet(self.request.POST,
            instance=self.object)
        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        for fs in self.formset:
            # Do not attempt to save blank form
            if fs.has_changed():
                if fs.cleaned_data['DELETE']:
                    siu = fs.cleaned_data['id']
                    if siu:
                        siu.delete()
                else:
                    fs.save()
        # Assume if doesn't begin with '/' something is fishy
        if self.get_referrer_url()[0] == '/':
            return HttpResponseRedirect(self.get_referrer_url())
        else:
            raise Http404

    def form_invalid(self, form):
        """
        Override this to render formset as well as form
        """
        return self.render_to_response(self.get_context_data(
            form=form, formset=self.formset))


@class_view_decorator(login_required)
class SalesItemDeleteView(DeleteView):
    model = om.SalesItem
    template_name = 'record_delete.html'
    default_referrer = reverse_lazy('sales_item_list')

    def get_referrer_url(self):
        return self.request.GET.get(
            'referrer', self.default_referrer)

    def get_success_url(self):
        return self.get_referrer_url()

    def get_context_data(self, **kwargs):
        context = super(SalesItemDeleteView, self).get_context_data(**kwargs)
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['model_text'] = 'Sales Item'
        context['referrer'] = self.get_referrer_url()
        return context


@login_required
def process_create(request, event):
    if request.method == 'POST':
        form = mf.CreateProcessForm(request.POST)
        if form.is_valid():
            bt = form.cleaned_data['bev_tank']
            d = form.cleaned_data['create_date']
            t = form.cleaned_data['type']

            p = mm.Process()
            p.bev_tank = bt
            p.create_date = d
            p.type = t
            p.save()

            e = mm.Event()
            e.title = t.name + u': ' + bt.name
            e.event_type = mm.EventType.objects.get(name="Process")
            e.process_type = t
            e.url = '/process/' + str(p.id)
            e.start = d
            e.end = d
            e.editable = False
            e.scheduled = False
            e.record_id = p.id
            e.save()

            if event:
                se = mm.Event.objects.get(pk=event)
                se.delete()  # delete scheduled event now it has been completed

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(process_create))
            else:
                return HttpResponseRedirect('/')
    else:
        if event:
            e = mm.Event.objects.get(pk=event)
            date = e.start.astimezone(pytz.timezone(settings.TIME_ZONE))
            form = mf.CreateProcessForm(initial={'create_date': date,
                                              'bev_tank': e.bev_tank,
                                              'type': e.process_type})
        else:
            form = mf.CreateProcessForm()
    return render_to_response('process_create.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3],
        'form': form}, context_instance=RequestContext(request))


@login_required
def process_detail(request, pk):
    process = get_object_or_404(mm.Process, id=pk)
    return render(request, 'process_detail.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'process': process})


@login_required
def process_schedule(request, date):
    if request.method == 'POST':
        form = mf.ScheduleProcessForm(request.POST)
        if form.is_valid():
            bev_tank = form.cleaned_data['bev_tank']
            ptype = form.cleaned_data['process_type']
            d = form.cleaned_data['date']

            e = mm.Event()
            e.title = ptype.name + u': ' + bev_tank.name
            e.event_type = mm.EventType.objects.get(name="Process")
            e.bev_tank = bev_tank
            e.process_type = ptype
            e.editable = True
            e.scheduled = True
            e.start = d
            e.end = d
            e.save()  # create e.id to reference next line
            e.url = reverse('process_create_with_event', args=(e.id,))
            e.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(process_schedule))
            else:
                return HttpResponseRedirect('/')
    else:
        form = mf.ScheduleProcessForm(initial={'date': date})
    return render_to_response('process_schedule.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'form': form},
        context_instance=RequestContext(request))


@login_required
def task_schedule(request, date):
    if request.method == 'POST':
        form = mf.ScheduleTaskForm(request.POST)
        if form.is_valid():
            ttype = form.cleaned_data['task_type']
            d = form.cleaned_data['date']

            e = mm.Event()
            e.title = str(ttype.name)
            e.event_type = mm.EventType.objects.get(name="Task")
            e.task_type = ttype
            e.editable = True
            e.scheduled = True
            e.start = d
            e.end = d
            e.save()  # create e.id to reference next line
            e.url = reverse('task_create_with_event', args=(e.id,))
            e.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(task_schedule))
            else:
                return HttpResponseRedirect('/')
    else:
        form = mf.ScheduleTaskForm(initial={'date': date})
    return render_to_response('task_schedule.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3],
        'form': form}, context_instance=RequestContext(request))


@login_required
def task_create(request, event):
    if request.method == 'POST':
        form = mf.ScheduleTaskForm(request.POST)
        if form.is_valid():
            ttype = form.cleaned_data['task_type']
            d = form.cleaned_data['date']

            e = mm.Event()
            e.title = str(ttype.name)
            e.event_type = mm.EventType.objects.get(name="Task")
            e.task_type = ttype
            e.editable = False
            e.scheduled = False
            e.start = d
            e.end = d
            e.save()  # create e.id to reference next line
            e.url = '/'  # TODO: need to have a task detail page
            e.save()

            if event:
                se = mm.Event.objects.get(pk=event)
                se.delete()  # delete scheduled event now it has been completed

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(task_schedule))
            else:
                return HttpResponseRedirect('/')
    else:
        se = mm.Event.objects.get(pk=event)
        form = mf.ScheduleTaskForm(initial={
            'date': se.start.astimezone(pytz.timezone(settings.TIME_ZONE)),
            'task_type': se.task_type}
        )
    return render_to_response('task_schedule.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'create': True,
        'form': form}, context_instance=RequestContext(request))


@login_required
def schedule(request):
    if request.method == 'POST':
        form = mf.ScheduleForm(request.POST)
        if form.is_valid():
            eid = form.cleaned_data['id']
            date = form.cleaned_data['date']

            e = mm.Event.objects.get(pk=eid)
            e.start = date
            e.end = date
            e.save()
    return HttpResponseRedirect('/')


@login_required
def event_delete(request):
    if request.method == 'POST':
        form = mf.EventDeleteForm(request.POST)
        if form.is_valid():
            eid = form.cleaned_data['id']

            e = mm.Event.objects.get(pk=eid)
            e.delete()
    return HttpResponseRedirect('/')


@login_required
def transfer_list(request):
    list_class = 'Transfer'
    list_app = "main"
    table = mt.TransferListTable(mm.Transfer.objects.all())
    table.order_by = '-create_date'
    RequestConfig(request, paginate=False).configure(table)
    create = reverse(transfer)
    create_text = 'Create Transfer'
    return render(request, 'record_list.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'table': table,
        'list_class': list_class, 'create': create,
        'list_app': list_app,
        'create_text': create_text,
        'pagination': mt.get_pagination()})


@login_required
def transfer(request, event, pk):
    if pk:
        edit = True
        transfer = get_object_or_404(mm.Transfer, pk=pk)
        src_tank = transfer.get_src_tank()
        dest_tank = transfer.get_dest_bevtank()
        bev_chunks = transfer.get_bev_chunks()
    else:
        edit = False
    if request.method == 'POST':
        form = mf.TransferForm(request.POST, edit_form=edit)
        if form.is_valid():
            if pk:
                # Change the transfer date in all models
                old_transfer_date = transfer.get_transfer_date()
                cd = form.cleaned_data['transfer_date']
                # If this transfer created the dest bev tank, change date
                if dest_tank.fill_date == bev_chunks[0].create_date:
                    dest_tank.fill_date = cd
                    dest_tank.save()
                # Change create date for all bev chunks
                for bc in bev_chunks:
                    bc.create_date = cd
                    bc.save()

                # Update dest volume
                transfer.set_volume(form.cleaned_data['dest_volume'])

                # Update empty date
                # If tank is unlimited (e.g. DAL), keep empty unchanged
                if form.cleaned_data['empty'] and not src_tank.unlimited:
                    if src_tank.empty_date is None:
                        src_tank.empty_date = cd
                        mv = mm.Measurement()
                        mv.measurement_type = mm.MeasurementType.objects.get(
                            name='Volume')
                        mv.bev_tank = src_tank
                        mv.measurement_date = cd
                        mv.value = 0.0
                        mv.save()
                        # Add the waste bev chunk(s)
                        for bc in bev_chunks:
                            wbc = mm.WasteBevChunk()
                            wbc.measurement = mv
                            wbc.bev_chunk = bc.parent
                            wbc.volume = bc.parent.get_volume(
                                mv.measurement_date)
                            wbc.save()

                    else:
                        if src_tank.empty_date == old_transfer_date:
                            src_tank.empty_date = cd
                            mv = mm.Measurement.objects.get(
                                measurement_type__name='Volume', value=0.0,
                                bev_tank=src_tank,
                                measurement_date=old_transfer_date)
                            mv.measurement_date = cd
                            mv.save()
                            # Update the waste bev chunk(s)
                            for bc in bev_chunks:
                                wbc = mm.WasteBevChunk.objects.get(
                                    measurement=mv, bev_chunk=bc.parent)
                                wbc.volume = bc.parent.get_volume(
                                    mv.measurement_date) + wbc.volume
                                wbc.save()
                        else:
                            # Don't update date when this transfer did not
                            # empty the tank
                            pass

                else:
                    if src_tank.empty_date is not None:
                        # Un-empty the bev tank
                        src_tank.empty_date = None
                        m = mm.Measurement.objects.get(
                            measurement_type__name='Volume', value=0.0,
                            bev_tank=src_tank,
                            measurement_date=old_transfer_date)
                        # Delete waste bev chunks
                        wbc = mm.WasteBevChunk.objects.filter(measurement=m)
                        for o in wbc:
                            o.delete()
                        # Delete empty measurement
                        m.delete()
                src_tank.save()

                # Update Transfer Event Date
                e = mm.Event.objects.get(
                    event_type__name="Transfer", record_id=pk)
                e.start = cd
                e.end = cd
                e.save()

                # Update initial measurements
                mqs = mm.Measurement.objects.filter(
                    bev_tank=dest_tank, measurement_date=old_transfer_date)
                for m in mqs:
                    m.measurement_date = cd
                    m.save()

            else:
                bt = form.cleaned_data['cur_tank']
                dt = form.cleaned_data['dest_tank']
    #            v = convert_to_base(float(form.cleaned_data['dest_volume']),
    #                                form.cleaned_data['dest_volume_UOM'].
    #                                mag_symbol, 'volume')
                v = float(form.cleaned_data['dest_volume'])
                d = form.cleaned_data['transfer_date']
                b = form.cleaned_data['blend_with']
                n = bt.name
                pt = form.cleaned_data['product_type']
                s = bt.status

                dbt = return_bev_tank(b, d, dt, n, pt, s)
                t = bt.transfer(d, dbt, v)

                # No Measurement for blend
                if not b:
                    m = mm.Measurement()
                    m.measurement_type = mm.MeasurementType.objects.get(
                        name='Density')
                    m.measurement_date = d
                    m.bev_tank = dbt
                    m.value = bt.get_density(d).value
                    m.parent = bt.get_density(d)
                    m.user = None
                    m.save()
                    m.calculate_alcohol(d)

                e = mm.Event()
                e.title = 'Transfer: ' + str(bt.name) + ' to ' + str(dt)
                e.event_type = mm.EventType.objects.get(name="Transfer")
                e.url = '/transfer/' + str(t.id)
                e.start = d
                e.end = d
                e.editable = False
                e.color = "darkblue"  # TODO: parameterise this
                e.record_id = t.id
                e.save()

                # If tank is unlimited (e.g. DAL), keep empty unchanged
                if form.cleaned_data['empty'] and not bt.unlimited:
                    bt.empty_date = d
                    bt.save()

                    mv = mm.Measurement()
                    mv.measurement_type = mm.MeasurementType.objects.get(
                        name='Volume')
                    mv.bev_tank = bt
                    mv.measurement_date = d
                    mv.value = 0.0
                    mv.save()

                    # Add the waste bev chunk(s)
                    bcs = t.get_bev_chunks()
                    for bc in bcs:
                        wbc = mm.WasteBevChunk()
                        wbc.bev_chunk = bc.parent
                        wbc.measurement = mv
                        parent_vol = bc.parent.get_volume(mv.measurement_date)
                        wbc.volume = parent_vol
                        wbc.save()

                if event:
                    se = mm.Event.objects.get(pk=event)
                    se.delete()  # del scheduld event now it has been completed

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse('transfer_create'))
            else:
                return HttpResponseRedirect(reverse(transfer_list))
    else:
        if event:
            e = mm.Event.objects.get(pk=event)
            date = e.start.astimezone(pytz.timezone(settings.TIME_ZONE))
            form = mf.TransferForm(initial={'transfer_date': date,
                                           'cur_tank': e.bev_tank,
                                           'dest_tank': e.dest_tank})
        else:
            if pk:
                t = get_object_or_404(mm.Transfer, pk=pk)
                pqs = mm.Package.objects.filter(
                    bev_tank__bevtank_cur_tank__transfer=t)
                btqs = mm.BevTank.objects.filter(
                    bevtank_cur_tank__transfer__isnull=False,
                    bevtank_cur_tank__src_tank__bevtank_cur_tank__transfer=t)
                error = ''
                if pqs:
                    pstr = ''
                    for p in pqs:
                        pstr += str(p) + ' '
                    error += (str(t) + ''' has been packaged.
                        If you wish to edit it,
                        delete the following first: ''' + pstr)
                if btqs:
                    btstr = ''
                    for bt in btqs:
                        t = mm.Transfer.objects.get(bevchunk__cur_tank=bt)
                        btstr += str(t) + ' '
                    error += str(t) + ''' has been transferred.
                        If you wish to edit
                        it, delete the following first: ''' + btstr
                if error:
                    logger.info(
                        "Unable to Edit Transfer: {}".format(error),
                        extra={'request': request})
                    return render(request, 'record_edit_error.html',
                        {'nav1': 'production', 'nav2': inspect.stack()[0][3],
                        'record': t, 'error': error},
                        context_instance=RequestContext(request))
                data = {'transfer_date': t.get_transfer_date(),
                        'cur_tank': t.get_src_tank(),
                        'empty': t.get_src_empty(),
                        'dest_tank': t.get_dest_tank(),
                        'product_type': t.get_dest_product_type(),
                        'dest_volume': t.get_volume()}
                form = mf.TransferForm(edit_form=edit, initial=data)
            else:
                form = mf.TransferForm(edit_form=edit)
    return render_to_response('transfer.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'form': form, 'edit': edit},
        context_instance=RequestContext(request))


@login_required
def transfer_detail(request, pk):
    transfer = get_object_or_404(mm.Transfer, id=pk)
    bev_chunks = mm.BevChunk.objects.filter(transfer=transfer)
    volume = transfer.get_volume()
    return render(request, 'transfer_detail.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3],
        'bev_chunk': bev_chunks[0], 'volume': volume})


@login_required
def transfer_schedule(request, date):
    if request.method == 'POST':
        form = mf.ScheduleTransferForm(request.POST)
        if form.is_valid():
            bev_tank = form.cleaned_data['bev_tank']
            dest_tank = form.cleaned_data['dest_tank']
            d = form.cleaned_data['date']

            e = mm.Event()
            e.title = ('Transfer: ' + str(bev_tank.name) +
                       ' to ' + str(dest_tank.name))
            e.event_type = mm.EventType.objects.get(name="Transfer")
            e.bev_tank = bev_tank
            e.dest_tank = dest_tank
            e.editable = True
            e.color = "darkblue"  # TODO: parameterise this
            e.borderColor = "yellow"
            e.textColor = "yellow"
            e.start = d
            e.end = d
            e.save()
            e.url = reverse('transfer_create_with_event', args=(e.id,))
            e.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(transfer_schedule))
            else:
                return HttpResponseRedirect('/')
    else:
        form = mf.ScheduleTransferForm(initial={'date': date})
    return render_to_response('transfer_schedule.html', {
        'nav1': 'production',
        'nav2': inspect.stack()[0][3],
        'form': form}, context_instance=RequestContext(request))


@login_required
def transfer_delete(request, pk):

    transfer = get_object_or_404(mm.Transfer, id=pk)
    can_delete, message = transfer.can_delete()
    error = not can_delete
    if not can_delete:
        logger.info(
            "Unable to Delete Transfer: {}".format(message),
            extra={'request': request})
        return render(request, 'record_delete.html', {
            'record': transfer,
            'message': mark_safe(message),
            'error': error,
            'nav1': "production",
            'nav2': inspect.stack()[0][3]},
            context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
            try:
                transfer.delete(user=request.user)
                return HttpResponseRedirect(reverse('transfer_list'))
            except ProtectedError, e:
                error = True
                message = e
        logger.warning(
            "Unable to Delete Transfer: {}".format(message),
            extra={'request': request})
        return render(
            request, 'record_delete.html', {
                'record': transfer,
                'nav1': 'production',
                'nav2': inspect.stack()[0][3],
                'error': error,
                'message': mark_safe(message)},
            context_instance=RequestContext(request))


@login_required
def package_list(request):
    list_class = "Package"
    list_app = "main"
    table = mt.PackageListTable(mm.Package.objects.all())
    table.order_by = '-create_date'
    RequestConfig(request, paginate=False).configure(table)
    create = reverse(package)
    create_text = 'Create Package'
    return render(request, 'record_list.html', {
        'table': table,
        'nav1': 'production', 'nav2': inspect.stack()[0][3],
        'list_class': list_class, 'create': create,
        'list_app': list_app,
        'create_text': create_text,
        'pagination': mt.get_pagination()})


@login_required
def package(request, event, pk):
    if pk:
        edit = True
    else:
        edit = False
    if request.method == 'POST':
        form = mf.PackageForm(request.POST, edit_form=edit)
        if form.is_valid():
            bt = form.cleaned_data['bev_tank']
#            v = convert_to_base(float(form.cleaned_data['volume']),
#                                form.cleaned_data['volume_UOM'].mag_symbol,
#                                'volume')
            u = form.cleaned_data['item_count']
            d = form.cleaned_data['create_date']
            pt = form.cleaned_data['package_type']
            n = form.cleaned_data['notes']
            coi = form.cleaned_data['coi']
            if pt.volume:
                v = float(u) * pt.volume
            else:
                v = float(u)
            if pk:
                p = mm.Package.objects.get(pk=pk)
                bt = p.bev_tank
                old_empty_date = p.bev_tank.empty_date
            else:
                p = mm.Package()
                p.bev_tank = bt
            p.volume = v
            p.create_date = d
            p.package_type = pt
            p.notes = n
            # If we are editing a package that emptied the tank we must pass
            # the measurement through save() so we can ignore the waste in its
            # calculations for packagebevchunk volumes
            if pk and old_empty_date:
                mv = mm.Measurement.objects.get(
                    measurement_type__name='Volume', value=0.0,
                    measurement_date=old_empty_date,
                    bev_tank=bt)
            else:
                mv = None
            p.save(measurement=mv, user=request.user)

            # Check out if settings say submit stock on hand
            if mm.Setting.objects.get(
                site__id=settings.SITE_ID).submit_stock_on_hand:
                coi = True
            # Check out if form field true
            if coi:
                co = mm.CheckOut(package=p, create_date=d, volume=v)
                co.save()

            if form.cleaned_data['empty']:
                latest_date = mm.Package.objects.filter(
                    bev_tank=bt).aggregate(Max('create_date'))
                bt.empty_date = latest_date['create_date__max']
                bt.save()

                if pk and old_empty_date:
                    mv = mm.Measurement.objects.get(
                        measurement_type__name='Volume', value=0.0,
                        measurement_date=old_empty_date,
                        bev_tank=bt)
                    if not old_empty_date == latest_date['create_date__max']:
                        mv.measurement_date = latest_date['create_date__max']
                        mv.save()
                    # Add the waste bev chunk(s)
                    for bc in bt.get_bev_chunks():
                        try:
                            wbc = mm.WasteBevChunk.objects.get(measurement=mv,
                                bev_chunk=bc)
                        except mm.WasteBevChunk.DoesNotExist:
                            wbc = mm.WasteBevChunk()
                            wbc.measurement = mv
                            wbc.bev_chunk = bc
                        wbc.volume = bc.get_volume(mv.measurement_date,
                            measurement=mv)
                        wbc.save()
                else:
                    mv = mm.Measurement()
                    mv.measurement_type = mm.MeasurementType.objects.get(
                        name='Volume')
                    mv.bev_tank = bt
                    mv.measurement_date = latest_date['create_date__max']
                    mv.value = 0.0
                    mv.save()
                    # Add the waste bev chunk(s)
                    for bc in bt.get_bev_chunks():
                        wbc = mm.WasteBevChunk()
                        wbc.measurement = mv
                        wbc.bev_chunk = bc
                        wbc.volume = bc.get_volume(
                            mv.measurement_date)
                        wbc.save()
            else:
                if pk:
                    p.bev_tank.empty_date = None
                    p.bev_tank.save()
                    mvs = mm.Measurement.objects.filter(bev_tank=bt,
                        measurement_date=old_empty_date,
                        measurement_type__name='Volume', value=0.0)
                    for mv in mvs:
                        mv.delete()  # will delete waste bev chunks too

            if pk:
                e = mm.Event.objects.get(event_type__name="Package",
                                   record_id=pk)
            else:
                e = mm.Event()
                e.title = 'Package: ' + str(bt.product_type)
                e.event_type = mm.EventType.objects.get(name="Package")
                e.url = '/package/' + str(p.id)
                e.editable = False
                e.color = "maroon"  # TODO: parameterise this
                e.record_id = p.id
            e.start = d
            e.end = d
            e.save()

            if event:
                se = mm.Event.objects.get(pk=event)
                se.delete()  # delete scheduled event now it has been completed

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(package))
            else:
                return HttpResponseRedirect(reverse(package_list))
    else:
        if event:
            e = mm.Event.objects.get(pk=event)
            date = e.start.astimezone(pytz.timezone(settings.TIME_ZONE))
            form = mf.PackageForm(initial={'create_date': date,
                                           'bev_tank': e.bev_tank})
        else:
            if pk:
                p = get_object_or_404(mm.Package, pk=pk)
                coqs = mm.CheckOut.objects.filter(package=p)
                if coqs:
                    error = ''
                    costr = ''
                    for co in coqs:
                        costr += str(co) + ' '
                        error += (str(p) + ''' has been checked out.
                            If you wish to edit it,
                            delete the following first: ''' + costr)
                    logger.info(
                        "Unable to Edit Package: {}".format(error),
                        extra={'request': request})
                    return render(request, 'record_edit_error.html',
                        {'nav1': 'production', 'nav2': inspect.stack()[0][3],
                        'record': p, 'error': error},
                        context_instance=RequestContext(request))
                data = {'create_date': p.create_date,
                        'bev_tank': p.bev_tank,
                        'empty': p.get_src_empty(),
                        'package_type': p.package_type,
                        'item_count': p.item_count,
                        'notes': p.notes}
                form = mf.PackageForm(edit_form=edit, initial=data)
            else:
                form = mf.PackageForm(edit_form=edit)
    return render_to_response('package.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3],
        'form': form}, context_instance=RequestContext(request))


@login_required
def package_detail(request, pk):
    package = get_object_or_404(mm.Package, id=pk)
    alcohol = package.bev_tank.get_alcohol(package.create_date)

    return render(request, 'package_detail.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'package': package, 'alcohol': alcohol})


@login_required
def package_schedule(request, date):
    if request.method == 'POST':
        form = mf.SchedulePackageForm(request.POST)
        if form.is_valid():
            bev_tank = form.cleaned_data['bev_tank']
            d = form.cleaned_data['date']

            e = mm.Event()
            e.title = 'Package: ' + str(bev_tank.name) + \
                ' (' + str(bev_tank.tank) + ')'
            e.event_type = mm.EventType.objects.get(name="Package")
            e.bev_tank = bev_tank
            e.editable = True
            e.scheduled = True
            e.start = d
            e.end = d
            e.save()
            e.url = reverse('package_create', args=(e.id,))
            e.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(package_schedule))
            else:
                return HttpResponseRedirect('/')
    else:
        form = mf.SchedulePackageForm(initial={'date': date})
    return render_to_response('package_schedule.html', {
        'nav1': 'production',
        'nav2': inspect.stack()[0][3],
        'form': form}, context_instance=RequestContext(request))


@login_required
def package_delete(request, pk):
    package = get_object_or_404(mm.Package, id=pk)
    can_delete, message = package.can_delete()
    error = not can_delete
    if not can_delete:
        logger.info(
            "Unable to Delete Package: {}".format(message),
            extra={'request': request})
        return render(request, 'record_delete.html', {
            'record': package,
            'message': mark_safe(message),
            'error': error,
            'nav1': "production",
            'nav2': inspect.stack()[0][3]},
            context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
            try:
                package.delete(user=request.user)
                return HttpResponseRedirect(reverse('package_list'))
            except ProtectedError, e:
                message = e
                error = True
            logger.warning(
                "Unable to Delete Package: {}".format(message),
                extra={'request': request})
        return render(
            request, 'record_delete.html', {
                'record': package,
                'nav1': 'production',
                'nav2': inspect.stack()[0][3],
                'message': mark_safe(message),
                'error': error},
            context_instance=RequestContext(request))


@login_required
def checkout_list(request):
    list_class = "Checkout"
    list_app = "main"
    table = mt.CheckoutListTable(mm.CheckOut.objects.all())
    table.order_by = '-create_date'
    RequestConfig(request, paginate=False).configure(table)
    create = reverse(checkout_create)
    create_text = 'Create Checkout'
    return render(request, 'record_list.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'table': table,
        'list_class': list_class, 'create': create,
        'list_app': list_app,
        'create_text': create_text,
        'pagination': mt.get_pagination()})


@login_required
def checkout_create(request, pk):
    if pk:
        edit = True
        instance = get_object_or_404(mm.CheckOut, pk=pk)
    else:
        edit = False
        instance = None
    if request.method == 'POST':
        form = mf.CreateCheckOutForm(
            request.POST, edit_form=edit, instance=instance)
        if form.is_valid():
            p = form.cleaned_data['package']
#            v = convert_to_base(float(form.cleaned_data['volume']),
#                                form.cleaned_data['volume_UOM'].mag_symbol,
#                                'volume')
#             v = form.cleaned_data['volume']
            u = form.cleaned_data['item_count']
            d = form.cleaned_data['create_date']
            e = form.cleaned_data['exempt']
            n = form.cleaned_data['notes']
            if p.package_type.volume:
                v = float(u) * p.package_type.volume
            else:
                v = float(u)
            if pk:
                co = mm.CheckOut.objects.get(pk=pk)
            else:
                co = mm.CheckOut()
            co.package = p
            co.volume = v
            co.create_date = d
            co.exempt = e
            co.notes = n
            co.save()

            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse(checkout_create))
            else:
                return HttpResponseRedirect(reverse(checkout_list))
    else:
        if pk:
            co = mm.CheckOut.objects.get(pk=pk)
            sqs = mm.Submission.objects.filter(checkout=co)
            if sqs:
                error = ''
                sstr = ''
                for s in sqs:
                    sstr += str(s) + ' '
                error += (str(co) + ' was submitted in period ' +
                    sstr + '. Unable to edit.')
                
                logger.info(
                    "Unable to Edit CheckOut: {}".format(error),
                    extra={'request': request})
                return render(request, 'record_edit_error.html',
                    {'nav1': 'production', 'nav2': inspect.stack()[0][3],
                    'record': co, 'error': error},
                    context_instance=RequestContext(request))
            form = mf.CreateCheckOutForm(edit_form=edit, instance=instance)
        else:
            form = mf.CreateCheckOutForm(edit_form=edit, instance=instance)
    return render_to_response('checkout_create.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3],
        'form': form}, context_instance=RequestContext(request))


@login_required
def checkout_detail(request, pk):
    checkout = get_object_or_404(mm.CheckOut, id=pk)
    alcohol = checkout.package.bev_tank.get_alcohol(
        checkout.package.create_date)

    return render(request, 'checkout_detail.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'checkout': checkout,
        'alcohol': alcohol})


@login_required
def checkout_delete(request, pk):
    checkout = get_object_or_404(mm.CheckOut, id=pk)
    message = ''
    error = False
    sqs = mm.Submission.objects.filter(checkout=checkout)
    if sqs:
        error = True
        sstr = ''
        for s in sqs:
            sstr += str(s) + ' '
        message += (
            str(checkout) + ' was submitted in period ' + sstr +
            '. Unable to delete.')
    if error:
        return render(request, 'record_delete.html', {
            'nav1': 'production',
            'nav2': inspect.stack()[0][3],
            'record': checkout, 'message': mark_safe(message),
            'error': error},
            context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
            try:
                checkout.delete()
                return HttpResponseRedirect(reverse('checkout_list'))
            except ProtectedError, e:
                error = True
                message = e
        return render(request, 'record_delete.html', {
            'nav1': 'production',
            'nav2': inspect.stack()[0][3], 'record': checkout,
            'error': error, 'message': mark_safe(message)},
            context_instance=RequestContext(request))


@login_required
def checkout_report(request, pk):
    if pk:
        return render(
            request, 'product_checkout_report.html',
            {'nav1': 'reports', 'nav2': inspect.stack()[0][3], 'pk': pk})
    else:
        return render(
            request, 'checkout_report.html', {
                'nav1': 'reports',
                'nav2': inspect.stack()[0][3]})


@login_required
def stock_report(request):
    list_class = 'Package'
    list_app = "main"
    headers = [
        'package_type', 'product_type', 'package_type_volume',
        'package_volume', 'checked_out_volume']
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('''select pt.name, prt.name, pt.volume, pvol, t2.cvol from (select p.package_type_id, b.product_type_id, sum(p.volume) as pvol from main_package p left join main_bevtank b on b.id = p.bev_tank_id group by p.package_type_id, b.product_type_id) as t1 left join (select p.package_type_id, b.product_type_id, sum(c.volume) as cvol from main_package p left join main_bevtank b on b.id = p.bev_tank_id left join main_checkout c on p.id = c.package_id group by p.package_type_id, b.product_type_id ) as t2 on t2.package_type_id = t1.package_type_id and t1.product_type_id = t2.product_type_id left join main_packagetype pt on pt.id = t1.package_type_id left join main_producttype prt on prt.id = t1.product_type_id where t2.cvol is null or t2.cvol < t1.pvol''')
    pqs = cursor.fetchall()
    data = [dict(zip(headers, row)) for row in pqs]
    table = mt.CheckoutReportTable(data)
    table.order_by = ()
    RequestConfig(request, paginate=False).configure(table)
    return render(request, 'record_list.html', {
        'nav1': 'reports',
        'nav2': inspect.stack()[0][3], 'table': table,
        'list_class': list_class,
        'list_app': list_app,
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def measurement_list(request):
    list_class = "Measurement"
    list_app = "main"
    table = mt.MeasurementListTable(
        mm.Measurement.objects.filter(user__isnull=False))
    table.order_by = '-measurement_date'
    RequestConfig(request, paginate=False).configure(table)
    create = reverse(measurement)
    create_text = 'Create Measurement'
    return render(request, 'record_list.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'table': table,
        'list_class': list_class, 'create': create,
        'list_app': list_app,
        'create_text': create_text,
        'pagination': mt.get_pagination()})


@login_required
def measurement(request, pk, bev_tank):
    if pk:
        edit = True
        instance = get_object_or_404(mm.Measurement, pk=pk)
        message = ''
        error = False
        m = mm.Measurement.objects.get(pk=pk)
        tqs = mm.Transfer.objects.filter(
            bevchunk__src_tank=m.bev_tank,
            transfer_date__gte=m.measurement_date)
        if tqs:
            tstr = ''
            for t in tqs:
                if tstr:
                    tstr += ', '
                tstr += str(t)
            if tqs.count() == 1:
                p = 'Transfer'
                t = 'this'
                i = 'includes'
            else:
                p = 'Transfers'
                t = 'these'
                i = 'include'

            error = True
            message += (
                p + ' ' + tstr + ' ' + i + ' ' + str(m) +
                '.\nTry deleting ' + t + ' first.\n')

        pqs = mm.Package.objects.filter(bev_tank=m.bev_tank).filter(
            create_date__gte=m.measurement_date)
        if pqs:
            pstr = ''
            for p in pqs:
                if pstr:
                    pstr += ', '
                pstr += str(p)
            if pqs.count() == 1:
                p = 'Package'
                t = 'this'
                i = 'includes'
            else:
                p = 'Packages'
                t = 'these'
                i = 'include'

            error = True
            message += (
                p + ' ' + pstr + ' ' + i + ' ' + str(measurement) +
                '.\nTry deleting ' + t + ' first.\n')
        if error:
            return render(request, 'record_delete.html', {
                'nav1': 'production', 'nav2': inspect.stack()[0][3],
                'record': m, 'error': error, 'message': mark_safe(message)},
                context_instance=RequestContext(request))
    else:
        edit = False
        instance = None
    if request.method == 'POST':
        form = mf.MeasurementForm(
            request.POST, edit_form=edit, instance=instance)
        if form.is_valid():
            bt = form.cleaned_data['bev_tank']
            d = form.cleaned_data['measurement_date']
            t = form.cleaned_data['measurement_type']
            v = form.cleaned_data['value']
#            u = form.cleaned_data['uom']

            if pk:
                m = mm.Measurement.objects.get(pk=pk)
            else:
                m = mm.Measurement()
                m.measurement_type = t
                m.bev_tank = bt
                m.measurement_date = d
                m.parent = None
#           m.value = convert_to_base(float(v), u.mag_symbol, u.type.type)
            m.value = v
            m.user = request.user
            if (
                m.measurement_type == mm.MeasurementType.objects.
                    get(name='Density')):
                m.save()
                m.calculate_alcohol(m.measurement_date)
                # Adjust any child densities e.g. on a tank transferred to
                dms = mm.Measurement.objects.filter(
                    measurement_type__name='Density', parent=m)
                for dm in dms:
                    dm.value = m.value
                    dm.save()
                    dm.calculate_alcohol(dm.measurement_date)
            elif (
                m.measurement_type == mm.MeasurementType.objects.
                    get(name='Volume')):
                for bc in m.bev_tank.get_bev_chunks():
                    if pk:
                        wbc = mm.WasteBevChunk.objects.get(
                            bev_chunk=bc, measurement=m)
                        # wbc.delete()
                    else:
                        wbc = mm.WasteBevChunk()
                        wbc.volume = 0
                    wbc.bev_chunk = bc
                    bc_vol = bc.get_volume(m.measurement_date)
                    bc_prop = bc.get_proportion(m.measurement_date)
                    wbc.volume += bc_vol - (float(m.value) * bc_prop)
                    m.save()
                    wbc.measurement = m
                    wbc.save()
            else:
                m.save()
            if 'Repeat' in request.POST:
                return HttpResponseRedirect(reverse('measurement'))
            else:
                return HttpResponseRedirect(reverse('measurement_list'))
    else:
        initial = {}
        if bev_tank:
            bt = mm.BevTank.objects.get(pk=bev_tank)
            initial['bev_tank'] = bt
        form = mf.MeasurementForm(
            edit_form=edit, instance=instance,
            initial=initial)
    return render_to_response('measurement_create.html', {
        'nav1': 'production',
        'nav2': inspect.stack()[0][3],
        'form': form}, context_instance=RequestContext(request))


@login_required
def measurement_detail(request, pk):
    measurement = get_object_or_404(mm.Measurement, id=pk)

    return render(request, 'measurement_detail.html', {
        'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'measurement': measurement})


@login_required
def measurement_delete(request, pk):
    measurement = get_object_or_404(mm.Measurement, id=pk)
    message = ''
    error = False
    tqs = mm.Transfer.objects.filter(
        bevchunk__src_tank=measurement.bev_tank,
        transfer_date__gte=measurement.measurement_date)
    if tqs:
        tstr = ''
        for t in tqs:
            if tstr:
                tstr += ', '
            tstr += str(t)
        if tqs.count() == 1:
            p = 'Transfer'
            t = 'this'
            i = 'includes'
        else:
            p = 'Transfers'
            t = 'these'
            i = 'include'

        error = True
        message += (
            p + ' ' + tstr + ' ' + i + ' ' + str(measurement) +
            '.\nTry deleting ' + t + ' first.\n')

    pqs = mm.Package.objects.filter(bev_tank=measurement.bev_tank).filter(
        create_date__gte=measurement.measurement_date)
    if pqs:
        pstr = ''
        for p in pqs:
            if pstr:
                pstr += ', '
            pstr += str(p)
        if pqs.count() == 1:
            p = 'Package'
            t = 'this'
            i = 'includes'
        else:
            p = 'Packages'
            t = 'these'
            i = 'include'

        error = True
        message += (
            p + ' ' + pstr + ' ' + i + ' ' + str(measurement) +
            '.\nTry deleting ' + t + ' first.\n')
    if error:
        return render(request, 'record_delete.html', {
            'nav1': 'production',
            'nav2': inspect.stack()[0][3], 'record': measurement,
            'error': error, 'message': mark_safe(message)},
            context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
            try:
                ms = mm.Measurement.objects.filter(
                    bev_tank=measurement.bev_tank, parent=measurement)
                for m in ms:
                    m.delete()
                measurement.delete()
                return HttpResponseRedirect(reverse('measurement_list'))
            except ProtectedError, e:
                message = e
                error = True
        return render(request, 'record_delete.html', {
            'nav1': 'production',
            'nav2': inspect.stack()[0][3], 'record': measurement,
            'error': error, 'message': mark_safe(message)},
            context_instance=RequestContext(request))


@login_required
def bev_tank_detail(request, pk):
    bev_tank = get_object_or_404(mm.BevTank, id=pk)
    return render(request, 'bev_tank_detail.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'bev_tank': bev_tank})


@login_required
def bev_tank_status_edit(request, pk):
    bev_tank = get_object_or_404(mm.BevTank, id=pk)
    if request.method == 'POST':
        form = mf.BevTankStatusEditForm(request.POST)
        if form.is_valid():
            bev_tank.status = form.cleaned_data['status']
            bev_tank.save()

            return HttpResponseRedirect('/')
    else:
        form = mf.BevTankStatusEditForm(instance=bev_tank)

    return render(request, 'bev_tank_status_edit.html', {'nav1': 'production',
        'nav2': inspect.stack()[0][3], 'form': form})


@class_view_decorator(login_required)
class BevTankStatusListView(ListView):
    model = mm.BevTankStatus

    def render_to_response(self, context, **response_kwargs):
        """
        convert to JSON response
        """
        json = serializers.serialize('json', self.get_queryset(),
            fields=('description',))
        return HttpResponse(json, mimetype="application/json")


@login_required
def bev_tank_list(request):

    base_vol_unit = mm.Unit.objects.get(
        pk=settings.BASE_UNIT.get(settings.VOLUME_UNIT_TYPE))
    default_vol_unit = mm.Unit.objects.filter(
        type=settings.VOLUME_UNIT_TYPE).get(default=True)

    btqs = mm.BevTank.objects.select_related().filter(hide=False).filter(
        (Q(empty_date__gt=date.today()) |
                                  Q(empty_date__isnull=True)) &
                                  Q(fill_date__lte=date.today()))
    tqs = btqs.distinct('tank')

    tanklist = []
    for row in tqs:
        tanklist.append(row.tank)

    alltqs = mm.Tank.objects.select_related().filter(active=True, hide=False)

    alltanklist = []
    for row in alltqs:
        alltanklist.append(row)

    missingtanklist = list(set(alltanklist) - set(tanklist))

    btlist = []

    for row in missingtanklist:
        trow = {}
        trow['id'] = None
        trow['tank'] = row.name
        trow['name'] = None
        trow['product_type'] = None
        trow['status'] = mark_safe('''<div class="cell-text">{}</div>
            <div class="cell-icons">
            <a title="Wash this Tank" class="tbl_icon wash">
            <span class="ui-icon ui-icon-gear">
            </span></a>'''.format(row.tank_status))
        trow['fill_date'] = None
        trow['original_volume'] = None
        trow['transferred_volume'] = None
        trow['packaged_volume'] = None
        trow['waste_volume'] = None
        trow['waste_percentage'] = None
        trow['volume'] = None
        trow['position'] = row.position
        btlist.append(trow)

    for row in btqs:
        btrow = {}
        btrow['id'] = row.id
        btrow['tank'] = row.tank.name
        btrow['name'] = row.name
        btrow['product_type'] = row.product_type
        btrow['status'] = row.status.description
        btrow['fill_date'] = row.fill_date
        btrow['original_volume'] = (Decimal(mt.convert_to_default(
            row.get_original_volume(), base_vol_unit, default_vol_unit)).
            quantize(Decimal('0.1')))
        btrow['transferred_volume'] = (Decimal(mt.convert_to_default(
            row.get_transferred_volume_today(), base_vol_unit,
            default_vol_unit)).quantize(Decimal('0.1')))
        btrow['packaged_volume'] = (Decimal(mt.convert_to_default(
            row.get_packaged_volume_today(), base_vol_unit, default_vol_unit)).
            quantize(Decimal('0.1')))
        btrow['waste_volume'] = (Decimal(mt.convert_to_default(
            row.get_waste_volume_today(), base_vol_unit, default_vol_unit)).
            quantize(Decimal('0.1')))
        btrow['waste_percentage'] = (Decimal(row.get_waste_percentage_today()).
            quantize(Decimal('0.1')))
        btrow['volume'] = (
            Decimal(mt.convert_to_default(row.get_volume_today(),
            base_vol_unit, default_vol_unit)).quantize(Decimal('0.1')))
        btrow['position'] = row.tank.position

        btlist.append(btrow)

    table = mt.BevTankTable(btlist)
    table.order_by = 'position'
    table.exclude = 'position'
    list_class = "Current Tank"
    RequestConfig(request, paginate=False).configure(table)
    return render(request, 'bevtank_list.html', {'nav1': 'reports',
        'nav2': inspect.stack()[0][3], 'table': table,
        'list_class': list_class,
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def main_settings(request):
    instance = mm.Setting.objects.get(site=get_current_site(request))
    company = mm.Company.objects.get(site=get_current_site(request))
    submission_company = mm.SubmissionCompany.objects.get(company=company)
    from orders.models import Address
    AddressForm = modelform_factory(Address, exclude=('attention', 'note'))
    if request.method == 'POST':
        form = mf.SettingsForm(request.POST, instance=instance)
        form2 = AddressForm(request.POST, instance=company.invoice_address)
        if form.is_valid() and form2.is_valid():
            instance.save()
            address = form2.save()
            company.invoice_address = address
            company.email = form.cleaned_data['email']
            company.name = form.cleaned_data['cca_name']
            submission_company.cca_code = form.cleaned_data['cca_code']
            submission_company.licensee = form.cleaned_data['licensee_name']
            submission_company.licensee_code = \
                form.cleaned_data['licensee_code']
            company.save()
            submission_company.save()
            return HttpResponseRedirect('/')
    else:
        data = {
            'cca_name': company.name,
            'cca_code': submission_company.cca_code,
            'licensee_name': submission_company.licensee,
            'licensee_code': submission_company.licensee_code,
            'email': company.email
        }
        form = mf.SettingsForm(instance=instance, initial=data)
        form2 = AddressForm(instance=company.invoice_address)
    return render(request, 'settings.html', {'nav1': 'admin',
        'nav2': inspect.stack()[0][3], 'form': form, 'form2': form2})


@login_required
def support(request):
    return render(request, 'support.html', {'nav1': 'support',
        'nav2': inspect.stack()[0][3]})


@login_required
def submission_list(request):
    list_class = "Submission"
    submissions = mm.Submission.objects.all().annotate(
        total_vol=Sum('checkout__volume'))
    table = mt.SubmissionListTable(submissions)
    table.order_by = ('-end_date',)
    table.exclude = ('submit_date',)
    RequestConfig(request, paginate=False).configure(table)
    records = mm.Submission.objects.all()
    create = reverse(submission_create)
    create_text = 'Create Submission'
    return render(request, 'record_list.html', {'nav1': 'customs',
        'nav2': inspect.stack()[0][3],
        'table': table, 'list_class': list_class, 'records': records,
        'create': create, 'create_text': create_text,
        'pagination': mt.get_pagination()})


@login_required
def submission_create(request):

    def first_day_of_month(d):
        return date(d.year, d.month, 1)

    if request.method == 'POST':
        form = mf.SubmissionCreateForm(request.POST)
        if form.is_valid():
            sd = form.cleaned_data['start_date']
            ed = form.cleaned_data['end_date']

            return HttpResponseRedirect('/submission/create/%s/%s' % (sd, ed))
    else:
        last_submission = mm.Submission.objects.aggregate(
            Max('end_date')).get('end_date__max')
        if last_submission:
            start = date.strftime(last_submission + timedelta(days=1),
                '%d/%m/%Y')
            period = mm.Setting.objects.get(
                site_id=settings.SITE_ID).submission_frequency.value
            # cludgy but it works. Gets last day of month for the
            # submission period specified in settings
            end = date.strftime(first_day_of_month(last_submission +
                timedelta(days=period * 32)) - timedelta(days=1), '%d/%m/%Y')
        else:
            start = None
            end = None
        form = mf.SubmissionCreateForm(initial={'start_date': start,
            'end_date': end})

    return render(request, 'submission_create.html', {'nav1': 'customs',
        'nav2': inspect.stack()[0][3], 'form': form})


@login_required
def submission_complete(request, start, end):
    sd = datetime.strptime(start, '%Y-%m-%d')
    ed = datetime.strptime(end, '%Y-%m-%d')
    periodqs = mm.CheckOut.objects.filter(create_date__lte=ed,
        create_date__gte=sd, submission__isnull=True)
    overdueqs = mm.CheckOut.objects.filter(create_date__lt=sd,
        submission__isnull=True)
    totalqs = periodqs | overdueqs
    drqs = sm.DutyCredit.objects.filter(submission=None)

    if request.method == 'POST':
        form = mf.SubmissionCompleteForm(request.POST)
        if form.is_valid():
            s = mm.Submission()
            s.start_date = sd
            s.end_date = ed
            s.submit_date = date.today()
            s.notes = form.cleaned_data['notes']
            s.save()

            for dr in drqs:
                dr.submission = s
                dr.save()

            for co in totalqs:
                co.submission = s
                co.save()

            return HttpResponseRedirect('/submission/' + str(s.id) + '/')
    else:
        form = mf.SubmissionCompleteForm()
        form.fields['start_date'].initial = sd
        form.fields['end_date'].initial = ed

        submissionqs = (
            totalqs.filter(exempt=False).
            values('package__bev_tank__product_type__name',
                'package__bev_tank__product_type__id').
            annotate(total=Sum('volume')))

        table = mt.SubmissionCheckoutTable(overdueqs)
        table.order_by = ('create_date',)
        RequestConfig(request, paginate=False).configure(table)
        table2 = mt.SubmissionCheckoutTable(periodqs)
        table2.order_by = ('create_date',)
        RequestConfig(request, paginate=False).configure(table2)
        table3 = mt.SubmissionTable(submissionqs, url=request.path_info)
        table3.order_by = ('package__bev_tank__product_type__name',)
        RequestConfig(request, paginate=False).configure(table3)

        return render(request, 'submission_complete.html', {'nav1': 'customs',
            'nav2': inspect.stack()[0][3], 'form': form, 'table': table,
            'table2': table2, 'table3': table3, 'start': sd, 'end': ed,
            'pagination': mt.get_pagination(unlimited=True)})


@login_required
def submission_detail(request, submission):
    s = mm.Submission.objects.get(pk=submission)
    submissionqs = (mm.CheckOut.objects.filter(submission=s.id, exempt=False).
        values('package__bev_tank__product_type__name',
            'package__bev_tank__product_type__id', 'submission').
        annotate(total=Sum('volume')))
    table = mt.SubmissionDetailTable(submissionqs)
    RequestConfig(request, paginate=False).configure(table)

    return render(request, 'submission_detail.html', {'nav1': 'customs',
        'nav2': inspect.stack()[0][3], 'submission': s, 'table': table,
        'pagination': mt.get_pagination(unlimited=True)})


@login_required
def submission_download(request, submission):
    s = get_object_or_404(mm.Submission, pk=submission)
    return wrv.write_submission(s)


@login_required
def credit_edit(request, pk, pt):
    next_page = request.GET.get('next', '/')
    if pk:
        instance = get_object_or_404(sm.DutyCredit, pk=pk)
    else:
        instance = None

    if request.method == 'POST':
        form = mf.CreditEditForm(request.POST, instance=instance)
        if form.is_valid():
            c = form.cleaned_data['credit']
            if pk:
                dc = sm.DutyCredit.objects.get(pk=pk)
            else:
                dc = sm.DutyCredit()
            dc.credit = c
            dc.product_type = mm.ProductType.objects.get(pk=pt)
            dc.save()

            return HttpResponseRedirect(next_page)
    else:
        if pk:
            form = mf.CreditEditForm(instance=instance)
        else:
            form = mf.CreditEditForm()
    return render_to_response(
        'credit_edit.html', {
            'nav1': 'customs',
            'nav2': inspect.stack()[0][3],
            'form': form, 'next': next_page},
        context_instance=RequestContext(request))


def return_bev_tank(b, d, dt, n, pt, s):
        bt = mm.BevTank()
        if not b:
            bt.emptyDate = None
            bt.fill_date = d
            bt.tank = dt
#             bt.name = n
            bt.status = s
        else:
            bt = b
#             bt.name += '+' + n
        bt.product_type = pt
        bt.save()
        return bt


def get_next_batch_number(bt):
    if mm.Setting.objects.get().batch_numbering.name == 'Global':
        qs = mm.Brew.objects.all()
    else:
        qs = mm.Brew.objects.all().filter(bev_type=bt)
    mx = qs.aggregate(Max('batch_no'))['batch_no__max']
    if not(mx):
        if mm.Setting.objects.get().batch_numbering.name == 'Global':
            return 1
        else:
            if bt.initial:
                return bt.initial
            else:
                return 1
    else:
        return mx + 1


# DEPENDENT DROP DOWN
@login_required
def all_json_blend_tanks(request, tank):
    current_tank = mm.Tank.objects.get(id=tank)
    blend_tanks = (mm.BevTank.objects.filter(tank=current_tank).
                   filter(empty_date__isnull=True))
    json_blend_tanks = serializers.serialize("json", blend_tanks)
    return HttpResponse(json_blend_tanks, mimetype="application/javascript")


# DEPENDENT DROP DOWN
@login_required
def all_json_product_types_bev_type(request, bt):
    bev_type = mm.BevType.objects.get(id=bt)
    product_bev_types = mm.ProductType.objects.filter(
        productbevtype__bev_type=bev_type)
    json_product_types = serializers.serialize(
        "json", product_bev_types)
    return HttpResponse(json_product_types, mimetype="application/javascript")


# DEPENDENT DROP DOWN
@login_required
def all_json_product_types_bev_tank(request, bt):
    bev_tank = mm.BevTank.objects.get(id=bt)
    product_type = mm.ProductType.objects.filter(id=bev_tank.product_type.id)
    json_product_type = serializers.serialize("json", product_type)
    return HttpResponse(json_product_type, mimetype="application/javascript")


# DEPENDENT DROP DOWN
@login_required
def initial_json_status(request, bt):
    bev_tank = mm.BevTank.objects.get(id=bt)
    status = mm.BevTankStatus.objects.filter(id=bev_tank.status.id)
    json_status = serializers.serialize("json", status)
    return HttpResponse(json_status, mimetype="application/javascript")


# DEPENDENT DROP DOWN
@login_required
def json_units(request, pk):
    unit_type = mm.MeasurementType.objects.get(id=pk).unit_type
    units = mm.Unit.objects.filter(type=unit_type).order_by('-default')
    json_status = serializers.serialize("json", units)
    return HttpResponse(json_status, mimetype="application/javascript")


# CALENDAR EVENTS
@login_required
def calendar_event_feed(request):
    localtz = pytz.timezone(settings.TIME_ZONE)
    try:
        start = localtz.localize(
            datetime.fromtimestamp(float(request.GET.get('start'))))
        end = localtz.localize(
            datetime.fromtimestamp(float(request.GET.get('end'))))
    except:
        raise Http404
    events = (mm.Event.objects.filter(start__lte=end).filter(end__gte=start).
        values('id', 'title', 'event_type', 'bev_type', 'bev_tank',
        'dest_tank', 'start', 'event_type__borderColor',
        'event_type__backgroundColor', 'event_type__textColor',
        'editable', 'url', 'scheduled'))
    for event in events:
        event['backgroundColor'] = event['event_type__backgroundColor']
        event['textColor'] = event['event_type__textColor']
        event['borderColor'] = event['event_type__backgroundColor']

    json_events = json.dumps(list(events), cls=DjangoJSONEncoder)
    # remove the prefix for the related fields for fullCalendar
    #json_events = json_events.replace('event_type__', '')
    return HttpResponse(json_events, mimetype="application/javascript")


# CHECKOUT GRAPH DATA
@login_required
def checkout_graph_feed(request, pk):
    if pk:
        coqs1 = (mm.CheckOut.objects.filter(
            package__bev_tank__product_type__id=pk).extra(
            select={'create_month':
            "EXTRACT(MONTH FROM main_checkout.create_date)"}).extra(
            select={'create_year':
            "EXTRACT(YEAR FROM main_checkout.create_date)"}).values(
            'create_month', 'create_year',
            'package__package_type__name'))
        coqs2 = coqs1.annotate(total=Sum(
            'volume')).order_by('package__package_type__name')
        pqs = (coqs2.values('package__package_type__name').order_by(
            'package__package_type__name'))
        dcoqs = coqs2.values('create_year', 'create_month').order_by(
            'create_year', 'create_month')
        # Make distinct on month
        prev = None
        distinct_months = []
        for d in dcoqs:
            if prev:
                if not (d['create_year'] == prev['create_year'] and
                    d['create_month'] == prev['create_month']):
                    distinct_months.append(d)
            else:
                distinct_months.append(d)
            prev = d

        checkout_data = []
        label_data = []
        for row in pqs:
            label = []
            label.append(row['package__package_type__name'])
            label_data.append(label)
        checkout_data.append(label_data)
        volumes = []
        for row in pqs:
            package_data = []
            package = row['package__package_type__name']
            pcoqs = coqs2.filter(package__package_type__name=package)
            for d in distinct_months:
                data = []
                time = mktime((int(d['create_year']),
                    int(d['create_month']), 1, 0, 0, 0, 0, 0, 0)) * 1000
                vol = 0
                for row in pcoqs:
                    if (d['create_year'] == row['create_year'] and
                        d['create_month'] == row['create_month']):
                        vol = row['total']
                        break
                data.append(time)
                data.append(vol)
                package_data.append(data)
            volumes.append(package_data)
        checkout_data.append(volumes)

        return HttpResponse(json.dumps(checkout_data),
            mimetype="application/javascript")
    else:
        coqs1 = (mm.CheckOut.objects.all().extra(
            select={'create_month':
            "EXTRACT(MONTH FROM main_checkout.create_date)"}).extra(
            select={'create_year':
            "EXTRACT(YEAR FROM main_checkout.create_date)"}).values(
            'create_month', 'create_year',
            'package__bev_tank__product_type__name',
            'package__bev_tank__product_type__colour'))
        coqs2 = coqs1.annotate(total=Sum(
            'volume')).order_by('package__bev_tank__product_type__name')
        pqs = (coqs2.values('package__bev_tank__product_type__name',
            'package__bev_tank__product_type__colour',
            'package__bev_tank__product_type__id').order_by(
            'package__bev_tank__product_type__name'))
        dcoqs = coqs1.values('create_year', 'create_month').order_by(
            'create_year', 'create_month')
        # Make distinct on month
        prev = None
        distinct_months = []
        for d in dcoqs:
            if prev:
                if not (d['create_year'] == prev['create_year'] and
                    d['create_month'] == prev['create_month']):
                    distinct_months.append(d)
            else:
                distinct_months.append(d)
            prev = d

        checkout_data = []
        label_data = []
        for row in pqs:
            label = []
            label.append(row['package__bev_tank__product_type__name'])
            label_data.append(label)
        checkout_data.append(label_data)
        colour_data = []
        for row in pqs:
            colour = []
            colour.append(row['package__bev_tank__product_type__colour'])
            colour_data.append(colour)
        checkout_data.append(colour_data)
        ptid_data = []
        for row in pqs:
            ptid = []
            ptid.append(row['package__bev_tank__product_type__id'])
            ptid_data.append(ptid)
        checkout_data.append(ptid_data)
        volumes = []
        for row in pqs:
            product_data = []
            product = row['package__bev_tank__product_type__name']
            pcoqs = coqs2.filter(package__bev_tank__product_type__name=product)
            for d in distinct_months:
                data = []
                time = mktime((int(d['create_year']),
                    int(d['create_month']), 1, 0, 0, 0, 0, 0, 0)) * 1000
                vol = 0
                for row in pcoqs:
                    if (d['create_year'] == row['create_year'] and
                        d['create_month'] == row['create_month']):
                        vol = row['total']
                        break
                data.append(time)
                data.append(vol)
                product_data.append(data)
            volumes.append(product_data)
        checkout_data.append(volumes)

        return HttpResponse(json.dumps(checkout_data),
            mimetype="application/javascript")


# FERMENTATION GRAPH DATA
@login_required
def fermentation_graph_feed(request, bev_tank):

    fermentation_data = []
    stm = mm.MeasurementType.objects.get(name="Set Temperature")
    set_temp = mm.Measurement.objects.filter(bev_tank=bev_tank,
        measurement_type=stm)
    set_temp_data = []
    if set_temp.count() == 0:
        set_temp_data.append(None)
    else:
        for row in set_temp:
            data = []
            data.append(mktime(row.measurement_date.timetuple()) * 1000)
            data.append(row.value)
            set_temp_data.append(data)
    fermentation_data.append(set_temp_data)
    atm = mm.MeasurementType.objects.get(name="Actual Temperature")
    actual_temp = mm.Measurement.objects.filter(bev_tank=bev_tank,
        measurement_type=atm)
    actual_temp_data = []
    if actual_temp.count() == 0:
        actual_temp_data.append(None)
    else:
        for row in actual_temp:
            data = []
            data.append(mktime(row.measurement_date.timetuple()) * 1000)
            data.append(row.value)
            actual_temp_data.append(data)
    fermentation_data.append(actual_temp_data)
    dm = mm.MeasurementType.objects.get(name="Density")
    density = mm.Measurement.objects.filter(bev_tank=bev_tank,
        measurement_type=dm)
    density_data = []
    if density.count() == 0:
        density_data.append(None)
    else:
        for row in density:
            data = []
            data.append(mktime(row.measurement_date.timetuple()) * 1000)
            data.append(row.value)
            density_data.append(data)
    fermentation_data.append(density_data)

    return HttpResponse(json.dumps(fermentation_data),
                        mimetype="application/javascript")


# LIST ORDERING
@login_required
def list_order(request):
    if request.method == 'POST':
        list_class = get_model(request.POST['list_app'],
            request.POST['list_class'])
        order = request.POST['order'].split('&')
        for i, item in enumerate(order):
            pk = item.split('=')[1].strip()  # get the pk of the item
            if pk:
                record = list_class.objects.get(pk=int(pk))
                record.position = i
                record.save()
    return HttpResponseRedirect('/')

