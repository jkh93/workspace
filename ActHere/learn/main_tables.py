# coding: utf-8
from main.models import (Tank, Unit, Location, BevType, ProductType,
    Measurement, EventType, Submission, Setting, BevChunk, PackageType)
from submission.models import DutyCredit
import django_tables2 as tables
from django_tables2.utils import A
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from quickbev import settings
from magnitude import mg
from django.contrib.sites.models import Site
from datetime import datetime


def get_td_text(order=False, edit=True, delete=True, link=None):
    order_icon = u'<span class="dragHandle ui-icon ui-icon-carat-2-n-s"></span>'
    edit_icon = (u'<a href="{}" class="tbl_icon edit">' +
        u'<span class="ui-icon ui-icon-pencil"></span></a>')
    delete_icon = (u'<a href="{}" class="tbl_icon delete">' +
        u'<span class="ui-icon ui-icon-trash"></span></a>')
    td_text = u'<div class="cell-text">'
    if link:
        td_text += '<a href="' + link + '">'
    td_text += '{}'
    if link:
        td_text += '</a>'
    td_text += '</div><div class="cell-icons">'
    if order:
        td_text += order_icon
    if edit:
        td_text += edit_icon
    if delete:
        td_text += delete_icon
    td_text += u'</div>'
    return td_text


def get_pagination(unlimited=False):
    '''
    Used to pass pagination parameters to list templates.
    Returns a tuple with the string to pass to javascript to set up the menu
    items. Second item is the initial list length
    '''
    if unlimited:
        default = -1
        pagination_string = '[[-1], ["All"]]'
    else:
        default = Setting.objects.get(site__id=settings.SITE_ID).list_length
        pagination_string = '[[{0}, -1], [{0}, "All"]]'.format(default)
    return (pagination_string, default)


def convert_to_base(quantity, unit, unit_type):
    # TODO: code base types elsewhere
    base_types = {"volume": "l", "temperature": "degC", "density": "SG(2020)"}
    return float(mg(quantity, unit).ounit(base_types[unit_type]))


def convert_to_default(quantity, base_unit, default_unit):
    base_unit_symbol = base_unit.mag_symbol
    default_unit_symbol = default_unit.mag_symbol
    return float(mg(quantity, base_unit_symbol).ounit(default_unit_symbol))


class TankTable(tables.Table):

    class Meta:
        model = Tank
        attrs = {"class": "paleblue", "id": "Tank"}
        exclude = ("hide", )

    position = tables.LinkColumn('tank_delete', args=[A('id')])
    name = tables.LinkColumn('tank_update', args=[A('id')])

    default_unit = Unit.objects.get_default_unit(settings.VOLUME_UNIT_TYPE)

#   volume = tables.Column(verbose_name="Volume (" + default_unit.symbol + ")")
    volume = tables.Column(verbose_name="Volume (L)")

    def render_name(self, record):
        update = reverse("tank_update", args=[record.pk])
        delete = reverse("tank_delete", args=[record.pk])
        return mark_safe(
            get_td_text(order=True).format(record.name, update, delete))

    def render_volume(self, value):
        base_vol_unit = Unit.objects.get(pk=settings.BASE_UNIT.get(
            settings.VOLUME_UNIT_TYPE))
        return convert_to_default(value, base_vol_unit, self.default_unit)


class LocationTable(tables.Table):
    class Meta:
        model = Location
        attrs = {"class": "paleblue", "id": "Location"}
        exclude = {'kegistry_id'}

    def render_name(self, record):
        update = reverse("location_update", args=[record.pk])
        delete = reverse("location_delete", args=[record.pk])
        return mark_safe(
            get_td_text(order=True).format(record.name, update, delete))


class BevTypeTable(tables.Table):
    class Meta:
        model = BevType
        attrs = {"class": "paleblue", "id": "BevType"}
        exclude = ("hide", "initial")

    def render_name(self, record):
        update = reverse("bevtype_update", args=[record.pk])
        delete = reverse("bevtype_delete", args=[record.pk])
        return mark_safe(
            get_td_text(order=True).format(record.name, update, delete))


class ProductTypeTable(tables.Table):
    class Meta:
        model = ProductType
        attrs = {"class": "paleblue", "id": "ProductType"}
        exclude = ("hide", "colour")

    def render_name(self, record):
        update = reverse("producttype_update", args=[record.pk])
        delete = reverse("producttype_delete", args=[record.pk])
        return mark_safe(
            get_td_text(order=True).format(record.name, update, delete))


