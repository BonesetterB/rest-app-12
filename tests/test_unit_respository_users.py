import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.model import User, Contact
from src.schemas import UserSchema, UserResponseSchema
from src.repository.users import get_user_by_email, user_to_response_schema, create_user, update_token,  update_avatar

class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user= User(id=1, username='Corwin', email='test50@example.com', 
                        avatar='https://www.gravatar.com/avatar/00000000000000000000000000000000?d=https%3A%2F%2Fexample.com%2Fimages%2Favatar.jpg',
                        refresh_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxMjo1NSIsImV4cCI6IjEzOjUwIiwic2NvcGUiOiJhY2Nlc3NfdG9rZW4ifQ.Pe9sfTZm6uYV8KuJkgtk5v6J1BkiqP0PQAQDE_V7rcg')
        self.token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxMzo1NSIsImV4cCI6IjE0OjUwIiwic2NvcGUiOiJhY2Nlc3NfdG9rZW4ifQ._PbxM4tv3f9DB6r37HHceE5Zu4TT6dgXRhwOr1337K4'
    def tearDown(self):
        del self.session
        del self.user

    async def test_create_user(self):
        body=UserSchema(username='Cor5win',email='test@example.com', password='qwer5ty')
        result = await create_user(body,self.session)

        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)

        self.assertTrue(hasattr(result, "id"))

    async def test_user_to_response_schema(self):
        result = await user_to_response_schema(self.user)

        self.assertEqual(result.username, self.user.username)
        self.assertEqual(result.email, self.user.email)
        self.assertEqual(result.avatar, self.user.avatar)

        self.assertTrue(hasattr(result, "id"))
    
   
    async def test_update_token(self):
        result = await update_token(self.user,self.token,self.session)

        self.assertEqual(self.token, self.user.refresh_token)


    

if __name__ == "__main__":
    unittest.main()