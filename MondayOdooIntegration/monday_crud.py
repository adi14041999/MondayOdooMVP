import json
import requests


class MondayAPI:
    api_url: str

    def __init__(self, api_url):
        """
        Initialize MondayAPI object with the provided API URL.

        Args:
            api_url (str): The URL of the Monday.com API.
        """
        self.api_url = api_url

    def __make_query(self, api_key, query):
        """
        Make a query to the Monday.com API.

        Args:
            api_key (str): The API key for authorization.
            query (str): The GraphQL query string.

        Returns:
            requests.Response: Response object from the API request.
        """
        data = {'query': query}
        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
        return requests.post(url=self.api_url, json=data, headers=headers)

    def __make_query_with_values(self, api_key, query, values_dictionary):
        """
        Make a query to the Monday.com API with a dictionary of values.

        Args:
            api_key (str): The API key for authorization.
            query (str): The GraphQL query string.
            values_dictionary (dict): A dictionary containing variables for the query.

        Returns:
            requests.Response: Response object from the API request.
        """
        data = {'query': query, 'variables': values_dictionary}
        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
        return requests.post(url=self.api_url, json=data, headers=headers)

    def get_boards(self, api_key):
        """
        Retrieve a list of boards from the Monday.com API.

        Args:
            api_key (str): The API key for authorization.

        Returns:
            requests.Response: Response object from the API request.
        """
        query = '{ boards { name id } }'
        return self.__make_query(api_key, query)

    # WORKS
    def create_board(self, api_key, board_name):
        """
        Create a new board on Monday.com.

        Args:
            api_key (str): The API key for authorization.
            board_name (str): The name of the new board.

        Returns:
            requests.Response: Response object from the API request.
        """
        query = 'mutation {{create_board (board_name: "{}", board_kind: public) {{id}}}}'.format(board_name)
        return self.__make_query(api_key, query)

    def get_column_ids_of_board(self, api_key, board_id):
        """
        Retrieve the IDs and titles of columns in a board.

        Args:
            api_key (str): The API key for authorization.
            board_id (str): The ID of the board.

        Returns:
            requests.Response: Response object from the API request.
        """
        query = '{{boards(ids: {}) {{columns {{id title}}}}}}'.format(board_id)
        return self.__make_query(api_key, query)

    # WORKING
    def get_items_names(self, api_key, board_id):
        query = ('{{boards(ids: {}) {{ items_page {{ items {{ name }}}}}}}}'.format(board_id))
        return self.__make_query(api_key, query)

    # WORKING
    def get_item_with_column(self, api_key, board_id, column_value):
        query = ('{{boards(ids: {}) {{ items_page {{ items {{ name column_values(ids: ["{}"]) {{ text '
                 'column {{ id }}}}}}}}}}}}'.format(board_id, column_value))
        return self.__make_query(api_key, query)

    def get_item_with_columns(self, api_key, board_id, column_value1, column_value2):
        """
        Get items with specific column values.

        Args:
            api_key (str): The API key for authorization.
            board_id (str): The ID of the board.
            column_value1 (str): The value of the first column.
            column_value2 (str): The value of the second column.

        Returns:
            requests.Response: Response object from the API request.
        """
        query = ('{{boards(ids: {}) {{ items_page {{ items {{ name column_values(ids: ["{}", "{}"]) {{ text '
                 'column {{ id } } } }}}}}}}}}'.format(board_id, column_value1, column_value2))
        return self.__make_query(api_key, query)

    def get_item_with_columns_list(self, api_key, board_id, column_values_list):
        """
        Get items with specific column values provided in a list.

        Args:
            api_key (str): The API key for authorization.
            board_id (str): The ID of the board.
            column_values_list (list): List of column values to search for.

        Returns:
            requests.Response: Response object from the API request.
        """
        column_ids = ['"{}"'.format(column_value) for column_value in column_values_list]
        query = ('{{boards(ids: {}) {{ items_page {{ items {{ name column_values(ids: [{}]) {{ text '
                 'column {{ id } } }}}}}}}}}'.format(board_id, ", ".join(column_ids)))
        return self.__make_query(api_key, query)

    def change_column_value_of_item(self, api_key, board_id, item_id, column_id, column_value):
        """
        Change the value of a column for an item.

        Args:
            api_key (str): The API key for authorization.
            board_id (str): The ID of the board.
            item_id (str): The ID of the item.
            column_id (str): The ID of the column.
            column_value (str): The new value for the column.

        Returns:
            requests.Response: Response object from the API request.
        """
        query = ('mutation {{ change_simple_column_value(item_id: {}, board_id: {}, column_id: "{}", value: "{}") {{'
                 'id}}}}').format(item_id, board_id, column_id, column_value)
        return self.__make_query(api_key, query)

    # WORKS
    def create_item(self, api_key, board_id, item_name):
        """
        Create a new item on a board.

        Args:
            api_key (str): The API key for authorization.
            board_id (str): The ID of the board.
            item_name (str): The name of the new item.

        Returns:
            requests.Response: Response object from the API request.
        """
        query = 'mutation {{ create_item (board_id: {}, item_name: "{}") {{ id }} }}'.format(board_id, item_name)
        return self.__make_query(api_key, query)

    def create_items_with_values(self, api_key, board_id, item_name, values_json):
        """
        Create a new item on a board with specified column values.

        Args:
            api_key (str): The API key for authorization.
            board_id (str): The ID of the board.
            item_name (str): The name of the new item.
            values_json (dict): A dictionary containing column values for the new item.

        Returns:
            requests.Response: Response object from the API request.
        """
        query = ('mutation ($myItemName: String!, $columnVals: JSON!) {{ create_item (board_id:{}, '
                 'item_name:$myItemName, column_values:$columnVals) {{ id }} }}').format(board_id)
        values_dictionary = {
            'myItemName': item_name,
            'columnVals': json.dumps(values_json)
        }
        return self.__make_query_with_values(api_key, query, values_dictionary)

    # WORKING
    def delete_item(self, api_key, item_id):
        """
        Delete an item from a board.

        Args:
            api_key (str): The API key for authorization.
            item_id (str): The ID of the item to be deleted.

        Returns:
            requests.Response: Response object from the API request.
        """
        query = 'mutation {{ delete_item (item_id: {}) {{ id }}}}'.format(item_id)
        return self.__make_query(api_key, query)
