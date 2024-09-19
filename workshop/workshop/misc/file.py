import os


class File:
    # creates an instance representing a file
    def __init__(self, default_file_save_folder, file_path, file_data):
        if isinstance(file_path, bytes):
            file_path = file_path.decode()

        self.file_path = file_path
        self.file_data = file_data
        self.file_name = os.path.basename(self.file_path)
        self.default_file_save_folder = default_file_save_folder

    def save(self, output_folder=None):
        if output_folder is None:
            output_folder = self.default_file_save_folder
        if not os.path.isdir(output_folder):
            raise Exception(f"output folder for file save {output_folder} doesn't exist!")

        with open(os.path.join(output_folder, self.file_name), "wb") as f:
            f.write(self.file_data)
