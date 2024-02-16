from auth import SecretManager
from auth import MondayAuth
from auth import OdooAuth
from monday_crud import MondayAPI
from odoo_crud import OdooAPI

from dotenv import dotenv_values

MONDAY_URL = "https://api.monday.com/v2"
MONDAY_BOARD_ID = 5990805927

ODOO_URL = "https://citrus2.odoo.com"
ODOO_DB = "citrus2"
ODOO_MODEL_NAME = "hr.applicant"
# ODOO_MODEL_NAME = "hr.employee"

STATUS_TO_STAGE_ID = {
    "New": 1,
    "Initial Qualification": 2,
    "First Interview": 3,
    "Second interview": 4,
    "Contract Proposal": 5,
    "Contract Signed": 6,
}


# Fetch all applicants with name "Chaves", and add them to Odoo
def use_case_1(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object):
    response = monday_api.read_items_and_names(monday_auth.api_key, MONDAY_BOARD_ID)
    if response.status_code == 200:
        response_json = response.json()
        if response_json:
            for board in response_json['data']['boards']:
                for item in board['items_page']['items']:
                    name = item['name']
                    if name == "Chaves":
                        odoo_api.create_applicant_with_name(odoo_object, odoo_uid, odoo_auth.api_password, name)
                        print(f"Applicant {name} created in Odoo.")
    else:
        print("Failed to fetch data from Monday.com")
        return None


# Updates the status of all Odoo applicants considering Monday as the source of truth
def use_case_2(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object):
    response = monday_api.read_items_with_column_id(monday_auth.api_key, MONDAY_BOARD_ID, "status")
    if response.status_code == 200:
        response_json = response.json()
        if response_json:
            for item in response_json['data']['boards'][0]['items_page']['items']:
                partner_name = item['name']
                status_text = item['column_values'][0]['text'] if item['column_values'] else 'Status not found'
                stage_id = STATUS_TO_STAGE_ID.get(status_text, None)
                if stage_id is None:
                    print(f"No stage ID found for status '{status_text}'. Skipping...")
                    continue
                applicant_ids = odoo_api.read_applicants_ids_with_name(odoo_object, odoo_uid, odoo_auth.api_password,
                                                                       partner_name)
                applicant_data = {
                    'partner_name': partner_name,
                    'name': 'Updated Status!',
                    'stage_id': stage_id
                }
                if not applicant_ids:
                    new_applicant_id = odoo_api.create_applicant_with_fields(odoo_object, odoo_uid,
                                                                             odoo_auth.api_password, applicant_data)
                    print(f"Created new applicant with ID: {new_applicant_id}")
                else:
                    for applicant_id in applicant_ids:
                        odoo_api.update_fields_of_applicant(odoo_object, odoo_uid, odoo_auth.api_password,
                                                            applicant_id, applicant_data)
                        print(
                            f"Updated applicant {partner_name} with new stage ID: {stage_id} and name: {partner_name}")
    else:
        print("Failed to fetch data from Monday.com")
        return None


# Move all the employees from Odoo to a board on Monday with similar fields
def use_case_3(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object):
    fields_list = ['name', 'work_email', 'job_id', 'department_id']
    # TODO: populate those fields on Monday
    monday_fields = []
    employees = odoo_api.read_employees_and_fields(odoo_object, odoo_uid, odoo_auth.api_password, fields_list)
    response = monday_api.create_board_with_name(monday_auth.api_key, "Employees from Odoo")
    if response.status_code == 200:
        response_json = response.json()
        if response_json:
            board_id = response_json['data']['create_board']['id']
            for employee in employees:
                monday_api.create_item_with_name(monday_auth.api_key, board_id, employee['name'])


# Get addresses of all employees in Odoo with name 'Andy' and do something with them on Monday
def use_case_4(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object):
    fields_list = ['private_street', 'private_city', 'private_zip']
    employees = odoo_api.read_employees_and_fields_with_name(odoo_object, odoo_uid, odoo_auth.api_password,
                                                             "Andy", fields_list)
    if employees:
        for employee in employees:
            address = f"{employee['private_street']}, {employee['private_city']}, {employee['private_zip']}"
            print(address)
            # TODO: Do something on Monday
    return None


# Delete some users from Monday and Odoo
def use_case_5(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object):
    delete_from_monday = [6076917957, 6076918096]
    for applicant_id in delete_from_monday:
        monday_api.delete_item(monday_auth.api_key, applicant_id)
        print("Deleted: ", applicant_id)
    delete_from_odoo = odoo_api.read_applicants_ids(odoo_object, odoo_uid, odoo_auth.api_password)
    for applicant_id in delete_from_odoo:
        odoo_api.delete_applicant(odoo_object, odoo_uid, odoo_auth.api_password, applicant_id)
        print("Deleted: ", applicant_id)


def main():
    loaded = SecretManager.load_secrets()
    if not loaded:
        print("What is your Monday API key?")
        monday_api_key = input()
        print("What is your Odoo username?")
        odoo_username = input()
        print("What is your Odoo password?")
        odoo_password = input()
        secret_manager = SecretManager()
        secret_manager.save_secrets(monday_api_key, odoo_username, odoo_password)
        print("Secrets saved. You won't be asked these again.")
    secrets = dotenv_values(SecretManager.DOT_ENV_FILENAME)
    monday_api_key = secrets[SecretManager.MONDAY_API_KEY_KEY]
    # print(monday_api_key)
    odoo_username = secrets[SecretManager.ODOO_USERNAME_KEY]
    # print(odoo_username)
    odoo_password = secrets[SecretManager.ODOO_PASSWORD_KEY]
    # print(odoo_password)

    monday_auth = MondayAuth(monday_api_key)
    odoo_auth = OdooAuth(odoo_username, odoo_password)

    odoo_uid = odoo_auth.authenticate(ODOO_DB, ODOO_URL)
    odoo_object = odoo_auth.get_object(ODOO_URL)

    monday_api = MondayAPI(MONDAY_URL)
    odoo_api = OdooAPI(ODOO_URL, ODOO_DB)

    # All use cases below
    """"
    use_case_1(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object)
    use_case_2(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object)
    use_case_3(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object)
    use_case_4(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object)
    use_case_5(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object)
    """


# Using the special variable __name__
if __name__ == "__main__":
    main()
