import subprocess
import re


class NodeNotInstalledError(Exception):
    pass


class NodeVersionTooLowError(Exception):
    def __init__(self, version_str: str):
        super().__init__(f"Node.js version too low: {version_str} (require >=20)")


def check_node_version(min_major: int = 20) -> None:
    try:
        result = subprocess.run(
            ["node", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        raise NodeNotInstalledError("Node.js not found in PATH")

    version_out = result.stdout.strip() or result.stderr.strip()
    if not version_out:
        raise NodeNotInstalledError("Node.js found but no version output")

    m = re.match(r"v?(\d+)(?:\.(\d+)\.(\d+))?", version_out)
    if not m:
        raise NodeNotInstalledError(f"Unexpected node version output: {version_out}")

    major = int(m.group(1))
    version_str = version_out

    if major < min_major:
        raise NodeVersionTooLowError(version_str)

    # print(f"Node.js version OK: {version_str}")


if __name__ == "__main__":
    try:
        check_node_version(20)
    except NodeNotInstalledError as e:
        print("Error:", e)
    except NodeVersionTooLowError as e:
        print("Error:", e)
    else:
        print("Node.js is installed and version >= 20, good to go!")
