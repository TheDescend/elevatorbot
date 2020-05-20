import pandas as pd
from datetime import datetime
import os
from functions.authfunctions        import getRasputinQuestProgress

rdata = pd.read_pickle('database/rasputinData.pickle')
print(rdata)

# rdata = rdata.set_index('datetime').resample('15T').mean()
# print(rdata)
# rdata = rdata.assign(edz=rdata.edz.interpolate(method='quadratic'))
# rdata = rdata.assign(moon=rdata.moon.interpolate(method='quadratic'))
# rdata = rdata.assign(io=rdata.io.interpolate(method='quadratic'))
# print(rdata)

# fig = rdata.plot().get_figure()
# filename = f'images/rasputin_{datetime.now().strftime("%Y_%m_%d__%H_%M")}.png'
# fig.savefig(filename)


def getdata():
    if not os.path.exists('database/rasputinData.pickle'):
        rasputindf = pd.DataFrame(columns=["datetime",'moon','edz', 'io'])
    else:
        rasputindf = pd.read_pickle('database/rasputinData.pickle')
    # now = datetime.now()
    # now = now.replace(hour=4, minute=10)
    # newdict = {
    #     'datetime':now
    # }
    # newdict['moon'] = 3000000
    # newdict['io'] = 3000000
    # newdict['edz'] = 3000000
    
    # rasputindf = rasputindf.append(newdict, ignore_index=True)
    # rasputindf.to_pickle('database/rasputinData.pickle')
    print(rasputindf)
getdata()