""" Unit Test Data
"""
import core_main_app.components.data.api as data_api
from core_main_app.components.data.models import Data
from core_main_app.components.template.models import Template
from core_main_app.commons import exceptions
from unittest.case import TestCase
from mock import patch
from collections import OrderedDict


class TestDataGetAll(TestCase):

    @patch.object(Data, 'get_all')
    def test_data_get_all_return_collection_of_data(self, mock_list):
        # Arrange
        mock_data_1 = _create_data(_get_template(), user_id='3', title='title_1', content="")
        mock_data_2 = _create_data(_get_template(), user_id='1', title='title_2', content="")
        mock_list.return_value = [mock_data_1, mock_data_2]
        # Act
        result = data_api.get_all()
        # Assert
        self.assertTrue(all(isinstance(item, Data) for item in result))


class TestDataGetById(TestCase):

    @patch.object(Data, 'get_by_id')
    def test_data_get_by_id_raises_api_error_if_not_found(self, mock_get):
        # Arrange
        mock_get.side_effect = exceptions.DoesNotExist('')
        # Act # Assert
        with self.assertRaises(exceptions.DoesNotExist):
            data_api.get_by_id(1)

    @patch.object(Data, 'get_by_id')
    def test_data_get_by_id_return_data_if_found(self, mock_get):
        # Arrange
        mock_data = Data(_get_template(), OrderedDict(), 'title', '2')
        mock_get.return_value = mock_data
        # Act
        result = data_api.get_by_id(1)
        # Assert
        self.assertIsInstance(result, Data)


class TestDataGetAllByUser(TestCase):

    @patch.object(Data, 'get_all_by_user_id')
    def test_data_get_all_by_user_return_collection_of_data_from_user(self, mock_list_by_user_id):
        # Arrange
        user_id = '2'
        mock_data_1 = _create_data(_get_template(), user_id=user_id, title='title_1', content="")
        mock_data_2 = _create_data(_get_template(), user_id=user_id, title='title_2', content="")
        mock_list_by_user_id.return_value = [mock_data_1, mock_data_2]
        # Act
        result = data_api.get_all_by_user_id(user_id)
        # Assert
        self.assertTrue(all(item.user_id == user_id for item in result))


class TestDataGetAllExceptUser(TestCase):

    @patch.object(Data, 'get_all_except_user_id')
    def test_data_get_all_except_user_return_collection_of_data_where_user_is_not_owner(self, mock_list_except_user_id):
        # Arrange
        user_id = '2'
        mock_data_1 = _create_data(_get_template(), user_id='3', title='title_1', content="")
        mock_data_2 = _create_data(_get_template(), user_id='1', title='title_2', content="")
        mock_list_except_user_id.return_value = [mock_data_1, mock_data_2]
        # Act
        result = data_api.get_all_except_user_id(user_id)
        # Assert
        self.assertTrue(all(item.user_id != user_id for item in result))


class TestDataGetAllByIdList(TestCase):

    @patch.object(Data, 'get_all_by_id_list')
    def test_data_get_all_by_id_list_return_collection_of_data(self, mock_list_by_id_list):
        # Arrange
        mock_data_1 = _create_data(_get_template(), user_id='3', title='title_1', content="")
        mock_data_2 = _create_data(_get_template(), user_id='1', title='title_2', content="")
        mock_list_by_id_list.return_value = [mock_data_1, mock_data_2]
        # Act
        result = data_api.get_all_by_id_list([1, 2])
        # Assert
        self.assertTrue(all(isinstance(item, Data) for item in result))

    @patch.object(Data, 'get_all_by_id_list')
    def test_data_get_all_by_id_list_return_collection_of_distinct_data_by_template(self, mock_list_by_id_list):
        # Arrange
        mock_data_1 = _create_data(_get_template(), user_id='2', title='title_1', content="")
        mock_list_by_id_list.return_value = [mock_data_1]
        # Act
        result = data_api.get_all_by_id_list([1], 'template_id')
        count_result = len([item.template.id_field == '1' for item in result])
        # Assert
        self.assertEqual(count_result, 1)


