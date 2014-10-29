# coding: utf-8
from django.db import models
import submission.models as sm
from datetime import date, datetime, timedelta
from django.contrib.sites.models import Site
from django.db.models import Sum, Count, Max, Q, F
from quickbev import settings
from django.contrib.auth.models import User
from pytz import timezone
from functools import wraps
import pytz
import json
from django.core.urlresolvers import reverse


def values_queryset_to_dict(vqs):
    return [item for item in vqs]


def unique_boolean(field, subset=[]):
    """
    Allows to specify a unique boolean for a model.
    """
    def cls_factory(cls):
        def factory(func):
            @wraps(func)
            def decorator(self):
                kwargs = {field: True}
                for arg in subset:
                    if getattr(self, arg):
                        kwargs[arg] = getattr(self, arg)
                if getattr(self, field):
                    try:
                        tmp = self.__class__.objects.get(**kwargs)
                        if self != tmp:
                            setattr(tmp, field, False)
                            tmp.save()
                    except self.__class__.DoesNotExist:
                        if getattr(self, field) != True:
                            setattr(self, field, True)
                else:
                    if self.__class__.objects.filter(**kwargs).count() == 0:
                        setattr(self, field, True)
                return func(self)
            return decorator
        if hasattr(cls, 'save'):
            cls.save = factory(cls.save)
        return cls
    return cls_factory


class Company(models.Model):
    site = models.OneToOneField(Site)
    subdomain = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=100, null=True)
    kegistry_user = models.CharField(max_length=50, null=True)
    kegistry_api_key = models.CharField(max_length=50, null=True)
    invoice_address = models.ForeignKey('orders.Address',
        null=True, blank=True)
    email = models.EmailField(null=True, blank=True)


class SubmissionCompany(models.Model):
    company = models.OneToOneField(Company)
    cca_code = models.CharField(max_length=50, null=True)
    licensee_code = models.CharField(max_length=50, null=True)
    licensee = models.CharField(max_length=100, null=True)


class Location(models.Model):
    name = models.CharField(max_length=30)
    position = models.IntegerField()
    kegistry_id = models.IntegerField(null=True)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name


class BevType(models.Model):
    name = models.CharField(max_length=30)
    prefix = models.CharField(max_length=20)
    position = models.IntegerField()
    initial = models.IntegerField(blank=True, null=True)
    active = models.BooleanField()
    hide = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=30)
    prefix = models.CharField(max_length=20)
    alcohol = models.FloatField()
    excise_category = models.ForeignKey(sm.ExciseCategory,
        on_delete=models.PROTECT)
    bev_types = models.ManyToManyField(BevType, through='ProductBevType')
    colour = models.CharField(max_length=20, null=True, blank=True)
    position = models.IntegerField()
    active = models.BooleanField()
    hide = models.BooleanField(default=False)

    def get_excise_item(self):
        ei = sm.ExciseItem.objects.filter(excise_category=self.excise_category,
            alcohol_limit__gte=self.alcohol).order_by('alcohol_limit')[0]
        return ei

    def get_hpa_item(self):
        hi = sm.HPAItem.objects.filter(excise_category=self.excise_category,
            alcohol_limit__gte=self.alcohol).order_by('alcohol_limit')[0]
        return hi

    def get_credit(self, submission):
        dc = sm.DutyCredit.objects.filter(submission=submission,
            product_type=self).aggregate(Sum('credit'))
        return dc

    def __unicode__(self):
        return self.name


class ProductBevType(models.Model):
    bev_type = models.ForeignKey(BevType)
    product_type = models.ForeignKey(ProductType)
    proportion = models.FloatField()


#currently only configured at db level
class UnitType(models.Model):
    type = models.CharField(max_length=30)


class UnitManager(models.Manager):

    def get_volume_units(self):
        return self.filter(type='1')

    def get_density_units(self):
        return self.filter(type='2')

    def get_temperature_units(self):
        return self.filter(type='3')

    def get_default_unit(self, unit_type):
        return self.get(default=True, type=unit_type)


#currently only configured at db level
class Unit(models.Model):
    symbol = models.CharField(max_length=20)
    mag_symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    default = models.BooleanField()
    active = models.BooleanField(default=True)

    objects = UnitManager()

    def __unicode__(self):
        return self.name


class Tank(models.Model):
    name = models.CharField(max_length=20, unique=True)
    volume = models.FloatField()
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    notes = models.TextField(null=True, blank=True)
    position = models.IntegerField()
    active = models.BooleanField()
    hide = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def _get_status(self):
        from washing import models as wm
        bevtanks = BevTank.objects.filter(tank=self)
        last_wash = wm.Wash.objects.filter(tanks=self
            ).order_by('-wash_date', '-id')
        if bevtanks.filter(empty_date=None):
            return bevtanks[0].status.description
        elif last_wash:
            last_empty = bevtanks.aggregate(
                Max('empty_date'))['empty_date__max']
            if not last_empty:
                return last_wash[0].wash_type.name
            last_wash_date = last_wash[0].wash_date.astimezone(
                timezone(settings.TIME_ZONE)).date()
            if last_wash_date >= last_empty:
                return last_wash[0].wash_type.name
            else:
                return 'Unwashed'
        else:
            return 'Unwashed'

    tank_status = property(_get_status)


class BevTankStatus(models.Model):
    description = models.CharField(max_length=20)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.description


