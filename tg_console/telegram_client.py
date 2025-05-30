"""
Telegram client handler for the Telegram Console Client.
"""

import asyncio
from telethon import utils
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser, InputPeerChat
from telethon.tl.functions.messages import GetHistoryRequest

class TelegramHandler:
    """Handle Telegram client operations."""
    
    def __init__(self, client):
        """Initialize the Telegram handler.
        
        Args:
            client: The Telegram client.
        """
        self.client = client
        self.dialogs = []
        self.folders = []
        self.current_messages = {}
        self.new_message_callback = None
        self.dialog_update_callback = None
    
    async def get_dialogs(self, folder_id=None):
        """Get all dialogs (chats) for the user.
        
        Args:
            folder_id: Optional folder ID to filter dialogs.
            
        Returns:
            List of dialog objects.
        """
        result = await self.client(GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=100,
            hash=0,
            folder_id=folder_id
        ))
        
        self.dialogs = result.dialogs
        return self.dialogs
    
    async def get_folders(self):
        """Get all folders for the user.
        
        Returns:
            List of folder objects.
        """
        # Get all dialogs to ensure we have folder info
        result = await self.client(GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=100,
            hash=0
        ))
        
        # Extract folders
        self.folders = []
        
        # Add "All Chats" as a pseudo-folder
        self.folders.append({
            "id": None,
            "title": "All Chats",
            "count": len(result.dialogs)
        })
        
        # Add real folders
        for folder in result.folder_peers:
            folder_info = {
                "id": folder.folder_id,
                "title": f"Folder {folder.folder_id}",
                "count": 0  # Will be updated when needed
            }
            self.folders.append(folder_info)
        
        return self.folders
    
    async def get_entity(self, dialog):
        """Get the entity (user/chat/channel) for a dialog.
        
        Args:
            dialog: The dialog object.
            
        Returns:
            The entity object.
        """
        return await self.client.get_entity(dialog.peer)
    
    async def get_chat_messages(self, dialog, limit=50, offset_id=0):
        """Get messages for a chat.
        
        Args:
            dialog: The dialog object.
            limit: Maximum number of messages to retrieve.
            offset_id: Message ID to start from (for pagination).
            
        Returns:
            List of message objects.
        """
        entity = await self.get_entity(dialog)
        
        # Get message history
        result = await self.client(GetHistoryRequest(
            peer=entity,
            limit=limit,
            offset_date=None,
            offset_id=offset_id,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))
        
        return result.messages
    
    async def send_message(self, dialog, text):
        """Send a message to a chat.
        
        Args:
            dialog: The dialog object.
            text: The message text.
            
        Returns:
            The sent message object.
        """
        entity = await self.get_entity(dialog)
        return await self.client.send_message(entity, text)
    
    async def on_new_message(self, event):
        """Handle new message events.
        
        Args:
            event: The message event.
        """
        # Store the new message
        chat_id = utils.get_peer_id(event.message.peer_id)
        
        if chat_id not in self.current_messages:
            self.current_messages[chat_id] = []
        
        self.current_messages[chat_id].insert(0, event.message)
        
        # Limit the number of stored messages
        if len(self.current_messages[chat_id]) > 100:
            self.current_messages[chat_id] = self.current_messages[chat_id][:100]
        
        # Call the callback if set
        if self.new_message_callback:
            self.new_message_callback(event.message)
        
        # Update dialog list if callback is set
        if self.dialog_update_callback:
            await self.dialog_update_callback()
    
    def set_new_message_callback(self, callback):
        """Set the callback for new messages.
        
        Args:
            callback: The callback function.
        """
        self.new_message_callback = callback
    
    def set_dialog_update_callback(self, callback):
        """Set the callback for dialog updates.
        
        Args:
            callback: The callback function.
        """
        self.dialog_update_callback = callback