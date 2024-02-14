import xmlrpc.client  # Importing the XML-RPC client library
from dataclasses import dataclass  # Importing the dataclass decorator for creating classes with lightweight syntax
from dotenv import load_dotenv  # Importing load_dotenv function to load environment variables from .env file


@dataclass
class MondayAuth:
    api_url: str  # URL of the Monday API
    api_key: str  # API key for authentication

    def get_headers(self):
        """
        Returns the headers for authentication.

        Returns:
            dict: The headers with the API key.
        """
        return {"Authorization": self.api_key}  # Returning headers with API key


@dataclass
class OdooAuth:
    api_url: str  # URL of the Odoo API
    api_db: str  # Database name for Odoo
    api_username: str  # Username for Odoo authentication
    api_password: str  # Password for Odoo authentication
    model_name: str  # Name of the model for Odoo operations

    def get_object(self):
        """
        Returns the XML-RPC server proxy object for Odoo object operations.

        Returns:
            xmlrpc.client.ServerProxy: The server proxy object.
        """
        return xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.api_url))

    def __get_common(self):
        """
        Returns the XML-RPC server proxy object for Odoo common operations.

        Returns:
            xmlrpc.client.ServerProxy: The server proxy object.
        """
        return xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.api_url))

    def authenticate(self):
        """
        Authenticates with the Odoo API.

        Returns:
            int: The user ID upon successful authentication.
        """
        return (self.__get_common()
                .authenticate(self.api_db, self.api_username, self.api_password, {}))  # Authenticating and returning


class SecretManager:
    MONDAY_API_KEY_KEY = "MONDAY_API_KEY"  # Key for Monday API key in .env file
    ODOO_USERNAME_KEY = "ODOO_USERNAME"  # Key for Odoo username in .env file
    ODOO_PASSWORD_KEY = "ODOO_PASSWORD"  # Key for Odoo password in .env file
    DOT_ENV_FILENAME = ".env"  # Filename for the .env file

    def save_secrets(self, monday_api_key, odoo_username, odoo_password):
        """
        Saves secrets (Monday API key, Odoo username, and Odoo password) to a .env file.

        Args:
            monday_api_key (str): The API key for Monday.
            odoo_username (str): The username for Odoo.
            odoo_password (str): The password for Odoo.
        """
        with open("{}".format(self.DOT_ENV_FILENAME), "w") as f:  # Opening .env file in write mode
            lines = ["{}={}\n".format(self.MONDAY_API_KEY_KEY, monday_api_key),  # Lines to write in .env file
                     "{}={}\n".format(self.ODOO_USERNAME_KEY, odoo_username),
                     "{}={}\n".format(self.ODOO_PASSWORD_KEY, odoo_password)]
            f.writelines(lines)  # Writing lines to .env file

    @staticmethod
    def load_secrets():
        """
        Loads secrets from a .env file.
        """
        return load_dotenv()  # Loading environment variables from .env file
