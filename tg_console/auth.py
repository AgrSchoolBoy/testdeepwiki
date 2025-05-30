"""
Authentication handler for the Telegram Console Client.
"""

import getpass
import asyncio

class AuthHandler:
    """Handle Telegram authentication."""
    
    def __init__(self, client):
        """Initialize the authentication handler.
        
        Args:
            client: The Telegram client.
        """
        self.client = client
    
    async def authenticate(self):
        """Authenticate the user with Telegram."""
        print("Authentication required.")
        
        # Get phone number
        phone = input("Enter your phone number (with country code): ")
        
        # Send code request
        await self.client.send_code_request(phone)
        
        # Get verification code
        code = input("Enter the verification code sent to your phone or Telegram: ")
        
        try:
            # Sign in with the code
            await self.client.sign_in(phone, code)
        except Exception as e:
            # If sign in fails due to 2FA
            if "2FA" in str(e) or "password" in str(e).lower():
                # Get 2FA password
                password = getpass.getpass("Enter your 2FA password: ")
                await self.client.sign_in(password=password)
            else:
                # Other authentication error
                raise Exception(f"Authentication failed: {e}")
        
        print("Authentication successful!")