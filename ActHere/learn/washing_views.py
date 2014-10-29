# coding: utf-8
import washing.models as wm
import washing.tables as wt
import washing.forms as wf
import main.models as mm
from main.tables import get_pagination
from django_tables2.views import SingleTableView
import inspect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, UpdateView, DeleteView,
    DetailView, ListView)
from django.views.generic.edit import ModelFormMixin
from django.core import serializers
from django.core.urlresolvers import reverse_lazy, reverse
from django.http.response import (HttpResponse, HttpResponseRedirect,
    HttpResponseServerError)
from django.db.models import Max
from django.utils import simplejson
import json
import pytz
from quickbev import settings
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist


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


@class_view_decorator(login_required)
class WashStepListView(SingleTableView):
    model = wm.WashStep
    table_class = wt.WashStepTable
    table_pagination = False
    template_name = 'record_list.html'

    def get_context_data(self, **kwargs):
        context = super(WashStepListView, self).get_context_data(**kwargs)
        context['list_class'] = 'WashStep'
        context['list_app'] = 'washing'
        context['create'] = reverse('washstep_create')
        context['create_text'] = 'Create Wash Step'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['pagination'] = get_pagination(unlimited=True)
        return context

    def get_queryset(self):
        qs = super(WashStepListView, self).get_queryset()
        qs = qs.filter(template=True).order_by('position')
        return qs


@class_view_decorator(login_required)
class WashStepCreateView(CreateView):
    form_class = wf.CreateWashStepForm
    model = wm.WashStep
    success_url = reverse_lazy('washstep_list')

    def get_context_data(self, **kwargs):
        context = super(WashStepCreateView, self).get_context_data(**kwargs)
        context['model_text'] = 'Wash Step'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['cancel_url'] = reverse('washstep_list')
        return context

    def form_valid(self, form):
        maxp = wm.WashType.objects.filter(
            template=True).aggregate(Max('position'))['position__max']
        if not maxp:
            maxp = 0
        form.instance.position = maxp + 1
        form.instance.template = True
        self.object = form.save()
        if 'Repeat' in self.request.POST:
            return HttpResponseRedirect(reverse('washstep_create'))
        else:
            return HttpResponseRedirect(self.success_url)


@class_view_decorator(login_required)
class WashStepUpdateView(UpdateView):
    form_class = wf.CreateWashStepForm
    model = wm.WashStep
    template_name = 'washing/washstep_form.html'
    success_url = reverse_lazy('washstep_list')

    def get_context_data(self, **kwargs):
        context = super(WashStepUpdateView, self).get_context_data(**kwargs)
        context['model_text'] = 'Wash Step'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['cancel_url'] = reverse('washstep_list')
        return context


@class_view_decorator(login_required)
class WashStepDetailView(DetailView):
    model = wm.WashStep
    slug_field = 'name'
    
    def get_object(self, queryset=None):
        """
        This is required 
        """
        if queryset is None:
            queryset = self.get_queryset()
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        if slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})
        # If none of those are defined, it's an error.
        else:
            raise AttributeError("Generic detail view %s must be called with "
                                 "a slug."
                                 % self.__class__.__name__)
        try:
            # We must only get where template=True as multiple will be returned
            obj = queryset.get(template=True)
        except ObjectDoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def render_to_response(self, context, **response_kwargs):
        json = serializers.serialize('json', [context['object']])
        return HttpResponse(json, mimetype="application/json")


@class_view_decorator(login_required)
class WashStepDeleteView(DeleteView):
    model = wm.WashStep
    template_name = 'record_delete.html'
    success_url = reverse_lazy('washstep_list')

    def get_context_data(self, **kwargs):
        context = super(WashStepDeleteView, self).get_context_data(**kwargs)
        context['model_text'] = 'Wash Step'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['cancel_url'] = reverse('washstep_list')
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        related = wm.WashType.objects.filter(
            washtypestep__wash_step=self.object).distinct(
            'washtypestep__wash_type')
        if related:
            error_text = '{} is used in the following Wash Types. Please delete these first:\n'.format(self.object)
            for o in related:
                error_text += '{}\n'.format(o)
            context['error'] = error_text
        return self.render_to_response(context)


