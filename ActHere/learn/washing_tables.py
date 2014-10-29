# coding: utf-8
import washing.models as wm
import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


class WashStepTable(tables.Table):
    class Meta:
        model = wm.WashStep
        attrs = {"class": "paleblue", "id": "WashStep"}
        exclude = ('position', 'template',)

    def render_name(self, record):
        update = reverse("washstep_update", args=[record.pk])
        delete = reverse("washstep_delete", args=[record.pk])
        return mark_safe(
            '<div class="cell-text"></span>{}</div>'.format(record.name) +
            '<div class="cell-icons">' +
            '<span class="dragHandle ui-icon ui-icon-carat-2-n-s"></span>' +
            '<a href="{}" class="tbl_icon edit">'.format(update) +
            '<span class="ui-icon ui-icon-pencil"></span></a>' +
            '<a href="{}" class="tbl_icon delete">'.format(delete) +
            '<span class="ui-icon ui-icon-trash"></span></a></div>')


class WashTypeTable(tables.Table):
    class Meta:
        model = wm.WashType
        attrs = {"class": "paleblue", "id": "WashType"}
        exclude = ('position', 'template',)

    def render_name(self, record):
        update = reverse("washtype_update", args=[record.pk])
        delete = reverse("washtype_delete", args=[record.pk])
        return mark_safe(
            '<div class="cell-text">{}</div>'.format(record.name) +
            '<div class="cell-icons">' +
            '<span class="dragHandle ui-icon ui-icon-carat-2-n-s">' +
            '</span><a href="{}" class="tbl_icon edit">'.format(update) +
            '<span class="ui-icon ui-icon-pencil"></span></a>' +
            '<a href="{}" class="tbl_icon delete">'.format(delete) +
            '<span class="ui-icon ui-icon-trash"></span></a></div>')

