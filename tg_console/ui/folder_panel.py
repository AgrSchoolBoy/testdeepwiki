"""
Folder panel for the Telegram Console Client.
"""

import urwid
import asyncio

class FolderPanel:
    """Panel for displaying and navigating Telegram folders."""
    
    def __init__(self, telegram_handler, on_select):
        """Initialize the folder panel.
        
        Args:
            telegram_handler: The Telegram handler.
            on_select: Callback function when a folder is selected.
        """
        self.telegram_handler = telegram_handler
        self.on_select = on_select
        self.folders = []
        self.list_walker = urwid.SimpleFocusListWalker([])
        
        # Create the panel
        self.panel = self._create_panel()
        
        # Initial loading of folders
        asyncio.create_task(self.refresh())
    
    def _create_panel(self):
        """Create the panel widget.
        
        Returns:
            The panel widget.
        """
        # Create header
        header = urwid.AttrMap(
            urwid.Text('Folders', align='center'),
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
        """Refresh the folder list."""
        # Get folders
        self.folders = await self.telegram_handler.get_folders()
        
        # Create folder items
        items = []
        for folder in self.folders:
            # Create item
            text = urwid.Text([('folder', f"{folder['title']} ({folder['count']})")])
            
            # Create selectable item
            item = urwid.AttrMap(
                FolderItem(text, folder, self.on_select),
                'panel',
                'folder_focus'
            )
            
            items.append(item)
        
        # Update the list
        self.list_walker[:] = items


class FolderItem(urwid.WidgetWrap):
    """Selectable item for folders."""
    
    def __init__(self, text_widget, folder, on_select):
        """Initialize the folder item.
        
        Args:
            text_widget: The text widget.
            folder: The folder object.
            on_select: Callback function when selected.
        """
        self.folder = folder
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
            self.on_select(self.folder)
            return None
        return key