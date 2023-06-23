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
    parser.add_argument('--dry-run', help='Do not actually delete any files.',
        action='store_true')
    args = parser.parse_args()

    # List all files in the dir
    files = os.listdir(args.dir)

    # Filter to only those that match the pattern
    files = list(filter(p.match, files))

    while files:
        keep, remove = next_batch(args.dir, files)

        print(f'Keeping {os.path.join(args.dir, keep)}!')

        for f in remove:
            file = os.path.join(args.dir, f)
            print(f'Removing {file}...')

            if not args.dry_run:
                os.remove(file)

        # Remove both keep and remove from the working list of files
        files = [f for f in files if f != keep and f not in remove]


def next_batch(dir, files):
    # Pick a file to keep
    file = files[0]

    # Identify a group of files identical to the original file
    group = list(filter(lambda f:
        filecmp.cmp(os.path.join(dir, file), os.path.join(dir, f)), files))

    # Sort the list to ensure that the one we keep is the first, alphabetically
    # (and make sure IMG_1234.jpg sorts before IMG_1234 1.jpg!)
    group.sort(key=lambda x: x.rsplit('.', 1)[0])

    return group[0], group[1:]


if __name__ == "__main__":
    main()