class PackageTypeTable(tables.Table):
    class Meta:
        model = PackageType
        attrs = {"class": "paleblue", "id": "PackageType"}
        exclude = ('legacy',)

    def render_name(self, record):
        update = reverse("packagetype_update", args=[record.pk])
        delete = reverse("packagetype_delete", args=[record.pk])
        return mark_safe(
            get_td_text(order=True).format(record.name, update, delete))


class EventTypeTable(tables.Table):
    class Meta:
        model = EventType
        attrs = {"class": "paleblue", "id": "EventType"}
        fields = ('name', 'active')

    def render_name(self, record):
        update = reverse("event_type_update", args=[record.pk])
        # delete = reverse("event_type_delete", args=[record.pk])
        return mark_safe(
            get_td_text(delete=False).format(record.name, update))


class BrewTable(tables.Table):
    class Meta:
        attrs = {"class": "paleblue"}

    create_date = tables.Column(verbose_name='Brew Date',
        order_by=(
            'create_date',
            'id'
        ))
    name = tables.Column(verbose_name='Brew Type', accessor='bev_type.name',
        order_by=(
            'bev_type__name',
            '-create_date',
            '-id'
        ))
    batch_no = tables.Column(verbose_name='Batch Number',
        order_by=(
            'bev_type__prefix',
            'batch_no',
            '-create_date',
            '-id'
        ))
    starting_density = tables.Column(
        order_by=(
            'starting_density',
            '-create_date',
            '-id'
        ))
    #tank = tables.Column() #TODO: get tanks(s)
    # select * from bevtank where brew= and srctank=null

    def render_batch_no(self, record):
        return '{}{}'.format(record.bev_type.prefix, record.batch_no)


class BrewListTable(tables.Table):

    batch_no = tables.Column(verbose_name='Batch Number',
        order_by=(
            'bev_type__prefix',
            'batch_no',
            '-create_date',
            '-id'
        ))
    bev_type = tables.Column(verbose_name='Brew Type',
        order_by=(
            'bev_type__name',
            '-create_date',
            '-id'
        ))
    create_date = tables.Column(verbose_name='Brew Date',
        order_by=(
            'create_date',
            'id'
        ))
    tank = tables.Column(empty_values=(), orderable=False)
    volume = tables.Column(empty_values=(), orderable=False)

    class Meta:
        attrs = {"class": "paleblue", "id": "brew-list-table"}

    def render_batch_no(self, record):
        view = reverse("brew_detail", args=[record.pk])
        edit = reverse("brew_edit", args=[record.pk])
        delete = reverse("brew_delete", args=[record.pk])
        return mark_safe('<div class="cell-text"><a href="{}">{}{}'.format(
            view, record.bev_type.prefix, record.batch_no) +
            '</a></div><div class="cell-icons"><a href="{}">'.format(view,) +
            '<span class="ui-icon ui-icon-play"></span></a>' +
            '<a href="{}"><span class="ui-icon ui-icon-pencil">'.format(edit,) +
            '</span></a><a href="{}">'.format(delete,) +
            '<span class="ui-icon ui-icon-trash"></span></a></div>')

    def render_tank(self, record):
        bev_chunks = BevChunk.objects.filter(
            brew=record, src_tank__isnull=True)
        string = ""
        for i, bc in enumerate(bev_chunks):
            if i != 0:
                string += ' '
            string += str(bc.cur_tank.tank.name)
        return mark_safe('''%s''' % (string))

    def render_volume(self, record):
        bev_chunks = BevChunk.objects.filter(
            brew=record, src_tank__isnull=True)
        vol = 0.0
        for bc in bev_chunks:
            vol += bc.volume
        return mark_safe('''%s''' % (vol))


class BevTankTable(tables.Table):
    class Meta:
        attrs = {"class": "paleblue", "id": "current-tanks-table"}

#    vol_unit = Unit.objects.get(default=True, type=1).symbol
# TODO: remove the hardcoding here
    vol_unit = 'L'

    tank = tables.Column(order_by='position')
    name = tables.Column()
    product_type = tables.Column()
    status = tables.Column()
    fill_date = tables.Column()
    original_volume = tables.Column(verbose_name='Original Volume ' +
                                    '(' + vol_unit + ')')
    transferred_volume = tables.Column(verbose_name='Transferred Volume ' +
                                       '(' + vol_unit + ')')
    packaged_volume = tables.Column(verbose_name='Packaged Volume ' +
                                    '(' + vol_unit + ')')
    waste_volume = tables.Column(verbose_name='Waste Volume ' +
                                 '(' + vol_unit + ')')
    waste_percentage = tables.Column(verbose_name='Waste %')
    volume = tables.Column(verbose_name='Volume ' + '(' + vol_unit + ')')
    position = tables.Column()

    def render_status(self, record):
        if record['id']:
            edit = reverse('bev_tank_status_edit', args=(record['id'],))
            return mark_safe('''<div class="cell-text">{}</div>
                <div class="cell-icons"><a href="{}" class="tbl_icon edit">
                <span title="Change the Status" class="ui-icon ui-icon-pencil">
                </span></a>'''.format(record['status'], edit))
        else:
            return record['status']


