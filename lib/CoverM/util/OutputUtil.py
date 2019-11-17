import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import os

from .PrintUtil import *


class CoverMOutput():


    def __init__(self, statsIn, statsOut, histIn, histOut, save_dir=None):
        '''
        '''
        self.statsOut_df = pd.read_csv(io.StringIO(statsOut), sep='\t', header=0)  
        self.histOut_df = pd.read_csv(io.StringIO(histOut), sep='\t', header=0, usecols=['Genome','Bases','Coverage'], dtype={'Genome': str, 'Bases':int, 'Coverage':int})
        self.save_dir = save_dir


        # add column for histograms
        self.out_df = self.statsOut_df
        self.out_df['Coverage Histogram'] = ['' for _ in range(self.out_df.shape[0])]

        # graph histograms, write into df, write as file
        self.write_insertToTable_hists()



    def write_insertToTable_hists(self):
        '''
        Extract histogram info
        Write to .png
        Insert img tag into table
        '''
        genomes_col = self.histOut_df['Genome']
        bases_col = self.histOut_df['Bases']
        coverage_col = self.histOut_df['Coverage']

        genomes_uniq = set(genomes_col)

        for genome in genomes_uniq:
            dprint(f'Generating hist .png / html-img-tag for genome: {genome}')

            hist = bases_col[genomes_col == genome].tolist(); 


            # CHECK HIST_BINS TODO check this in coverm code
            hist_bins = coverage_col[genomes_col == genome].tolist(); histBins_gen = range(len(hist));
            if hist_bins != list(histBins_gen):
                dprint('WARNING ' * 30 + f'hist_bins for genome {genome} is not [0 ... len(hist)-1]')
           

            # CONSOLIDATE HIST - TEMP HACK TODO
            cutoff_ind = min(np.where(np.array(hist) == 2)[0][-1] + 100, len(hist) - 1)
 
            hist = hist[:cutoff_ind]

            #dprint(f'hist: {hist}')
            #dprint(f'hist_bins: {hist_bins}')

            plt.hist(hist, bins=hist_bins)

            img_filename = f'hist_{genome}.png'
            img_path = os.path.join(self.save_dir, img_filename)
            plt.savefig(img_path, format='png')

            self.out_df.loc[self.out_df['Genome'] == genome, 'Coverage Histogram'] = self.to_image_tag(img_filename)




    def to_image_tag(self, img_filename):
        return f'<img src={img_filename} alt={img_filename} height="200" width="400">'



    def get_final_htmlTable(self):
        return self.statsOut_df.to_html(justify='center', escape=False)



    def get_html_wholeStr(self):
        html = ('<!DOCTYPE html>'
                 '<html>'
                 '<head>' 
                 '<title>'
                 'CoverM Output'
                 '</title>'
                 '</head>'
                 '<body>')


        html += self.get_final_htmlTable()


        html += ('</body>'
                '</html>')

        return html


    

    def gen_write_html_output(self):
        with open(os.path.join(self.save_dir, 'coverm_report.html'), 'w') as htmlOutput_file:
            htmlOutput_file.write(self.get_html_wholeStr())




