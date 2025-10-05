"""

"""

from xarray import open_dataset, Dataset
import datetime
import polars as pl
from numpy import array_split, arange
import sys
import matplotlib.pyplot as plt

def main(ds:Dataset, variable_name:str, n:int):
    n=int(n)
    if n%2 == 1: raise 'The subset need be pair'
    ds = open_dataset(ds)
    print(variable_name)
    fig, axes = plt.subplots(n//2, n//2, figsize=(12, 10))
    k=0
    times = array_split(
        len(arange(ds[f'{variable_name}']))
        )
    for row in range(n//2):
        for column in range(n//2):
            ds[f'{variable_name}'].isel(time=times[k]).mean(['lat', 'lon']).plot(ax=axes[row, column], cmap='RdBu')
    plt.tight_layout()
    plt.save('test.png')

if __name__ == "__main__":
    dataset = sys.argv[1]
    variable_name = sys.argv[2]
    n = sys.argv[3]#the graph will be separated in n intervals
    # call the function with paramns gived
    main(dataset, variable_name, n)
