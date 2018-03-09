""" XSD Flattener Database or URL class
"""
from xml_utils.xsd_flattener.xsd_flattener_url import XSDFlattenerURL
from urlparse import urlparse
from core_main_app.components.template import api as template_api
from core_main_app.commons import exceptions
from django.core.urlresolvers import reverse


class XSDFlattenerDatabaseOrURL(XSDFlattenerURL):
    """ Get the content of the dependency from the database or from the URL.
    """

    def __init__(self, xml_string, download_enabled=True):
        """Initializes the flattener

        Args:
            xml_string:
            download_enabled:
        """
        XSDFlattenerURL.__init__(self, xml_string=xml_string, download_enabled=download_enabled)

    def get_dependency_content(self, uri):
        """ Get the content of the dependency from the database or from the URL. Try to get the content from the
        database first and then try to download it from the provided URI.

        Args:
            uri: Content URI.

        Returns:
            Content.

        """
        url = urlparse(uri)
        url_template_download = reverse('core_main_app_rest_template_download')
        if url.path == url_template_download:
            try:
                _id = url.query.split("=")[1]
                template = template_api.get(_id)
                content = template.content
            except (exceptions.DoesNotExist, exceptions.ModelError, Exception):
                content = super(XSDFlattenerDatabaseOrURL, self).get_dependency_content(uri)
        else:
            content = super(XSDFlattenerDatabaseOrURL, self).get_dependency_content(uri)

        return content
