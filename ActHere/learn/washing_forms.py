# coding: utf-8
from django import forms
import washing.models as wm


class WashStepsMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, data):
        valid_wash_steps = wm.WashStep.objects.filter(template=True)
        valid_wash_steps_list = []
        for i in valid_wash_steps:
            valid_wash_steps_list.append(i.id)
        for d in data:
            if int(d) not in valid_wash_steps_list:
                raise forms.ValidationError("Option not valid")


def validate_steps_list(data):
    valid_wash_steps = wm.WashStep.objects.filter(template=True).values('id')
    for d in data:
        if int(d) not in valid_wash_steps:
            raise forms.ValidationError("Option not valid")


class CreateWashStepForm(forms.ModelForm):
    class Meta:
        model = wm.WashStep
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get("name")
        ws = wm.WashStep.objects.filter(name=name, template=True)
        if self.instance and self.instance.pk:
            ws = ws.exclude(pk=self.instance.pk)
        if ws.count() > 0:
            raise forms.ValidationError(u'This name is already in use.')
        return name


class CreateWashTypeForm(forms.ModelForm):
    class Meta:
        model = wm.WashType
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(CreateWashTypeForm, self).__init__(*args, **kwargs)
        ws = wm.WashStep.objects.filter(
            washtype=self.instance).order_by('washtypestep__position')
        self.fields['wash_steps_list'].choices = [(o.id, o.name) for o in ws]

    wash_steps_list = WashStepsMultipleChoiceField()

    def clean_name(self):
        name = self.cleaned_data.get("name")
        wt = wm.WashType.objects.filter(name=name, template=True)
        if self.instance and self.instance.pk:
            wt = wt.exclude(pk=self.instance.pk)
        if wt.count() > 0:
            raise forms.ValidationError(u'This name is already in use.')
        return name


class CreateWashForm(forms.ModelForm):
    class Meta:
        model = wm.Wash
        fields = ['wash_date', 'wash_type']

    tank_name = forms.CharField()

