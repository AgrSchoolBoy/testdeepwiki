"""
Main application class for the Telegram Console Client.
"""

import os
import asyncio
import urwid
from telethon import TelegramClient, events

from .config import Config
from .auth import AuthHandler
from .ui.main_view import MainView
from .telegram_client import TelegramHandler

class TelegramConsoleApp:
    """Main application class for the Telegram Console Client."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = Config()
        self.loop = None
        self.client = None
        self.telegram_handler = None
        self.ui = None
        
    async def run(self):
        """Run the application."""
        # Initialize the event loop
        self.loop = asyncio.get_event_loop()
        
        # Create and initialize the Telegram client
        self.client = TelegramClient(
            self.config.session_file,
            self.config.api_id,
            self.config.api_hash
        )
        
        # Create telegram handler
        self.telegram_handler = TelegramHandler(self.client)
        
        # Start the client
        await self.client.start()
        
        # Check if authentication is needed
        auth_handler = AuthHandler(self.client)
        if not await self.client.is_user_authorized():
            await auth_handler.authenticate()
        
        # Create and initialize the UI
        self.ui = MainView(self.telegram_handler, self.exit_application)
        
        # Set up event handlers for new messages
        self.client.add_event_handler(
            self.telegram_handler.on_new_message,
            events.NewMessage()
        )
        
        # Run the UI
        self.ui_loop = urwid.MainLoop(
            self.ui.get_widget(),
            palette=self.ui.palette,
            event_loop=urwid.AsyncioEventLoop(loop=self.loop),
            unhandled_input=self.unhandled_input
        )
        
        # Start the UI
        self.ui_loop.run()
    
    def unhandled_input(self, key):
        """Handle unhandled key inputs."""
        if key in ('q', 'Q', 'ctrl q'):
            self.exit_application()
            return True
        return False
    
    def exit_application(self):
        """Exit the application."""
        # Close the UI loop
        raise urwid.ExitMainLoop()