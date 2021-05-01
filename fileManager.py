from singleton import Singleton
import os, shutil, glob
class FileManager(metaclass=Singleton):
    def __init__(self):
        pass

    @staticmethod
    def clear_folder(path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                print("Successfully removed %s" % file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    @staticmethod
    def upload_files(files, path):
        pass

    @staticmethod
    def get_files(path, extension):
        """gets an array of file names from `path` with `extension` extension.

        Args:
            path ([str]): [folder path]
            extension ([str[]]): [file extension (e.g: ["png"])]

        Returns:
            [array]: [list of file names]
        """
        return [item for i in [glob.glob('%s/*.%s' % (path, ext)) for ext in extension] for item in i]

    @staticmethod
    def get_filename_from_path(path):
        head, tail = os.path.split(path)
        return tail