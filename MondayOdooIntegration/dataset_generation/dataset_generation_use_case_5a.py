import xmlrpc.client  # Importing the XML-RPC client library
from dataclasses import dataclass  # Importing the dataclass decorator for creating classes with lightweight syntax

ODOO_URL = "https://citrus2.odoo.com"
ODOO_DB = "citrus2"
ODOO_MODEL_NAME = "hr.applicant"


@dataclass
class OdooAuth:
    api_username: str  # Username for Odoo authentication
    api_password: str  # Password for Odoo authentication

    @staticmethod
    def get_object(api_url: str) -> xmlrpc.client.ServerProxy:
        """
        Static method to get the ServerProxy object.

        Parameters:
            api_url (str): URL of the API.

        Returns:
            xmlrpc.client.ServerProxy: ServerProxy object for the specified API URL.
        """
        return xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(api_url))

    @staticmethod
    def __get_common(api_url: str) -> xmlrpc.client.ServerProxy:
        """
        Private static method to get the common ServerProxy object.

        Parameters:
            api_url (str): URL of the API.

        Returns:
            xmlrpc.client.ServerProxy: Common ServerProxy object for the specified API URL.
        """
        return xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(api_url))

    def authenticate(self, api_db: str, api_url: str) -> int:
        """
        Method to authenticate with Odoo.

        Parameters:
            api_db (str): Name of the Odoo database.
            api_url (str): URL of the Odoo API.

        Returns:
            int: Authentication result.
        """
        return (self.__get_common(api_url)
                .authenticate(api_db, self.api_username, self.api_password, {}))  # Authenticating and returning


class OdooAPI:
    api_url: str
    api_db: str

    def __init__(self, api_url: str, api_db: str):
        """
        Initializes OdooAPI with the API URL and database name.

        Parameters:
            api_url (str): URL of the Odoo API.
            api_db (str): Name of the database.
        """
        self.api_url = api_url
        self.api_db = api_db

    def __make_query(self, api_model_name: str, odoo_object, api_uid, api_password, action: str, search_filter, fields):
        """
        Makes a query to the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            action (str): Action to perform (e.g., 'create', 'search').
            search_filter: Filters to be applied in the query.
            fields: Fields to be retrieved.

        Returns:
            Query result.
        """
        if fields:
            return odoo_object.execute_kw(
                self.api_db, api_uid, api_password, api_model_name, action, search_filter, fields
            )
        else:
            return odoo_object.execute_kw(
                self.api_db, api_uid, api_password, api_model_name, action, search_filter
            )

    def delete_applicant(self, api_model_name: str, odoo_object, api_uid, api_password, applicant_id):
        """
        Deletes an applicant from the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            applicant_id: ID of the applicant to be deleted.

        Returns:
            Query result.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'unlink', [[int(applicant_id)]], None
        )


def delete_applicant_from_odoo(odoo_object, odoo_uid, odoo_auth, applicant_id_on_odoo):
    odoo_api.delete_applicant(ODOO_MODEL_NAME, odoo_object, odoo_uid, odoo_auth.api_password, applicant_id_on_odoo)
    print("Deleted: ", applicant_id_on_odoo)


print('Enter the odoo_username:')
odoo_username = input()
print('Enter the odoo_password:')
odoo_password = input()

odoo_auth = OdooAuth(odoo_username, odoo_password)

odoo_uid = odoo_auth.authenticate(ODOO_DB, ODOO_URL)
odoo_object = odoo_auth.get_object(ODOO_URL)

odoo_api = OdooAPI(ODOO_URL, ODOO_DB)

print('Enter the id of applicant on Odoo to delete:')
applicant_id_on_odoo = int(input())

delete_applicant_from_odoo(odoo_object, odoo_uid, odoo_auth, applicant_id_on_odoo)
