import sys

def main():
  if len(sys.argv) != 2:
    print("Use: python your_parser.py <archivo>.uedge")
    sys.exit(1)

  route = sys.argv[1]

  if not route.endswith(".uedge"):
    print("Error: the file need .uedge extension.")
    sys.exit(1)

  try:
    with open(route, "r", encoding="utf-8") as file:
      code = file.read()
  except FileNotFoundError:
    print(f"Error: file not found '{route}'")
    sys.exit(1)

  print("File read correctly.")

if __name__ == "__main__":
  main()