@class_view_decorator(login_required)
class WashTypeListView(SingleTableView):
    model = wm.WashType
    table_class = wt.WashTypeTable
    table_pagination = False
    template_name = 'record_list.html'

    def get_context_data(self, **kwargs):
        context = super(WashTypeListView, self).get_context_data(**kwargs)
        context['list_class'] = 'WashType'
        context['list_app'] = 'washing'
        context['create'] = reverse('washtype_create')
        context['create_text'] = 'Create Wash Type'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['pagination'] = get_pagination(unlimited=True)
        return context

    def get_queryset(self):
        qs = super(WashTypeListView, self).get_queryset()
        qs = qs.filter(template=True).order_by('position')
        return qs


@class_view_decorator(login_required)
class WashTypeCreateView(CreateView):
    form_class = wf.CreateWashTypeForm
    model = wm.WashType
    template_name = 'washing/washstep_form.html'
    success_url = reverse_lazy('washtype_list')

    def get_context_data(self, **kwargs):
        context = super(WashTypeCreateView, self).get_context_data(**kwargs)
        context['model_text'] = 'Wash Type'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['cancel_url'] = reverse('washtype_list')
        return context

    def form_valid(self, form):
        # Determine the position of the new object
        maxp = wm.WashType.objects.filter(
            template=True).aggregate(Max('position'))['position__max']
        if not maxp:
            maxp = 0
        # Need to override this since there is an intermediary model
        self.object = form.save(commit=False)
        form.instance.position = maxp + 1
        form.instance.template = True
        self.object.save()
        for i, step in enumerate(form.cleaned_data['wash_steps_list']):
            ws = wm.WashStep.objects.get(pk=int(step))
            wts = wm.WashTypeStep()
            wts.wash_type = self.object
            wts.wash_step = ws
            wts.position = i
            wts.save()
        if 'Repeat' in self.request.POST:
            return HttpResponseRedirect(reverse('washtype_create'))
        else:
            return HttpResponseRedirect(self.success_url)


@class_view_decorator(login_required)
class WashTypeUpdateView(UpdateView):
    form_class = wf.CreateWashTypeForm
    model = wm.WashType
    template_name = 'washing/washstep_form.html'
    success_url = reverse_lazy('washtype_list')

    def get_context_data(self, **kwargs):
        context = super(WashTypeUpdateView, self).get_context_data(**kwargs)
        context['model_text'] = 'Wash Type'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['cancel_url'] = reverse('washtype_list')
        return context

    def form_valid(self, form):
        # Need to override this since there is an intermediary model
        self.object = form.save(commit=False)
        existing = wm.WashTypeStep.objects.filter(wash_type=self.object)
        for e in existing:
            e.delete()
        for i, step in enumerate(form.cleaned_data['wash_steps_list']):
            ws = wm.WashStep.objects.get(pk=int(step))
            wts = wm.WashTypeStep()
            wts.wash_type = self.object
            wts.wash_step = ws
            wts.position = i
            wts.save()
        return super(ModelFormMixin, self).form_valid(form)


@class_view_decorator(login_required)
class WashTypeDeleteView(DeleteView):
    model = wm.WashType
    template_name = 'record_delete.html'
    success_url = reverse_lazy('washtype_list')

    def get_context_data(self, **kwargs):
        context = super(WashTypeDeleteView, self).get_context_data(**kwargs)
        context['model_text'] = 'Wash Type'
        context['nav1'] = 'admin'
        context['nav2'] = type(self).__name__
        context['cancel_url'] = reverse('washtype_list')
        return context


