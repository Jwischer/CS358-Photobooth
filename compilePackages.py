import subprocess
#pip install BackendPackage/ --break-system-packages
subprocess.call(["pip", "install", "BackendPackage/", "--break-system-packages"])
#pip install FrontendPackage/ --break-system-packages
subprocess.call(["pip", "install", "FrontendPackage/", "--break-system-packages"])