class TransferListTable(tables.Table):

    name = tables.Column(empty_values=(), verbose_name='Beverage Name',
        order_by=(
            'bevchunk__src_tank__name',
            'bevchunk__src_tank__product_type__name',
            '-transfer_date',
            '-id'
        ))
    create_date = tables.DateTimeColumn(accessor='transfer_date',
        verbose_name='Fill Date',
        format='M j, Y',
        order_by=(
            'transfer_date',
            'id'
        ))
    src_tank = tables.Column(empty_values=(), verbose_name='Source Tank',
        order_by=(
            'bevchunk__src_tank__tank__position',
            '-transfer_date',
            '-id'
        ))
    dest_tank = tables.Column(empty_values=(), verbose_name='Destination Tank',
        order_by=(
            'bevchunk__cur_tank__tank__position',
            '-transfer_date',
            '-id'
        ))
    volume = tables.Column(empty_values=(), orderable=False)

    class Meta:
        attrs = {"class": "paleblue", "id": "brew-list-table"}

    def render_name(self, record):
        name = BevChunk.objects.filter(transfer=record)[0].src_tank.name
        product_type = BevChunk.objects.filter(
            transfer=record)[0].src_tank.product_type.name
        view = reverse("transfer_detail", args=[record.pk])
        edit = reverse("transfer_edit", args=[record.pk])
        delete = reverse("transfer_delete", args=[record.pk])
        return mark_safe('''<div class="cell-text">%s (%s)</div>
            <div class="cell-icons"><a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-play"></span></a>
            <a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-pencil"></span></a>
            <a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-trash"></span></a></div>'''
            % (product_type, name, view, edit, delete))

    def render_src_tank(self, record):
        bev_chunks = BevChunk.objects.filter(
            transfer=record)
        string = ""
        for i, bc in enumerate(bev_chunks):
            if i != 0:
                string += ' '
            string += str(bc.src_tank.tank.name)
        return mark_safe('''%s''' % (string))

    def render_dest_tank(self, record):
        bev_chunks = BevChunk.objects.filter(
            transfer=record)
        string = ""
        for i, bc in enumerate(bev_chunks):
            if i != 0:
                string += ' '
            string += str(bc.cur_tank.tank.name)
        return mark_safe('''%s''' % (string))

    def render_volume(self, record):
        bev_chunks = BevChunk.objects.filter(
            transfer=record)
        vol = 0.0
        for bc in bev_chunks:
            vol += bc.volume
        return mark_safe('''%s''' % (vol))


class PackageListTable(tables.Table):

    name = tables.Column(empty_values=(), verbose_name='Beverage Name',
        order_by=(
            'bev_tank__product_type__name',
            'bev_tank__name',
            '-create_date',
            '-id'
            ))
    create_date = tables.Column(verbose_name='Package Date',
        order_by=(
            'create_date',
            'id'
            ))
    tank = tables.Column(empty_values=(),
        order_by=(
            'bev_tank__tank__position',
            '-create_date',
            '-id'
        ))
    package_type = tables.Column(
        order_by=(
            'package_type__name',
            '-create_date',
            '-id'
        ))
    item_count = tables.Column(
        order_by=(
            'item_count',
            '-create_date',
            '-id'
        ))
    volume = tables.Column(
        order_by=(
            'volume',
            '-create_date',
            '-id'
        ))
    notes = tables.Column(
        order_by=(
            'notes',
            '-create_date',
            '-id'
        ))
    #TODO: Total volume checked out

    class Meta:
        attrs = {"class": "paleblue", "id": "package-list-table"}

    def render_name(self, record):
        name = record.bev_tank.name
        product_type = record.bev_tank.product_type.name
        view = reverse("package_detail", args=[record.pk])
        edit = reverse("package_edit", args=[record.pk])
        delete = reverse("package_delete", args=[record.pk])
        return mark_safe('''<div class="cell-text">%s (%s)</div>
            <div class="cell-icons"><a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-play"></a>
            <a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-pencil"></span></a>
            <a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-trash"></span></a></div>'''
            % (product_type, name, view, edit, delete))

    def render_tank(self, record):
        return mark_safe('''%s''' % (record.bev_tank.tank.name))


