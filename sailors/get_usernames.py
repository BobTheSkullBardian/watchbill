from django.contrib import admin
from .sailors.models import Sailor
import csv
import pandas as pd

def main():
    file = 'slack-csa63dutysection-members'
    slack_data = pd.read_csv(file)
    for sailor in slack_data:
        print(sailor)
    # qs = Sailor.objects.get(email=)
    
