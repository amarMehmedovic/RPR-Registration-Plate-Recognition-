import cv2
import numpy as np

# Read the image
image = cv2.imread('polo.jpg')

# Convert the image from BGR to RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Define the lower and upper bounds for the blue color in RGB format
lower_blue = np.array([0, 0, 100], dtype=np.uint8)
upper_blue = np.array([100, 100, 255], dtype=np.uint8)

# Create a mask where blue pixels are set to 255 (white) and non-blue pixels are set to 0 (black)
mask_blue = cv2.inRange(image_rgb, lower_blue, upper_blue)

# Invert the mask so that blue pixels are set to 0 (black) and non-blue pixels are set to 255 (white)
mask_not_blue = cv2.bitwise_not(mask_blue)

# Create a white image
white_image = np.ones_like(image) * 255

# Replace the blue parts of the original image with white
result = cv2.bitwise_and(image, image, mask=mask_not_blue) + cv2.bitwise_and(white_image, white_image, mask=mask_blue)

# Save or display the result
cv2.imwrite('result_image.jpg', result)
# cv2.imshow('Result', result)
# cv2.waitKey(0)
# cv2.destroyAllWindows()