@class_view_decorator(login_required)
class WashCreateView(CreateView):
    form_class = wf.CreateWashForm
    model = wm.Wash
    template_name = 'washing/washstep_form.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(WashCreateView, self).get_context_data(**kwargs)
        context['form'].fields['wash_type'].queryset = wm.WashType.objects.filter(
            template=True)
        return context

    def form_invalid(self, form):
        '''
        This probably should return a 400, but we're using a 500 so a
        notification is sent to the administrator
        '''
        return HttpResponseServerError()

    def form_valid(self, form):
        tank = mm.Tank.objects.get(name=form.cleaned_data['tank_name'])
        wash_steps = wm.WashStep.objects.filter(
            washtypestep__wash_type=form.cleaned_data['wash_type'])
        new_wash_type = form.cleaned_data['wash_type']
        wt_id = new_wash_type.id
        new_wash_type.pk = None
        new_wash_type.template = False
        new_wash_type.save()
        for ws in wash_steps.distinct():
            ws_id = ws.id
            new_ws = ws
            new_ws.pk = None
            new_ws.template = False
            new_ws.save()
            wts = wm.WashTypeStep.objects.filter(wash_type__id=wt_id,
                wash_step__id=ws_id)
            for o in wts:
                new_wts = o
                new_wts.pk = None
                new_wts.wash_type = new_wash_type
                new_wts.wash_step = new_ws
                new_wts.save()
        wash = wm.Wash()
        wash.wash_date = form.cleaned_data['wash_date']
        wash.wash_type = new_wash_type
        wash.save()
        wash.tanks.add(tank)
        return HttpResponseRedirect(self.success_url)


@class_view_decorator(login_required)
class WashDetailView(DetailView):
    model = wm.Wash

    def render_to_response(self, context, **response_kwargs):
        # convert to local timezone before constructing json
        context['object'].wash_date = context['object'].wash_date.astimezone(
            pytz.timezone(settings.TIME_ZONE))
        json = serializers.serialize('json', [context['object']],
            relations={'tanks': {'fields': ('name',)},
            'wash_type': {'fields': ('name',)}})
        return HttpResponse(json, mimetype="application/json")


@class_view_decorator(login_required)
class WashUpdateView(UpdateView):
    model = wm.Wash
    success_url = reverse_lazy('home')


@class_view_decorator(login_required)
class WashDeleteView(DeleteView):
    model = wm.Wash
    template_name = 'record_delete.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.wash_type.wash_steps.all().delete()
        self.object.wash_type.delete()
        self.object.delete()
        payload = {'delete': 'ok'}
        return HttpResponse(json.dumps(payload), mimetype="application/json")
            

@class_view_decorator(login_required)
class WashTankListView(ListView):
    """
    This is used to retrieve the tanks NOT involved in a particular wash.
    Used in updating a wash.
    """
    
    model = mm.Tank

    def get_queryset(self):
        """
        Exclude the tanks that are included in the wash already
        """
        qs = super(WashTankListView, self).get_queryset()
        qs = qs.exclude(hide=True).exclude(active=False)
        qs = qs.exclude(wash__pk=self.kwargs['pk']).order_by('position')
        return qs

    def render_to_response(self, context, **response_kwargs):
        """
        convert to JSON response
        """
        json = serializers.serialize('json', self.get_queryset(),
            fields=('name',))
        return HttpResponse(json, mimetype="application/json")


@login_required
def json_wash_steps(request):
    wash_steps = wm.WashStep.objects.filter(template=True).order_by('position')
    json = serializers.serialize("json", wash_steps)
    return HttpResponse(json, mimetype="application/javascript")


@login_required
def json_wash_types(request):
    wash_types = wm.WashType.objects.filter(template=True).order_by('position')
    json = serializers.serialize("json", wash_types)
    return HttpResponse(json, mimetype="application/javascript")


@login_required
def json_washes(request, tank):
    washes = wm.Wash.objects.filter(tanks__name=tank).order_by('-wash_date')
    wash_list = [{
        'wash_id': w.id,
        'wash_date': w.wash_date.astimezone(
            pytz.timezone(settings.TIME_ZONE)).strftime('%d %b %Y'),
        'wash_type': w.wash_type.name
        } for w in washes]
    return HttpResponse(simplejson.dumps(wash_list),
        mimetype="application/javascript")

