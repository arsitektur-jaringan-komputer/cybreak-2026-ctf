import sys
import os
import time
import logging
from datetime import datetime

FLAG = "CYB26{1_H0P3_y0u_L34rN_N3W_7h1n92_fr0M_l1Nux_m3m0Ry}"

CHALLENGES = [
    {
        "question": "What is the ip:port of the service that run on that server?",
        "format": "IP:PORT",
        "valid_answers": ["192.168.238.135:50012"]
    },
    {
        "question": "What is the IP address of the attacker?",
        "format": "IPV4 address",
        "valid_answers": ["192.168.238.134"]
    },
    {
        "question": "What is the value of the Database Backup password that the service used?",
        "format": "Password",
        "valid_answers": ["ThisIsYourBackpPasswdRememberToChangeIt"]
    },
    {
        "question": "After the attacker exploit the service and got the valid credentials, when does the attacker connect to the machine's ssh service?",
        "format": "YYYY-MM-DD HH:MM:SS UTC",
        #from pslist
        "valid_answers": ["2026-08-20 07:57:43 UTC"]
    },
    {
        "question": "What are the PIDs of the compromised bash processes connected to the C2 server?",
        "format": "PID list comma separated (ascending order)",
        "valid_answers": ["3019,3241", "3019, 3241"]
    },
    {
        "question": "What is the first file that attacker read on the first compromised user?",
        "format": "/path/to/file",
        "valid_answers": ["/etc/passwd"]
    },  
    {
        "question": "What is the command that attacker used to find way to escalate privileges?",
        "format": "command",
        "valid_answers": ["find / -user root -perm -4000 -exec ls -ldb {} \\; 2>/dev/null"]
    },  
    {
        "question": "What is the binary that attacker used to escalate privileges?",
        "format": "/path/to/binary",
        "valid_answers": ["/usr/bin/bash"]
    },
    {
        "question": "What is the last command that attacker run on root shell before exit?",
        "format": "command",
        "valid_answers": ["cat /etc/shadow > /home/viewer_operator/shadow.txt"]
    },
]

LOG_FILE = "/home/ctf/answers.log"
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

def print_banner():
    print(Colors.HEADER + "="*55 + Colors.ENDC)
    banner_text = r"""      .__                            
___  _|__| ______  _  __ ___________ 
\  \/ /  |/ __ \ \/ \/ // __ \_  __ \
 \   /|  \  ___/\     /\  ___/|  | \/
  \_/ |__|\___  >\/\_/  \___  >__|   
              \/            \/                             
  """
    print(Colors.CYAN + banner_text + Colors.ENDC)
    print(Colors.HEADER + "="*55)
    print(f"      Welcome to CYBREAK CTF 2026 Challenge")
    print("="*55 + Colors.ENDC + "\n")

def check_answer(user_input, correct_answer):
    cleaned_input = user_input.strip()
    
    if isinstance(correct_answer, list):
        return cleaned_input in correct_answer
    return cleaned_input == correct_answer


def main():
    client_ip = os.environ.get('SOCAT_PEERADDR', 'Unknown IP')
    logging.info(f"[{client_ip}] start connection")
    try:
        print_banner()
        print("Answer the following questions to get the flag. Good luck!")
        
        print("")
        len_challenges = len(CHALLENGES)
        print(Colors.MSG + f"There are {len_challenges} questions in total." + Colors.ENDC)
        
        for index, challenge in enumerate(CHALLENGES, start=1):
            print(f"\n{Colors.BLUE}[Question #{index}]{Colors.ENDC}")
            print(f"{challenge['question']}")
            print(f"{Colors.WARNING}Format: {challenge['format']}{Colors.ENDC}")
            
            try:
                user_answer = input(f"Answer: ")
                logging.info(f"[{client_ip}] Q{index} -> {user_answer}")
            except KeyboardInterrupt:
                print("\nExiting...")
                time.sleep(2)
                sys.exit()
            except EOFError:
                print("\nExiting...")
                time.sleep(2)
                sys.exit()

            if check_answer(user_answer, challenge['valid_answers']):
                print(f"{Colors.GREEN}[+] Correct{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[-] Incorrect answer.{Colors.ENDC}")
                time.sleep(2)
                return 

        print("\n" + "="*50)
        print(f"{Colors.HEADER}CONGRATULATIONS!!{Colors.ENDC}")
        print(f"Flag: {Colors.BOLD}{FLAG}{Colors.ENDC}")
        print("="*50 + "\n")
    finally:
        logging.info(f"[{client_ip}] end connection")

if __name__ == "__main__":
    main()