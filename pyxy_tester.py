import pyxy  # noqa


if __name__ == "__main__":
    exec(b"print(<custom-tag disabled custom-attr=\"blue\">asdf 2378409 asdf</custom-tag>)".decode(encoding="pyxy"))