class CheckoutListTable(tables.Table):

    class Meta:
        attrs = {"class": "paleblue", "id": "checkout-list-table"}

    name = tables.Column(empty_values=(), verbose_name='Beverage Name',
        accessor='package.bev_tank.product_type.name',
        order_by=(
            'package__bev_tank__product_type__name',
            'package__bev_tank__name',
            '-create_date',
            '-package__id'
        ))
    create_date = tables.Column(verbose_name='Checkout Date',
        order_by=(
            'create_date',
            'package__id'
        ))
    package = tables.Column(
        order_by=(
            'package__bev_tank__name',
            'package__package_type__name',
            'package__volume',
            '-create_date',
            '-package__id'
        ))
    item_count = tables.Column(
        order_by=(
            'item_count',
            '-create_date',
            '-id'
        ))
    volume = tables.Column(
        order_by=(
            'volume',
            '-create_date',
            '-package__id'
        ))
    exempt = tables.Column(verbose_name='Duty Exemption',
        order_by=(
            'exempt',
            '-create_date',
            '-package__id'
        ))
    submission = tables.Column(verbose_name='Period Submitted',
        order_by=(
            '-submission__start_date',
            '-create_date',
            '-package__id'
        ))
    notes = tables.Column(
        order_by=(
            'notes',
            '-create_date',
            '-package__id'
        ))

    def render_name(self, record):
        name = record.package.bev_tank.name
        product_type = record.package.bev_tank.product_type.name
        view = reverse("checkout_detail", args=[record.pk])
        edit = reverse("checkout_edit", args=[record.pk])
        delete = reverse("checkout_delete", args=[record.pk])
        return mark_safe('''<div class="cell-text">%s (%s)</div>
            <div class="cell-icons"><a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-play"></span></a>
            <a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-pencil"></span></a>
            <a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-trash"></span></a></div>'''
            % (product_type, name, view, edit, delete))

    def render_package(self, record):
        return record.package.get_name()


class CheckoutReportTable(tables.Table):
    class Meta:
        attrs = {"class": "paleblue"}
#         order_by = ('bev_tank.name', 'bev_tank.product_type.name',
#             '-create_date', '-id')
    product_type = tables.Column(empty_values=())
    package_type = tables.Column(empty_values=(), verbose_name='Package Type')
    item_count = tables.Column(empty_values=(), verbose_name='Items on Hand', orderable=False)
    volume = tables.Column(empty_values=(), verbose_name='Volume on Hand', orderable=False)

    def render_item_count(self, record):
        if record['package_type_volume']:
            return self.render_volume(record) / record['package_type_volume']
        else:
            return self.render_volume(record)

    def render_volume(self, record):
        if record['checked_out_volume'] is not None:
            return record['package_volume'] - record['checked_out_volume']
        else:
            return record['package_volume']


class SubmissionCheckoutTable(tables.Table):

    class Meta:
        attrs = {"class": "paleblue", "id": "submission-checkout-table"}
        empty_text = "Nothing to Submit"

    create_date = tables.Column(verbose_name='Checkout Date',
        order_by=(
            'create_date',
            'id'
        ))
    package = tables.Column(verbose_name='Package Name',
        order_by=(
            'package__bev_tank__name',
            'package__package_type__name',
            'package__volume',
            '-create_date',
            '-id'
        ))
    volume = tables.Column(
        order_by=(
            'volume',
            '-create_date',
            '-id'
        ))
    exempt = tables.Column(verbose_name='Duty Exemption',
        order_by=(
            'exempt',
            '-create_date',
            '-id'
        ))

    def render_package(self, record):
        return record.package.get_name()


