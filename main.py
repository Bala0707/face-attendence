"""
Main entry point for Face Recognition Attendance System.
Launches Desktop GUI Application by default or CLI runner if --cli is passed.
"""

import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Main")


def main():
    parser = argparse.ArgumentParser(description="Face Recognition Attendance System Launcher")
    parser.add_argument("--cli", action="store_true", help="Launch in Headless Command Line Interface mode")
    parser.add_argument("--cam", type=int, default=0, help="Camera index for CLI mode (default: 0)")
    args = parser.parse_args()

    if args.cli:
        logger.info("Launching Face Attendance System in CLI Mode...")
        from cli import main as cli_main
        cli_main()
    else:
        logger.info("Launching Face Attendance System GUI Dashboard...")
        from gui import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