class TestDataUpsert(TestCase):

    @patch.object(Data, 'convert_to_file')
    @patch.object(data_api, 'check_xml_file_is_valid')
    @patch.object(Data, 'save')
    def test_data_upsert_return_data_with_new_title_if_is_called_with_only_title_modified(self, mock_save,
                                                                                          mock_check,
                                                                                          mock_convert_file):
        # Arrange
        data = _create_data(_get_template(), user_id='2', title='new_title', content='<tag></tag>')
        mock_save.return_value = data
        mock_check.return_value = None
        mock_convert_file.return_value = None
        # Act
        result = data_api.upsert(data)
        # Assert
        self.assertEqual('new_title', result.title)

    @patch.object(Data, 'convert_to_file')
    @patch.object(data_api, 'check_xml_file_is_valid')
    @patch.object(Data, 'save')
    def test_data_upsert_return_data_with_new_user_id_if_is_called_with_only_user_id_modified(self, mock_save,
                                                                                              mock_check,
                                                                                              mock_convert_file):
        # Arrange
        data = _create_data(_get_template(), user_id='3', title='new_title', content='<tag></tag>')
        mock_save.return_value = data
        mock_check.return_value = None
        mock_convert_file.return_value = None
        # Act
        result = data_api.upsert(data)
        # Assert
        self.assertEqual('3', result.user_id)

    @patch.object(Data, 'convert_to_file')
    @patch.object(data_api, 'check_xml_file_is_valid')
    @patch.object(Data, 'save')
    def test_data_upsert_return_data_with_new_xml_if_is_called_with_only_xml_modified(self, mock_save,
                                                                                      mock_check, mock_convert_file):
        # Arrange
        xml = '<new_tag></new_tag>'
        data = _create_data(_get_template(), user_id='3', title='title', content=xml)
        mock_save.return_value = data
        mock_check.return_value = None
        mock_convert_file.return_value = None
        # Act
        result = data_api.upsert(data)
        # Assert
        self.assertEqual(xml, result.xml_content)

    @patch.object(Data, 'convert_to_file')
    @patch.object(data_api, 'check_xml_file_is_valid')
    @patch.object(Data, 'save')
    def test_data_upsert_return_data_with_last_modification_date(self, mock_save,
                                                                 mock_check, mock_convert_file):
        # Arrange
        data = _create_data(_get_template(), user_id='3', title='title', content='<tag></tag>')
        mock_save.return_value = data
        mock_check.return_value = None
        mock_convert_file.return_value = None
        # Act
        result = data_api.upsert(data)
        # Assert
        self.assertIsNotNone(result.last_modification_date)

    def test_data_upsert_raises_xml_error_if_failed_during_xml_validation(self):
        # Arrange
        data = _create_data(None, user_id='3', title='title', content='')
        # Act # Assert
        with self.assertRaises(exceptions.XMLError):
            data_api.upsert(data)

    def test_data_upsert_raises_xsd_error_if_failed_during_xsd_validation(self):
        # Arrange
        template = _get_template()
        template.content += "<"
        data = _create_data(template, user_id='3', title='title', content='<new_tag></new_tag>')
        # Act # Assert
        with self.assertRaises(exceptions.XSDError):
            data_api.upsert(data)

    def test_data_upsert_raises_xml_error_if_failed_during_validation(self):
        # Arrange
        template = _get_template()
        data = _create_data(template, user_id='3', title='title', content='<new_tag></new_tag>')
        # Act # Assert
        with self.assertRaises(exceptions.XMLError):
            data_api.upsert(data)


class TestDataCheckXmlFileIsValid(TestCase):

    def test_data_check_xml_file_is_valid_raises_xml_error_if_failed_during_xml_validation(self):
        # Arrange
        data = _create_data(None, user_id='3', title='title', content='')
        # Act # Assert
        with self.assertRaises(exceptions.XMLError):
            data_api.check_xml_file_is_valid(data)

    def test_data_check_xml_file_is_valid_raises_xsd_error_if_failed_during_xsd_validation(self):
        # Arrange
        template = _get_template()
        template.content += "<"
        data = _create_data(template, user_id='3', title='title', content='<new_tag></new_tag>')
        # Act # Assert
        with self.assertRaises(exceptions.XSDError):
            data_api.check_xml_file_is_valid(data)

    def test_data_check_xml_file_is_valid_raises_xml_error_if_failed_during_validation(self):
        # Arrange
        template = _get_template()
        data = _create_data(template, user_id='3', title='title', content='<new_tag></new_tag>')
        # Act # Assert
        with self.assertRaises(exceptions.XMLError):
            data_api.check_xml_file_is_valid(data)

    def test_data_check_xml_data_valid_return_true_if_validation_success(self):
        # Arrange
        template = _get_template()
        data = _create_data(template, user_id='3', title='title', content='<tag>toto</tag>')
        # Act
        result = data_api.check_xml_file_is_valid(data)
        # Assert
        self.assertEqual(result, True)


