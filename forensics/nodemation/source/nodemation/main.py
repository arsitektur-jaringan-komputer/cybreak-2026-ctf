import argparse
import os
import socketserver
import sys
import logging

FLAG = "CYB26{5usp1c10us_w0rkfl0w_3xecut10n_iN_n8n_s4ndb0x}"

TOKEN = os.environ.get("QUIZ_TOKEN", "elsche-1788423551")
RUNTIME_DIR = os.path.dirname(os.path.abspath(__file__))

CHALLENGES = [
    {
        "question": "What sequence in the malicious workflow enables process execution?",
        "format": "function, module, function",
        "example": "someFunction, some_module, anotherFunction",
        "valid_answers": ["getbuiltinmodule, child_process, execsync"],
        "case_insensitive": True,
    },
    {
        "question": "What encryption key was used for the valid exfiltration payload?",
        "format": "key string",
        "example": "example-key-string",
        "valid_answers": ["hcs-at-cybreak-2026-chall-by-ursourcecode"],
    },
    {
        "question": "Which workflow and execution produced the valid exfiltration?",
        "format": "workflow-id, execution-id",
        "example": "wf-example-0001, 123",
        "valid_answers": ["wf-nightly-backup-0001, 531"],
        "case_insensitive": True,
    },
    {
        "question": "Which account owned and saved the tampered workflow?",
        "format": "email address",
        "example": "analyst@example.org",
        "valid_answers": ["grb@hcs.org"],
        "case_insensitive": True,
    },
    {
        "question": "What token was exfiltrated from the host?",
        "format": "hostname-unix_epoch",
        "example": "host-1234567890",
        "valid_answers": [TOKEN],
    },
    {
        "question": "When did the successful exfiltration occur in UTC?",
        "format": "ISO-8601 UTC timestamp",
        "example": "2026-01-01T12:34:56.000Z",
        "valid_answers": ["2026-09-02T09:32:16.237Z"],
    },
    {
        "question": "Which workflow and execution produced the connection-refused request to port 8081?",
        "format": "workflow-id, execution-id",
        "example": "wf-example-0002, 456",
        "valid_answers": ["wf-invoice-totalizer-0002, 529"],
        "case_insensitive": True,
    },
    {
        "question": "What is the SHA-256 digest of the hex-decoded C2 seed material in captured process memory?",
        "format": "64 lowercase hexadecimal characters",
        "example": "a1b2c3d4e5f60708a1b2c3d4e5f60708a1b2c3d4e5f60708a1b2c3d4e5f60708",
        "valid_answers": ["dbbf142a78ee9485894e2a6f0e991c6ce1125eddd4160bae2d5a8b5d4d56db63"],
    },
]

def _resolve_log_file():
    configured = os.environ.get("QUIZ_LOG", os.path.join(RUNTIME_DIR, "answers.log"))
    try:
        parent = os.path.dirname(os.path.abspath(configured))
        os.makedirs(parent, exist_ok=True)
        with open(configured, "a"):
            pass
        return configured
    except OSError:
        return os.path.join(RUNTIME_DIR, "answers.log")

LOG_FILE = _resolve_log_file()
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    MSG = '\033[33;3m'


def normalize(s):
    return " ".join(s.strip().split()).lower()


def check_answer(user_input, correct_answer, case_insensitive=False):
    cleaned_input = user_input.strip()
    if case_insensitive:
        cleaned_input = normalize(cleaned_input)
        if isinstance(correct_answer, list):
            return cleaned_input in [normalize(a) for a in correct_answer]
        return cleaned_input == normalize(correct_answer)

    if isinstance(correct_answer, list):
        return cleaned_input in correct_answer
    return cleaned_input == correct_answer


def run_quiz(read_answer, write, client_address):
    logging.info(f"[{client_address}] start connection")
    try:
        write(Colors.HEADER + "=" * 55 + Colors.ENDC)
        banner_text = r"""
                 _                      _   _
 _ __   ___   __| | ___ _ __ ___   __ _| |_(_) ___  _ __
| '_ \ / _ \ / _` |/ _ \ '_ ` _ \ / _` | __| |/ _ \| '_ \
| | | | (_) | (_| |  __/ | | | | | (_| | |_| | (_) | | | |
|_| |_|\___/ \__,_|\___|_| |_| |_|\__,_|\__|_|\___/|_| |_|
        """
        write(Colors.CYAN + banner_text + Colors.ENDC)
        write(Colors.HEADER + "=" * 55)
        write("      Welcome to CYBREAK CTF 2026 - nodemation")
        write("=" * 55 + Colors.ENDC + "\n")
        write("Answer the following questions to get the flag. Good luck!")

        write("")
        len_challenges = len(CHALLENGES)
        write(Colors.MSG + f"There are {len_challenges} questions in total." + Colors.ENDC)

        for index, challenge in enumerate(CHALLENGES, start=1):
            write(f"\n{Colors.BLUE}[Question #{index}]{Colors.ENDC}")
            write(challenge["question"])
            write(f"{Colors.WARNING}Format: {challenge['format']}{Colors.ENDC}")
            write(f"{Colors.WARNING}Example: {challenge['example']}{Colors.ENDC}")
            user_answer = read_answer("Answer: ")
            if user_answer is None:
                write("\nExiting...")
                return
            logging.info(f"[{client_address}] Q{index} -> {user_answer}")

            if check_answer(user_answer, challenge['valid_answers'], challenge.get('case_insensitive', False)):
                write(f"{Colors.GREEN}[+] Correct{Colors.ENDC}")
            else:
                write(f"{Colors.FAIL}[-] Incorrect answer.{Colors.ENDC}")
                return

        write("\n" + "=" * 50)
        write(f"{Colors.HEADER}CONGRATULATIONS!!{Colors.ENDC}")
        write(f"Flag: {Colors.BOLD}{FLAG}{Colors.ENDC}")
        write("=" * 50 + "\n")
    finally:
        logging.info(f"[{client_address}] end connection")


class QuizHandler(socketserver.StreamRequestHandler):
    def handle(self):
        client_address = f"{self.client_address[0]}:{self.client_address[1]}"

        def write(message=""):
            self.wfile.write((message + "\n").encode("utf-8"))
            self.wfile.flush()

        def read_answer(prompt):
            self.wfile.write(prompt.encode("utf-8"))
            self.wfile.flush()
            line = self.rfile.readline()
            return line.decode("utf-8", "replace").rstrip("\r\n") if line else None

        run_quiz(read_answer, write, client_address)


class QuizServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description="nodemation forensic quiz server")
    parser.add_argument("--host", default=os.environ.get("QUIZ_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("QUIZ_PORT", "31338")))
    parser.add_argument("--stdio", action="store_true", help="run one local stdin/stdout session")
    args = parser.parse_args()

    if args.stdio:
        def read_answer(prompt):
            try:
                return input(prompt)
            except (EOFError, KeyboardInterrupt):
                return None

        run_quiz(read_answer, print, "stdio")
        return

    with QuizServer((args.host, args.port), QuizHandler) as server:
        print(f"[quiz] listening on {args.host}:{args.port}", flush=True)
        logging.info("quiz server listening on %s:%s", args.host, args.port)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("quiz server shutting down")


if __name__ == "__main__":
    main()
