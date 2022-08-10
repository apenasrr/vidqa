import logging
import os
import sys


def test_folders_has_path_too_long(
    list_path_folder: list, max_path: int = 260, max_name: int = 260
):
    """tests a serie of folders if any of them has files whose filepath
    has a larger length than stipulated in max_path

    Args:
        list_path_folder (list): list of path_folder to be tested
        max_path (int, optional): max filepath len permitted. Defaults to 260.

    Returns:
        list: [list_folders_path_approved: less than max_path
               list_folders_path_rejected: bigger than max_path]
    """

    list_folders_path_approved = []
    list_folders_path_rejected = []

    for path_folder in list_path_folder:
        dict_result_test_filepath_too_long = test_folder_has_filepath_too_long(
            path_folder, max_path, max_name
        )
        if dict_result_test_filepath_too_long["result"]:
            list_folders_path_approved.append(path_folder)
        else:
            show_alert_filepath_too_long(dict_result_test_filepath_too_long)

            list_folders_path_rejected.append(path_folder)

    return list_folders_path_approved, list_folders_path_rejected


def test_folder_has_filepath_too_long(path_folder, max_path=260, max_name=260):
    """Test if a folder has any file with filepath too long

    Args:
        path_folder (string):
    return:
        dict: keys: {result: bol, list_path_file_long: list}
    """

    list_file_name_long = []
    list_file_path_long = []
    return_dict = {}
    return_dict["result"] = True

    for root, _, files in os.walk(path_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if len(file) > max_name:
                list_file_name_long.append(file_path)
            len_file_path = len(file_path)
            if len_file_path > max_path:
                list_file_path_long.append(file_path)

    if len(list_file_path_long) != 0 or len(list_file_name_long) != 0:
        return_dict["result"] = False

    return_dict["list_file_path_long"] = list_file_path_long
    return_dict["list_file_name_long"] = list_file_name_long
    return return_dict


def open_folder_in_explorer(list_file_path: list):
    """Opens folder where the first file is located.
    Valid only for Windows operating system.

    Args:
        list_stringa (list): list of file path
    """

    if len(list_file_path) > 0 and sys.platform == "win32":
        first_file_path = list_file_path[0]
        folder_path = os.path.dirname(first_file_path)
        print(f'start "{folder_path}"')
        os.startfile(folder_path)
    else:
        pass


def show_alert_filepath_too_long(dict_result_test_filepath_too_long: dict):

    return_ = dict_result_test_filepath_too_long
    if return_["result"] is False:
        # Open folders that need adjustments
        open_folder_in_explorer(return_["list_file_path_long"])
        open_folder_in_explorer(return_["list_file_name_long"])

        logging.info("File path too long:")
        for path_file_long in return_["list_file_path_long"]:
            logging.info("- %s", path_file_long)
        print("")
        logging.info("File name too long:")
        for path_file_long in return_["list_file_name_long"]:
            file_name_long = os.path.basename(path_file_long)
            logging.info("- %s", file_name_long)

    print("")
