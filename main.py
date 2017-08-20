from os import listdir
from glob import glob
import sys
import pandas as pd
from weibo import *
if __name__=="__main__":
    folder_data=sys.argv[1]
    folder_output=sys.argv[2]
    folders=listdir(folder_data)
    for folder in folders:
        files=glob(folder_data+"/"+folder+"/*.html")
        dfout=[]
        for f in files:
            print(f)
            c=Collector(f)
            c.run()
            dfout.append(c.df)
        dfall=pd.DataFrame()
        for d in dfout:
            dfall=dfall.append(d)
        dfall.to_excel(folder_output+"/"+folder+".xls",index=False)
        print("-------------")
    print("THANK YOU")