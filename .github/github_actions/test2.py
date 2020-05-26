import logging
import os

print(os.getcwd())
print(os.path.abspath(os.path.join(os.getcwd(), "../..")))
os.chdir(os.path.abspath(os.path.join(os.getcwd(), "../..")))
print(os.getcwd())
