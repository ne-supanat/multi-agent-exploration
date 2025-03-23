from PIL import Image
import numpy as np
from constants.gridCellType import GridCellType


def imageToArray(path: str, row, column):
    # Load the image
    img = Image.open(path).convert("L")  # convert to grayscale

    # Resize image to match parameters
    img = img.resize((column, row))  # (width, height)

    # Convert to NumPy array
    arr = np.array(img, dtype=int)

    # Change value white pixel (>100) to unexplored cell and black pixel (<=100) to wall cell
    return np.where(arr > 100, GridCellType.UNEXPLORED.value, GridCellType.WALL.value)
