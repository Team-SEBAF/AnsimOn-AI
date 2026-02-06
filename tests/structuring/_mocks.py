class MockValidator:
    def validate(self, output_json):
        return {
            "status": "PASS",
            "error_codes": [],
            "message": None,
        }

class MemoryCache(dict):
    def get(self, key):
        return super().get(key)

    def set(self, key, value):
        self[key] = value
