from dataclasses import dataclass  # Importing the dataclass decorator for creating classes with lightweight syntax
import requests

MONDAY_URL = "https://api.monday.com/v2"


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

    def delete_item(self, api_key: str, item_id: int) -> requests.Response:
        """
        Deletes an item from the Monday API.

        Parameters:
            api_key (str): API key for authentication.
            item_id (int): ID of the item to be deleted.

        Returns:
            requests.Response: Response object from the API.
        """
        query = 'mutation {{ delete_item (item_id: {}) {{ id }}}}'.format(item_id)
        return self.__make_query(api_key, query)


def delete_item_from_monday(monday_auth, monday_api, item_id_on_monday):
    monday_api.delete_item(monday_auth.api_key, item_id_on_monday)
    print("Deleted: ", item_id_on_monday)


print('Enter the monday_api_key:')
monday_api_key = input()

monday_auth = MondayAuth(monday_api_key)
monday_api = MondayAPI(MONDAY_URL)

print('Enter the id of item on Monday to delete:')
item_id_on_monday = int(input())

delete_item_from_monday(monday_auth, monday_api, item_id_on_monday)
