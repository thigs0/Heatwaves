""""
If the referenc of tmax, tmin, pr or others are only one latitude and longitude.
Expand the dimension to run heatwave
    """
import xarray as xr
import sys

def chance_dimension(p1, p2):
    ds1 = xr.open_dataset(p1)
    ds2 = xr.open_dataset(p2)

    var = list(ds1.data_vars)[0]
    if len(list(ds1.data_vars)) > 1:
        raise ValueError("The firs dataset need be only one variable, like tmax, tmin or others")

    # Adjust coords names
    for ds in [ds1, ds2]:
        if "latitude" in ds.coords:
            ds = ds.rename({"latitude": "lat"})
        if "longitude" in ds.coords:
            ds = ds.rename({"longitude": "lon"})
    print(ds.lat)
    if len(ds1.lat) > 1 or len(ds1.lon) > 1:
        raise ValueError("The firs dataset need be only one latitude and longitude")


    ds1 = ds1.groupby('time.dayofyear').mean()
    data_dayofyear = ds2.time.dt.dayofyear.astype(int)
    ref_values = ds1.sel(dayofyear=data_dayofyear, method='nearest')
    ref_values = ref_values.fillna(0)
    ref_base = ref_values[var] if isinstance(ref_values, xr.Dataset) else ref_values
    ref_broadcasted = ref_base.broadcast_like(ds2[var])
    ref_broadcasted.to_netcdf('out.nc')

if __name__ == "__main__":
    p1 = sys.argv[1] #netcdf with only one latlon
    p2 = sys.argv[2] #netcdf with lat-lon that we want base
    chance_dimension(p1, p2)
