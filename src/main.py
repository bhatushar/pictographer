import file_handler
import metadata_handler
from argparse import ArgumentParser
from dotenv import dotenv_values


def parse_cla():
    parser = ArgumentParser("Pictographer")
    parser.add_argument("lib_root", help="Absolute path to the root directory of the photo library")
    return parser.parse_args()


def main():
    config: dict = dotenv_values(".env")
    args = parse_cla()

    # Check for unknown file types
    unknown_files = metadata_handler.check_unkown_files(config["raw_metadata_path"])
    if unknown_files:
        print("Following files are not recognized as media:")
        print(*unknown_files, sep="\n")
        exit(1)
    
    metadata = metadata_handler.sanitized_df(config["raw_metadata_path"], args.lib_root)
    file_handler.rename(metadata, args.lib_root)
    file_handler.move(metadata, args.lib_root, config["folder_labels"].split("; "))

    metadata.to_csv(config["final_metadata_path"], index=False)
    


if __name__ == "__main__":
    main()
