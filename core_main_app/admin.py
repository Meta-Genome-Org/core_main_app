"""
Url router for the administration site
"""
from django.contrib import admin
from django.conf.urls import url

from views.admin import views as admin_views, ajax as admin_ajax

admin_urls = [
    url(r'^templates$', admin_views.manage_templates,
        name='core_main_app_templates'),
    url(r'^template/upload$', admin_views.upload_template,
        name='core_main_app_upload_template'),
    url(r'^template/upload/(?P<version_manager_id>\w+)', admin_views.upload_template_version,
        name='core_main_app_upload_template_version'),
    url(r'^template/versions/(?P<version_manager_id>\w+)', admin_views.manage_template_versions,
        name='core_main_app_manage_template_versions'),


    url(r'^template/disable', admin_ajax.disable_template,
        name='core_main_app_disable_template'),
    url(r'^template/restore', admin_ajax.restore_template,
        name='core_main_app_restore_template'),
    url(r'^template/version/disable', admin_ajax.disable_template_version,
        name='core_main_app_disable_template_version'),
    url(r'^template/version/restore', admin_ajax.restore_template_version,
        name='core_main_app_restore_template_version'),
    url(r'^template/version/current', admin_ajax.set_current_version,
        name='core_main_app_set_current_template_version'),
    url(r'^template/resolve-dependencies', admin_ajax.resolve_dependencies,
        name='core_main_app_restore_template'),
    url(r'^template/edit', admin_ajax.edit_template,
        name='core_main_app_edit_template'),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls