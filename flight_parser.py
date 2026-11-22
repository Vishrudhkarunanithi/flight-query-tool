"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251AD035"
FIRST_NAME = "Vishrudh"
LAST_NAME = "PattukkottaiKarunanithi"


def main(argv: list[str] | None = None) -> int:
    """Run the flight parser and return the appropriate exit code."""

    parser = argparse.ArgumentParser(
        description="Flight Schedule Parser and Query Tool"
    )

    source_group = parser.add_mutually_exclusive_group(required=True)

    source_group.add_argument("-i", metavar="FILE")
    source_group.add_argument("-d", metavar="FOLDER")
    source_group.add_argument("-j", metavar="FILE")

    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", metavar="FILE", default=None)
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", metavar="FOLDER", default=".")

    # Parse arguments and handle argparse usage errors.
    try:
        args = parser.parse_args(argv)

        if (args.i or args.d) and not args.a:
            parser.error("-a FILE is required with -i or -d")

        if args.j and args.o is not None:
            parser.error("-o cannot be used with -j")

    except SystemExit as exc:
        return int(exc.code)

    logger = logging.getLogger("flight_parser")
    handler = None

    try:
        # -------------------------------------------------
        # OPTION 1: Load an existing JSON database (-j)
        # -------------------------------------------------
        if args.j:
            with open(args.j, "r", encoding="utf-8") as file:
                db = json.load(file)

            if not isinstance(db, list) or not all(
                isinstance(record, dict) for record in db
            ):
                raise ValueError(
                    "JSON database must be an array of objects"
                )

        # -------------------------------------------------
        # OPTION 2: Parse CSV files (-i or -d)
        # -------------------------------------------------
        else:
            output_path = args.o if args.o is not None else "db.json"

            # Get CSV file paths.
            if args.i:
                csv_paths = [args.i]

            else:
                if not os.path.isdir(args.d):
                    raise ValueError(
                        f"Folder does not exist or is not a directory: {args.d}"
                    )

                csv_paths = [
                    os.path.join(args.d, filename)
                    for filename in sorted(os.listdir(args.d))
                    if filename.endswith(".csv")
                    and os.path.isfile(os.path.join(args.d, filename))
                ]

                if not csv_paths:
                    raise ValueError(
                        f"No CSV files found in folder: {args.d}"
                    )

            # Load airport codes.
            airports = load_airports(args.a)

            # Prepare the errors.log file.
            log_folder = os.path.dirname(os.path.abspath(output_path))
            log_path = os.path.join(log_folder, "errors.log")

            logger.setLevel(logging.INFO)
            logger.propagate = False

            handler = logging.FileHandler(
                log_path,
                mode="w",
                encoding="utf-8"
            )

            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # Parse CSV files.
            records, errors = parse_files(csv_paths, airports)

            # Save valid flight records.
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=2, ensure_ascii=False)

            # Write invalid rows to errors.log.
            for error in errors:
                logger.warning(error)

            db = records

        # -------------------------------------------------
        # OPTION 3: Run queries (-q)
        # -------------------------------------------------
        if args.q:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if isinstance(queries, dict):
                pass
            elif isinstance(queries, list):
                if not all(isinstance(query, dict) for query in queries):
                    raise ValueError(
                        "Query file must contain an object or an array of objects"
                    )
            else:
                raise ValueError(
                    "Query file must contain an object or an array of objects"
                )

            # Check response folder.
            if not os.path.isdir(args.r):
                raise ValueError(
                    f"Response folder does not exist: {args.r}"
                )

            # Execute queries.
            responses = run_queries(db, queries)

            # Generate response filename.
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            response_filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_"
                f"{LAST_NAME}_{timestamp}.json"
            )

            response_path = os.path.join(
                args.r,
                response_filename
            )

            # Save query responses.
            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(responses, file, indent=2, ensure_ascii=False)

        return 0

    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    finally:
        # Always remove and close the logging handler.
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()

if __name__ == "__main__":
    sys.exit(main())  