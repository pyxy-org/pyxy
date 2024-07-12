# pyxy.importer

Import `.pyxy` files like regular `.py` files. Inspired by [pyximport](https://github.com/cython/cython/tree/master/pyximport).

If you have a module named `foo.pyxy`, you can now just use `import foo` to import it. This also works for running it as a module: `python3 -m foo`.

## Recommended usage

```sh
# Installs the hook for importing .pyxy files
# Persists in the site-packages where this is run
python3 -m pyxy.importer install

# Removes the hook
python3 -m pyxy.importer uninstall
```

## Without installation

To use the hook without installing it to your environment, just `import pyxy.importer.hook` before attempting to import any `.pyxy` files.
