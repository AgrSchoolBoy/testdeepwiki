"""
Chat view for the Telegram Console Client.
"""

import urwid
import asyncio
from datetime import datetime
from ..image_converter import ImageToAscii

class ChatView:
    """View for displaying and interacting with a chat."""
    
    def __init__(self, telegram_handler, dialog, on_close):
        """Initialize the chat view.
        
        Args:
            telegram_handler: The Telegram handler.
            dialog: The dialog object.
            on_close: Callback function when the view is closed.
        """
        self.telegram_handler = telegram_handler
        self.dialog = dialog
        self.on_close = on_close
        self.messages = []
        self.entity = None
        self.image_converter = ImageToAscii()
        self.list_walker = urwid.SimpleFocusListWalker([])
        
        # Create the view
        self.view = self._create_view()
        
        # Load initial messages
        asyncio.create_task(self._load_messages())
    
    def _create_view(self):
        """Create the view widget.
        
        Returns:
            The view widget.
        """
        # Create header (will be updated with entity name)
        self.header = urwid.AttrMap(
            urwid.Text('Loading...', align='center'),
            'dialog_focus'
        )
        
        # Create the message list
        self.list_box = urwid.ListBox(self.list_walker)
        
        # Create the message input
        self.message_edit = urwid.Edit('Message: ')
        
        # Create send button
        send_button = urwid.Button('Send', self._on_send)
        send_button = urwid.AttrMap(send_button, 'panel', 'dialog_focus')
        
        # Create load more button
        load_more_button = urwid.Button('Load More', self._on_load_more)
        load_more_button = urwid.AttrMap(load_more_button, 'panel', 'dialog_focus')
        
        # Create input area
        input_area = urwid.Columns([
            ('weight', 8, self.message_edit),
            ('weight', 2, send_button)
        ])
        
        # Create footer with buttons
        footer = urwid.Pile([
            load_more_button,
            urwid.AttrMap(input_area, 'panel')
        ])
        
        # Create the frame with header, body and footer
        frame = urwid.Frame(
            body=self.list_box,
            header=self.header,
            footer=footer,
            focus_part='footer'
        )
        
        # Handle key presses
        return urwid.AttrMap(frame, 'panel')
    
    def get_widget(self):
        """Get the view widget.
        
        Returns:
            The view widget.
        """
        return self.view
    
    async def _load_messages(self, offset_id=0):
        """Load messages for the chat.
        
        Args:
            offset_id: Message ID to start from (for pagination).
        """
        try:
            # Get entity
            if not self.entity:
                self.entity = await self.telegram_handler.get_entity(self.dialog)
                
                # Update header with entity name
                name = getattr(self.entity, 'title', None) or getattr(self.entity, 'first_name', '')
                if hasattr(self.entity, 'last_name') and self.entity.last_name:
                    name += f" {self.entity.last_name}"
                
                self.header.original_widget.set_text(name)
            
            # Get messages
            messages = await self.telegram_handler.get_chat_messages(
                self.dialog,
                limit=50,
                offset_id=offset_id
            )
            
            # If loading more, append to existing messages
            if offset_id > 0:
                self.messages.extend(messages)
            else:
                self.messages = messages
            
            # Create message items
            items = []
            for message in self.messages:
                # Get sender
                try:
                    sender = await self.telegram_handler.client.get_entity(message.from_id)
                    sender_name = getattr(sender, 'first_name', '')
                    if hasattr(sender, 'last_name') and sender.last_name:
                        sender_name += f" {sender.last_name}"
                except:
                    sender_name = "Unknown"
                
                # Format timestamp
                timestamp = datetime.fromtimestamp(message.date.timestamp()).strftime('%Y-%m-%d %H:%M:%S')
                
                # Process message content
                content = []
                
                # Add sender and time
                content.append([
                    ('message_sender', f"{sender_name}"),
                    ('message_time', f" [{timestamp}]:\n")
                ])
                
                # Add text
                if message.message:
                    content.append(f"{message.message}\n")
                
                # Process media
                if message.media:
                    try:
                        # Download media
                        media_data = await self.telegram_handler.client.download_media(
                            message.media,
                            bytes
                        )
                        
                        if media_data:
                            # Convert image to ASCII
                            ascii_art = self.image_converter.convert_image_to_ascii(media_data)
                            if ascii_art:
                                content.append(f"\n{ascii_art}\n")
                            else:
                                content.append("[Media: Could not render]\n")
                        else:
                            content.append("[Media: Could not download]\n")
                    except Exception as e:
                        content.append(f"[Media: {str(e)}]\n")
                
                # Create message widget
                message_widget = urwid.Text(content)
                items.append(urwid.Padding(message_widget, left=1, right=1))
                
                # Add separator
                items.append(urwid.Divider('─'))
            
            # Update the list
            self.list_walker[:] = items
            
            # Scroll to bottom for new messages
            if offset_id == 0:
                self.list_box.set_focus(0)
        
        except Exception as e:
            # Show error
            self.list_walker[:] = [urwid.Text(f"Error loading messages: {e}")]
    
    def _on_send(self, button):
        """Handle send button press.
        
        Args:
            button: The button widget.
        """
        # Get message text
        message_text = self.message_edit.edit_text
        
        if not message_text.strip():
            # Empty message, do nothing
            return
        
        # Clear input
        self.message_edit.edit_text = ""
        
        # Send message
        asyncio.create_task(self._send_message(message_text))
    
    async def _send_message(self, text):
        """Send a message.
        
        Args:
            text: The message text.
        """
        try:
            # Send the message
            await self.telegram_handler.send_message(self.dialog, text)
            
            # Reload messages to show the sent message
            await self._load_messages()
        except Exception as e:
            # Show error
            self.list_walker[:] = [urwid.Text(f"Error sending message: {e}")]
    
    def _on_load_more(self, button):
        """Handle load more button press.
        
        Args:
            button: The button widget.
        """
        if self.messages:
            # Get the oldest message ID
            oldest_id = min(m.id for m in self.messages)
            
            # Load more messages
            asyncio.create_task(self._load_messages(offset_id=oldest_id))
    
    def keypress(self, size, key):
        """Handle key presses.
        
        Args:
            size: The size of the widget.
            key: The key pressed.
            
        Returns:
            The key if not handled, or None.
        """
        if key == 'esc':
            self.on_close()
            return None
        elif key == 'enter' and self.view.focus_part == 'footer':
            # If Enter is pressed in the input area, send the message
            self._on_send(None)
            return None
        
        # Pass other keys to the parent
        return super().keypress(size, key)