class TestDataQueryFullText(TestCase):

    @patch('core_main_app.components.data.models.Data.execute_full_text_query')
    def test_data_execute_full_text_query_return_collection(self, mock_execute):
        # Arrange
        template = _get_template()
        mock_data_1 = _create_data(template, user_id='2', title='title_1', content="")
        mock_data_2 = _create_data(template, user_id='2', title='title_2', content="")
        mock_execute.return_value = [mock_data_1, mock_data_2]
        # Act
        result = data_api.query_full_text('', '1')
        # Assert
        self.assertTrue(all(isinstance(item, Data) for item in result))


class TestSetPublish(TestCase):

    @patch.object(Data, 'get_by_id')
    @patch.object(data_api, 'upsert')
    def test_data_set_publish_set_to_true_test_is_published(self, mock_upsert, mock_get):
        # Create Data
        data = Data(is_published=False)
        mock_get.return_value = data
        mock_upsert.return_value = None
        # Update data
        data_api.set_publish(1, True)
        # Check update
        self.assertTrue(data.is_published)

    @patch('core_main_app.components.data.api.settings', DATA_AUTO_PUBLISH=True)
    @patch.object(Data, 'get_by_id')
    @patch.object(data_api, 'upsert')
    def test_data_set_publish_set_to_true_test_publication_date_when_DATA_AUTO_PUBLISH_is_True(self, mock_upsert,
                                                                                               mock_get, mock_DATA_AUTO_PUBLISH):
        # Create Data
        data = Data(is_published=False)
        mock_get.return_value = data
        mock_upsert.return_value = None
        # Update data
        data_api.set_publish(1, True)
        # Check update
        self.assertIsNone(data.publication_date)

    @patch('core_main_app.components.data.api.settings', DATA_AUTO_PUBLISH=False)
    @patch.object(Data, 'get_by_id')
    @patch.object(data_api, 'upsert')
    def test_data_set_publish_set_to_true_test_publication_date_when_DATA_AUTO_PUBLISH_is_False(self, mock_upsert,
                                                                                                mock_get, mock_DATA_AUTO_PUBLISH):
        # Create Data
        data = Data(is_published=False)
        mock_get.return_value = data
        mock_upsert.return_value = None
        # Update data
        data_api.set_publish(1, True)
        # Check update
        self.assertIsNotNone(data.publication_date)

    @patch.object(Data, 'get_by_id')
    @patch.object(data_api, 'upsert')
    def test_data_set_publish_set_to_false_test_is_published(self, mock_upsert, mock_get):
        # Create Data
        data = Data(is_published=True)
        mock_get.return_value = data
        mock_upsert.return_value = None
        # Update data
        data_api.set_publish(1, False)
        # Check update
        self.assertFalse(data.is_published)

    @patch.object(Data, 'get_by_id')
    @patch.object(data_api, 'upsert')
    def test_data_set_publish_set_to_false_test_publication_date(self, mock_upsert, mock_get):
        # Create Data
        data = Data(is_published=True)
        mock_get.return_value = data
        mock_upsert.return_value = None
        # Update data
        data_api.set_publish(1, False)
        # Check update
        self.assertIsNone(data.publication_date)


def _get_template():
    template = Template()
    template.id_field = 1
    xsd = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
          '<xs:element name="tag"></xs:element></xs:schema>'
    template.content = xsd
    return template


def _create_data(template, user_id, title, content):
    data = Data(template=template,
                user_id=user_id,
                title=title)
    data.xml_content = content
    return data
