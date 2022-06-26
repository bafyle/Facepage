from PIL import Image

def image_resize(image):
    
    if image.width > 1000 or image.height > 1000:
        aspect_ratio = image.height / image.width 

        new_width = image.width // 2
        new_height = int(new_width * aspect_ratio)

        image = image.resize((new_width, new_height), Image.BOX)

def save_compressed_image(image, absolute_path_with_name):
     image.save(absolute_path_with_name, 
                "JPEG", 
                optimize = True, 
                quality = 50)