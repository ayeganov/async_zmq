#!/usr/bin/python3

import argparse

import examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p",
                        "--program",
                        choices=['publisher', 'subscriber'],
                        required=True,
                        help="Start the specified program.")

    args = parser.parse_args()

    eval("examples." + args.program)()

if __name__ == "__main__":
    main()
