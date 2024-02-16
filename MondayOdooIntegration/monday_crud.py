import json
import requests


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

    def create_item_with_name(self, api_key: str, board_id: int, item_name: str) -> requests.Response:
        """
        Creates an item with the specified name.

        Parameters:
            api_key (str): API key for authentication.
            board_id (int): ID of the board.
            item_name (str): Name of the item to be created.

        Returns:
            requests.Response: Response object from the API.
        """
        query = 'mutation {{ create_item (board_id: {}, item_name: "{}") {{ id }} }}'.format(board_id, item_name)
        return self.__make_query(api_key, query)

    def create_item_with_values(self, api_key: str, board_id: int, item_name: str,
                                values_json: dict) -> requests.Response:
        """
        Creates an item with the specified values.

        Parameters:
            api_key (str): API key for authentication.
            board_id (int): ID of the board.
            item_name (str): Name of the item to be created.
            values_json (dict): JSON containing values for the item.

        Returns:
            requests.Response: Response object from the API.
        """
        query = ('mutation ($myItemName: String!, $columnVals: JSON!) {{ create_item (board_id:{}, '
                 'item_name:$myItemName, column_values:$columnVals) {{ id }} }}').format(board_id)
        values_dictionary = {
            'myItemName': item_name,
            'columnVals': json.dumps(values_json)
        }
        return self.__make_query_with_values(api_key, query, values_dictionary)

    def read_boards(self, api_key: str) -> requests.Response:
        """
        Reads boards from the Monday API.

        Parameters:
            api_key (str): API key for authentication.

        Returns:
            requests.Response: Response object from the API.
        """
        query = '{ boards { name id } }'
        return self.__make_query(api_key, query)

    def read_column_ids_of_board(self, api_key: str, board_id: int) -> requests.Response:
        """
        Reads column IDs of a board from the Monday API.

        Parameters:
            api_key (str): API key for authentication.
            board_id (int): ID of the board.

        Returns:
            requests.Response: Response object from the API.
        """
        query = '{{boards(ids: {}) {{columns {{id title}}}}}}'.format(board_id)
        return self.__make_query(api_key, query)

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

    def read_items_with_column_ids(self, api_key: str, board_id: int, column_id1: str,
                                   column_id2: str) -> requests.Response:
        """
        Reads items with multiple column IDs from the Monday API.

        Parameters:
            api_key (str): API key for authentication.
            board_id (int): ID of the board.
            column_id1 (str): ID of the first column.
            column_id2 (str): ID of the second column.

        Returns:
            requests.Response: Response object from the API.
        """
        query = ('{{boards(ids: {}) {{ items_page {{ items {{ name column_values(ids: ["{}", "{}"]) {{ text '
                 'column {{ id } } } }}}}}}}}}'.format(board_id, column_id1, column_id2))
        return self.__make_query(api_key, query)

    def read_items_with_column_ids_list(self, api_key: str, board_id: int, column_ids_list: list) -> requests.Response:
        """
        Reads items with a list of column ids from the Monday API.

        Parameters:
            api_key (str): API key for authentication.
            board_id (int): ID of the board.
            column_ids_list (list): List of column values.

        Returns:
            requests.Response: Response object from the API.
        """
        column_ids = ['"{}"'.format(column_value) for column_value in column_ids_list]
        query = ('{{boards(ids: {}) {{ items_page {{ items {{ name column_values(ids: [{}]) {{ text '
                 'column {{ id } } }}}}}}}}}'.format(board_id, ", ".join(column_ids)))
        return self.__make_query(api_key, query)

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
