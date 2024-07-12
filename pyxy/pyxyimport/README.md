# pyxyimport

Automatically converts a .pyxy file to .py, then imports that. Inspired by [pyximport](https://github.com/cython/cython/tree/master/pyximport).

Recommended usage:

```sh
# Installs the importer hook to enable importing .pyxy files
# Persists in the site-packages where this is run
python3 -m pyxy.importer install

# Removes the hook
python3 -m pyxy.importer uninstall
```

To use the hook without installing it to your environment, just `import pyxy.importer.hook`

Once installed, `.pyxy` files will work exactly the same as `.py` files. If you have a module named `foo.pyxy`, you can now just use `import foo` to import it. This also works for running it as a module: `python3 -m foo`.
