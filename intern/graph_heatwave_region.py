import xarray as xr
import sys
import matplotlib.pyplot as plt

def heat_opt1(ds:str) -> None:
    ds = xr.open_dataset(ds)

    plot_obj = None
    fig, ax = plt.subplots(3,5, figsize=(20, 12), dpi=300)
    for i in range(3):
        for j in range(5):

            plot_obj = ds.heatwave.sel(
                time = ds.time.dt.year == 2010+i*5+j
                ).sum(dim='time').plot(ax=ax[i,j], add_colorbar=False, vmin=0, vmax=60)
            ax[i,j].set_title(f'year {i*5+j+2010}')
            plt.plot()
            cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])  # [left, bottom, width, height]
            fig.colorbar(plot_obj, cax=cbar_ax, label='Heatwaves per year')
    plt.savefig('heatwave_opt1set.png')
    plt.close()
    #Hot days plot
    plot_obj = None
    fig, ax = plt.subplots(3,5, figsize=(20, 12), dpi=300)
    for i in range(3):
        for j in range(5):
            plot_obj = ds.greater.sel(
                time = ds.time.dt.year == 2010+i*5+j
                ).sum(dim='time').plot(ax=ax[i,j], add_colorbar=False, vmin=0, vmax=150)
            ax[i,j].set_title(f'year {i*5+j+2010}')
            plt.plot()
            cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])  # [left, bottom, width, height]
            fig.colorbar(plot_obj, cax=cbar_ax, label='Hotdays per year')
    plt.savefig('hotdays_opt1set.png')
    plt.close()


def main(p1:int, ds:str):
    print(f'Calculatin heatwave by heat with opt={p1}')
    p1 = int(p1)
    match p1:
        case 1: heat_opt1(ds)
        case _: print('Input a right option')
    pass

if __name__ == '__main__':
    p1 = sys.argv[1]
    p2 = sys.argv[2]
    main(p1, p2)

