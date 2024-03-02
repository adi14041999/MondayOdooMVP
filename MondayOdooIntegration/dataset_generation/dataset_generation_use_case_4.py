import xmlrpc.client  # Importing the XML-RPC client library
from dataclasses import dataclass  # Importing the dataclass decorator for creating classes with lightweight syntax
import requests
import json

MONDAY_URL = "https://api.monday.com/v2"

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

    def read_applicant_id_with_phone(self, api_model_name: str, odoo_object, api_uid, api_password,
                                     applicant_phone: str) -> list:
        """
        Reads applicant IDs with a specific name from the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            applicant_phone (str): Phone number of the applicant.

        Returns:
            List of applicant IDs.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'search', [[['partner_phone', '=', applicant_phone]]],
            None
        )


@dataclass
class MondayAuth:
    api_key: str  # API key for authentication

    def get_headers(self) -> dict:
        """
        Function to get authentication headers.

        Parameters:
            self (MondayAuth): Instance of MondayAuth class.

        Returns:
            dict: Dictionary containing authorization headers with API key.
        """
        return {"Authorization": self.api_key}  # Returning headers with API key


class MondayAPI:
    api_url: str

    def __init__(self, api_url: str):
        """
        Initializes MondayAPI with the API URL.

        Parameters:
            api_url (str): URL of the Monday API.
        """
        self.api_url = api_url

    def __make_query(self, api_key: str, query: str) -> requests.Response:
        """
        Makes a query to the Monday API.

        Parameters:
            api_key (str): API key for authentication.
            query (str): Query to be executed.

        Returns:
            requests.Response: Response object from the API.
        """
        data = {'query': query}
        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
        return requests.post(url=self.api_url, json=data, headers=headers)

    def __make_query_with_values(self, api_key: str, query: str, values_dictionary: dict) -> requests.Response:
        """
        Makes a query to the Monday API with values.

        Parameters:
            api_key (str): API key for authentication.
            query (str): Query to be executed.
            values_dictionary (dict): Dictionary containing values for the query.

        Returns:
            requests.Response: Response object from the API.
        """
        data = {'query': query, 'variables': values_dictionary}
        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
        return requests.post(url=self.api_url, json=data, headers=headers)

    def update_column_value_of_item(self, api_key: str, board_id: int, item_id: int, column_id: str,
                                    column_value: str) -> requests.Response:
        """
        Updates the column value of an item in the Monday API.

        Parameters:
            api_key (str): API key for authentication.
            board_id (int): ID of the board.
            item_id (int): ID of the item.
            column_id (str): ID of the column.
            column_value (str): Value to be updated.

        Returns:
            requests.Response: Response object from the API.
        """
        query = ('mutation {{ change_simple_column_value(item_id: {}, board_id: {}, column_id: "{}", value: "{}") {{'
                 'id}}}}').format(item_id, board_id, column_id, column_value)
        return self.__make_query(api_key, query)


def fetch_applicant_from_odoo_and_update_on_monday(odoo_object, odoo_uid, odoo_auth, monday_auth, monday_api, board_id,
                                                   applicant_phone, applicant_id_on_monday, mapping):
    applicants = odoo_api.read_applicant_id_with_phone(ODOO_MODEL_NAME, odoo_object, odoo_uid,
                                                       odoo_auth.api_password, applicant_phone)
    if applicants:
        for applicant in applicants:
            for key, value in mapping.items():
                monday_key = value
                monday_value = applicant[key]
                monday_api.update_column_value_of_item(monday_auth.api_key, board_id, applicant_id_on_monday,
                                                       monday_key, monday_value)


print('Enter the odoo_username:')
odoo_username = input()
print('Enter the odoo_password:')
odoo_password = input()
print('Enter the monday_api_key:')
monday_api_key = input()

monday_auth = MondayAuth(monday_api_key)
odoo_auth = OdooAuth(odoo_username, odoo_password)

odoo_uid = odoo_auth.authenticate(ODOO_DB, ODOO_URL)
odoo_object = odoo_auth.get_object(ODOO_URL)

monday_api = MondayAPI(MONDAY_URL)
odoo_api = OdooAPI(ODOO_URL, ODOO_DB)

print('Enter the board_id:')
board_id = int(input())

print('Enter the phone of the applicant in Odoo to update on Monday:')
applicant_phone = input()

print('Enter the id of applicant on Monday to update:')
applicant_id_on_monday = int(input())

print('Enter the odoo to monday field mapping:')
mapping = json.loads(input())

fetch_applicant_from_odoo_and_update_on_monday(odoo_object, odoo_uid, odoo_auth, monday_auth, monday_api, board_id,
                                               applicant_phone, applicant_id_on_monday, mapping)
