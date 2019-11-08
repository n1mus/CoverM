import pandas as pd
import matplotlib.pyplot as plt
import StringIO








def handle_statsOut(statsOut, cover_per):
    statsOut_df = pd.from_csv(StringIO(stats_out), sep='\t', header=0)  
    stats = statsOut_df.index[2:end]











