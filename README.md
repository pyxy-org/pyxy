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

logged_in = False
some_class = "wrapper"
name = "world"

hello = <div class={some_class}>Hello, {name}!</div>
custom = (<el-banner some-attr="something" disabled>
              { <img src="logged-in.png" /> if logged_in else <img src="logged-out.png" /> }
          </el-banner>)

print(hello)
print(custom)

```

```html
<div class="wrapper">Hello, world!</div>
<el-banner some-attr="something" disabled><img src="logged-out.png"></el-banner>
```
