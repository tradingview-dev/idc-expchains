import os
import subprocess


def tokyo_handler():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    cmd_line = ["ruby", os.path.join(current_dir, "tokyo_descriptions.rb")]

    with open("tokyo_local_descriptions.csv", "w", encoding="utf-8") as f:
        cmd_result = subprocess.run(cmd_line, stdout=f)
        if cmd_result.returncode != 0:
            raise RuntimeError(f"External command {cmd_line} finished with non zero code: " + str(cmd_result.returncode))
        else:
            print(f"External command {cmd_line} finished successfully")
