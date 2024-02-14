from dotenv import dotenv_values
from auth import SecretManager
from auth import MondayAuth
from auth import OdooAuth
from monday_crud import MondayAPI
from odoo_crud import OdooAPI

MONDAY_URL = "https://api.monday.com/v2"
MONDAY_BOARD_ID = 5990805927

ODOO_URL = "https://citrus2.odoo.com"
ODOO_DB = "citrus2"
ODOO_MODEL_NAME = "hr.applicant"


# Fetch all applicants with name "Chavex", and add them to Odoo
def use_case_1(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object):
    response = monday_api.get_items_names(monday_auth.api_key, MONDAY_BOARD_ID)
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        if response_json:
            for board in response_json['data']['boards']:
                for item in board['items_page']['items']:
                    name = item['name']
                    if name == "Chavex":
                        odoo_api.create_applicant_with_name(odoo_object, odoo_uid, odoo_auth.api_password, name)
                        print(f"Applicant {name} created in Odoo.")
    else:
        print("Failed to fetch data from Monday.com")
        return None


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

    monday_auth = MondayAuth(MONDAY_URL, monday_api_key)
    odoo_auth = OdooAuth(ODOO_URL, ODOO_DB, odoo_username, odoo_password, ODOO_MODEL_NAME)

    odoo_uid = odoo_auth.authenticate()
    odoo_object = odoo_auth.get_object()

    monday_api = MondayAPI(MONDAY_URL)
    odoo_api = OdooAPI(ODOO_URL, ODOO_DB, ODOO_MODEL_NAME)

    # All use cases below
    use_case_1(monday_auth, monday_api, odoo_auth, odoo_api, odoo_uid, odoo_object)


# Using the special variable __name__
if __name__ == "__main__":
    main()
