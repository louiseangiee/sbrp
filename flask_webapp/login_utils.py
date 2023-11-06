# login_utils.py

from flask_login import login_user

def login_as_user(user_id, allowed_roles):
    # Create a mock user with the specified user ID and roles
    class MockUser:
        def is_authenticated(self):
            return True

        def is_active(self):
            return True

        def is_anonymous(self):
            return False

        def get_id(self):
            return user_id

        def has_role(self, role_id):
            return role_id in allowed_roles

    user = MockUser()
    login_user(user)


