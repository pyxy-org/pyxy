# pyxy

<p align="center">
    <em>
        HTML in Python
    </em>
</p>
<hr>

`pyxy` is lets you put HTML in Python. Right now there are two approaches for this: raw markup and tagged strings.

## Raw Markup

You can think of this as JSX for Python, but it builds on the fantastic work of PyXL and mixt. Compared to the previous implementations, it takes a new approach:

* `parso` provides the tokenization and parsing
* `htpy` is used to rebuild markup

This uses a standard Python lexer (provided by `parso`), but with a [custom grammar](https://github.com/pyxy-org/pyxy/blob/5494493ffc105f1cc8103b58ea56fda3d89fc4fe/pyxy/grammar/pyxy312.txt#L171-L193) to enable handling XML.

This is still very much a work-in-progress. Here's a minimal example:

```
# coding: pyxy

def is_logged_in() -> bool:
    return False

animal_images = ["cat.png", "dog.png", "cow.png"]
status_image = "logged-in.png" if is_logged_in() else "logged-out.png"

def demo():
    return (
        <div>
            <img src={status_image} />
            <ul>
                { <li><img src={image_file} /></li> for image_file in animal_images }
            </ul>
        </div>
    )

print(demo())
```

```html
<div><img src="logged-out.png"><ul><li><img src="cat.png"></li><li><img src="dog.png"></li><li><img src="cow.png"></li></ul></div>
```

## Tagged Strings

I've also been experimenting with tagged strings. This is similar to [what's being planned for a future PEP](https://github.com/jimbaker/tagstr/blob/main/pep.rst).
It some `ast` magic to automatically replace any **uppercase** f-strings (`F'...'`) with behavior similar to what's described in the PEP.

The advantage to this is that all existing tooling will continue to work without any modifications.

Here's an example:

```python
from pyxy.tagstr import html

def is_logged_in() -> bool:
    return False

animal_images = ["cat.png", "dog.png", "cow.png"]
status_image = "logged-in.png" if is_logged_in() else "logged-out.png"

@html
def demo():
    return F'''
        <div>
            <img src={status_image}>
            <ul>
                {(F'<li><img src={image_file}></li>' for image_file in animal_images)}
            </ul>
        </div>
    '''

print(demo())
```

```html
<div>
    <img src='logged-out.png'>
    <ul>
        <li><img src='cat.png'></li><li><img src='dog.png'></li><li><img src='cow.png'></li>
    </ul>
</div>
```
