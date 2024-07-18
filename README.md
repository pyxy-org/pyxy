# pyxy
<img alt="pyxy logo" src="https://raw.githubusercontent.com/pyxy-org/pyxy/main/etc/header.png">

<p align="center">
    <em>
        HTML in Python<br><br><b>work-in-progress<br>contributions appreciated</b>
    </em>
</p>
<hr>

`pyxy` lets you put HTML directly in Python code. You can think of it as JSX for Python.
It builds on the fantastic work of [pyxl](https://github.com/dropbox/pyxl), which is a similar project predating JSX.
Compared to pyxl, it takes a new approach that makes other tools do most of the work:

* `parso` provides the tokenization and parsing, using a [custom grammar](https://github.com/pyxy-org/pyxy/blob/5494493ffc105f1cc8103b58ea56fda3d89fc4fe/pyxy/grammar/pyxy312.txt#L171-L193) to enable handling XML
* `htpy` is used to rebuild markup

Here's a minimal example:

```python
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

## IDE Support

* [PyCharm Plugin](https://plugins.jetbrains.com/plugin/24817-pyxy-support/)
* [Sublime Text syntax highlighting](https://github.com/pyxy-org/sublime-pyxy)
* VSCode - not yet supported, see https://github.com/pyxy-org/pyxy/issues/10

## Tool support

* `ruff` - partial support, see https://github.com/pyxy-org/pyxy/issues/8
* `mypy` - not yet supported, see https://github.com/pyxy-org/pyxy/issues/9
* `pyright` - not yet supported, see https://github.com/pyxy-org/pyxy/issues/11
* `black` - not yet supported, see https://github.com/pyxy-org/pyxy/issues/7

## See also

### HTML-in-Python Implementations
* [dropbox/pyxl](https://github.com/dropbox/pyxl) - The original
* [gvanrossum/pyxl3](https://github.com/gvanrossum/pyxl3) - Python 3 support
* [pyxl4/pyxl4](https://github.com/pyxl4/pyxl4) - A fork created when `pyxl3` was no longer maintained
* [twidi/mixt](https://github.com/twidi/mixt) - Another fork of Pyxl with a lot of features
* [michaeljones/packed](https://github.com/michaeljones/packed) - A unique effort that uses decorators and a compilation step
* [pelme/htpy](https://github.com/pelme/htpy) - Not HTML-in-Python, but close. A great solution to generating HTML with Python
* [RudreshVeerkhare/ReactPy](https://github.com/RudreshVeerkhare/ReactPy) - Another implementation of HTML in Python

#### Using tagged strings

* [rmorshea/tagstr](https://github.com/rmorshea/tagstr)
* [jviide/htm.py](https://github.com/jviide/htm.py)
* [treykeown/taglit](https://github.com/treykeown/taglit)

#### Syntax Support 
* [christoffer/pycharm-pyxl](https://github.com/christoffer/pycharm-pyxl) - Pyxl support for PyCharm
* [yyjhao/sublime-pyxl](https://github.com/yyjhao/sublime-pyxl) - Pyxl syntax highlighting for Sublime Text

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
* [php](https://www.php.net/)
