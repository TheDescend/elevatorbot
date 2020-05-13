import pandas as pd
from datetime import datetime

rdata = pd.read_pickle('database/rasputinData.pickle')
print(rdata)

fig = rdata.set_index('datetime').plot().get_figure()
filename = f'images/rasputin_{datetime.now().strftime("%Y_%m_%d__%H_%M")}.png'
fig.savefig(filename)