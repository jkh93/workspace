# coding: utf-8
from django.conf.urls import patterns, url, include
import main.views as mv
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from quickbev.urls_files import washing_urls, orders_urls
from django.views.generic import TemplateView
from django.http import HttpResponse


urlpatterns = patterns('',

    (r'^robots\.txt$', lambda r: HttpResponse(
        "User-agent: *\nDisallow: /", mimetype="text/plain")),

    url(r'^brewery_setup/$',
        TemplateView.as_view(
            template_name='navigation/brewery_setup.html'),
            name="brewery_setup"),
    url(r'^sales_setup/$',
        TemplateView.as_view(
            template_name='navigation/sales_setup.html'),
            name="sales_setup"),

    url(r'^$', mv.home, name='home'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name="logout"),
    url(r'^password/$', 'django.contrib.auth.views.password_change',
        name="password_change"),
    url(r'^password/done$', 'django.contrib.auth.views.password_change_done',
        name="password_change_done"),
    url(r'^password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/password/reset/done/'},
        name="password_reset"),
    (r'^password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/password/done/'}),
    (r'^password/done/$',
        'django.contrib.auth.views.password_reset_complete'),

    url(r'^user/create/$', mv.user_create, name="user_create"),
    url(r'^user/list/$', mv.user_list, name="user_list"),
    url(r'^user/(?P<pk>\d+)/$', mv.user_detail, name="user_detail"),

    url(r'^group/create/$', mv.group_detail,
        {'pk': None}, name="group_create"),
    url(r'^group/list/$', mv.group_list, name="group_list"),
    url(r'^group/(?P<pk>\d+)/$', mv.group_detail, name="group_detail"),

    url(r'^tank/json/(?P<name>.+)/$', mv.tank_detail, name='tank_detail_json'),
    url(r'^tank/list/$', mv.tank_list, name='tank_list'),
    url(r'^tank/create/$', mv.tank_create, {'pk': None}, name='tank_create'),
    url(r'^tank/update/(?P<pk>\d+)/$', mv.tank_create, name='tank_update'),
    url(r'^tank/delete/(?P<pk>\d+)/$', mv.tank_delete, name='tank_delete'),

    url(r'^location/list/$', mv.location_list, name="location_list"),
    url(r'^location/create/$', mv.location_create, {'pk': None},
        name='location_create'),
    url(r'^location/update/(?P<pk>\d+)/$', mv.location_create,
        name='location_update'),
    url(r'^location/delete/(?P<pk>\d+)/$', mv.location_delete,
        name='location_delete'),

    url(r'^bevtype/list/$', mv.bevtype_list, name='bevtype_list'),
    url(r'^bevtype/create/$', mv.bevtype_create,
        {'pk': None}, name='bevtype_create'),
    url(r'^bevtype/update/(?P<pk>\d+)/$', mv.bevtype_create,
        name='bevtype_update'),
    url(r'^bevtype/delete/(?P<pk>\d+)/$', mv.bevtype_delete,
        name='bevtype_delete'),

    url(r'^producttype/list/$', mv.producttype_list, name="producttype_list"),
    url(r'^producttype/create/$', mv.producttype_create, {'pk': None},
        name='producttype_create'),
    url(r'^producttype/update/(?P<pk>\d+)/$', mv.producttype_create,
        name='producttype_update'),
    url(r'^producttype/delete/(?P<pk>\d+)/$', mv.producttype_delete,
        name='producttype_delete'),

    url(r'^packagetype/list/$', mv.PackageTypeListView.as_view(),
        name='packagetype_list'),
    url(r'^packagetype/create/$', mv.PackageTypeCreateView.as_view(),
        name='packagetype_create'),
    url(r'^packagetype/update/(?P<pk>\d+)/$',
        mv.PackageTypeUpdateView.as_view(),
        name='packagetype_update'),
    url(r'^packagetype/delete/(?P<pk>\d+)/$',
        mv.PackageTypeDeleteView.as_view(),
        name='packagetype_delete'),

    url(r'^brew/report/$', mv.brew_report, name='brew_report'),
    url(r'^brew/list/$', mv.brew_list, name='brew_list'),
    url(r'^brew/create/$', mv.brew_create, {'event': None, 'pk': None},
        name='brew_create'),
    url(r'^brew/create/(?P<event>\d+)/$',
        mv.brew_create, {'pk': None}, name='brew_create_with_event'),
    url(r'^brew/edit/(?P<pk>\d+)/$', mv.brew_create, {'event': None},
        name='brew_edit'),
    url(r'^brew/(?P<pk>\d+)/$', mv.BrewDetailView.as_view(),
        name='brew_detail'),
    url(r'^brew/view/(?P<pk>\d+)/$', mv.brew_detail, name='brew_view'),
    url(r'^brew/view/recipe/(?P<pk>\d+)/$', mv.brew_create,
        {'detail': True, 'event': None}, name='brew_recipe_detail'),
    url((r'^brew/schedule/(?P<date>(?:19|20)\d\d[- /.](?:[1-9]|1[012])'
         '[- /.](?:[1-9]|[12][0-9]|3[01]))/$'),
        mv.brew_schedule, name='brew_schedule'),
    url(r'^brew/schedule/$',
        mv.brew_schedule, {'date': None}, name='brew_schedule'),
    url(r'^brew/delete/(?P<pk>\d+)/$', mv.brew_delete,
        name='brew_delete'),

    url(r'^event_type/list/$', mv.event_type_list, name="event_type_list"),
    url(r'^event_type/create/$', mv.event_type_create, {'pk': None},
        name='event_type_create'),
    url(r'^event_type/update/(?P<pk>\d+)/$', mv.event_type_create,
        name='event_type_update'),
    url(r'^event_type/delete/(?P<pk>\d+)/$', mv.event_type_delete,
        name='event_type_delete'),
    url(r'^process_type/create/$', mv.process_type_create, {'name': None},
        name='process_type_create'),
    url(r'^process_type/update/(?P<name>.+)/$', mv.process_type_create,
        name='process_type_update'),
    url(r'^task_type/create/$', mv.task_type_create, {'name': None},
        name='task_type_create'),
    url(r'^task_type/update/(?P<name>.+)/$', mv.task_type_create,
        name='task_type_update'),

    url(r'^sales_item/list/$', mv.SalesItemListView.as_view(),
        name="sales_item_list"),
    url(r'^sales_item/create/$', mv.SalesItemCreateView.as_view(),
        name="sales_item_create"),
    url(r'^sales_item/update/(?P<pk>\d+)/$', mv.SalesItemUpdateView.as_view(),
        name='sales_item_update'),
    url(r'^sales_item/delete/(?P<pk>\d+)/$', mv.SalesItemDeleteView.as_view(),
        name='sales_item_delete'),

    url(r'^process/create/(?P<event>\d+)/$', mv.process_create,
        name='process_create_with_event'),
    url(r'^process/create/$', mv.process_create, {'event': None},
        name='process_create'),
    url((r'^process/schedule/((?:19|20)\d\d[- /.](?:[1-9]|1[012])[- /.]'
         '(?:[1-9]|[12][0-9]|3[01]))/$'),
        mv.process_schedule, name='process_schedule'),
    url((r'^process/schedule/$'), mv.process_schedule, {'date': None},
        name='process_schedule'),
    url(r'^process/(?P<pk>\d+)/$',
        mv.process_detail, name='process_detail'),

    url((r'^task/schedule/((?:19|20)\d\d[- /.](?:[1-9]|1[012])'
         '[- /.](?:[1-9]|[12][0-9]|3[01]))/$'),
        mv.task_schedule, name='task_schedule_with_date'),
    url(r'^task/schedule/$',
        mv.task_schedule, {'date': None}, name='task_schedule'),
    url(r'^task/create/(?P<event>\d+)/$', mv.task_create,
        name='task_create_with_event'),
    url(r'^task/create/$', mv.task_create, {'event': None},
        name='task_create'),

    url(r'^schedule/$', mv.schedule, name='schedule'),

    url(r'^transfer/list/$', mv.transfer_list, name='transfer_list'),
    url(r'^transfer/create/$', mv.transfer, {'event': None, 'pk': None},
        name='transfer_create'),
    url(r'^transfer/create/(?P<event>\d+)/$',
        mv.transfer, {'pk': None}, name='transfer_create_with_event'),
    url(r'^transfer/edit/(?P<pk>\d+)/$', mv.transfer, {'event': None},
        name='transfer_edit'),
    url((r'^transfer/schedule/((?:19|20)\d\d[- /.](?:[1-9]|1[012])'
         '[- /.](?:[1-9]|[12][0-9]|3[01]))/$'),
        mv.transfer_schedule, name='transfer_schedule'),
    url((r'^transfer/schedule/$'), mv.transfer_schedule, {'date': None},
        name='transfer_schedule'),
    url(r'^transfer/(?P<pk>\d+)/$',
        mv.transfer_detail, name='transfer_detail'),
    url(r'^transfer/delete/(?P<pk>\d+)/$', mv.transfer_delete,
        name='transfer_delete'),

    url(r'^package/list/$', mv.package_list, name='package_list'),
    url(r'^package/create/$', mv.package, {'event': None, 'pk': None},
        name='package_create'),
    url(r'^package/create/(?P<event>\d+)/$',
        mv.package, {'pk': None}, name='package_create'),
    url(r'^package/edit/(?P<pk>\d+)/$',
        mv.package, {'event': None}, name='package_edit'),
    url(((r'^package/schedule/((?:19|20)\d\d[- /.](?:[1-9]|1[012])'
          '[- /.](?:[1-9]|[12][0-9]|3[01]))/$')),
        mv.package_schedule, name='package_schedule'),
    url(r'^package/schedule/$',
        mv.package_schedule, {'date': None}, name='package_schedule'),
    url(r'^package/(?P<pk>\d+)/$',
        mv.package_detail, name='package_detail'),
    url(r'^package/delete/(?P<pk>\d+)/$', mv.package_delete,
        name='package_delete'),

    url(r'^checkout/list/$', mv.checkout_list, name='checkout_list'),
    url(r'^checkout/create/$', mv.checkout_create, {'pk': None},
        name='checkout_create'),
    url(r'^checkout/edit/(?P<pk>\d+)/$', mv.checkout_create,
        name='checkout_edit'),
    url(r'^checkout/(?P<pk>\d+)/$', mv.checkout_detail,
        name='checkout_detail'),
    url(r'^checkout/delete/(?P<pk>\d+)/$', mv.checkout_delete,
        name='checkout_delete'),
    url(r'^checkout/report/$', mv.checkout_report, {'pk': None},
        name='checkout_report'),
    url(r'^checkout/report/(?P<pk>\d+)/$', mv.checkout_report,
        name='checkout_report_product'),
    url(r'^stock/report/$', mv.stock_report,
        name='stock_report'),

    url(r'^measurement/list/$', mv.measurement_list, name='measurement_list'),
    url(r'^measurement/$', mv.measurement, {'pk': None, 'bev_tank': None},
        name='measurement'),
    url(r'^measurement/tank/(?P<bev_tank>\d+)$', mv.measurement, {'pk': None},
        name='measurement_bev_tank'),
    url(r'^measurement/(?P<pk>\d+)/$', mv.measurement_detail,
        name='measurement_detail'),
    url(r'^measurement/edit/(?P<pk>\d+)/$', mv.measurement, {'bev_tank': None},
        name='measurement_edit'),
    url(r'^measurement/delete/(?P<pk>\d+)/$', mv.measurement_delete,
        name='measurement_delete'),

    url(r'^bev_tank/(?P<pk>\d+)/$', mv.bev_tank_detail,
        name='bev_tank_detail'),
    url(r'^bev_tank/status/(?P<pk>\d+)/$', mv.bev_tank_status_edit,
        name='bev_tank_status_edit'),
    url(r'^bev_tank/status/list/$', mv.BevTankStatusListView.as_view(),
        name='bev_tank_status_list'),

    url(r'^tank_list/$', mv.bev_tank_list, name='bev_tank_list'),

    url(r'^settings/$', mv.main_settings, name='main_settings'),

    url(r'^support/$', mv.support, name='support'),

    url(r'^submission/list/$', mv.submission_list, name="submission_list"),
    url(r'^submission/create/$', mv.submission_create,
        name='submission_create'),
    url((r'^submission/create/((?:19|20)\d\d[-](?:0[1-9]|1[012])[-]'
         '(?:0[1-9]|[12][0-9]|3[01]))/((?:19|20)\d\d[-](?:0[1-9]|1[012])[-]'
         '(?:0[1-9]|[12][0-9]|3[01]))/$'), mv.submission_complete,
         name='submission_complete'),
    url(r'^submission/(?P<submission>\d+)/$', mv.submission_detail,
        name='submission_detail'),
    url(r'^submission/download/(?P<submission>\d+)/$', mv.submission_download,
        name='submission_download'),

    url(r'^credit/create/(?P<pt>\d+)/$', mv.credit_edit, {'pk': None},
        name='credit_create'),
    url(r'^credit/edit/(?P<pk>\d+)/(?P<pt>\d+)/$', mv.credit_edit,
        name='credit_edit'),

    # for dynamic blend drop down
    (r'^tank/(?P<tank>[-\w]+)/all_json_blend_tanks/$',
        mv.all_json_blend_tanks),
    # for dynamic product type drop down
    (r'^bev_type/(?P<bt>[-\w]+)/all_json_product_types/$',
        mv.all_json_product_types_bev_type),
    # for dynamic product type drop down
    (r'^bev_tank/(?P<bt>[-\w]+)/all_json_product_types/$',
        mv.all_json_product_types_bev_tank),
    # for dynamic status drop down
    (r'^bev_tank/(?P<bt>[-\w]+)/initial_json_status/$',
        mv.initial_json_status),
    # for dynamic unit type drop down
    (r'^measurement_type/(?P<pk>[-\w]+)/json_units/$', mv.json_units),

    # for calendar events
    (r'^eventfeed$', mv.calendar_event_feed),
    (r'^event/delete/$', mv.event_delete),

    # for checkout graph
    (r'^checkout_graph_feed/$', mv.checkout_graph_feed, {'pk': None}),
    (r'^checkout_graph_feed/(?P<pk>\d+)/$', mv.checkout_graph_feed),

    # for fermentation graph
    (r'^fermentation_graph_feed/(?P<bev_tank>\d+)$',
        mv.fermentation_graph_feed),

    # for list ordering
    (r'^list_order/$', mv.list_order),

    (r'^', include(washing_urls)),
    (r'^', include(orders_urls))
)

urlpatterns += staticfiles_urlpatterns()

