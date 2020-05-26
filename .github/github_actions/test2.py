import logging
import os

print(os.getcwd())
print(os.path.abspath(os.path.join(os.getcwd(), "../..")))
