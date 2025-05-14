import argparse
from mds import pull_index, search_service

def main():
    parser = argparse.ArgumentParser(prog="mds", description="ModelCard Discovery Service CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # mds index
    subparsers.add_parser("index", help="Pull ModelCards from OCI registry and index them")

    # mds serve
    subparsers.add_parser("serve", help="Run search API server")

    args = parser.parse_args()

    if args.command == "index":
        pull_index.run()
    elif args.command == "serve":
        search_service.run()
