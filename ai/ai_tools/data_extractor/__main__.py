"""CLI entrypoint for the data extractor.

This module exposes a small `main()` that parses command-line arguments
and calls into the extractor implementation in `run_extractor.run_extraction`.
Only lightweight comments are added; behavior is unchanged.
"""

# standard library imports
import argparse
import os

# local extractor implementation
from ai.ai_tools.data_extractor.run_extractor import run_extraction


def main():
    """Parse CLI args and invoke the extraction pipeline.

    The function expects a directory containing QnA-style `.txt` files and
    an optional target location to write the resulting JSON file. It
    delegates the heavy lifting to `run_extraction`.
    """

    parser = argparse.ArgumentParser(description="Extracts data from .txt files in QnA format.")
    # directory to search for .txt QnA files
    parser.add_argument('-d', '--directory', required=True, help='The directory path to extract data from')
    # where to save processed JSON; defaults to current working directory
    parser.add_argument('-l', '--location', default=os.getcwd(), required=False, help='The destination file path to save the JSON')

    args = parser.parse_args()

    # hand off to extractor implementation
    run_extraction(args.directory, args.location)


if __name__ == "__main__":
    main()

