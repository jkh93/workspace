# coding: utf-8
from django import forms
from main.models import (Brew, BevType, BevTank, Tank, Unit, ProductType,
    Location, ProcessType, TaskType, EventType, Setting,
    PackageType, MeasurementType, CheckOut, Package, Measurement)
from submission.models import ExciseCategory, DutyCredit
from django.contrib.auth.models import User, Group
from django.db.models import Sum, F, Count, Q
from quickbev import settings
from decimal import Decimal
from django.forms.formsets import BaseFormSet
import sys


class BrewBevTankForm(forms.Form):
    bev_tank_field = forms.ModelChoiceField(None, empty_label=None)


class BrewDetailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        mtqs = kwargs.pop('measurement_types')
        super(BrewDetailForm, self).__init__(*args, **kwargs)

        for i, mt in enumerate(mtqs):
            self.fields['custom_%s' % i] = forms.CharField(
                label=mt.measurement_type.name)


class CreateBrewForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.edit = kwargs.pop('edit_form', None)
        super(CreateBrewForm, self).__init__(*args, **kwargs)
        if self.edit:
            self.fields['starting_density'].required = False
            self.fields['dest_tank'].required = False
            self.fields['starting_density'].widget.attrs['disabled'] = True
            self.fields['dest_tank'].widget.attrs['disabled'] = True
            self.fields['blend_with'].widget.attrs['disabled'] = True

    btqs = BevType.objects.filter(active=True, hide=False)
    btankqs = BevTank.objects.all()
    tqs = Tank.objects.filter(active=True, hide=False)
    duqs = Unit.objects.get_density_units().order_by('-default')
    vuqs = Unit.objects.get_volume_units().order_by('-default')
    ptqs = ProductType.objects.filter(active=True, hide=False)
    create_date = forms.DateField()
    bev_type = forms.ModelChoiceField(btqs)
    product_type = forms.ModelChoiceField(ptqs)
    malt = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}),
                           required=False)
    hops = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}),
                           required=False)
    yeast = forms.CharField(required=False)
    starting_density = forms.DecimalField(max_digits=10, decimal_places=4)
#    starting_density_UOM = forms.ModelChoiceField(duqs, empty_label=None)
    dest_tank = forms.ModelChoiceField(tqs)
    blend_with = forms.ModelChoiceField(btankqs, required=False)
    dest_volume = forms.DecimalField()
#    dest_volume_UOM = forms.ModelChoiceField(vuqs, empty_label=None)
    #TODO: find out how to repeat dest tanks

    def clean_starting_density(self):
        data = self.cleaned_data['starting_density']
        if data != None:
            if data >= 2 or data < 0.7:
                raise forms.ValidationError(
                    "Please enter SG in the following format: 1.xxx")
        return data


class ScheduleBrewForm(forms.Form):
    btqs = BevType.objects.filter(active=True, hide=False)
    id = forms.IntegerField(required=False)
    date = forms.DateField()
    bev_type = forms.ModelChoiceField(btqs)


class ScheduleProcessForm(forms.Form):
    btqs = BevTank.objects.filter(empty_date__isnull=True, hide=False)
    process = EventType.objects.get(name="Process")
    ptqs = ProcessType.objects.filter(active=True)
    id = forms.IntegerField(required=False)
    date = forms.DateField()
    bev_tank = forms.ModelChoiceField(btqs)
    process_type = forms.ModelChoiceField(ptqs)


class ScheduleTransferForm(forms.Form):
    btqs = BevTank.objects.filter(empty_date__isnull=True)
    tqs = Tank.objects.filter(active=True, hide=False)
    id = forms.IntegerField(required=False)
    date = forms.DateField()
    bev_tank = forms.ModelChoiceField(btqs)
    dest_tank = forms.ModelChoiceField(tqs)


class SchedulePackageForm(forms.Form):
    btqs = BevTank.objects.filter(empty_date__isnull=True, hide=False)
    id = forms.IntegerField(required=False)
    date = forms.DateField()
    bev_tank = forms.ModelChoiceField(btqs)


