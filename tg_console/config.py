"""
Configuration handling for the Telegram Console Client.
"""

import os
import json
import getpass
from pathlib import Path

class Config:
    """Configuration handler for the Telegram Console Client."""
    
    DEFAULT_CONFIG = {
        "api_id": None,
        "api_hash": None,
        "session_file": "tg_session",
        "ascii_art_width": 40,
        "max_messages": 50
    }
    
    def __init__(self):
        """Initialize the configuration."""
        self.config_dir = os.path.join(Path.home(), ".tg_console")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config = self._load_config()
    
    def _load_config(self):
        """Load the configuration from file."""
        # Create config directory if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Try to load existing config
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Update with any missing default values
                    for key, value in self.DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception:
                # If there's an error, use the default config
                pass
        
        # If no valid config, prompt for API credentials
        config = self.DEFAULT_CONFIG.copy()
        print("Telegram API credentials are required to use this application.")
        print("You can obtain them from https://my.telegram.org/apps")
        
        config["api_id"] = input("Enter API ID: ")
        config["api_hash"] = getpass.getpass("Enter API Hash: ")
        
        # Save the config
        self._save_config(config)
        
        return config
    
    def _save_config(self, config):
        """Save the configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    @property
    def api_id(self):
        """Get the API ID."""
        return self.config.get("api_id")
    
    @property
    def api_hash(self):
        """Get the API hash."""
        return self.config.get("api_hash")
    
    @property
    def session_file(self):
        """Get the session file path."""
        return os.path.join(self.config_dir, self.config.get("session_file"))
    
    @property
    def ascii_art_width(self):
        """Get the ASCII art width."""
        return self.config.get("ascii_art_width", 40)
    
    @property
    def max_messages(self):
        """Get the maximum number of messages to display."""
        return self.config.get("max_messages", 50)