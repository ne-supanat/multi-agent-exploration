from PIL import Image
import numpy as np
from constants.gridCellType import GridCellType


def imageToArray(path: str, width, height):
    # Load the image
    img = Image.open(path).convert("L")  # convert to grayscale

    # Resize image to match parameters
    img = img.resize((width, height))

    # Convert to NumPy array
    arr = np.array(img, dtype=int)

    return np.where(arr > 100, GridCellType.UNEXPLORED.value, GridCellType.WALL.value)
