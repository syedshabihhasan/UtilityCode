# author: Syed Shabih Hasan
import argparse
import os
import sys
from tqdm import tqdm


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", help="folder", required=True)
    parser.add_argument("-e", help="extension", required=True)
    parser.add_argument("-o", help="output", required=True)
    parser.add_argument("-l", help="first line", default="")

    args = parser.parse_args()

    return args.f, args.e, args.o, args.l


def get_sorted_list(folder, extension):
    file_list = []
    print("Finding files...")
    for root, dirs, files in tqdm(os.walk(folder)):
        for file in files:
            temp = os.path.join(root, file)
            if extension in temp:
                file_list.append(temp)
    return sorted(file_list)


def combine_files(file_list, final_file, first_line):
    error_files = {}
    print("combining files")
    with open(final_file, 'w') as f:
        if not(first_line is ''):
            f.write(first_line+"\n")
        for file in tqdm(file_list):
            try:
                with open(file, 'r') as f1:
                    data = f1.read()
                    f.write(data)
            except:
                error_files[file] = sys.exc_info()[0]
                continue
    return error_files


def main():
    print("starting...gathering arguments")
    folder, extension, output, first_line = get_args()
    sorted_file_list = get_sorted_list(folder, extension)
    err = combine_files(sorted_file_list, output, first_line)
    print("errors:")
    if len(err) == 0:
        print("None")
    else:
        for i in err:
            print(i, err[i])
    print("TADAAA!")


if __name__ == "__main__":
    main()
