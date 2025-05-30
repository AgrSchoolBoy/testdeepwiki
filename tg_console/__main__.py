#!/usr/bin/env python3
"""
Main entry point for the Telegram Console Client.
"""

import os
import sys
import asyncio
from .app import TelegramConsoleApp

def main():
    """Main entry point for the application."""
    # Create application instance
    app = TelegramConsoleApp()
    
    try:
        # Run the application
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("Application terminated by user.")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())