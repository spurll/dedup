#!/usr/bin/env python3

# Written by Gem Newman. This work is licensed under the MIT License.


from argparse import ArgumentParser
import re, os, filecmp


PATTERN = r'(IMG_(\d{4}))|(\w{8}\-\w{4}\-\w{4}\-\w{4}\-\w{12}).*'
p = re.compile(PATTERN)


def main():
    parser = ArgumentParser(
        description=f'Deduplicates files matching "{PATTERN}".')
    parser.add_argument("dir", nargs='?',
        help='The directory to search. Defaults to ".".', default='.')
    parser.add_argument('-v', '--verbose', help='Dump file info to console.',
        action='store_true')
    parser.add_argument('-r', '--recursive', help='Include subdirectories.',
        action='store_true')
    parser.add_argument('--dry-run', help='Do not actually delete any files.',
        action='store_true')
    args = parser.parse_args()

    process_dir(args.dir, args.verbose, args.recursive, args.dry_run)


def process_dir(dir, verbose, recursive, dry_run):
    # List all files in the dir
    print(f'Scanning {dir} for duplicates...')
    files = list(filter(lambda f: f.is_file(), os.scandir(dir)))

    # Filter to only those that match the pattern
    files = list(filter(lambda f: p.match(f.name), files))

    while files:
        keep, remove = next_batch(dir, files)

        if verbose:
            print(f'Keeping {keep.name}!')

        for f in remove:
            if verbose:
                print(f'Removing {f.name}...')

            if not dry_run:
                os.remove(f.path)

        # Remove both keep and remove from the working list of files
        files = [f for f in files if f != keep and f not in remove]

    if recursive:
        for subdir in filter(lambda d: d.is_dir(), os.scandir(dir)):
            process_dir(subdir.path, True, dry_run)


def next_batch(dir, files):
    # Pick a file to keep
    file = files[0]

    # Identify a group of files identical to the original file
    group = list(filter(lambda f: filecmp.cmp(file.path, f.path), files))

    # Sort the list to ensure that the one we keep is the first, alphabetically
    # (and make sure IMG_1234.jpg sorts before IMG_1234 1.jpg!)
    group.sort(key=lambda x: x.name.rsplit('.', 1)[0])

    return group[0], group[1:]


if __name__ == "__main__":
    main()

