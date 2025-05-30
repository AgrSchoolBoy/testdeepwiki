"""
Message panel for the Telegram Console Client.
"""

import urwid
import asyncio
from datetime import datetime

class MessagePanel:
    """Panel for displaying messages from all chats."""
    
    def __init__(self, telegram_handler, on_select):
        """Initialize the message panel.
        
        Args:
            telegram_handler: The Telegram handler.
            on_select: Callback function when a message is selected.
        """
        self.telegram_handler = telegram_handler
        self.on_select = on_select
        self.dialogs = []
        self.folder_id = None
        self.list_walker = urwid.SimpleFocusListWalker([])
        
        # Create the panel
        self.panel = self._create_panel()
        
        # Set up callbacks for updates
        self.telegram_handler.set_new_message_callback(self._on_new_message)
        self.telegram_handler.set_dialog_update_callback(self.refresh)
        
        # Initial loading of dialogs
        asyncio.create_task(self.refresh())
    
    def _create_panel(self):
        """Create the panel widget.
        
        Returns:
            The panel widget.
        """
        # Create header
        header = urwid.AttrMap(
            urwid.Text('Recent Messages', align='center'),
            'dialog_focus'
        )
        
        # Create the list box
        self.list_box = urwid.ListBox(self.list_walker)
        
        # Create the frame with header and list box
        frame = urwid.Frame(
            body=self.list_box,
            header=header
        )
        
        # Handle key presses
        return urwid.AttrMap(frame, 'panel')
    
    def get_widget(self):
        """Get the panel widget.
        
        Returns:
            The panel widget.
        """
        return self.panel
    
    async def refresh(self):
        """Refresh the dialog list."""
        # Get dialogs
        self.dialogs = await self.telegram_handler.get_dialogs(self.folder_id)
        
        # Create dialog items
        items = []
        for dialog in self.dialogs:
            try:
                # Get entity (user, chat, channel)
                entity = await self.telegram_handler.get_entity(dialog)
                
                # Get dialog name
                name = getattr(entity, 'title', None) or getattr(entity, 'first_name', '')
                if hasattr(entity, 'last_name') and entity.last_name:
                    name += f" {entity.last_name}"
                
                # Check for unread messages
                unread = dialog.unread_count > 0
                
                # Create item
                if unread:
                    text = urwid.Text([('unread', f"({dialog.unread_count}) "), name])
                else:
                    text = urwid.Text(name)
                
                # Create selectable item
                item = urwid.AttrMap(
                    DialogItem(text, dialog, self.on_select),
                    'panel',
                    'dialog_focus'
                )
                
                items.append(item)
            except Exception as e:
                # Skip any dialogs that cause errors
                continue
        
        # Update the list
        self.list_walker[:] = items
    
    def set_folder(self, folder_id):
        """Set the current folder.
        
        Args:
            folder_id: The folder ID.
        """
        self.folder_id = folder_id
        asyncio.create_task(self.refresh())
    
    def _on_new_message(self, message):
        """Handle new messages.
        
        Args:
            message: The new message.
        """
        # Refresh the dialog list to show updated unread counts
        asyncio.create_task(self.refresh())


class DialogItem(urwid.WidgetWrap):
    """Selectable item for dialogs."""
    
    def __init__(self, text_widget, dialog, on_select):
        """Initialize the dialog item.
        
        Args:
            text_widget: The text widget.
            dialog: The dialog object.
            on_select: Callback function when selected.
        """
        self.dialog = dialog
        self.on_select = on_select
        self._selectable = True
        super().__init__(text_widget)
    
    def keypress(self, size, key):
        """Handle key presses.
        
        Args:
            size: The size of the widget.
            key: The key pressed.
            
        Returns:
            The key if not handled, or None.
        """
        if key == 'enter':
            self.on_select(self.dialog)
            return None
        return key