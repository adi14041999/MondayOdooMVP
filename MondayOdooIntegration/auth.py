import xmlrpc.client  # Importing the XML-RPC client library
from dataclasses import dataclass  # Importing the dataclass decorator for creating classes with lightweight syntax
from dotenv import load_dotenv  # Importing load_dotenv function to load environment variables from .env file


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


@dataclass
class OdooAuth:
    api_username: str  # Username for Odoo authentication
    api_password: str  # Password for Odoo authentication

    @staticmethod
    def get_object(api_url: str) -> xmlrpc.client.ServerProxy:
        """
        Static method to get the ServerProxy object.

        Parameters:
            api_url (str): URL of the API.

        Returns:
            xmlrpc.client.ServerProxy: ServerProxy object for the specified API URL.
        """
        return xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(api_url))

    @staticmethod
    def __get_common(api_url: str) -> xmlrpc.client.ServerProxy:
        """
        Private static method to get the common ServerProxy object.

        Parameters:
            api_url (str): URL of the API.

        Returns:
            xmlrpc.client.ServerProxy: Common ServerProxy object for the specified API URL.
        """
        return xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(api_url))

    def authenticate(self, api_db: str, api_url: str) -> int:
        """
        Method to authenticate with Odoo.

        Parameters:
            api_db (str): Name of the Odoo database.
            api_url (str): URL of the Odoo API.

        Returns:
            int: Authentication result.
        """
        return (self.__get_common(api_url)
                .authenticate(api_db, self.api_username, self.api_password, {}))  # Authenticating and returning


class SecretManager:
    MONDAY_API_KEY_KEY = "MONDAY_API_KEY"  # Key for Monday API key in .env file
    ODOO_USERNAME_KEY = "ODOO_USERNAME"  # Key for Odoo username in .env file
    ODOO_PASSWORD_KEY = "ODOO_PASSWORD"  # Key for Odoo password in .env file
    DOT_ENV_FILENAME = ".env"  # Filename for the .env file

    def save_secrets(self, monday_api_key: str, odoo_username: str, odoo_password: str) -> None:
        """
        Method to save secrets to .env file.

        Parameters:
            monday_api_key (str): API key for Monday.
            odoo_username (str): Username for Odoo.
            odoo_password (str): Password for Odoo.
        """
        with open("{}".format(self.DOT_ENV_FILENAME), "w") as f:  # Opening .env file in write mode
            lines = ["{}={}\n".format(self.MONDAY_API_KEY_KEY, monday_api_key),  # Lines to write in .env file
                     "{}={}\n".format(self.ODOO_USERNAME_KEY, odoo_username),
                     "{}={}\n".format(self.ODOO_PASSWORD_KEY, odoo_password)]
            f.writelines(lines)  # Writing lines to .env file

    @staticmethod
    def load_secrets() -> bool:
        """
        Static method to load secrets from .env file.

        Returns:
            bool: Whether the loading was successful or not.
        """
        return load_dotenv()  # Loading environment variables from .env file
