from . import div, img, ul, li, _, xml

def is_logged_in() -> bool:
    return False

animal_images = ["cat.png", "dog.png", "cow.png"]
status_image = "logged-in.png" if is_logged_in() else "logged-out.png"

markup = (xml
    <div>_
        <img(src=status_image)>_
        <ul>_
            ( xml <li>_<img(src=image_file)>_<-li>_ for image_file in animal_images )
        <-ul>_
        ("Some character data")
    <-div>_
)

print(markup)