class ScheduleTaskForm(forms.Form):
    task = EventType.objects.get(name="Task")
    ttqs = TaskType.objects.filter(active=True)
    id = forms.IntegerField(required=False)
    date = forms.DateField()
    task_type = forms.ModelChoiceField(ttqs)


class ScheduleForm(forms.Form):
    id = forms.IntegerField()
    date = forms.DateField()


class EventDeleteForm(forms.Form):
    id = forms.IntegerField()


class CreateTankForm(forms.Form):
    lqs = Location.objects.all()
    vuqs = Unit.objects.get_volume_units().order_by('-default')

    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField()
    volume = forms.FloatField()
#    volume_UOM = forms.ModelChoiceField(vuqs, empty_label=None)
    location = forms.ModelChoiceField(lqs)
    active = forms.BooleanField(initial=True, required=False)


class CreateLocationForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField()
    active = forms.BooleanField(initial=True, required=False)


class CreateBevTypeForm(forms.ModelForm):
    class Meta:
        model = BevType
        exclude = ['position']

    def __init__(self, *args, **kwargs):
        super(CreateBevTypeForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            if (Brew.objects.filter(bev_type=self.instance).count() or
                Setting.objects.get().batch_numbering.name == 'Global'):
                self.fields['initial'].widget.attrs['disabled'] = True

    initial = forms.IntegerField(required=False, min_value=1)
    active = forms.BooleanField(initial=True, required=False)
    create_product_type = forms.BooleanField(required=False)


class CreatePackageTypeForm(forms.ModelForm):
    class Meta:
        model = PackageType
        exclude = ('legacy',)

    def clean(self):
        cleaned_data = super(CreatePackageTypeForm, self).clean()
        if ((cleaned_data.get('volume') == None and
            cleaned_data.get('variable_size') == False)
            or (cleaned_data.get('volume') != None and
            cleaned_data.get('variable_size') == True)):
            raise forms.ValidationError("Please enter a volume")
        return cleaned_data

    def clean_volume(self):
        vol = self.cleaned_data['volume']
        var = self.cleaned_data['variable_size']
        # If is variable, we don't want to return a volume
        if var:
            return None

        if vol != None and vol <= 0:
            raise forms.ValidationError("The volume must be greater than zero")
        elif vol == None:
            raise forms.ValidationError("Please enter a volume")
        else:
            return vol


class CreateProcessForm(forms.Form):
    btqs = BevTank.objects.filter(empty_date__isnull=True)
    process = EventType.objects.get(name="Process")
    ptqs = ProcessType.objects.filter(active=True)

    create_date = forms.DateField()
    bev_tank = forms.ModelChoiceField(btqs)
    type = forms.ModelChoiceField(ptqs)


class TransferForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.edit = kwargs.pop('edit_form', None)
        super(TransferForm, self).__init__(*args, **kwargs)
        if self.edit:
            self.fields['cur_tank'].required = False
            self.fields['dest_tank'].required = False
            self.fields['blend_with'].required = False
            self.fields['cur_tank'].widget.attrs['disabled'] = True
            self.fields['dest_tank'].widget.attrs['disabled'] = True
            self.fields['blend_with'].widget.attrs['disabled'] = True
            self.fields['cur_tank'].queryset = self.btqs_edit
        else:
            # Limit to only non-empty tanks
            self.fields['cur_tank'].queryset = self.btqs

    vuqs = Unit.objects.get_volume_units().order_by('-default')
    btqs = BevTank.objects.filter(
        empty_date__isnull=True).order_by('tank__position')
    btqs_edit = BevTank.objects.all().order_by('tank__position')
    btankqs = BevTank.objects.all()
    tqs = Tank.objects.filter(active=True, hide=False)
    ptqs = ProductType.objects.filter(active=True, hide=False)

    transfer_date = forms.DateField()
    cur_tank = forms.ModelChoiceField(btqs_edit)
    dest_volume = forms.DecimalField()
#    dest_volume_UOM = forms.ModelChoiceField(vuqs, empty_label=None)
    dest_tank = forms.ModelChoiceField(tqs)
    blend_with = forms.ModelChoiceField(btankqs, required=False)
    product_type = forms.ModelChoiceField(ptqs)
    empty = forms.BooleanField(initial=False, required=False)

    def clean(self):
        cleaned_data = super(TransferForm, self).clean()

        if cleaned_data.get('transfer_date') and cleaned_data.get('cur_tank'):
            transfer_date = cleaned_data.get('transfer_date')
            tank_create_date = cleaned_data.get('cur_tank').fill_date

            if transfer_date < tank_create_date:
                msg = u"The transfer date is before the tank was filled."
                self.errors["transfer_date"] = self.error_class([msg])
                del cleaned_data["transfer_date"]

        return cleaned_data


class PackageForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.edit = kwargs.pop('edit_form', None)
        super(PackageForm, self).__init__(*args, **kwargs)

        if Setting.objects.get(site__id=settings.SITE_ID).submit_stock_on_hand:
            self.fields['coi'].initial = True
            self.fields['coi'].widget.attrs['disabled'] = True
        if self.edit:
            # Because widget is disabled it does not return value in
            # cleaned_data. Insert manually:
            self.bev_tank = self.fields['bev_tank'].queryset[0]
            self.fields['bev_tank'].required = False
            self.fields['bev_tank'].widget.attrs['disabled'] = True
            self.fields['bev_tank'].queryset = self.btqs_edit
        else:
            # Limit to only non-empty tanks
            self.fields['bev_tank'].queryset = self.btqs

    vuqs = Unit.objects.get_volume_units().order_by('-default')
    btqs = BevTank.objects.filter(
        empty_date__isnull=True, no_package=False).order_by('tank__position')
    btqs_edit = BevTank.objects.filter(
        no_package=False).order_by('tank__position')
    ptqs = PackageType.objects.filter(active=True, legacy=False)

    create_date = forms.DateField()
    bev_tank = forms.ModelChoiceField(btqs_edit)
    package_type = forms.ModelChoiceField(ptqs)
    item_count = forms.DecimalField()
#    volume_UOM = forms.ModelChoiceField(vuqs, empty_label=None)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}),
        required=False)
    empty = forms.BooleanField(initial=False, required=False)
    coi = forms.BooleanField(initial=False, required=False)

    def clean(self):
        cleaned_data = super(PackageForm, self).clean()

        if cleaned_data.get('create_date') and cleaned_data.get('bev_tank'):
            package_date = cleaned_data.get('create_date')
            tank_create_date = cleaned_data.get('bev_tank').fill_date

            if package_date < tank_create_date:
                    msg = u"The package date is before the tank was filled."
                    self.errors["create_date"] = self.error_class([msg])
                    del cleaned_data["create_date"]
        else:
            if (cleaned_data.get('create_date') and
                cleaned_data.get('bev_tank')):
                package_date = cleaned_data.get('create_date')
                tank_create_date = self.bev_tank.fill_date

                if package_date < tank_create_date:
                    msg = u"The package date is before the tank was filled."
                    self.errors["create_date"] = self.error_class([msg])
                    del cleaned_data["create_date"]

        return cleaned_data