class BevTank(models.Model):
    tank = models.ForeignKey(Tank)
    fill_date = models.DateField()
    empty_date = models.DateField(null=True)
    custom_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.ForeignKey(BevTankStatus, on_delete=models.PROTECT)
    product_type = models.ForeignKey(ProductType)
    notes = models.TextField(null=True, blank=True)
    no_package = models.BooleanField(default=False)
    hide = models.BooleanField(default=False)
    unlimited = models.BooleanField(default=False)

    def _get_name(self):
        name = u''
        for i, bc in enumerate(self.get_bev_chunks()):
            if i != 0:
                name += u'+'
            name += bc.brew.bev_type.prefix
            name += str(bc.brew.batch_no)
        return name

    name = property(_get_name)

    def __unicode__(self):
        return u'%s: %s (%s)' % (self.tank, self.product_type.name, self.name)

    def get_original_volume(self):
        bc = BevChunk.objects.filter(cur_tank=self)
        total_vol_in = 0.0
        if(bc.count() != 0):
            total_vol_in = bc.aggregate(models.Sum('volume'))['volume__sum']
        return total_vol_in

    def get_volume_today(self):
        return self.get_volume(date.today())

    def get_volume(self, date, measurement=None, package=None):

        level_volume = self.get_measured_level(date, measurement)
        level_date = self.get_last_measure_date(date)

        # take off any volumes transferred out after last level
        # assumes a level is taken before a transfer that day
        # TODO: Bad assumption. Fix
        vol_transferred = self.get_transferred_volume_between(
            level_date - timedelta(days=1), date)
        # take off any volumes packaged after last level
        # assumes a level is taken before a package that day
        # TODO: Bad assumption. Fix
        vol_packaged = self.get_packaged_volume_between(
            level_date - timedelta(days=1), date, package)
        cur_vol = level_volume - vol_transferred - vol_packaged

        return cur_vol

    def get_transferred_volume_today(self):
        return self.get_transferred_volume(date.today())

    def get_transferred_volume(self, date):
        tbc = TransferBevChunk.objects.filter(
            bev_chunk__cur_tank=self).filter(transfer__transfer_date__lte=date)
        total_vol_out = 0.0
        if tbc.count() != 0:
            total_vol_out = tbc.aggregate(models.Sum('volume'))['volume__sum']
        return total_vol_out

    def get_transferred_volume_between(self, start_date, end_date):
        tbc = TransferBevChunk.objects.filter(
            bev_chunk__cur_tank=self, transfer__transfer_date__lte=end_date,
            transfer__transfer_date__gt=start_date)
        total_vol_out = 0.0
        if tbc.count() != 0:
            total_vol_out = tbc.aggregate(models.Sum('volume'))['volume__sum']
        return total_vol_out

    def get_packaged_volume_today(self):
        return self.get_packaged_volume(date.today())

    def get_packaged_volume(self, date):
        pbc = PackageBevChunk.objects.filter(
            bev_chunk__cur_tank=self).filter(package__create_date__lte=date)
        total_vol_packaged = 0.0
        if(pbc.count() != 0):
            total_vol_packaged = pbc.aggregate(
                models.Sum('volume'))['volume__sum']
        return total_vol_packaged

    def get_packaged_volume_between(self, start_date, end_date, package=None):
        pbc = PackageBevChunk.objects.filter(
            bev_chunk__cur_tank=self, package__create_date__lte=end_date,
            package__create_date__gt=start_date)
        if package:
            pbc = pbc.exclude(package=package)
        total_vol_packaged = 0.0
        if(pbc.count() != 0):
            total_vol_packaged = pbc.aggregate(
                models.Sum('volume'))['volume__sum']
        return total_vol_packaged

    def get_waste_volume_today(self):
        return self.get_waste_volume(date.today())

    def get_waste_volume(self, date):
        level_date = self.get_last_measure_date(date)
        original_vol = self.get_original_volume()
        latest_level = self.get_measured_level(date)
        packaged_before_level_date = self.get_packaged_volume_between(
            self.fill_date, level_date)
        trans_before_level_date = self.get_transferred_volume_between(
            self.fill_date, level_date)

        waste = (original_vol - packaged_before_level_date -
            trans_before_level_date - latest_level)
        return waste

    def get_last_measure_date(self, date):
        level_date = self.fill_date
        vm = MeasurementType.objects.get(name='Volume')
        levels = Measurement.objects.filter(measurement_type=vm, bev_tank=self,
                                            measurement_date__lte=date)

        if levels:
            level = Measurement.objects.filter(measurement_type=vm,
                                               bev_tank=self,
                                               measurement_date__lte=date
                                               ).order_by('-measurement_date')

            level_date = level[0].measurement_date
        return level_date

    def get_measured_level(self, date, measurement=None):
        level_volume = self.get_original_volume()
        vm = MeasurementType.objects.get(name='Volume')
        levels = Measurement.objects.filter(measurement_type=vm, bev_tank=self,
                                            measurement_date__lte=date)

        if levels:
            level = Measurement.objects.filter(measurement_type=vm,
                                               bev_tank=self,
                                               measurement_date__lte=date
                                               ).order_by('-measurement_date')
            if measurement:
                level = level.exclude(pk=measurement.pk)
            if level:
                level_volume = level[0].value
        return level_volume

    def get_waste_proportion_today(self):
        return self.get_waste_proportion(date.today())

    def get_waste_proportion(self, date):
        p = 0.0
        d = self.get_original_volume() - self.get_volume(date)
        if d:
            p = self.get_waste_volume(date) / d
        return p

    def get_waste_percentage_today(self):
        return self.get_waste_proportion(date.today()) * 100

    def get_volume_proportion(self):
        p = self.get_current_volume() / self.get_original_volume()
        return p

    def get_density(self, date):
        density = None

        dm = MeasurementType.objects.get(name='Density')
        densities = Measurement.objects.filter(
            bev_tank=self, measurement_type=dm, measurement_date__lte=date)

        if densities:
            level = Measurement.objects.filter(
                bev_tank=self, measurement_type=dm,
                measurement_date__lte=date).order_by('-measurement_date')

            density = level[0]
        return density

    def get_alcohol(self, date):
        alcohol = 0.0

        dm = MeasurementType.objects.get(name='Alcohol')
        densities = Measurement.objects.filter(
            bev_tank=self, measurement_type=dm, measurement_date__lte=date)

        if densities:
            level = Measurement.objects.filter(
                bev_tank=self, measurement_type=dm,
                measurement_date__lte=date).order_by( '-measurement_date')

            alcohol = level[0].value
        return alcohol

    def get_bev_chunks(self):
        bc = BevChunk.objects.filter(cur_tank=self).order_by('id')
        return bc

    def transfer(self, date, bevtank, transfer_volume):
        t = Transfer()
        t.transfer_date = date
        t.save()
        bc = self.get_bev_chunks()
        if self.get_volume(date) == 0:
            # Avoid div by zero error.
            # Will create empty bevchunks though
            # TODO: What is the effect of this?
            p = 0
        else:
            p = transfer_volume / self.get_volume(date)

        for c in bc:
            vol = c.get_volume(date) * p
            dbc = BevChunk(brew=c.brew, src_tank=c.cur_tank,
            cur_tank=bevtank, starting_density=c.starting_density, volume=vol,
            create_date=date, transfer=t, parent=c)
            dbc.save()
            if not self.unlimited:
                tbc = TransferBevChunk(transfer=t, bev_chunk=c, volume=vol)
                tbc.save()
        return t

    def fermenting(self):
        return BevTankStatus(pk=1)


