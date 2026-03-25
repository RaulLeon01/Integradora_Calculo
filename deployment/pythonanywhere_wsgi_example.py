import os
import sys
from dotenv import load_dotenv

project_home = '/home/TU_USUARIO/utez_laplace_web'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

load_dotenv(os.path.join(project_home, '.env'))

from app import app as application
