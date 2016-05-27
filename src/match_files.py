import hashlib
import argparse
import os
import shutil


def define_argument_parsing():
    parser = argparse.ArgumentParser(
        'Script to match files between two folders, and store differences in different '
        'folder')
    parser.add_argument('-f1', '-F1', help='Folder 1, with more files', required=True)
    parser.add_argument('-f2', '-F2', help='Folder 2', required=True)
    parser.add_argument('-t', '-T', help='File extension (eg. txt)', required=True)
    parser.add_argument('-s', '-S', help='Folder to store difference in', required=True)
    args = parser.parse_args()
    folder1 = args.f1
    folder2 = args.f2
    file_type = args.t
    location_to_store = args.s
    return folder1, folder2, file_type, location_to_store


def get_file_list_dict(folder_location, file_extension):
    """
    Returns all the files within the folder_location that have the given path extension
    :param folder_location: location of the folder where to look, all subdirectories will also be traversed
    :param file_extension: the extension that you want to match
    :return: dictionary of unique filenames, key = filename, value = full path + filename
    """
    file_list_dict = {}
    for dirpath, _, filenames in os.walk(folder_location):
        for filen in filenames:
            if filen not in file_list_dict and filen.endswith(file_extension):
                file_list_dict[filen] = os.path.join(dirpath, filen)
    return file_list_dict


def get_file_list(folder_location, file_extension):
    """
    Returns all the files within the folder_location that have the given path extension
    :param folder_location: location of the folder where to look, all subdirectories will also be traversed
    :param file_extension: the extension that you want to match
    :return: list of all full path + filename
    """
    file_list = []
    for dirpath, _, filenames in os.walk(folder_location):
        for filen in filenames:
            if filen.endswith(file_extension):
                file_list.append(os.path.join(dirpath, filen))
    return file_list


def get_common_files(file_list1, file_list2, get_difference=False):
    """
    :param file_list1: list containing files from folder 1, the keys from file_list_dict
    :param file_list2: list containing files from folder 2, the keys from file_list_dict
    :param get_difference: If true, return the files in present folder 1, but not in folder 2
    :return: common files, and difference (if get_difference=True)
    """
    file1_set = set(file_list1)
    file2_set = set(file_list2)
    common_files = file1_set.intersection(file2_set)
    if get_difference:
        difference = file1_set.difference(file2_set)
        return list(common_files), list(difference)
    else:
        return list(common_files)


def __read_all_file_hasher(file_obj, block_size, hasher):
    buf = file_obj.read(block_size)
    while len(buf) > 0:
        hasher.update(buf)
        buf = file_obj.read(block_size)
    return hasher


def is_content_same(file1, file2, block_size=32768):
    """
    Checks the contents of the files and returns whether they are the same or not
    :param file1:
    :param file2:
    :param block_size: the block size to read for the hashing
    :return: True when contents are the same, returns False when contents are not the same
    """
    hasher1 = hashlib.sha256()
    hasher2 = hashlib.sha256()
    f1_hash = __read_all_file_hasher(open(file1, 'rb'), block_size, hasher1).hexdigest()
    f2_hash = __read_all_file_hasher(open(file2, 'rb'), block_size, hasher2).hexdigest()
    return f1_hash == f2_hash


def copy_files(filepath_list, location_to_store):
    if not os.path.isdir(location_to_store):
        os.makedirs(location_to_store)
    for filen in filepath_list:
        shutil.copy2(filen, location_to_store)


def main():
    print 'reading arguments'
    folder1, folder2, file_extension, location_to_store = define_argument_parsing()
    print 'extracting file list for folder 1'
    folder1_file_dict = get_file_list_dict(folder1, file_extension)
    print 'extracting file list for folder 2'
    folder2_file_dict = get_file_list_dict(folder2, file_extension)
    print 'getting common files, and files in folder 1 but not in 2'
    common_files, present_in_1_not_in_2 = get_common_files(folder1_file_dict.keys(), folder2_file_dict.keys(),
                                                           get_difference=True)
    print 'getting files in folder 2 but not in 1'
    _, present_in_2_not_in_1 = get_common_files(folder2_file_dict.keys(), folder1_file_dict.keys(), get_difference=True)
    common_and_same_content = []
    common_and_different_content_1 = []
    common_and_different_content_2 = []
    in_1_not_in_2 = []
    in_2_not_in_1 = []
    idx = 1
    n = len(common_files)
    print 'Checking content matches for common files'
    for filen in common_files:
        print 'On file '+str(idx)+'/'+str(n)
        idx += 1
        if is_content_same(folder1_file_dict[filen], folder2_file_dict[filen]):
            common_and_same_content.append(folder1_file_dict[filen])
        else:
            common_and_different_content_1.append(folder1_file_dict[filen])
            common_and_different_content_2.append(folder2_file_dict[filen])
    for filen in present_in_1_not_in_2:
        in_1_not_in_2.append(folder1_file_dict[filen])
    for filen in present_in_2_not_in_1:
        in_2_not_in_1.append(folder2_file_dict[filen])
    print 'Copying common files with same content'
    copy_files(common_and_same_content, location_to_store+'common_and_same_content/')
    print 'Copying common files with different content'
    copy_files(common_and_different_content_1, location_to_store+'common_and_different_content_1/')
    copy_files(common_and_different_content_2, location_to_store+'common_and_different_content_2/')
    print 'Copying files in 1 but not in 2'
    copy_files(in_1_not_in_2, location_to_store+'in_1_not_in_2/')
    print 'Copying files in 2 but not in 1'
    copy_files(in_2_not_in_1, location_to_store+'in_2_not_in_1/')
    print 'TADAA!!!'
if __name__ == "__main__":
    main()