class CreateCheckOutForm(forms.ModelForm):
    class Meta:
        model = CheckOut
        exclude = ('volume',)

    def __init__(self, *args, **kwargs):
        self.edit = kwargs.pop('edit_form', None)
        super(CreateCheckOutForm, self).__init__(*args, **kwargs)
        # Only display those that have an outstanding balance
        # Had to use Count to get around the null Sums. Query must be performed
        # in this order
        pqs = Package.objects.annotate(checkedoutsum=Sum(
            'checkout__volume')).annotate(checkedoutcount=Count(
            'checkout__volume')).filter(Q(volume__gt=F('checkedoutsum')) |
            Q(checkedoutcount=0)
            ).order_by('create_date')
        if self.instance.id:
            if self.instance.package not in pqs:
                pqs = Package.objects.filter(checkout=self.instance)
        self.fields['package'].queryset = pqs

    item_count = forms.DecimalField()

    def clean(self):
        cleaned_data = super(CreateCheckOutForm, self).clean()

        if cleaned_data.get('create_date') and cleaned_data.get('package'):
            checkout_date = cleaned_data.get('create_date')
            package_date = cleaned_data.get('package').create_date

            if checkout_date < package_date:
                    msg = u"The checkout date is before the package date."
                    self.errors["create_date"] = self.error_class([msg])
                    del cleaned_data["create_date"]

        if cleaned_data.get('volume'):
            if not cleaned_data.get('volume') > 0.0:
                msg = u"Please enter a positive volume."
                self.errors["volume"] = self.error_class([msg])
                del cleaned_data["volume"]
            if cleaned_data.get('package'):
                checkedout = CheckOut.objects.filter(
                    package=cleaned_data.get('package')).aggregate(
                    Sum('volume'))['volume__sum']
                if checkedout:
                    remaining = cleaned_data.get('package').volume - checkedout
                else:
                    remaining = cleaned_data.get('package').volume
                # If we are editing, do not double count the volume
                if (self.instance.pk and
                    self.instance.package == cleaned_data.get('package')):
                    remaining += self.instance.volume
                if (Decimal("%.2f" % cleaned_data.get('volume')) >
                    Decimal("%.2f" % remaining)):
                    msg = u"Only %dL remains to be checked out" % remaining
                    self.errors["volume"] = self.error_class([msg])
                    del cleaned_data["volume"]

        return cleaned_data


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement

    def __init__(self, *args, **kwargs):
        self.edit = kwargs.pop('edit_form', None)
        super(MeasurementForm, self).__init__(*args, **kwargs)
        if self.edit:
            self.fields['measurement_date'].required = False
            self.fields['measurement_date'].widget.attrs['disabled'] = True
            self.fields['measurement_type'].required = False
            self.fields['measurement_type'].widget.attrs['disabled'] = True
            self.fields['bev_tank'].required = False
            self.fields['bev_tank'].widget.attrs['disabled'] = True

    def clean_bev_tank(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.bev_tank
        else:
            return self.cleaned_data['bev_tank']

    def clean_measurement_type(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.measurement_type
        else:
            return self.cleaned_data['measurement_type']

    def clean_measurement_date(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.measurement_date
        else:
            return self.cleaned_data['measurement_date']

    btqs = BevTank.objects.filter(
        empty_date__isnull=True, hide=False).order_by('tank__position')
    duqs = Unit.objects.get_density_units().order_by('-default')
    mtqs = MeasurementType.objects.all()
    uqs = Unit.objects.filter(active=True)

    measurement_date = forms.DateField()
    measurement_type = forms.ModelChoiceField(mtqs)
    bev_tank = forms.ModelChoiceField(btqs)
    value = forms.DecimalField(max_digits=10, decimal_places=4)
#    uom = forms.ModelChoiceField(uqs, empty_label=None)

    def clean(self):
        cleaned_data = super(MeasurementForm, self).clean()

        if (cleaned_data.get('measurement_date') and
            cleaned_data.get('bev_tank')):
            measurement_date = cleaned_data.get('measurement_date')
            tank_create_date = cleaned_data.get('bev_tank').fill_date

            if measurement_date < tank_create_date:
                msg = u"The measurement date is before the tank was filled."
                self.errors["measurement_date"] = self.error_class([msg])
                del cleaned_data["measurement_date"]

        mt = cleaned_data.get("measurement_type")
        v = cleaned_data.get("value")
        if v != None and mt.name == 'Density':
            if v >= 2 or v < 0.7:
                msg = u"Please enter SG in the following format: 1.xxx"
                self.errors["value"] = self.error_class([msg])
                del cleaned_data["value"]
        return cleaned_data


class BevTankStatusEditForm(forms.ModelForm):
    class Meta:
        model = BevTank
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super(BevTankStatusEditForm, self).__init__(*args, **kwargs)
        self.fields['status'].empty_label = None


class BevTypeForm(forms.Form):
    proportion = forms.DecimalField(
        max_digits=5, decimal_places=1, initial=0.0,
        max_value=100.0, min_value=0.0)
    id = forms.IntegerField(widget=forms.HiddenInput())


class BaseBevTypeFormSet(BaseFormSet):
    def clean(self):
        cleaned_data = super(BaseBevTypeFormSet, self).clean()
        if any(self.errors):
            # Don't validatie the formset unless each form is valid on its own
            return
        total = Decimal(0.0)
        for form in self.forms:
            total += form.cleaned_data['proportion']
        if total != 100.0:
            raise forms.ValidationError(u"Proportion must total 100%")
        return cleaned_data


class CreateProductTypeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.bet_type_form = kwargs.pop('bev_type_form', False)
        super(CreateProductTypeForm, self).__init__(*args, **kwargs)
        if self.bet_type_form:
            self.fields['name'].required = False
            self.fields['prefix'].required = False

    ecqs = ExciseCategory.objects.all()
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField()
    prefix = forms.CharField()
    alcohol = forms.FloatField()
    excise_category = forms.ModelChoiceField(ecqs)
    colour = forms.CharField(initial="#000")
    active = forms.BooleanField(initial=True, required=False)


class CreateEventTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CreateEventTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['readonly'] = True

    class Meta:
        model = EventType

    process_types = forms.ModelMultipleChoiceField(
        queryset=ProcessType.objects.all(), required=False)
    task_types = forms.ModelMultipleChoiceField(
        queryset=TaskType.objects.all(), required=False)


class CreateProcessTypeForm(forms.ModelForm):
    class Meta:
        model = ProcessType


class CreateTaskTypeForm(forms.ModelForm):
    class Meta:
        model = TaskType


class SubmissionCreateForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()


class SubmissionCompleteForm(forms.Form):
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}),
        required=False)


