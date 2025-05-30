"""
Main view for the Telegram Console Client.
"""

import urwid
from .message_panel import MessagePanel
from .folder_panel import FolderPanel
from .chat_view import ChatView

class MainView:
    """Main view with two-panel interface."""
    
    def __init__(self, telegram_handler, exit_callback):
        """Initialize the main view.
        
        Args:
            telegram_handler: The Telegram handler.
            exit_callback: Callback function to exit the application.
        """
        self.telegram_handler = telegram_handler
        self.exit_callback = exit_callback
        self.active_panel = 'messages'  # 'messages' or 'folders'
        self.chat_view = None
        
        # Set up color palette
        self.palette = [
            ('header', 'white', 'dark blue'),
            ('footer', 'white', 'dark blue'),
            ('panel', 'white', 'black'),
            ('panel_focus', 'black', 'light gray'),
            ('dialog', 'black', 'light gray'),
            ('dialog_focus', 'white', 'dark blue'),
            ('status', 'white', 'dark green'),
            ('error', 'white', 'dark red'),
            ('message_sender', 'light green', 'black'),
            ('message_time', 'dark cyan', 'black'),
            ('unread', 'light red', 'black'),
            ('folder', 'yellow', 'black'),
            ('folder_focus', 'black', 'yellow'),
        ]
        
        # Create the panels
        self.message_panel = MessagePanel(telegram_handler, self.open_chat)
        self.folder_panel = FolderPanel(telegram_handler, self.open_folder)
        
        # Create the main layout
        self.main_layout = self._create_main_layout()
    
    def _create_main_layout(self):
        """Create the main layout with header, footer and panels.
        
        Returns:
            The main layout widget.
        """
        # Create header
        header = urwid.AttrMap(
            urwid.Text(' Telegram Console Client', align='center'),
            'header'
        )
        
        # Create footer with key bindings
        footer_text = ' Tab: Switch panel | Enter: Select | Esc: Back | Ctrl+Q: Quit '
        footer = urwid.AttrMap(
            urwid.Text(footer_text, align='center'),
            'footer'
        )
        
        # Create columns with message and folder panels
        self.columns = urwid.Columns([
            ('weight', 1, self.message_panel.get_widget()),
            ('weight', 1, self.folder_panel.get_widget())
        ])
        
        # Set focus to the message panel by default
        self.columns.focus_position = 0
        
        # Create the frame with header, body and footer
        frame = urwid.Frame(
            body=self.columns,
            header=header,
            footer=footer
        )
        
        # Handle key presses
        return urwid.Padding(urwid.AttrMap(frame, 'panel'), left=1, right=1)
    
    def get_widget(self):
        """Get the main widget.
        
        Returns:
            The main widget.
        """
        return self.main_layout
    
    def switch_panel(self):
        """Switch focus between message and folder panels."""
        if self.columns.focus_position == 0:
            self.columns.focus_position = 1
            self.active_panel = 'folders'
        else:
            self.columns.focus_position = 0
            self.active_panel = 'messages'
    
    def open_chat(self, dialog):
        """Open a chat view.
        
        Args:
            dialog: The dialog object for the chat.
        """
        # Create the chat view
        self.chat_view = ChatView(self.telegram_handler, dialog, self.close_chat)
        
        # Replace the main body with the chat view
        self.main_layout.original_widget.body = self.chat_view.get_widget()
    
    def open_folder(self, folder):
        """Open a folder view.
        
        Args:
            folder: The folder object.
        """
        # Update the message panel to show dialogs from the selected folder
        self.message_panel.set_folder(folder['id'])
        
        # Switch focus to the message panel
        self.columns.focus_position = 0
        self.active_panel = 'messages'
    
    def close_chat(self):
        """Close the chat view and return to the main view."""
        # Restore the main columns view
        self.main_layout.original_widget.body = self.columns
        
        # Update the message list
        self.message_panel.refresh()