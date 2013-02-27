import sys


if __name__ == '__main__':
    if sys.argv[1] == "server":
        from server_app.server import run
    else:
        from client_app.client import run

    run()
