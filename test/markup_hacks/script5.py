from . import div, img, ul, li, xml

def is_logged_in() -> bool:
    return False

animal_images = ["cat.png", "dog.png", "cow.png"]
status_image = "logged-in.png" if is_logged_in() else "logged-out.png"

# This is insane
ᐸimg = img
ᐸdiv = div
ᐸⳆdiv = div
ᐸul = ul
ᐸⳆul = ul
ᐸli = li
ᐸⳆli = li

markup = (
    ᐸdiv>
        ᐸimg(src=status_image)>
        ᐸul>
            xml( ᐸli>ᐸimg(src=image_file)>ᐸⳆli>xml for image_file in animal_images ) +
        ᐸⳆul>
        xml("Some character data") +
    ᐸⳆdiv>
xml)

print(markup)