class Brew(models.Model):
    #recipe
    create_date = models.DateField()
    starting_density = models.FloatField()
    bev_type = models.ForeignKey(BevType, on_delete=models.PROTECT)
    batch_no = models.IntegerField()
    malt = models.TextField(null=True, blank=True)
    hops = models.TextField(null=True, blank=True)
    yeast = models.CharField(null=True, blank=True, max_length=50)
    notes = models.TextField(null=True, blank=True)
    hide = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s%s' % (self.bev_type.prefix, self.batch_no)

    def can_delete(self):
        """
        checks to see if the brew can be deleted.
        Returns a tuple with True/False at 0
        and a message at 1
        """
        message = u''
        can_delete = True

        bcqs = BevChunk.objects.filter(src_tank__isnull=True, brew=self)
        # Check if the brew has been packaged out of the FV
        pbcqs = PackageBevChunk.objects.filter(bev_chunk__in=bcqs)
        pqs = Package.objects.filter(packagebevchunk__in=pbcqs)
        # Check to see if any packages have been checked out
        coqs = CheckOut.objects.filter(package__in=pqs)
        # Check if the brew has been transferred out of the FV
        tbcqs = TransferBevChunk.objects.filter(bev_chunk__in=bcqs)
        # The transfers from this FV
        tqs = Transfer.objects.filter(transferbevchunk__in=tbcqs)
        # The bevchunks created by the transfers
        t_bcqs = BevChunk.objects.filter(transfer__in=tqs)
        # Check to see if these have been packaged...
        t_pbcqs = PackageBevChunk.objects.filter(bev_chunk__in=t_bcqs)
        # ...or transferred
        t_tbcqs = TransferBevChunk.objects.filter(bev_chunk__in=t_bcqs)
        if coqs:
            can_delete = False
            pstr = u''
            for i, co in enumerate(coqs):
                if i == 0:
                    pstr += u'<a href = "{0}">{1}</a>'.format(
                        reverse(
                            'package_delete',
                            args=(co.package.pk,)),
                        co.package)
                else:
                    pstr += u', <a href = "{0}">{1}</a>'.format(
                        reverse(
                            'package_delete',
                            args=(co.package.pk,)),
                        co.package)
            message += (
                u'{0} has been packaged.'.format(self) +
                u' The following packages have been checked out.' +
                u' Please delete the packages and checkouts before' +
                u' deleting this brew:<br />' + pstr)
        if t_pbcqs:
            can_delete = False
            tstr = ''
            for i, p in enumerate(t_pbcqs):
                if i == 0:
                    tstr += u'<a href = "{0}">{1}</a>'.format(
                        reverse(
                            'transfer_delete',
                            args=(p.bev_chunk.transfer.pk,)),
                        p.bev_chunk.transfer)
                else:
                    tstr += u', <a href = "{0}">{1}</a>'.format(
                        reverse(
                            'transfer_delete',
                            args=(p.bev_chunk.transfer.pk,)),
                        p.bev_chunk.transfer)
            if message:
                message += u'<p />'
            message += (
                u'{} has been transferred.'.format(self) +
                u' The following transfers have been packaged. Please delete' +
                u' the transfers and packages before deleting this brew:' +
                u'<br />' + tstr)
        if t_tbcqs:
            can_delete = False
            tstr = ''
            for i, t in enumerate(t_tbcqs):
                if i == 0:
                    tstr += u'<a href = "{0}">{1}</a>'.format(
                        reverse(
                            'transfer_delete',
                            args=(t.bev_chunk.transfer.pk,)),
                        t.bev_chunk.transfer)
                else:
                    tstr += u', <a href = "{0}">{1}</a>'.format(
                        reverse(
                            'transfer_delete',
                            args=(t.bev_chunk.transfer.pk,)),
                        t.bev_chunk.transfer)
            if message:
                message += u'<p />'
            message += (
                u'{} has been transferred.'.format(self) +
                u' The following transfers have been transferred. Please ' +
                u'delete the transfers before deleting this brew:<br />' +
                tstr)
        # Add a warning message if deleting more than just the brew
        if can_delete:
            for i, p in enumerate(pqs):
                if i == 0:
                    message += u'The following packages will also be deleted:'
                    message += u'<br />'
                else:
                    message += u', '
                message += p.__unicode__()
            for i, t in enumerate(tqs):
                if i == 0:
                    if message:
                        message += u'<p />'
                    message += u'The following transfers will also be deleted:'
                    message += u'<br />'
                else:
                    message += u', '
                message += t.__unicode__()

        return (can_delete, message)

    def delete(self, using=None, *args, **kwargs):

        user = kwargs.pop('user', None)
        bcqs = BevChunk.objects.filter(src_tank__isnull=True, brew=self)
        # Check if the brew has been packaged out of the FV
        pbcqs = PackageBevChunk.objects.filter(bev_chunk__in=bcqs)
        pqs = Package.objects.filter(packagebevchunk__in=pbcqs)
        # Check if the brew has been transferred out of the FV
        tbcqs = TransferBevChunk.objects.filter(bev_chunk__in=bcqs)
        # The transfers from this FV
        tqs = Transfer.objects.filter(transferbevchunk__in=tbcqs)
        bcqs = BevChunk.objects.filter(brew=self)
        btqs = list(BevTank.objects.filter(bevtank_cur_tank__brew=self))
        brews_in_bt = list(Brew.objects.filter(
            bevchunk__cur_tank__in=btqs,
            bevchunk__src_tank__isnull=True).order_by('create_date', 'id'))
        eqs = Event.objects.filter(brew=self)
        prqs = Process.objects.filter(
            bev_tank__bevtank_cur_tank__brew=self)
        for transfer in tqs:
            transfer.delete()
        for package in pqs:
            package.delete(user=user)
        for p in prqs:
            e = Event.objects.get(
                event_type__name='Process',
                record_id=p.id
            )
            e.delete()
            p.delete()
        for bc in bcqs:
            bc.delete()
        # Check for blend. Can't delete dest tank
        for bt in btqs:
            if not BevChunk.objects.filter(cur_tank=bt):
                for m in Measurement.objects.filter(bev_tank=bt):
                    ms = Measurement.objects.filter(
                        bev_tank=bt,
                        parent=m
                    )
                    for cm in ms:
                        cm.delete()
                    m.delete()
                bt.delete()
            else:
                # Leave measurements with the tank. May result in measurements
                # being left that need to be deleted manually
                # Update OG if first brew in blend deleted
                if brews_in_bt[0] == self:
                    new_og = brews_in_bt[1].starting_density
                    densities = Measurement.objects.filter(
                        bev_tank=bt,
                        measurement_type__name='Density').order_by('id')
                    first_density = densities[0]
                    first_density.value = new_og
                    first_density.save()
        for e in eqs:
            e.delete()
        models.Model.delete(self, using=using)


