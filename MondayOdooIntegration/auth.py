import xmlrpc.client
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class MondayAuth:
    api_url: str
    api_key: str

    def get_headers(self):
        return {"Authorization": self.api_key}


@dataclass
class OdooAuth:
    api_url: str
    api_db: str
    api_username: str
    api_password: str
    model_name: str

    def get_object(self):
        return xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.api_url))

    def __get_common(self):
        return xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.api_url))

    def authenticate(self):
        return (self.__get_common()
                .authenticate(self.api_db, self.api_username, self.api_password, {}))


class SecretManager:
    MONDAY_API_KEY_KEY = "MONDAY_API_KEY"
    ODOO_USERNAME_KEY = "ODOO_USERNAME"
    ODOO_PASSWORD_KEY = "ODOO_PASSWORD"
    DOT_ENV_FILENAME = ".env"

    def save_secrets(self, monday_api_key, odoo_username, odoo_password):
        with open("{}".format(self.DOT_ENV_FILENAME), "w") as f:
            lines = ["{}={}\n".format(self.MONDAY_API_KEY_KEY, monday_api_key),
                     "{}={}\n".format(self.ODOO_USERNAME_KEY, odoo_username),
                     "{}={}\n".format(self.ODOO_PASSWORD_KEY, odoo_password)]
            f.writelines(lines)

    @staticmethod
    def load_secrets():
        load_dotenv()