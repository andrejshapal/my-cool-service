import logging

from flask import current_app
from opa_client.opa import OpaClient

class OpaValidator:
    def __init__(self, port=8181):
        host = current_app.config.get("OPA_HOST")
        port = current_app.config.get("OPA_PORT")
        try:
            self.client = OpaClient(host=host, port=int(port))
        except Exception as e:
            current_app.logger.error(f"Failed to initialize OpaClient with host={host}, port={port}: {e}")
            raise
    def close(self):
        try:
            self.client.close_connection()
            current_app.logger.info("OPA connection closed successfully")
        except Exception as e:
            current_app.logger.error("Was not able to close OPA connection: %s", e)

    def check_connection(self):
        try:
            status = self.client.check_connection()
            current_app.logger.info("Testing connection with OPA: %s", status)
            return status
        except Exception as e:
            current_app.logger.error("Connection with OPA failed: %s", e)
            # Optionally, attempt to close the client
            self.close()
            return False

    def validate_call(self, name, email, role, method, path: str) -> bool:
        check_data = {
            'path': path.strip("/").split("/"),
            'name': name,
            'email': email,
            'role': role,
            'method': method,
        }

        try:
            result = self.client.query_rule(
                input_data=check_data,
                package_path="httpapi.authz",
                rule_name="allow"
            )
            return result.get('result', False)
        except Exception as e:
            current_app.logger.error("Failed to evaluate policy: %s", e)
            return False
        finally:
            self.close()