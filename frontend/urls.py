from django.urls import path, include
from django.conf.urls import url
from . import views

app_name = "frontend"

urlpatterns = [
    path('', views.home_page, name="home_page"),
    path('set-language', views.set_language, name="set_language"),
    path('register', views.register_page, name="register"),
    path('login', views.login_page, name="login"),
    url(r'^logout/$', views.logout_page, name='logout'),
    path('set-language', views.set_language, name="set_language"),
    path('get-started', views.get_started, name="get_started"),
    url(r'^get-started/(?P<code>[\w-]+)/$', views.get_started, name="get_started_type"),
    path('load-project', views.load_project, name="load_project"),
    path('external-link', views.external_link, name="external_link"),
    path('requested-data', views.requested_data, name="requested_data"),
    path('visualization', views.visualization, name="visualization"),
    url(r'^visualization/(?P<code>[\w-]+)/$', views.visualization, name="special_visualization"),
    path('file-upload', views.file_upload, name="file_upload"),
    path('delete-file', views.delete_file, name="delete_file"),
    path('view-file', views.view_file, name="view_file"),
    path('get-unique-values', views.get_unique_values, name="get_unique_values"),
    path('action-traceability', views.action_traceability, name="action_traceability"),
    path('create-visualization', views.create_visualization, name="create_visualization"),
    path('save-score', views.save_score, name="save_score"),
    path('addto-dash', views.addto_dash, name="addto_dash"),
    path('addto-embed', views.addto_embed, name="addto_embed"),
    url(r'^dashboard/(?P<code>[\w-]+)/$', views.dashboard, name="dashboard"),
    path('save-dashboard', views.save_dashboard, name="save_dashboard"),
    url(r'^update-dashboard/(?P<code>[\w-]+)/$', views.update_dashboard, name="update_dashboard"),
    path('view-visualization', views.view_visualization, name="view_visualization"),
    path('drop-visualization', views.drop_visualization, name="drop_visualization"),
    path('select-file', views.select_file, name="select_file"),
    url(r'^nb-recommend/(?P<code>[\w-]+)/$', views.nb_recommend, name="nb_recommend"),
    url(r'^get-recommend/(?P<code>[\w-]+)/$', views.get_recommend, name="get_recommend"),
    path('share-project', views.share_project, name="share_project"),
    url(r'^data-content/(?P<code>[\w-]+)/$', views.data_content, name="data_content"),
    path('load-opdaset', views.load_opdaset, name="load_opdaset"),
    path('load-more-opdaset', views.load_more_opdaset, name="load_more_opdaset"),
    path('get-whole-dataset', views.get_whole_dataset, name="get_whole_dataset"),
    path('get-all-datasets', views.get_all_datasets, name="get_all_datasets"),
    path('get-dataset-columns', views.get_dataset_columns, name="get_dataset_columns"),
    path('combata', views.combata, name="combata"),
    path('dropcol', views.dropcol, name="dropcol"),
    path('repval', views.repval, name="repval"),
    path('aggdata', views.aggdata, name="aggdata"),
    path('customize-dashboard', views.customize_dashboard, name="customize_dashboard"),
    url(r'^explore-data/(?P<project_code>[\w-]+)/(?P<code>[\w-]+)/$', views.explore_data, name="explore_data"),
    path('edit-datainfo', views.edit_datainfo, name="edit_datainfo"),
    path('edit-dataform', views.edit_dataform, name="edit_dataform"),
    url(r'^generate-datatable/(?P<project_code>[\w-]+)/(?P<file_code>[\w-]+)/(?P<query>(.)+)/$', views.generate_datatable, name="generate_datatable"),
    path('explore-column', views.explore_column, name="explore_column"),
    path('projects', views.projects, name="projects"),
    url(r'^detail-project/(?P<code>[\w-]+)/$', views.detail_project, name="detail_project"),
    path('get-states', views.get_states, name="get_states"),
    path('get-transstates', views.get_transstates, name="get_transstates"),
    path('save-like', views.save_like, name="save_like"),
    path('autocomplete-title', views.autocomplete_title, name="autocomplete_title"),
    path('datasets', views.datasets, name="datasets"),
    path('issues', views.issues, name="issues"),
    path('summary', views.summary, name="summary"),
    path('home-proto', views.home_proto, name="home_proto"),
    path('home-trans', views.home_trans, name="home_trans"),
    path('about', views.about, name="about"),
    path('about-apps', views.about_apps, name="about_apps"),
    path('how_works', views.how_works, name="how_works"),
    path('privacy', views.privacy, name="privacy"),
    path('home-mobile', views.home_mobile, name="home_mobile"),
    path('login-mobile', views.login_mobile, name="login_mobile"),
    path('register-mobile', views.register_mobile, name="register_mobile"),
    path('logout-mobile', views.logout_mobile, name="logout_mobile"),
    path('projects-mobile', views.projects_mobile, name="projects_mobile"),
    path('favorites-mobile', views.favorites_mobile, name="favorites_mobile"),
    path('topics-mobile', views.topics_mobile, name="topics_mobile"),
    url(r'^detail-project-mobile/(?P<code>[\w-]+)/$', views.detail_project_mobile, name="detail_project_mobile"),
    path('import-reuses', views.import_reuses, name="import_reuses"),
    url(r'^embed/(?P<project_code>[\w-]+)/(?P<code>[\w-]+)/$', views.embed, name="embed"),
    path('switch-display', views.switch_display, name="switch_display"),
    path('trans-started', views.trans_started, name="trans_started"),
    url(r'^trans-started/(?P<code>[\w-]+)/$', views.trans_started, name="trans_started_update"),
    url(r'^view-trans/$', views.view_trans, name="view_trans_init"),
    url(r'^view-trans/(?P<code>[\w-]+)/$', views.view_trans, name="view_trans"),
    url(r'^view-trans/(?P<code>[\w-]+)/(?P<theme>[\w-]+)/$', views.view_trans, name="view_trans_theme"),
    #url(r'^view-trans/(?P<code>[\w-]+)/(?P<theme>[\w-]+)/(?P<dash_code>[\w-]+)/$', views.view_trans, name="view_trans_project"),
    url(r'^dashboard/(?P<code>[\w-]+)/(?P<theme>[\w-]+)/(?P<trans_code>[\w-]+)/$', views.dashboard, name="dashboard_trans"),

]
