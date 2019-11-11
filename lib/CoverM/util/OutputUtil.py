import pandas as pd
#import matplotlib.pyplot as plt
import io



class CoverMOutput():


    def __init__(self, statsIn, statsOut, histIn, histOut):
        '''
        '''
        self.statsOut_df = pd.read_csv(io.StringIO(statsOut), sep='\t', header=0)  
        header = self.statsOut_df.index



    def get_htmlTable(self):
        return self.statsOut_df.to_html(escape=False)




    def get_html_wholeStr(self):
        html = ('<!DOCTYPE html>'
                 '<html>'
                 '<head>' 
                 '<title>'
                 'CoverM Output'
                 '</title>'
                 '</head>'
                 '<body>')


        html += self.get_htmlTable()


        html += ('</body>'
                '</html>')

        return html


    









    def handle_metabatOut(metabatOut):
        '''
        Contig subcommand only
        '''
        raise NotImplementedError






