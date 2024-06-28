# pyxy

<p align="center">
    <em>
        HTML in Python
    </em>
</p>
<hr>

`pyxy` is lets you put HTML in Python. You can think of it as JSX for Python, but it builds on the fantastic work of PyXL and mixt. It takes a new approach for its implementation:

* `parso` provides the tokenization and parsing
* `htpy` is used to rebuild markup

This is still very much a work-in-progress. Here's a minimal example:

```
# coding: pyxy

hello = <div class="test">Hello, world!</div>
custom = (<custom-element custom-attr="some value" disabled>
            <img src="example.png" />
          </custom-element>)
print(hello)
print(custom)
```

```html
<div class="test">Hello, world!</div>
<custom-element custom-attr="some value" disabled><img src="example.png"></custom-element>
```
