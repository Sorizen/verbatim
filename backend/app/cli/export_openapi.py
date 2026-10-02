import json
import sys

from main import app


def main() -> None:
    sys.stdout.write(json.dumps(app.openapi(), ensure_ascii=False))


if __name__ == '__main__':
    main()
