from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file

info_tests: list[tuple] = [
        ("calculator", "."),
        ("calculator", "pkg"),
        ("calculator", "/bin"),
        ("calculator", "../")
    ]

content_tests: list[tuple] = [
    ("calculator", "main.py"),
    ("calculator", "pkg/calculator.py"),
    ("calculator", "/bin/cat"),
    ("calculator", "pkg/does_not_exist.py")
]

write_tests: list[tuple] = [
    ("calculator", "lorem.txt", "wait, this isn't lorem ipsum"),
    ("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"),
    ("calculator", "/tmp/temp.txt", "this should not be allowed")
]

def test_info() -> None:
    for test in info_tests:
        dir: str = f"'{test[1]}'" if test[1] != "." else "current"
        print(f"Result for {dir} directory:")
        print(get_files_info(*test))
    
def test_content() -> None:
    for test in content_tests:
        print(f"Result for file '{test[1]}':")
        print(get_file_content(*test))

def test_write() -> None:
    for test in write_tests:
        print(f"Result for file '{test[1]}':")
        print(write_file(*test))


def main():
    # test_info()
    # test_content()
    test_write()

if __name__ == "__main__":
    main()