"""
Image to ASCII converter for the Telegram Console Client.
"""

import io
from PIL import Image, UnidentifiedImageError

class ImageToAscii:
    """Convert images to ASCII art."""
    
    # ASCII characters used for different brightness levels (from dark to light)
    ASCII_CHARS = '@%#*+=-:. '
    
    def __init__(self, width=40):
        """Initialize the converter.
        
        Args:
            width: Width of the ASCII art in characters.
        """
        self.width = width
    
    def convert_image_to_ascii(self, image_data):
        """Convert an image to ASCII art.
        
        Args:
            image_data: The raw image data.
            
        Returns:
            A string containing the ASCII art, or None if conversion failed.
        """
        try:
            # Open the image from binary data
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Resize maintaining aspect ratio
            orig_width, orig_height = image.size
            aspect_ratio = orig_height / orig_width
            new_height = int(self.width * aspect_ratio * 0.5)  # Adjust for terminal's character aspect ratio
            image = image.resize((self.width, new_height))
            
            # Convert pixels to ASCII characters
            pixels = list(image.getdata())
            ascii_art = []
            for i in range(0, len(pixels), self.width):
                row = pixels[i:i + self.width]
                ascii_row = ''.join([self._pixel_to_ascii(pixel) for pixel in row])
                ascii_art.append(ascii_row)
            
            return '\n'.join(ascii_art)
        
        except UnidentifiedImageError:
            return "[Image format not supported]"
        except Exception as e:
            return f"[Error converting image: {e}]"
    
    def _pixel_to_ascii(self, pixel_value):
        """Convert a pixel value to an ASCII character.
        
        Args:
            pixel_value: The pixel brightness value (0-255).
            
        Returns:
            An ASCII character representing the brightness.
        """
        # Map the pixel value to an index in the ASCII_CHARS list
        index = int(pixel_value * (len(self.ASCII_CHARS) - 1) / 255)
        return self.ASCII_CHARS[index]