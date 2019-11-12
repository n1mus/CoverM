# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
import pprint
import itertools
import uuid
import re

from Bio import SeqIO

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.ReadsUtilsClient import ReadsUtils
from installed_clients.DataFileUtilClient import DataFileUtil

from .util import *
from .util.PrintUtil import *



#END_HEADER


class CoverM:
    '''
    Module Name:
    CoverM

    Module Description:
    A KBase module: CoverM
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/n1mus/CoverM.git"
    GIT_COMMIT_HASH = "13e8654e177fb64e6ca96c0b9f488fe8d68d9b65"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.workspace_url = config['workspace-url']
        self.srv_wiz_url = config['srv-wiz-url']
        self.shared_folder = config['scratch']
        self.config = config
        self.config['callback_url'] = self.callback_url
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)

        dprint(f'os.environ: {os.environ}')
        dprint(f'config: {config}')
        #END_CONSTRUCTOR
        pass


    def run_CoverM(self, ctx, params):
        """
        This example function returns results in a KBaseReport
        :param params: instance of type "CoverMParams" -> structure:
           parameter "workspace_name" of String, parameter "workspace_id" of
           String, parameter "genome_ref" of String, parameter "mapping_ref"
           of String, parameter "reads_ref" of String
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_CoverM
        ############################################################################################
        ############################################################################################
        # TODO handle alignment input (also install htslib)
        # TODO check if alignment/reads input matches with assembly provenance info

        dprint(f'Running run_CoverM with:\nctx: {ctx}\nparams: {params}')
        dprint(f'ctx.provenance(): {ctx.provenance()}')

        genome_ref = params['genome_ref']


        cmd = ['coverm', 'genome']
        cmdArgs_out = '--min-covered-fraction 0'.split()
        cmdArgs_out.extend('--output-format sparse'.split()) # TODO toggle


        # RETRIEVE FASTAS
        
        dprint('Retrieving fasta(s)')


        #
        fasta_paths = FileUtil.load_fastas(self.config, self.shared_folder, genome_ref) # ref -> [(path,upa)]
                                                                                    # hopefully each fasta is a genome (?)


        dprint(f'FASTA_PATHS: {fasta_paths}')
        dprint(f'NUM FASTAS: {len(fasta_paths)}')
        for fasta_path in fasta_paths:
            dprint(f'path: {fasta_paths[0][0]}, upa: {fasta_paths[0][1]}')



        fasta_paths = [path for (path,_) in fasta_paths]
        
       


        #
        cmd.append('--genome-fasta-files')
        cmd.extend(fasta_paths)


        # RETRIEVE READS OR ALIGNMENT
        if 'mapping_ref' in params and params['mapping_ref'] != None:
            raise NotImplementedError()

        elif 'reads_ref' in params and params['reads_ref'] != None:

            #
            cmdArgs_align = ['--mapper']
            cmdArgs_align.append(params['mapper'])


            cmdArgs_align.append('--reference')  # FASTA file of contigs e.g. concatenated 
                                       #  genomes or assembly, or minimap2 index
                                       # (with --minimap2-reference-is-index),
                                       #  or BWA index stem (with -p bwa-mem).
                                       #  If multiple references FASTA files are
                                       #  provided and --sharded is specified,
                                       #  then reads will be mapped to references
                                       #  separately as sharded BAMs.
            cmdArgs_align.extend(fasta_paths)


            dprint('Retrieving reads')

            # GET ALL REFS IF REF IS TO SET

            reads_ref = params['reads_ref']; dprint(f'reads_ref before fetch from sampleset: {reads_ref}') 
            # upa -> [{'ref':upa,'name':name}]
            reads_refsAndInfo = FileUtil.fetch_reads_refs_from_sampleset(reads_ref, self.workspace_url, self.srv_wiz_url); dprint(f'reads_refsAndInfo after fetch from sampleset: {reads_refsAndInfo}')
            


            # ISOLATE REFS
            reads_refs = [reads_refAndInfo['ref'] for reads_refAndInfo in reads_refsAndInfo]


            # REFS -> PATHS
            reads_pathsAndInfo = list(map(FileUtil.dl_getPath_from_upa, reads_refs, itertools.repeat(self.callback_url)))
            

            # SEPARATE PATHS BY READLIB TYPE
            readsPaths_byType_dict = dict()
            readsPaths_byType_dict['single'] = [reads_pathAndInfo['file_fwd'] for reads_pathAndInfo in reads_pathsAndInfo if reads_pathAndInfo['style'] == 'single']
            readsPaths_byType_dict['interleaved'] = [reads_pathAndInfo['file_fwd'] for reads_pathAndInfo in reads_pathsAndInfo if reads_pathAndInfo['style'] == 'interleaved']


            
            # ADD READS PATHS TO CMD

            if readsPaths_byType_dict['interleaved']:
                cmdArgs_align.append('--interleaved') # interleaved FASTA(Q) files for mapping
                cmdArgs_align.extend(readsPaths_byType_dict['interleaved'])

            if readsPaths_byType_dict['single']:
                cmdArgs_align.append('--single')
                cmdArgs_align.extend(readsPaths_byType_dict['single'])





            # CACHE BAM

            bam_dir_fullPath = os.path.join(self.shared_folder, 'bam_dir')
            cmdArgs_align.extend(['--bam-file-cache-directory', bam_dir_fullPath]) # Output BAM files generated during alignment to this directory



            


        else:
            raise Exception('Must supply either mapping or reads, neither was supplied')

        


        # OUTPUT TYPE ARGS

        cmdArgs_genStats = '--methods relative_abundance mean trimmed_mean covered_fraction covered_bases variance length count reads_per_base rpkm'.split()  
        cmdArgs_hist = '--methods coverage_histogram'.split()
                




        # RUN STATS CMD

        cmd_run = cmd + cmdArgs_align + cmdArgs_genStats + cmdArgs_out
        dprint('CMD:', cmd_run)
        dprint('RUNNING/PRINT STATS CMD'); dprint(cmd_run); out_genStats = subprocess.run(cmd_run, stdout=subprocess.PIPE).stdout.decode('utf-8'); dprint(out_genStats)
       


        # SORT BAM
        
        bam_filenames = [f for f in os.listdir(bam_dir_fullPath) if re.compile('.*\.bam').fullmatch(f) ]
        bam_fullPaths = list(map(lambda fn: os.path.join(bam_dir_fullPath, fn), bam_filenames))
        '''for bam_fullPath in bam_fullPaths:
            out = subprocess.run(f'samtools sort {bam_fullPath} > {bam_fullPath}', shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
            dprint(out)
        '''
        
        # RUN HIST CMD


        cmdArgs_reuseMap = ['--bam-files'] + bam_fullPaths
        
        cmd_run = cmd + cmdArgs_reuseMap + cmdArgs_hist + cmdArgs_out
        dprint('RUNNING/PRINT HIST CMD'); dprint(cmd_run); out_hist = subprocess.run(cmd_run, stdout=subprocess.PIPE).stdout.decode('utf-8'); dprint(out_hist)

        



        # HTML OUTPUT

        dprint('Generating html')


        htmlOutput_dir = os.path.join(self.shared_folder, f'htmlOutput_{uuid.uuid4()}'); os.mkdir(htmlOutput_dir)

        out_handler = OutputUtil.CoverMOutput(cmd + cmdArgs_genStats, 
                                            out_genStats, 
                                            cmd + cmdArgs_hist, 
                                            out_hist, 
                                            htmlOutput_dir)

        out_handler.gen_write_html_output()


        dfu = DataFileUtil(self.callback_url)

        htmlZip_shock_id = dfu.file_to_shock({'file_path': htmlOutput_dir,
                                              'pack': 'zip'})['shock_id']
        
        htmlZip_report_dict = {'shock_id': htmlZip_shock_id, 
                               'name': 'coverm_report.html',
                                'label': 'coverm_report.html',
                                'description': 'CoverM output in HTML table'}

        #####
        #####
        #####
        #####
        #####
        #####


        report_params = {
            'message': '`report_params message`',
            'report_object_name': 'CoverM.Report',
            'workspace_name': params['workspace_name'],
            'warnings': [],
            'file_links': [htmlZip_report_dict],
            'html_links': [htmlZip_report_dict],
            'direct_html_link_index': 0
            }

        report_client = KBaseReport(self.callback_url)
        report_info = report_client.create_extended_report(report_params)
                
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        ############################################################################################
        ############################################################################################
        #END run_CoverM

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_CoverM return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]


    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
