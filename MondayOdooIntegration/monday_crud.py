import json

import requests


class MondayAPI:
    api_url: str

    def __init__(self, api_url):
        self.api_url = api_url

    def __make_query(self, api_key, query, values_dictionary):
        data = {'query': query, 'variables': values_dictionary}
        headers = {'Authorization': api_key, 'Content-Type': 'application/json'
                   }
        return requests.post(url=self.api_url, json=data, headers=headers)

    def get_boards(self, api_key):
        query = '{ boards { name id } }'
        return self.__make_query(api_key, query, None)

    def create_board(self, api_key, board_name):
        query = 'mutation {{create_board (board_name: "{}", board_kind: public) {{id}}}}'.format(board_name)
        return self.__make_query(api_key, query, None)

    def get_column_ids_of_board(self, api_key, board_id):
        query = '{{boards(ids: {}) {{columns {{id title}}}}}}'.format(board_id)
        return self.__make_query(api_key, query, None)

    def change_column_value_of_item(self, api_key, board_id, item_id, column_id, column_value):
        query = ('mutation {{ change_simple_column_value(item_id: {}, board_id: {}, column_id: "{}", value: "{}") {{'
                 'id}}}}').format(item_id, board_id, column_id, column_value)
        return self.__make_query(api_key, query, None)

    def create_item(self, api_key, board_id, item_name):
        query = 'mutation {{ create_item (board_id: {}, item_name: "{}") {{ id }} }}'.format(board_id, item_name)
        return self.__make_query(api_key, query, None)

    def create_items_with_values(self, api_key, board_id, item_name, values_json):
        query = ('mutation ($myItemName: String!, $columnVals: JSON!) {{ create_item (board_id:{}, '
                 'item_name:$myItemName, column_values:$columnVals) {{ id }} }}').format(board_id)
        values_dictionary = {
            'myItemName': item_name,
            'columnVals': json.dumps(values_json)
        }
        return self.__make_query(api_key, query, values_dictionary)

    def delete_item(self, api_key, item_id):
        query = 'mutation {{ delete_item (item_id: {}) {{ id }}}}'.format(item_id)
        return self.__make_query(api_key, query, None)
