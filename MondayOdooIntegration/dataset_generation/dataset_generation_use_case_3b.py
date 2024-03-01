import xmlrpc.client  # Importing the XML-RPC client library
from dataclasses import dataclass  # Importing the dataclass decorator for creating classes with lightweight syntax
import requests
import json

MONDAY_URL = "https://api.monday.com/v2"

ODOO_URL = "https://citrus2.odoo.com"
ODOO_DB = "citrus2"
ODOO_MODEL_NAME = "hr.employee"


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

    def read_employees_and_fields(self, api_model_name: str, odoo_object, api_uid, api_password, fields_list: list):
        """
        Reads employees and specified fields from the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            fields_list (list): List of fields to be retrieved.

        Returns:
            Query result.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'search_read', [[]], {'fields': fields_list}
        )


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

    def create_board_with_name(self, api_key: str, board_name: str) -> requests.Response:
        """
        Creates a board with the specified name.

        Parameters:
            api_key (str): API key for authentication.
            board_name (str): Name of the board to be created.

        Returns:
            requests.Response: Response object from the API.
        """
        query = 'mutation {{create_board (board_name: "{}", board_kind: public) {{id}}}}'.format(board_name)
        return self.__make_query(api_key, query)

    def create_item_with_values(self, api_key: str, board_id: int, item_name: str,
                                values: dict) -> requests.Response:
        """
        Creates an item with the specified values.

        Parameters:
            api_key (str): API key for authentication.
            board_id (int): ID of the board.
            item_name (str): Name of the item to be created.
            values (dict): dict containing values for the item.

        Returns:
            requests.Response: Response object from the API.
        """
        query = ('mutation ($myItemName: String!, $columnVals: JSON!) {{ create_item (board_id:{}, '
                 'item_name:$myItemName, column_values:$columnVals) {{ id }} }}').format(board_id)
        values_dictionary = {
            'myItemName': item_name,
            'columnVals': json.dumps(values)
        }
        return self.__make_query_with_values(api_key, query, values_dictionary)


def fetch_employees_from_odoo_and_create_on_monday(odoo_object, odoo_uid, odoo_auth, monday_auth, monday_api, mapping):
    odoo_fields = list(mapping.keys())
    employees = odoo_api.read_employees_and_fields(ODOO_MODEL_NAME, odoo_object, odoo_uid, odoo_auth.api_password,
                                                    odoo_fields)
    response = monday_api.create_board_with_name(monday_auth.api_key, "Applicants from Odoo")
    if response.status_code == 200:
        response_json = response.json()
        if response_json:
            board_id = response_json['data']['create_board']['id']
            for employee in employees:
                monday_key_values = {}
                for key, value in mapping.items():
                    monday_key_values[value] = employee[key]
                monday_api.create_item_with_values(monday_auth.api_key, board_id, employee['name'],
                                                   monday_key_values)


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

print('Enter the odoo to monday field mapping:')
mapping = json.loads(input())

fetch_employees_from_odoo_and_create_on_monday(odoo_object, odoo_uid, odoo_auth, monday_auth, monday_api, mapping)
