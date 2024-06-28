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