class CreditEditForm(forms.ModelForm):
    class Meta:
        model = DutyCredit
        fields = ('credit',)
    credit = forms.DecimalField()


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  # 'groups',  # uncomment once groups/permissions working
                  'is_active',)


class UserCreateForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    is_active = forms.BooleanField(initial=True)


class GroupProfileForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name',)  # remove this to enable permissions

    def clean_name(self):
        name = self.cleaned_data['name']
        if (Group.objects.filter(name=name).
            exclude(pk=self.instance.pk).exists()):
            raise forms.ValidationError("Group with this name already exists")
        return name


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Setting
        exclude = ('site', 'volume_unit', 'temperature_unit', 'density_unit')

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
#        self.fields['volume_unit'].widget.attrs['disabled'] = True
#        self.fields['temperature_unit'].widget.attrs['disabled'] = True
#        self.fields['density_unit'].widget.attrs['disabled'] = True
        if Brew.objects.all():
            self.fields['batch_numbering'].required = False
            self.fields['batch_numbering'].widget.attrs['disabled'] = True
        for field in self.fields:
            self.fields[field].empty_label = None

    def clean(self):
        instance = getattr(self, 'instance', None)
        if Brew.objects.all():
            self.cleaned_data['batch_numbering'] = instance.batch_numbering
        cleaned_data = super(SettingsForm, self).clean()
        return cleaned_data

    def clean_list_length(self):
        list_length = self.cleaned_data['list_length']
        if list_length < 1:
            raise forms.ValidationError("Please enter a positive length")
        return list_length

    cca_name = forms.CharField(required=False)
    cca_code = forms.CharField(required=False)
    licensee_name = forms.CharField(required=False)
    licensee_code = forms.CharField(required=False)
    email = forms.EmailField(required=False)

