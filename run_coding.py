import pyxy.coding  # noqa

def print_heading(script_name: str) -> None:
    print("\n\n========================================")
    print(f"{script_name.replace('/', '.')[:-3]}")
    print("----------------------------------------")
    with open(script_name, "rb") as fh:
        print(fh.read().decode("pyxy"))
    print("----------------------------------------")


if __name__ == "__main__":
    print_heading("test/scripts/basic1.py")
    import test.scripts.basic1  # noqa

    print_heading("test/scripts/basic2.py")
    import test.scripts.basic2  # noqa

    print_heading("test/scripts/basic3.py")
    import test.scripts.basic3  # noqa

    print_heading("test/scripts/basic4.py")
    import test.scripts.basic4  # noqa

    print_heading("test/scripts/basic5.py")
    import test.scripts.basic5  # noqa

    print_heading("test/scripts/basic6.py")
    import test.scripts.basic6  # noqa
