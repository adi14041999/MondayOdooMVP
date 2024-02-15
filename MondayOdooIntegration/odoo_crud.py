class OdooAPI:
    # Class variables
    api_url: str
    api_db: str
    api_model_name: str

    # Constructor
    def __init__(self, api_url: str, api_db: str, api_model_name: str):
        """
        Initialize OdooAPI object with API URL, database name, and model name.

        Parameters:
            api_url (str): The URL of the Odoo API.
            api_db (str): The name of the database to connect to.
            api_model_name (str): The name of the model to interact with.
        """
        self.api_url = api_url
        self.api_db = api_db
        self.api_model_name = api_model_name

    # Private method for making queries
    def __make_query(self, odoo_object, api_uid, api_password, action, search_filter, fields):
        """
        Make a query to the Odoo API.

        Parameters:
            odoo_object: The Odoo API object used to make the request.
            api_uid: The user ID for authentication.
            api_password: The password for authentication.
            action (str): The action to perform (e.g., 'search', 'read', 'create', 'write', 'unlink').
            search_filter: The filter criteria for the query.
            fields: The fields to retrieve or manipulate in the query.

        Returns:
            The result of the query.
        """
        if fields:
            return odoo_object.execute_kw(
                self.api_db, api_uid, api_password, self.api_model_name, action, search_filter, fields
            )
        else:
            return odoo_object.execute_kw(
                self.api_db, api_uid, api_password, self.api_model_name, action, search_filter
            )

    # Methods for fetching data

    def get_applicants_ids(self, odoo_object, api_uid, api_password):
        """
        Get IDs of all applicants.

        Parameters:
            odoo_object: The Odoo API object used to make the request.
            api_uid: The user ID for authentication.
            api_password: The password for authentication.

        Returns:
            List of IDs of all applicants.
        """
        return self.__make_query(odoo_object, api_uid, api_password, 'search', [[]], None)

    def get_applicants_ids_and_names(self, odoo_object, api_uid, api_password):
        """
        Get IDs and names of all applicants.

        Parameters:
            odoo_object: The Odoo API object used to make the request.
            api_uid: The user ID for authentication.
            api_password: The password for authentication.

        Returns:
            List of tuples containing (ID, name) of all applicants.
        """
        applicant_ids = self.get_applicants_ids(odoo_object, api_uid, api_password)
        applicants_details = self.__make_query(
            odoo_object, api_uid, api_password, 'read', [applicant_ids], {'fields': ['id', 'partner_name', 'name']}
        )
        applicant_tuples = [(applicant['id'], applicant['partner_name']) for applicant in applicants_details]
        return applicant_tuples

    def get_applicants_details(self, odoo_object, api_uid, api_password):
        """
        Get details of all applicants.

        Parameters:
            odoo_object: The Odoo API object used to make the request.
            api_uid: The user ID for authentication.
            api_password: The password for authentication.

        Returns:
            Details of all applicants.
        """
        return self.__make_query(odoo_object, api_uid, api_password, 'fields_get', [],
                                 {'attributes': ['string', 'type']})

    # WORKING
    def get_applicant_id_with_name(self, odoo_object, api_uid, api_password, applicant_name):
        """
        Get the ID of an applicant by name.

        Parameters:
            odoo_object: The Odoo API object used to make the request.
            api_uid: The user ID for authentication.
            api_password: The password for authentication.
            applicant_name (str): The name of the applicant to search for.

        Returns:
            ID of the applicant with the specified name.
        """
        return self.__make_query(
            odoo_object, api_uid, api_password, 'search', [[['partner_name', '=', applicant_name]]], None
        )

    # Methods for creating data

    # WORKING
    def create_applicant_with_field_id_and_field_value(
            self, odoo_object, api_uid, api_password, field_id, field_name
    ):
        """
        Create an applicant with a specified field ID and value.

        Parameters:
            odoo_object: The Odoo API object used to make the request.
            api_uid: The user ID for authentication.
            api_password: The password for authentication.
            field_id: The ID of the field to set.
            field_name: The value to set for the field.

        Returns:
            ID of the created applicant.
        """
        return self.__make_query(
            odoo_object, api_uid, api_password, 'create', [{field_id: field_name}], None
        )

    # WORKING
    def create_applicant_with_fields(
            self, odoo_object, api_uid, api_password, field_dictionary
    ):
        return self.__make_query(
            odoo_object, api_uid, api_password, 'create', [field_dictionary], None
        )

    # WORKING
    def create_applicant_with_name(self, odoo_object, api_uid, api_password, applicant_name):
        """
        Create an applicant with a specified name.

        Parameters:
            odoo_object: The Odoo API object used to make the request.
            api_uid: The user ID for authentication.
            api_password: The password for authentication.
            applicant_name (str): The name of the applicant to create.

        Returns:
            ID of the created applicant.
        """
        return self.__make_query(
            odoo_object, api_uid, api_password, 'create',
            [{'partner_name': applicant_name, 'name': 'New Applicant!'}], None)

    # Methods for updating data

    # WORKING
    def update_field_of_applicant_with_id(
            self, odoo_object, api_uid, api_password, applicant_id, field_id, field_value
    ):
        """
        Update a field of an applicant by ID.

        Parameters:
            odoo_object: The Odoo API object used to make the request.
            api_uid: The user ID for authentication.
            api_password: The password for authentication.
            applicant_id: The ID of the applicant to update.
            field_id: The ID of the field to update.
            field_value: The new value for the field.

        Returns:
            ID of the updated applicant.
        """
        return self.__make_query(
            odoo_object, api_uid, api_password, 'write',
            [[int(applicant_id)], {field_id: field_value}], None
        )

    # WORKING
    def update_fields_of_applicant_with_id(
            self, odoo_object, api_uid, api_password, applicant_id, field_dictionary
    ):
        return self.__make_query(
            odoo_object, api_uid, api_password, 'write', [[int(applicant_id)], field_dictionary], None
        )

    # Method for deleting data

    def delete_applicant_with_id(self, odoo_object, api_uid, api_password, applicant_id):
        """
        Delete an applicant by ID.

        Parameters:
            odoo_object: The Odoo API object used to make the request.
            api_uid: The user ID for authentication.
            api_password: The password for authentication.
            applicant_id: The ID of the applicant to delete.

        Returns:
            ID of the deleted applicant.
        """
        return self.__make_query(
            odoo_object, api_uid, api_password, 'unlink', [[int(applicant_id)]], None
        )