class TaskType(models.Model):
    name = models.CharField(max_length=30, unique=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class ProcessType(models.Model):
    name = models.CharField(max_length=30, unique=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class Process(models.Model):
    create_date = models.DateField()
    bev_tank = models.ForeignKey(BevTank, on_delete=models.PROTECT)
    type = models.ForeignKey(ProcessType)
    active = models.BooleanField(default=True)
    # TODO Remove active


class Transfer(models.Model):
    transfer_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def get_bev_chunks(self):
        return BevChunk.objects.filter(transfer=self)

    def get_volume(self):
        volume = 0.0
        bev_chunks = BevChunk.objects.filter(transfer=self)
        for item in bev_chunks:
            volume += item.volume
        return volume

    def set_volume(self, vol):
        cur_volume = self.get_volume()
        # TODO: Division by zero a problem here
        proportion = float(vol) / cur_volume
        for bc in BevChunk.objects.filter(transfer=self):
            bc.volume *= proportion
            bc.save()
            # Update transferbevchunk
            try:
                tbc = TransferBevChunk.objects.get(
                    bev_chunk=bc.parent, transfer=self)
                tbc.volume = bc.volume
                tbc.save()
            except:
                pass

    def get_transfer_date(self):
        bev_chunks = BevChunk.objects.filter(transfer=self)
        return bev_chunks[0].create_date

    def get_src_tank(self):
        bev_chunks = BevChunk.objects.filter(transfer=self)
        return bev_chunks[0].src_tank

    def get_src_status(self):
        bev_chunks = BevChunk.objects.filter(transfer=self)
        return bev_chunks[0].src_tank.status

    def get_src_empty(self):
        bev_chunks = BevChunk.objects.filter(transfer=self)
        if bev_chunks[0].src_tank.empty_date:
            return True
        else:
            return False

    def get_dest_tank(self):
        bev_chunks = BevChunk.objects.filter(transfer=self)
        return bev_chunks[0].cur_tank.tank

    def get_dest_bevtank(self):
        bev_chunks = BevChunk.objects.filter(transfer=self)
        return bev_chunks[0].cur_tank

    def get_dest_product_type(self):
        bev_chunks = BevChunk.objects.filter(transfer=self)
        return bev_chunks[0].cur_tank.product_type

    def get_dest_status(self):
        bev_chunks = BevChunk.objects.filter(transfer=self)
        return bev_chunks[0].cur_tank.status

    def __unicode__(self):
        return u'%s to %s' % (self.get_src_tank(), self.get_dest_tank())

    def can_delete(self):
        """
        checks to see if the transfer can be deleted.
        Returns a tuple with True/False at 0
        and a message at 1
        """
        message = u''
        can_delete = True

        bcqs = BevChunk.objects.filter(transfer=self)
        # Check if the transfered beer has been packaged directly
        pbcqs = PackageBevChunk.objects.filter(bev_chunk__in=bcqs)
        pqs = Package.objects.filter(packagebevchunk__in=pbcqs)
        # Check to see if any packages have been checked out
        coqs = CheckOut.objects.filter(package__in=pqs)
        # Check if the beer has been transferred directly
        tbcqs = TransferBevChunk.objects.filter(bev_chunk__in=bcqs)
        tqs = Transfer.objects.filter(transferbevchunk__in=tbcqs)
        # The bevchunks created by the transfers
        t_bcqs = BevChunk.objects.filter(transfer__in=tqs)
        # Check to see if these have been packaged...
        t_pbcqs = PackageBevChunk.objects.filter(bev_chunk__in=t_bcqs)
        # ...or transferred
        t_tbcqs = TransferBevChunk.objects.filter(bev_chunk__in=t_bcqs)
        if coqs:
            can_delete = False
            pstr = u''
            for i, co in enumerate(coqs):
                if i == 0:
                    pstr += u'<a href = "{0}">{1}</a>'.format(
                        reverse(
                            'package_delete',
                            args=(co.package.pk,)),
                        co.package)
                else:
                    pstr += u', <a href = "{0}">{1}</a>'.format(
                        reverse(
                            'package_delete',
                            args=(co.package.pk,)),
                        co.package)
            message += (
                u'{0} has been packaged.'.format(self) +
                u' The following packages have been' +
                u' checked out. Please delete the packages and checkouts' +
                u' before deleting this transfer:<br />' + pstr)
        if t_pbcqs:
            can_delete = False
            tstr = ''
            for i, p in enumerate(t_pbcqs):
                if i == 0:
                    tstr += u'<a href = "{0}">{1}</a>'.format(
                        reverse(
                            'transfer_delete',
                            args=(p.bev_chunk.transfer.pk,)),
                        p.bev_chunk.transfer)
                else:
                    tstr += u', <a href = "{0}">{1}</a>'.format(
                        reverse(
                            'transfer_delete',
                            args=(p.bev_chunk.transfer.pk,)),
                        p.bev_chunk.transfer)
            if message:
                message += u'<p />'
            message += (
                u'{} has been transferred.'.format(self) +
                u' The following transfers have been packaged. Please delete' +
                u' the transfers and packages before deleting this transfer:' +
                u'<br />' + tstr)
        if t_tbcqs:
            can_delete = False
            tstr = ''
            for i, t in enumerate(t_tbcqs):
                if i == 0:
                    tstr += u'<a href = "{0}">{1}</a>'.format(
                        reverse(
                            'transfer_delete',
                            args=(t.bev_chunk.transfer.pk,)),
                        t.bev_chunk.transfer)
                else:
                    tstr += u', <a href = "{0}">{1}</a>'.format(
                        reverse(
                            'transfer_delete',
                            args=(t.bev_chunk.transfer.pk,)),
                        t.bev_chunk.transfer)
            if message:
                message += u'<p />'
            message += (
                u'{} has been transferred.'.format(self) +
                u' The following transfers have been transferred. Please ' +
                u'delete the transfers before deleting this transfer:<br />' +
                tstr)
        # Add a warning message if deleting more than just the transfer
        if can_delete:
            for i, p in enumerate(pqs):
                if i == 0:
                    message += u'The following packages will also be deleted:'
                    message += u'<br />'
                else:
                    message += u', '
                message += p.__unicode__()
            for i, t in enumerate(tqs):
                if i == 0:
                    if message:
                        message += u'<p />'
                    message += u'The following transfers will also be deleted:'
                    message += u'<br />'
                else:
                    message += u', '
                message += t.__unicode__()
        return (can_delete, message)

    def delete(self, using=None, *args, **kwargs):

        user = kwargs.pop('user', None)

        # The bevchunks created by the transfer
        bcqs = BevChunk.objects.filter(transfer=self)
        # Check if the transfered beer has been packaged directly
        pbcqs = PackageBevChunk.objects.filter(bev_chunk__in=bcqs)
        pqs = Package.objects.filter(packagebevchunk__in=pbcqs)
        # Check if the beer has been transferred directly
        tbcqs = TransferBevChunk.objects.filter(bev_chunk__in=bcqs)
        tqs = Transfer.objects.filter(transferbevchunk__in=tbcqs)
        bt = BevTank.objects.filter(
            bevtank_cur_tank__transfer=self)[0]
        all_bc = list(BevChunk.objects.filter(
            cur_tank=bt).order_by('create_date', 'id'))
        blend = bcqs.count() != len(all_bc)
        initial_bc = all_bc[0] in bcqs
        new_og = Measurement.objects.filter(
            bev_tank=bt,
            measurement_type__name='Density').order_by('id')[0]
        if blend and initial_bc:
            for bc in all_bc:
                if bc not in bcqs:
                    if bc.src_tank:  # This is a transfer
                        new_og = Measurement()
                        new_og.value = bc.src_tank.get_density(
                            self.transfer_date).value
                        new_og.measurement_date = bc.create_date
                        new_og.measurement_type = \
                            MeasurementType.objects.get(name='Density')
                        new_og.bev_tank = bt
                    else:  # This is a brew
                        new_og = Measurement(value=bc.brew.starting_density)
                        new_og.measurement_date = bc.brew.create_date
                        new_og.measurement_type = \
                            MeasurementType.objects.get(name='Density')
                        new_og.bev_tank = bt
                        break

        for transfer in tqs:
            transfer.delete()
        for package in pqs:
            package.delete(user=user)

        # order by -parent as there may be protected errors if deleted
        # in wrong order
        mqs = Measurement.objects.filter(
            bev_tank=bt).order_by('-parent')
        e = Event.objects.get(
            event_type__name="Transfer",
            record_id=self.id)
        tbcqs = TransferBevChunk.objects.filter(transfer=self)
        e.delete()
        for bc in bcqs:
            # If the transfer emptied the source tank, un-empty it
            # and remove the 0 volume measurement
            if bc.src_tank.empty_date:
                m = Measurement.objects.filter(
                    bev_tank=bc.src_tank,
                    value=0.0, measurement_type__name='Volume',
                    measurement_date=bc.src_tank.empty_date)
                for i in m:
                    # Delete waste bev chunk(s)
                    wbc = WasteBevChunk.objects.filter(
                        measurement=i)
                    for o in wbc:
                        o.delete()
                    i.delete()
                bc.src_tank.empty_date = None
                bc.src_tank.save()
            bc.delete()
        for tbc in tbcqs:
            tbc.delete()
        # Check for blend. Can't delete dest tank
        if not blend:
            for m in mqs:
                m.delete()
            bt.delete()
        else:
            # Update OG if this is the first beer in the tank
            if initial_bc:
                old_og = Measurement.objects.filter(
                    bev_tank=bt,
                    measurement_type__name='Density').earliest('id')
                for m in Measurement.objects.filter(parent=old_og):
                    m.delete()
                old_og.delete()
                new_og.save()
                new_og.calculate_alcohol(new_og.measurement_date)
        models.Model.delete(self, using=using)


class BevChunk(models.Model):
    brew = models.ForeignKey(Brew)
    starting_density = models.DecimalField(
        null=True, blank=True,
        max_digits=5, decimal_places=4)
    src_tank = models.ForeignKey(
        BevTank, related_name='bevtank_src_tank',
        null=True, on_delete=models.PROTECT)
    cur_tank = models.ForeignKey(
        BevTank, related_name='bevtank_cur_tank',
        on_delete=models.PROTECT)
    volume = models.FloatField()
    create_date = models.DateField()
    transfer = models.ForeignKey(
        Transfer, null=True, blank=True,
        on_delete=models.PROTECT)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.PROTECT)

    def get_volume(self, date, measurement=None, package=None):
        # Transferred volume
        tvol = TransferBevChunk.objects.filter(
            bev_chunk=self,
            transfer__transfer_date__lte=date).aggregate(
            Sum('volume'))['volume__sum']
        # Packaged volume
        pvolqs = PackageBevChunk.objects.filter(
            bev_chunk=self,
            package__create_date__lte=date)
        if package:
            pvolqs = pvolqs.exclude(package=package)
        pvol = pvolqs.aggregate(Sum('volume'))['volume__sum']
        # Waste volume
        wvolqs = WasteBevChunk.objects.filter(bev_chunk=self,
            measurement__measurement_date__lte=date)
        if measurement:
            wvolqs = wvolqs.exclude(measurement=measurement)
        wvol = wvolqs.aggregate(Sum('volume'))['volume__sum']

        return self.volume - (pvol or 0) - (tvol or 0) - (wvol or 0)

    def get_volume_today(self):
        return self.get_volume(datetime.now())

    def get_proportion(self, date):
        part = self.get_volume(date)
        total = self.cur_tank.get_volume(date)
        return part / total

    def transferred_or_packaged(self, date):
        tbc = TransferBevChunk.objects.filter(bev_chunk=self)
        pbc = PackageBevChunk.objects.filter(bev_chunk=self)
        if tbc or pbc:
            return True
        else:
            return False

    def transferred_or_packaged_today(self):
        return self.transferred_or_packaged(datetime.now())


class TransferBevChunk(models.Model):
    transfer = models.ForeignKey(Transfer, on_delete=models.PROTECT)
    bev_chunk = models.ForeignKey(BevChunk, on_delete=models.PROTECT)
    volume = models.FloatField()


class MeasurementType(models.Model):
    name = models.CharField(max_length=30)
    unit_type = models.ForeignKey(UnitType, null=True, blank=True,
                                  on_delete=models.PROTECT)

    def __unicode__(self):
        return self.name


class Measurement(models.Model):
    measurement_date = models.DateField()
    bev_tank = models.ForeignKey(BevTank, on_delete=models.PROTECT)
    value = models.FloatField()
    measurement_type = models.ForeignKey(MeasurementType)
    notes = models.TextField(null=True, blank=True)
    # eg for alcohol estimated from density measurement
    parent = models.ForeignKey(
        'self', on_delete=models.PROTECT,
        null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return 'Measurement: {0} ({1})'.format(
            self.measurement_type.name, self.value)

    def calculate_alcohol(self, date):
        bev_chunks = self.bev_tank.get_bev_chunks()
        alc_vol = 0.0
        factor = float(Setting.objects.get(
            site=Site.objects.get_current()).sg_to_abv_factor)

        # TODO: Giving false Readings for blends
        # e.g. if a 1.050 gets transferred onto a 1.042 it calculates an abv
        # even though both may not have fermented at all
        for bc in bev_chunks:
            og = bc.starting_density
            sg = bc.cur_tank.get_density(date).value
            alc_vol += float(float(og) - sg) * factor * bc.volume / 100

        if self.bev_tank.get_original_volume():
            abv = alc_vol / self.bev_tank.get_original_volume() * 100
        else:
            # Avoid div by zero error
            abv = 0.0

        ams = Measurement.objects.filter(parent=self)
        # Adjust alcohol measurements already in the system
        if ams:
            for am in ams:
                am.value = abv
                am.save()
        # Create new alcohol measurement if none already exist
        else:
            am = Measurement()
            am.measurement_type = MeasurementType.objects.get(name="Alcohol")
            am.measurement_date = self.measurement_date
            am.bev_tank = self.bev_tank
            am.value = abv
            am.user = None
            am.parent = self.bev_tank.get_density(date)
            am.save()


class BevTankDensity(models.Model):
    bev_tank = models.ForeignKey(BevTank, on_delete=models.PROTECT)
    measurement_date = models.DateField()
    density = models.FloatField(null=True, blank=True)
    alcohol = models.FloatField(null=True, blank=True)
    alcohol_calc = models.FloatField(null=True, blank=True)
    set_temp = models.FloatField(null=True, blank=True)
    actual_temp = models.FloatField(null=True, blank=True)
    co2 = models.FloatField(null=True, blank=True)
    o2 = models.FloatField(null=True, blank=True)
    actual_pressure = models.FloatField(null=True, blank=True)

    def calculate_alcohol(self, date):
        bev_chunks = self.bev_tank.get_bev_chunks()
        alc_vol = 0.0
        factor = (float(Setting.objects.get(site=Site.objects.get_current()).
                       sg_to_abv_factor))

        for bc in bev_chunks:
            og = bc.brew.starting_density
            if bc.src_tank:
                sg = bc.src_tank.get_density(date)
            else:
                sg = og
            alc_vol += (og - sg) * factor * bc.volume / 100

        abv = alc_vol / self.bev_tank.get_original_volume() * 100
        self.alcohol_calc = abv


class Submission(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    submit_date = models.DateField()
    notes = models.TextField(null=True, blank=True)

    def get_rows(self):
        rows = (CheckOut.objects.filter(submission=self, exempt=False).
        values('package__bev_tank__product_type__name').annotate(Count('id')))
        return rows.count()

    def get_row(self, index):
        rows = (CheckOut.objects.filter(submission=self, exempt=False).
            values('package__bev_tank__product_type').
            annotate(total=Sum('volume')).
            order_by('package__bev_tank__product_type'))
        try:
            row = rows[index]
        except:
            row = None
        return row

    def __unicode__(self):
        return u'%s - %s' % (self.start_date, self.end_date)


class PackageType(models.Model):
    name = models.CharField(max_length=30, unique=True)
    variable_size = models.BooleanField(default=False)
    volume = models.FloatField(null=True, blank=True)
    active = models.BooleanField(default=True)
    legacy = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class PackageManager(models.Manager):
    def available_packages(self, prod, pack,
        date=pytz.utc.localize(datetime.utcnow()), units=None):
        qs = super(PackageManager, self).get_queryset()
        qs = qs.filter(bev_tank__product_type=prod, package_type=pack)
        result_list = []
        items_avail = 0
        for o in qs:
            if not o.is_complete(date):
                result_list.append(o)
                items_avail += o.get_items_in_stock(date)
        if units != None:
            if items_avail < units:
                raise ValueError(items_avail)
        return result_list

    def available_product_packages(self):
        """
        returns distinct json of dictionaries of product_type and package_types
        available
        """
        packages = super(PackageManager, self).get_queryset().annotate(
            checkedoutsum=Sum(
            'checkout__volume')).annotate(checkedoutcount=Count(
            'checkout__volume')).filter(Q(volume__gt=F('checkedoutsum')) |
            Q(checkedoutcount=0)
            ).order_by('create_date').distinct()

        product_packages = packages.values('bev_tank__product_type',
            'bev_tank__product_type__name', 'package_type',
            'package_type__name').order_by(
            'bev_tank__product_type', 'package_type').distinct()

        products = []
        for pp in product_packages:
            if not any(o['product_type']['pk'] == pp['bev_tank__product_type'] for o in products):
                prt = {}
                prt['pk'] = pp['bev_tank__product_type']
                prt['name'] = pp['bev_tank__product_type__name']
                outer_dict = {}
                products.append(outer_dict)
                outer_dict['product_type'] = prt
                pkt_list = []
                pkt = {}
                pkt['pk'] = pp['package_type']
                pkt['name'] = pp['package_type__name']
                pkt_list.append(pkt)
            else:
                pkt = {}
                pkt['pk'] = pp['package_type']
                pkt['name'] = pp['package_type__name']
                pkt_list.append(pkt)
            outer_dict['package_types'] = pkt_list

        output = json.dumps(products)
        return output

    def packages_in_stock(self):
        # Only display those that have an outstanding balance
        # Had to use Count to get around the null Sums. Query must be performed
        # in this order
        pqs = super(PackageManager, self).get_queryset().annotate(
            checkedoutsum=Sum(
            'checkout__volume')).annotate(checkedoutcount=Count(
            'checkout__volume')).filter(Q(volume__gt=F('checkedoutsum')) |
            Q(checkedoutcount=0)
            ).order_by('create_date').distinct()
        return pqs


class Package(models.Model):
    objects = PackageManager()

    def _get_item_count(self):
        if self.package_type.volume:
            return self.volume / self.package_type.volume
        else:
            return self.volume

    bev_tank = models.ForeignKey(BevTank, on_delete=models.PROTECT)
    create_date = models.DateField()
    volume = models.FloatField()
    item_count = property(_get_item_count)
    package_type = models.ForeignKey(PackageType, on_delete=models.PROTECT)
    left_cca = models.DateField(null=True, blank=True)
    submission = models.ForeignKey(Submission, null=True, blank=True,
                                   on_delete=models.PROTECT)
    notes = models.TextField(null=True, blank=True)

    def get_items_in_stock(self, date):
        check_out_vol = CheckOut.objects.filter(package=self,
            create_date__lte=date).aggregate(Sum('volume'))['volume__sum']
        in_stock = self.volume - (check_out_vol or 0)
        if self.package_type.volume:
            in_stock = in_stock / self.package_type.volume
        return in_stock

    def is_complete(self, date):
        check_out_vol = CheckOut.objects.filter(package=self,
            create_date__lte=date).aggregate(Sum('volume'))['volume__sum']
        if check_out_vol < self.volume:
            return False
        else:
            return True

    def is_complete_today(self):
        return self.is_complete(datetime.now())

    def has_checkout(self, date):
        check_outs = CheckOut.objects.filter(package=self,
            create_date__lte=date)
        if check_outs:
            return True
        else:
            return False

    def has_checkout_today(self):
        return self.has_checkout(datetime.now())

    def get_src_empty(self):
        if self.bev_tank.empty_date:
            return True
        else:
            return False

    def get_name(self):
        return '%s: %s (%s)' % (self.bev_tank.name,
            self.package_type.name, self.create_date.strftime('%d %b'))

    def get_name_date_stock(self):
        return '%s: %s (%s in stock)' % (self.bev_tank.name,
            self.create_date.strftime('%d %b'),
            self.get_items_in_stock(datetime.now()))

    def __unicode__(self):
        return '%s: %s (%s in stock)' % (self.bev_tank.name,
            self.package_type.name, self.get_items_in_stock(datetime.now()))

    def save(self, *args, **kwargs):
        measurement = kwargs.pop('measurement', None)
        user = kwargs.pop('user', None)

        # Create the PackageTransaction for billing purposes
        from billing.models import PackageTransaction
        pt = PackageTransaction()
        pt.package_type = self.package_type.name
        pt.user_id = user.id
        pt.user_name = user.username
        pt.datetime = pytz.utc.localize(datetime.utcnow())
        pt.tank = self.bev_tank.tank.name
        pt.name = self.bev_tank.name
        pt.notes = self.notes
        pt.billed = None
        pt.package_date = self.create_date
        # For new Packages
        if self.pk is None:
            pt.transaction_type = "Create"
            pt.volume = self.volume
        # For updates
        else:
            pt.transaction_type = "Update"
            prev_volume = Package.objects.get(pk=self.pk).volume
            pt.volume = float(self.volume) - prev_volume

        super(Package, self).save(*args, **kwargs)

        pt.package_id = self.id
        pt.save()
        bc = self.bev_tank.get_bev_chunks()

        # Get proportion this package is of the tank volume at the time
        # of packaging. Make sure we ignore the empty volume if we emptied the
        # tank
        p = float(self.volume) / (
            self.bev_tank.get_volume(
                self.create_date, measurement=measurement, package=self))

        for c in bc:
            # Simple case for one-bevchunk bevtanks
            if bc.count() == 1:
                vol = self.volume
            else:
                # Multiply each bevchunk's volume at the time of packaging
                # by the proportion removed from the tank
                vol = (c.get_volume(self.create_date, measurement=measurement,
                    package=self)) * p
            try:  # If we are updating an existing Package
                pbc = PackageBevChunk.objects.get(package=self, bev_chunk=c)
                pbc.volume = vol
            except PackageBevChunk.DoesNotExist:  # If this is a new Package
                pbc = PackageBevChunk(package=self, bev_chunk=c, volume=vol)
            pbc.save()

    def can_delete(self):
        """
        checks to see if the package can be deleted.
        Returns a tuple with True/False at 0
        and a message at 1
        """
        message = u''
        can_delete = True

        # Check to see if the package has been checked out
        coqs = CheckOut.objects.filter(package=self)
        from orders.models import Shipment
        shqs = Shipment.objects.filter(shipmentline__checkout__in=coqs)
        # If so, can't delete
        if coqs:
            can_delete = False
            pstr = u''
            for i, sh in enumerate(shqs):
                if i == 0:
                    pstr += u'<a href = "{0}">{1}</a>'.format(
                        reverse('shipment_delete', args=(sh.pk,)), sh)
                else:
                    pstr += u', <a href = "{0}">{1}</a>'.format(
                        reverse('shipment_delete', args=(sh.pk,)), sh)
            message += (
                u'{0} has been checked out.'.format(self) +
                u' The following shipments contain this package.' +
                u' Please delete the shipments' +
                u' before deleting this package:<br />' + pstr)
        return (can_delete, message)

    def delete(self, using=None, *args, **kwargs):

        user = kwargs.pop('user', None)
        from billing.models import PackageTransaction
        pt = PackageTransaction()
        pt.package_id = self.id
        pt.package_type = self.package_type.name
        pt.user_id = user.id
        pt.user_name = user.username
        pt.datetime = pytz.utc.localize(datetime.utcnow())
        pt.tank = self.bev_tank.tank.name
        pt.name = self.bev_tank.name
        pt.notes = self.notes
        # For new Packages
        pt.transaction_type = "Delete"
        pt.package_date = self.create_date
        pt.volume = -self.volume
        pt.billed = None
        pt.save()

        e = Event.objects.get(
            event_type__name="Package",
            record_id=self.id)
        pbcqs = PackageBevChunk.objects.filter(package=self)
        for pbc in pbcqs:
            if pbc.bev_chunk.cur_tank.empty_date:
                m = Measurement.objects.filter(
                    bev_tank=pbc.bev_chunk.cur_tank,
                    value=0.0, measurement_type__name='Volume',
                    measurement_date=pbc.bev_chunk.cur_tank.empty_date)
                for i in m:
                    # Delete waste bev chunk(s)
                    wbc = WasteBevChunk.objects.filter(
                        measurement=i)
                    for o in wbc:
                        o.delete()
                    i.delete()
                pbc.bev_chunk.cur_tank.empty_date = None
                pbc.bev_chunk.cur_tank.save()
            pbc.delete()
        e.delete()
        models.Model.delete(self, using=using)


class PackageBevChunk(models.Model):
    package = models.ForeignKey(Package, on_delete=models.PROTECT)
    bev_chunk = models.ForeignKey(BevChunk, on_delete=models.PROTECT)
    volume = models.FloatField()


class PackageGroup(models.Model):
    package = models.ForeignKey(Package, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    count = models.IntegerField()


class CheckOut(models.Model):

    def _get_item_count(self):
        if self.package.package_type.volume:
            return self.volume / self.package.package_type.volume
        else:
            return self.volume

    package = models.ForeignKey(Package, on_delete=models.PROTECT)
    create_date = models.DateField()
    volume = models.FloatField()
    item_count = property(_get_item_count)
    submission = models.ForeignKey(Submission, null=True, blank=True,
                                   on_delete=models.PROTECT)
    exempt = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __unicode__(self):
        # TODO: un hard code L
        return '%s: %s %sL' % (
            self.package.bev_tank.name,
            self.package.package_type.name, self.volume)

    def save(self, *args, **kwargs):
        super(CheckOut, self).save(*args, **kwargs)
        # Save the checkout's checkout bev chunks
        pbcs = PackageBevChunk.objects.filter(package=self.package)
        for pbc in pbcs:
            vol = self.volume * pbc.volume / self.package.volume
            try:
                cbc = CheckOutBevChunk.objects.get(
                    checkout=self, bev_chunk=pbc.bev_chunk)
                cbc.volume = vol
            except:
                cbc = CheckOutBevChunk(
                    checkout=self, bev_chunk=pbc.bev_chunk, volume=vol)
            cbc.save()


class CheckOutBevChunk(models.Model):
    checkout = models.ForeignKey(CheckOut)
    bev_chunk = models.ForeignKey(BevChunk)
    volume = models.FloatField()


class WasteBevChunk(models.Model):
    measurement = models.ForeignKey(Measurement)
    bev_chunk = models.ForeignKey(BevChunk)
    volume = models.FloatField()


class CalendarViewOption(models.Model):
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class SubmissionFrequencyOption(models.Model):
    name = models.CharField(max_length=30)
    value = models.IntegerField()

    def __unicode__(self):
        return self.name


class BatchNumberingOption(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class Setting(models.Model):
    site = models.OneToOneField(Site)
    calendar_view = models.ForeignKey(CalendarViewOption)
    list_length = models.IntegerField(default=10)
    batch_numbering = models.ForeignKey(BatchNumberingOption)
    volume_unit = models.ForeignKey(Unit,
        limit_choices_to={'type': settings.VOLUME_UNIT_TYPE},
        related_name="vu")
    temperature_unit = models.ForeignKey(Unit,
        limit_choices_to={'type': settings.TEMPERATURE_UNIT_TYPE},
        related_name="tu")
    density_unit = models.ForeignKey(Unit,
        limit_choices_to={'type': settings.DENSITY_UNIT_TYPE},
        related_name="du")
    sg_to_abv_factor = models.FloatField()
    submission_frequency = models.ForeignKey(SubmissionFrequencyOption)
    submit_stock_on_hand = models.BooleanField()


class EventType(models.Model):
    name = models.CharField(max_length=30)
    active = models.BooleanField()
    color = models.CharField(max_length=20, null=True, blank=True)
    backgroundColor = models.CharField(max_length=20, null=True, blank=True)
    borderColor = models.CharField(max_length=20, null=True, blank=True)
    textColor = models.CharField(max_length=20, null=True, blank=True)


class Event(models.Model):
    title = models.CharField(max_length=100)
    event_type = models.ForeignKey(EventType)
    scheduled = models.BooleanField(default=False)
    process_type = models.ForeignKey(ProcessType, null=True, blank=True)
    task_type = models.ForeignKey(TaskType, null=True, blank=True)
    brew = models.ForeignKey(Brew, null=True, blank=True)
    bev_tank = models.ForeignKey(BevTank, null=True, blank=True)
    bev_type = models.ForeignKey(BevType, null=True, blank=True)
    dest_tank = models.ForeignKey(Tank, null=True, blank=True)
    allDay = models.NullBooleanField(null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    editable = models.NullBooleanField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    record_id = models.IntegerField(null=True, blank=True)

