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

    def read_applicants_ids_with_name(self, api_model_name: str, odoo_object, api_uid, api_password,
                                      applicant_name: str) -> list:
        """
        Reads applicant IDs with a specific name from the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            applicant_name (str): Name of the applicant.

        Returns:
            List of applicant IDs.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'search', [[['partner_name', '=', applicant_name]]],
            None
        )

    def create_applicant_with_fields(
            self, api_model_name: str, odoo_object, api_uid, api_password, field_dictionary
    ):
        """
        Creates an applicant with the specified fields.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            field_dictionary: Dictionary containing fields and their values.

        Returns:
            Query result.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'create', [field_dictionary], None
        )

    def update_fields_of_applicant(
            self, api_model_name: str, odoo_object, api_uid, api_password, applicant_id, field_dictionary
    ):
        """
        Updates fields of an applicant in the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            applicant_id: ID of the applicant.
            field_dictionary: Dictionary containing fields and their values to be updated.

        Returns:
            Query result.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'write', [[int(applicant_id)], field_dictionary], None
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

    def read_items_with_column_id(self, api_key: str, board_id: int, column_id: str) -> requests.Response:
        """
        Reads items with a specific column ID from the Monday API.

        Parameters:
            api_key (str): API key for authentication.
            board_id (int): ID of the board.
            column_id (str): ID of the column.

        Returns:
            requests.Response: Response object from the API.
        """
        query = ('{{boards(ids: {}) {{ items_page {{ items {{ name column_values(ids: ["{}"]) {{ text '
                 'column {{ id }}}}}}}}}}}}'.format(board_id, column_id))
        return self.__make_query(api_key, query)


def fetch_applicants_from_monday_and_update_on_odoo(odoo_object, odoo_uid, odoo_auth, monday_auth, monday_api, board_id, id_name,
                                 id_status, STATUS_TO_STAGE_ID):
    response = monday_api.read_items_with_column_id(monday_auth.api_key, board_id, id_status)
    if response.status_code == 200:
        response_json = response.json()
        if response_json:
            for item in response_json['data']['boards'][0]['items_page']['items']:
                partner_name = item[id_name]
                status_text = item['column_values'][0]['text'] if item['column_values'] else 'Status not found'
                stage_id = STATUS_TO_STAGE_ID.get(status_text, None)
                if stage_id is None:
                    print(f"No stage ID found for status '{status_text}'. Skipping...")
                    continue
                applicant_ids = odoo_api.read_applicants_ids_with_name(ODOO_MODEL_NAME, odoo_object, odoo_uid,
                                                                       odoo_auth.api_password, partner_name)
                applicant_data = {
                    'partner_name': partner_name,
                    'name': 'Updated Status!',
                    'stage_id': stage_id
                }
                if not applicant_ids:
                    new_applicant_id = odoo_api.create_applicant_with_fields(ODOO_MODEL_NAME, odoo_object, odoo_uid,
                                                                             odoo_auth.api_password, applicant_data)
                    print(f"Created new applicant with ID: {new_applicant_id}")
                else:
                    for applicant_id in applicant_ids:
                        odoo_api.update_fields_of_applicant(ODOO_MODEL_NAME, odoo_object, odoo_uid,
                                                            odoo_auth.api_password, applicant_id, applicant_data)
                        print(
                            f"Updated applicant {partner_name} with new stage ID: {stage_id} and name: {partner_name}")
    else:
        print("Failed to fetch data from Monday.com")


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
print('Enter the id of the name of the applicant on Monday:')
id_name = input()
print('Enter the id of the status of the applicant on Monday:')
id_status = input()
print('Enter the status list on Monday: ')
STATUS_TO_STAGE_ID = {}
for i in range(1, 7):
    STATUS_TO_STAGE_ID[input()] = i

fetch_applicants_from_monday_and_update_on_odoo(odoo_object, odoo_uid, odoo_auth, monday_auth, monday_api, board_id, id_name, id_status,
                             STATUS_TO_STAGE_ID)
