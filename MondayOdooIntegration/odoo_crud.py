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

    def create_applicant_with_field_id_and_field_value(
            self, api_model_name: str, odoo_object, api_uid, api_password, field_id, field_name
    ):
        """
        Creates an applicant with the specified field ID and field value.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            field_id: ID of the field.
            field_name: Name of the field.

        Returns:
            Query result.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'create', [{field_id: field_name}], None
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

    def read_applicants_ids(self, api_model_name: str, odoo_object, api_uid, api_password) -> list:
        """
        Reads applicant IDs from the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.

        Returns:
            List of applicant IDs.
        """
        return self.__make_query(api_model_name, odoo_object, api_uid, api_password, 'search', [[]], None)

    def read_applicants_ids_and_names(self, api_model_name: str, odoo_object, api_uid, api_password) -> list:
        """
        Reads applicant IDs and names from the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.

        Returns:
            List of tuples containing applicant ID and name.
        """
        applicant_ids = self.read_applicants_ids(api_model_name, odoo_object, api_uid, api_password)
        applicants_details = self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'read', [applicant_ids],
            {'fields': ['id', 'partner_name', 'name']}
        )
        applicant_tuples = [(applicant['id'], applicant['partner_name']) for applicant in applicants_details]
        return applicant_tuples

    def read_applicants_details(self, api_model_name: str, odoo_object, api_uid, api_password):
        """
        Reads applicant details from the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.

        Returns:
            Applicant details.
        """
        return self.__make_query(api_model_name, odoo_object, api_uid, api_password, 'fields_get', [],
                                 {'attributes': ['string', 'type']})

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

    def read_applicants_and_fields(self, api_model_name: str, odoo_object, api_uid, api_password, fields_list: list):
        """
        Reads applicants and specified fields from the Odoo API.

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
        return self.read_applicants_and_fields(api_model_name, odoo_object, api_uid, api_password, fields_list)

    def read_employees_and_fields_with_name(self, api_model_name: str, odoo_object, api_uid, api_password,
                                            employee_name: str,
                                            fields_list: list):
        """
        Reads employees with a specific name and specified fields from the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            employee_name (str): Name of the employee.
            fields_list (list): List of fields to be retrieved.

        Returns:
            Query result.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'search_read',
            [[['name', '=', employee_name]]], {'fields': fields_list}
        )

    def update_field_of_applicant(
            self, api_model_name: str, odoo_object, api_uid, api_password, applicant_id, field_id, field_value
    ):
        """
        Updates a field of an applicant in the Odoo API.

        Parameters:
            api_model_name (str): Name of the model.
            odoo_object: Object for executing the query.
            api_uid: User ID for authentication.
            api_password: Password for authentication.
            applicant_id: ID of the applicant.
            field_id: ID of the field.
            field_value: Value of the field.

        Returns:
            Query result.
        """
        return self.__make_query(
            api_model_name, odoo_object, api_uid, api_password, 'write',
            [[int(applicant_id)], {field_id: field_value}], None
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
