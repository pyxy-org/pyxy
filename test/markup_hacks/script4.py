from . import div, img, ul, li, _

def is_logged_in() -> bool:
    return False

animal_images = ["cat.png", "dog.png", "cow.png"]
status_image = "logged-in.png" if is_logged_in() else "logged-out.png"

markup = (_
    [div]
        [img(src=status_image)]
        [ul]
            ( _[li][img(src=image_file)][-li] for image_file in animal_images )
        [-ul]
        ("Some character data")
    [-div]
)

print(markup)
