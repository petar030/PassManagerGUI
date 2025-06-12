import json
import base64
import hashlib
from cryptography.fernet import Fernet

class PasswordManagerAPI:
    def __init__(self, data=None):
        self.data = data if data else {"metadata": {}, "entries": []}
        self.key = None

    def _derive_key(self, password):
        digest = hashlib.sha256(password.encode()).digest()
        return base64.urlsafe_b64encode(digest)

    def list_entries(self):
        return [(e["name"], e.get("username", "")) for e in self.data["entries"]]

    def add_entry(self, name, username, password, notes=""):
        if any(e["name"] == name for e in self.data["entries"]):
            return False
        self.data["entries"].append({
            "name": name,
            "username": username,
            "password": password,
            "notes": notes
        })
        return True

    def find_entry_index(self, name):
        for i, e in enumerate(self.data["entries"]):
            if e["name"] == name:
                return i
        return -1

    def edit_entry(self, name, **kwargs):
        idx = self.find_entry_index(name)
        if idx == -1:
            return False
        for key, value in kwargs.items():
            if key in self.data["entries"][idx]:
                self.data["entries"][idx][key] = value
        return True

    def delete_entry(self, name):
        idx = self.find_entry_index(name)
        if idx == -1:
            return False
        del self.data["entries"][idx]
        return True

    def save_to_file(self, filepath, password=None):
        if password:
            self.key = self._derive_key(password)
        if not self.key:
            return False
        fernet = Fernet(self.key)
        try:
            with open(filepath, "wb") as f:
                f.write(fernet.encrypt(json.dumps(self.data).encode()))
            return True
        except Exception:
            return False

    def load_from_file(self, filepath, password):
        if not filepath.endswith(".pass"):
            return False
        self.key = self._derive_key(password)
        fernet = Fernet(self.key)
        try:
            with open(filepath, "rb") as f:
                decrypted = fernet.decrypt(f.read())
            self.data = json.loads(decrypted.decode())
            return True
        except Exception:
            return False
