import sys
from mcg.generator import generate_modelcard

def main():
    print("MCG CLI works.")
    if len(sys.argv) != 2:
        print("Usage: mcg <model_name>")
        sys.exit(1)
    generate_modelcard(sys.argv[1])
