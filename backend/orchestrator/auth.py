class SentinelAuth:
    @staticmethod
    def get_firestore():
        class MockDb:
            def collection(self, name):
                return self
            def where(self, *args):
                return self
            def get(self):
                return []
            def add(self, data):
                pass
        return MockDb()
        
    @staticmethod
    def init_vertex():
        pass
