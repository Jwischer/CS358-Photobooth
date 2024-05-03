#run.py  Copyright (C) 2024  Valparaiso University

import subprocess

subprocess.Popen(["python", "frontend.py"])
subprocess.call(["python", "backend.py"])
