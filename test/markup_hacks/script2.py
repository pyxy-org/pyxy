from . import div, img, ul, li, xml

def is_logged_in() -> bool:
    return False

animal_images = ["cat.png", "dog.png", "cow.png"]
status_image = "logged-in.png" if is_logged_in() else "logged-out.png"

markup = (xml
    <div
        <img(src=status_image)
        <ul
            ( xml <li <img(src=image_file) /li for image_file in animal_images )
        /ul
        ("Some character data")
    /div
/xml)

print(markup)
