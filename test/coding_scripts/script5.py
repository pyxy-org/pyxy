# coding: pyxy

el = <a>{<img /> if True else ""}</a>
el2 = (<a>
          { <img src={url} /> for url in ["cat.png", "dog.png", "cow.png"] }
      </a>)
print(el)
print(el2)