class MeasurementListTable(tables.Table):

    class Meta:
        attrs = {"class": "paleblue", "id": "measurement-list-table"}

    measurement_date = tables.Column(verbose_name='Measurement Date',
        order_by=(
            'measurement_date',
            'id'
        ))
    bev_tank = tables.Column(verbose_name='Tank',
        order_by=(
            'bev_tank__tank__name',
            'bev_tank__product_type__name',
            'bev_tank__name',
            '-measurement_date',
            '-id'
        ))
    measurement_type = tables.Column(verbose_name='Type',
        order_by=(
            'measurement_type__name',
            '-measurement_date',
            '-id'
        ))
    value = tables.Column(
        order_by=(
            'value',
            '-measurement_date',
            '-id'
        ))
    notes = tables.Column(
        order_by=(
            'notes',
            '-measurement_date',
            '-id'
        ))

    def render_measurement_date(self, record):
        date = datetime.strftime(record.measurement_date, "%B %-d, %Y")
        view = reverse("measurement_detail", args=[record.pk])
        edit = reverse("measurement_edit", args=[record.pk])
        delete = reverse("measurement_delete", args=[record.pk])
        return mark_safe('''<div class="cell-text">%s</div>
            <div class="cell-icons"><a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-play"></span></a>
            <a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-pencil"></span></a>
            <a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-trash"></span></a></div>'''
            % (date, view, edit, delete))


class MeasurementTable(tables.Table):
    class Meta:
        attrs = {"class": "paleblue"}
        model = Measurement

    measurement_date = tables.DateTimeColumn(format='M j, Y')


class SubmissionTable(tables.Table):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop("url", "/")
        super(SubmissionTable, self).__init__(*args, **kwargs)

    class Meta:
        attrs = {"class": "paleblue"}
        empty_text = "Nothing to Submit"

    package__bev_tank__product_type__name = tables.Column(
        verbose_name="Product Type")
    total = tables.Column(verbose_name="Volume to Submit (L)")
    credit = tables.Column(empty_values=(), verbose_name="Duty Credit ($)",
        orderable=False)
    url = "/"

    def render_credit(self, record):
        pt = ProductType.objects.get(
            pk=record['package__bev_tank__product_type__id'])
        ptid = pt.id
        creditqs = DutyCredit.objects.filter(product_type=pt, submission=None)
        if creditqs:
            credit = creditqs[0].credit
            cid = creditqs[0].id
            edit = reverse("credit_edit",
                kwargs={'pk': cid, 'pt': ptid}) + '?next=' + self.url
        else:
            credit = 0.0
            cid = None
            edit = reverse("credit_create",
                kwargs={'pt': ptid}) + '?next=' + self.url

        return mark_safe(('<div class="cell-text">%s</div><a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-pencil"></span></a></div>'
            % (credit, edit)))


class SubmissionDetailTable(tables.Table):
    class Meta:
        attrs = {"class": "paleblue"}
        empty_text = "Nothing Submitted"

    package__bev_tank__product_type__name = tables.Column(
        verbose_name="Product Type")
    total = tables.Column(verbose_name="Volume Submitted (L)")
    credit = tables.Column(empty_values=(), verbose_name="Duty Credit ($)",
        orderable=False)

    def render_credit(self, record):
        pt = ProductType.objects.get(
            pk=record['package__bev_tank__product_type__id'])
        credit = pt.get_credit(record['submission'])['credit__sum'] or 0.0

        return mark_safe('%s' % (credit))


class SubmissionListTable(tables.Table):
    class Meta:
        model = Submission
        attrs = {"class": "paleblue"}
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        super(SubmissionListTable, self).__init__(*args, **kwargs)
        setting = Setting.objects.get(site=Site.objects.get_current())
        self.vol_unit = setting.volume_unit

    setting = Setting.objects.get(site=Site.objects.get_current())
    vol_unit = setting.volume_unit
    base_vol_unit = Unit.objects.get(id=settings.BASE_VOLUME_UNIT)
#    total_vol = tables.Column(
#        verbose_name="Total Volume (" + vol_unit.symbol + ")")
    total_vol = tables.Column(
        verbose_name="Total Volume Submitted (L)")

    def render_total_vol(self, record):
        view = reverse("submission_detail", args=[record.pk])
        converted_vol = convert_to_default(
            record.total_vol, self.base_vol_unit, self.vol_unit)
        return mark_safe(('<div class="cell-text">%s</div><div class="cell-icons"><a href="%s" class="tbl_icon edit"><span class="ui-icon ui-icon-play"></span></a></div>'
                          % (converted_vol, view)))


class UserTable(tables.Table):
    class Meta:
        attrs = {"class": "paleblue"}
        model = User

    last_login = tables.DateTimeColumn(format='D F j, f a')

    def render_username(self, record):
        update = reverse("user_detail", args=[record.pk])
        return mark_safe(
            get_td_text(delete=False).format(record.username, update))


class GroupTable(tables.Table):
    class Meta:
        attrs = {"class": "paleblue"}
        model = Group

    def render_name(self, record):
        update = reverse("group_detail", args=[record.pk])
        return mark_safe(
            get_td_text(delete=False).format(record.name, update))

