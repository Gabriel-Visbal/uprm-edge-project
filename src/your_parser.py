import sys

def main():
  if len(sys.argv) != 2:
    print("Use: python your_parser.py <archivo>.eudge")
    sys.exit(1)

  route = sys.argv[1]

  if not route.endswith(".eudge"):
    print("Error: the file need .eudge extension.")
    sys.exit(1)

  try:
    with open(route, "r", encoding="utf-8") as file:
      code = file.read()
  except:
    print("Error: file not found '{route}'")
    sys.exit(1)

  print("File read correctly.")

if __name__ == "main":
  main()