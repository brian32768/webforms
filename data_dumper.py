"""
    Dump out the cases data so we can see what is going on in there.
"""
import os, sys
import pandas as pd
import read_cases

if __name__ == "__main__":
    df = read_cases.read_local_cases()
    print(df)

