""" REST views for the template version manager API
"""
from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core_main_app.commons import exceptions as exceptions
from core_main_app.components.template_version_manager import (
    api as template_version_manager_api,
)
from core_main_app.components.version_manager import api as version_manager_api
from core_main_app.rest.template_version_manager.abstract_views import (
    AbstractTemplateVersionManagerList,
    AbstractTemplateList,
    AbstractStatusTemplateVersion,
    AbstractStatusTemplateVersionManager,
    AbstractTemplateVersionManagerDetail,
)
from core_main_app.rest.template_version_manager.serializers import (
    TemplateVersionManagerSerializer,
    CreateTemplateSerializer,
)
from core_main_app.utils.decorators import api_staff_member_required
from core_main_app.access_control.exceptions import AccessControlError


class GlobalTemplateVersionManagerList(AbstractTemplateVersionManagerList):
    """List all GlobalTemplateVersionManager"""

    def get_template_version_managers(self):
        """Get GlobalTemplateVersionManager

        Returns:

            List of GlobalTemplateVersionManager
        """
        return template_version_manager_api.get_global_version_managers(
            request=self.request
        )


class UserTemplateVersionManagerList(AbstractTemplateVersionManagerList):
    """List all UserTemplateVersionManager"""

    permission_classes = (IsAuthenticated,)

    def get_template_version_managers(self):
        """Get all UserTemplateVersionManager

        Returns:

            List of UserTemplateVersionManager
        """
        return template_version_manager_api.get_all_by_user_id(
            request=self.request
        )


class GlobalAndUserTemplateVersionManagerList(
    AbstractTemplateVersionManagerList
):
    """List Global And User Template Version Manager"""

    permission_classes = (IsAdminUser,)

    def get_template_version_managers(self):
        """Get all Template Version Manager

        Returns:

            List of Template Version Manager
        """

        return template_version_manager_api.get_all(request=self.request)


