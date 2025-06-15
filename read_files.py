import os

def get_file_contents(file_paths):
    """
    Получает содержимое указанных файлов.

    :param file_paths: Список файлов с указанием их путей.
    :return: Словарь с именами файлов и их содержимым.
    """
    file_contents = {}

    for file_path in file_paths:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                file_contents[file_path] = f.read()
        else:
            file_contents[file_path] = "Файл не найден."

    return file_contents


def main():
    # Ввод файлов для чтения
    file_paths = input("Введите пути к файлам через запятую: ").split(",")
    file_paths = [path.strip() for path in file_paths]

    # Получаем содержимое файлов
    file_contents = get_file_contents(file_paths)

    # Выводим содержимое файлов в заданном формате
    print("\nСодержимое файлов:")
    for file, content in file_contents.items():
        print(f"\n{file}:\n{content}")


if __name__ == "__main__":
    main()