import os
from utils import execute_to_file


def tokyo_handler():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cmd_line = ["ruby", os.path.join(current_dir, "tokyo_descriptions.rb")]
    execute_to_file(cmd_line, "tokyo_local_descriptions.csv")
