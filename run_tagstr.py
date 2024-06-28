import pyxy.coding  # noqa

def print_heading(script_name: str) -> None:
    print("\n\n========================================")
    print(f"{script_name.replace('/', '.')[:-3]}")
    print("----------------------------------------")


if __name__ == "__main__":
    print_heading("test/scripts/basic1.py")
    import test.tagstr_scripts.basic1  # noqa
