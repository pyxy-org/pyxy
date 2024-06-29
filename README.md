# pyxy

<p align="center">
    <em>
        HTML in Python
    </em>
</p>
<hr>

`pyxy` is lets you put HTML in Python. Right now there are two approaches for this:

* Raw Markup - HTML directly in source code (like JSX). This currently won't work with most Python tooling.
* Tagged Strings - More powerful f-strings that can do arbitrary transformations (including things useful for HTML). Doesn't break any existing Python tooling.

## Implementations

### Raw Markup

You can think of this as JSX for Python. It builds on the fantastic work of PyXL, which is a similar project that actually predates JSX. Compared to Pyxl, it takes a new approach that makes other tools do most of the work:

* `parso` provides the tokenization and parsing
* `htpy` is used to rebuild markup

This uses a standard Python parser (provided by `parso`), but with a [custom grammar](https://github.com/pyxy-org/pyxy/blob/5494493ffc105f1cc8103b58ea56fda3d89fc4fe/pyxy/grammar/pyxy312.txt#L171-L193) to enable handling XML.

This is still very much a work-in-progress. Here's a minimal example:

```python
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

### Tagged Strings

I've also been experimenting with tagged strings. This is similar to [what's being planned for a future PEP](https://github.com/jimbaker/tagstr/blob/main/pep.rst).
It some `ast` magic to automatically replace any **uppercase** f-strings (`F'...'`) with behavior similar to what's described in the PEP.

The advantage to this is that all existing tooling will continue to work without any modifications.

Here's an example:

```python
from pyxy.tagstr import tagstr, html

def is_logged_in() -> bool:
    return False

animal_images = ["cat.png", "dog.png", "cow.png"]
status_image = "logged-in.png" if is_logged_in() else "logged-out.png"

@tagstr(html)
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

## See also

### HTML-in-Python Implementations
* [dropbox/pyxl](https://github.com/dropbox/pyxl) - The original
* [gvanrossum/pyxl3](https://github.com/gvanrossum/pyxl3)
* [pyxl4/pyxl4](https://github.com/pyxl4/pyxl4)
* [twidi/mixt](https://github.com/twidi/mixt)
* [michaeljones/packed](https://github.com/michaeljones/packed)

#### Syntax Support 
* [christoffer/pycharm-pyxl](https://github.com/christoffer/pycharm-pyxl)
* [yyjhao/sublime-pyxl](https://github.com/yyjhao/sublime-pyxl)

### HTML-in-* Implementations
* [ECMAScript 4 XML (E4X)](https://en.wikipedia.org/wiki/ECMAScript_for_XML) - The oldest example I can find of XML being embedded in another language (2004!)
* [JSX](https://facebook.github.io/jsx/) - A document detailing the motivations for JSX over other alternatives
* [gox](https://github.com/8byt/gox) - HTML in Go
* [templ](https://github.com/a-h/templ) - HTML in Go (but templates?)
* [rsx](https://github.com/victorporof/rsx) - HTML in Rust
* [syn-rsx](https://github.com/stoically/syn-rsx) - HTML in Rust
* [rstml](https://github.com/rs-tml/rstml) - HTML in Rust
* [LuaX](https://bvisness.me/luax/) - HTML in Lua
* [gccx](https://github.com/mbasso/gccx) - HTML in C++
* [rux](https://github.com/camertron/rux) - HTML in Ruby
* [php](https://www.php.net/) - heh
