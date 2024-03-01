import xmlrpc.client  # Importing the XML-RPC client library
from dataclasses import dataclass  # Importing the dataclass decorator for creating classes with lightweight syntax
import requests

MONDAY_URL = "https://api.monday.com/v2"

ODOO_URL = "https://citrus2.odoo.com"
ODOO_DB = "citrus2"
ODOO_MODEL_NAME = "hr.applicant"


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

    def create_applicant_with_name(self, api_model_name: str, odoo_object, api_uid, api_password, applicant_name: str):
        """
        Creates an applicant with the specified name.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            applicant_name (str): Name of the applicant.

        Returns:
            Query result.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'create',
            [{'partner_name': applicant_name, 'name': 'New Applicant!'}], None)


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

    def read_items_and_names(self, api_key: str, board_id: int) -> requests.Response:
        """
        Reads items and names from a board in the Monday API.

        Parameters:
            api_key (str): API key for authentication.
            board_id (int): ID of the board.

        Returns:
            requests.Response: Response object from the API.
        """
        query = ('{{boards(ids: {}) {{ items_page {{ items {{ name }}}}}}}}'.format(board_id))
        return self.__make_query(api_key, query)


def fetch_applicants_from_monday(odoo_object, odoo_uid, odoo_auth, monday_auth, monday_api, board_id, item_name):
    response = monday_api.read_items_and_names(monday_auth.api_key, board_id)
    if response.status_code == 200:
        response_json = response.json()
        if response_json:
            for board in response_json['data']['boards']:
                for item in board['items_page']['items']:
                    name = item['name']
                    if name == item_name:
                        create_applicant_on_odoo(odoo_auth, odoo_api, odoo_uid, odoo_object, item_name)
    else:
        print("Failed to fetch data from Monday.com")


def create_applicant_on_odoo(odoo_auth, odoo_api, odoo_uid, odoo_object, item_name):
    odoo_api.create_applicant_with_name(odoo_object, odoo_uid, odoo_auth.api_password, item_name)
    print(f"Applicant {item_name} created in Odoo.")


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
print('Enter the name of the applicant on Monday:')
item_name = input()
fetch_applicants_from_monday(odoo_object, odoo_uid, odoo_auth, monday_auth, monday_api, board_id, item_name)