class TemplateVersionManagerDetail(APIView):
    """Retrieve a TemplateVersionManager"""

    permission_classes = (IsAuthenticated,)

    def get_object(self, pk, request):
        """Get TemplateVersionManager from db

        Args:

            pk: ObjectId
            request:

        Returns:

            TemplateVersionManager
        """
        try:
            return template_version_manager_api.get_by_id(pk, request=request)
        except exceptions.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Retrieve a TemplateVersionManager

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: TemplateVersionManager
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            template_version_manager_object = self.get_object(
                pk, request=request
            )

            # Serialize object
            serializer = TemplateVersionManagerSerializer(
                template_version_manager_object
            )

            # Return response
            return Response(serializer.data)
        except Http404:
            content = {"message": "Template Version Manager not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(
                content, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TemplateVersion(AbstractTemplateVersionManagerDetail):
    """Create a TemplateVersion"""

    @method_decorator(api_staff_member_required())
    def post(self, request, pk):
        """Create a TemplateVersion

        Parameters:

            {
                "filename": "filename",
                "content": "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><xs:element name='root'/></xs:schema>"
            }

        Note:

            "dependencies_dict": json.dumps({"schemaLocation1": "id1" ,"schemaLocation2":"id2"})

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: Created TemplateVersionManager
            - code: 400
              content: Validation error
            - code: 404
              content: Template was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            template_version_manager_object = self.get_object(pk)

            # Build serializers
            template_serializer = CreateTemplateSerializer(
                data=request.data, context={"request": request}
            )

            # Validate data
            template_serializer.is_valid(raise_exception=True)

            # Save data
            template_serializer.save(
                template_version_manager=template_version_manager_object,
                user=template_version_manager_object.user,
            )

            return Response(
                template_serializer.data, status=status.HTTP_201_CREATED
            )
        except Http404:
            content = {"message": "Template Version Manager not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as validation_exception:
            content = {"message": validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(
                content, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserTemplateList(AbstractTemplateList):
    """Create a Template (linked to the user)"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """Create a Template (linked to the user)

        Parameters:

            {
                "title": "title",
                "filename": "filename",
                "content": "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><xs:element name='root'/></xs:schema>"
            }

        Note:

            "dependencies_dict": json.dumps({"schemaLocation1": "id1" ,"schemaLocation2":"id2"})

        Args:

            request: HTTP request

        Returns:

            - code: 201
              content: Created Template
            - code: 400
              content: Validation error / not unique / XSD error
            - code: 500
              content: Internal server error
        """
        return super().post(request)

    def get_user(self):
        """Retrieve the user from the request

        Returns:

            User ID
        """
        return str(self.request.user.id)


class GlobalTemplateList(AbstractTemplateList):
    """Create a Template (global schema)"""

    @method_decorator(api_staff_member_required())
    def post(self, request):
        """Create a Template (global schema)

        Parameters:

            {
                "title": "title",
                "filename": "filename",
                "content": "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><xs:element name='root'/></xs:schema>"
            }

        Note:

            "dependencies_dict": json.dumps({"schemaLocation1": "id1" ,"schemaLocation2":"id2"})

        Args:

            request: HTTP request

        Returns:

            - code: 201
              content: Created template
            - code: 400
              content: Validation error / not unique / XSD error
            - code: 500
              content: Internal server error
        """
        return super().post(request)

    def get_user(self):
        """The user is None for a global template

        Returns:

            None
        """
        return None


class CurrentTemplateVersion(AbstractStatusTemplateVersion):
    """Update status to current"""

    permission_classes = (IsAuthenticated,)

    def status_update(self, template_object):
        """Update status to current

        Args:

            template_object: template_version

        Returns:

            TemplateVersion
        """
        return version_manager_api.set_current(
            template_object, request=self.request
        )


class DisableTemplateVersion(AbstractStatusTemplateVersion):
    """Update status to disabled"""

    permission_classes = (IsAuthenticated,)

    def status_update(self, template_object):
        """Update status to disabled

        Args:

            template_object: template_version

        Returns:

            TemplateVersion
        """
        return version_manager_api.disable_version(
            template_object, request=self.request
        )


class RestoreTemplateVersion(AbstractStatusTemplateVersion):
    """Update status to restored"""

    permission_classes = (IsAuthenticated,)

    def status_update(self, template_object):
        """Update status to restored

        Args:

            template_object: template_version

        Returns:

            TemplateVersion
        """
        return version_manager_api.restore_version(
            template_object, request=self.request
        )


class DisableTemplateVersionManager(AbstractStatusTemplateVersionManager):
    """Update status to disabled"""

    permission_classes = (IsAuthenticated,)

    def status_update(self, template_version_manager_object):
        """Update status to disabled

        Args:

            template_version_manager_object: template_version_manager

        Returns:

            TemplateVersionManager
        """
        # FIXME: add return?
        version_manager_api.disable(
            template_version_manager_object, request=self.request
        )


class RestoreTemplateVersionManager(AbstractStatusTemplateVersionManager):
    """Update status to restored"""

    permission_classes = (IsAuthenticated,)

    def status_update(self, template_version_manager_object):
        """Update status to restored

        Args:

            template_version_manager_object: template_version_manager

        """
        # FIXME: add return?
        version_manager_api.restore(
            template_version_manager_object, request=self.request
        )


class TemplateVersionManagerOrdering(APIView):
    """Update templates ordering"""

    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        """Update templates ordering

        Args:
            request:

        Returns:

            - code: 200
              content: None
            - code: 403
              content: Authentication error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # get list ids
            template_ids = request.data.get("template_list", [])

            # get template list
            template_list = template_version_manager_api.sort_by_id_list(
                template_ids, request
            )

            # update template ordering
            template_version_manager_api.update_templates_ordering(
                template_list, user=self.request.user
            )

            # return response
            return Response({}, status=status.HTTP_200_OK)
        except AccessControlError as ace:
            content = {"message": str(ace)}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(
                content, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
