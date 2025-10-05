"""

"""

from xarray import open_dataset
import datetime
import polars as pl
from numpy import array_split, arange
import sys
import matplotlib.pyplot as plt

def main(df:pl.Dataset, variable_name:str, n:int):
    if n%2 == 1: raise 'The subset need be pair'
    ds = open_dataset(ds)
    fig, axes = plt.subplots(n//2, n//2, figsize=(12, 10))
    k=0
    times = array_split(
        arange(ds[f'{variable_name}']).length()
        )
    for row in range(n//2):
        for column in range(n//2):
            ds[f'{variable_name}'].isel(time=times[k]).max(['lat', 'lon']).plot(ax=axes[row, column], cmap='RdBu')
    plt.tight_layout()
    plt.save('test.png')

if __name__ == "__main__":
    dataset = sys.argv[1]
    variable_name = sys.argv[2]
    n = sys.argv[3]#the graph will be separated in n intervals
    main(dataset, variable_name, n)
