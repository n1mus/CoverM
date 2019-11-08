# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
import pprint
import itertools

from Bio import SeqIO

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.ReadsUtilsClient import ReadsUtils

from . import FileUtil, OutputUtil
from .PrintUtil import *



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


        cmd = ['coverm']
        cmd.append(params['cover_per'])
        cmd.extend('--min-covered-fraction 0'.split())
        cmd.extend('--bam-file-cache-directory bam_dir'.split()) # Output BAM files generated during alignment to this directory
        cmd.extend('--output-format sparse'.split())


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
        if params['cover_per'] == 'genome':
            cmd.append('--genome-fasta-files')
            cmd.extend(fasta_paths)


        # RETRIEVE READS OR ALIGNMENT
        if 'mapping_ref' in params and params['mapping_ref'] != None:
            raise NotImplementedError()

        elif 'reads_ref' in params and params['reads_ref'] != None:
            dprint('Retrieving reads')
            '''
            # get all refs if ref is to set
            dprint(f'reads_ref before fetch from sampleset: {reads_ref}') 
            reads_refs = Util.fetch_reads_refs_from_sampleset(reads_ref, self.workspace_url, self.srv_wiz_url) # upa -> [{ref:upa,name}]
            dprint(f'reads_ref after fetch from sampleset: {reads_ref}')

            # retrieve file info for all refs
            readsRef_fileInfo_list = []
            for reads_ref in reads_refs:
                readsRef_fileInfo = Util.fetch_reads_from_reference(reads_ref['ref'], self.callback_url) # repeat: ref -> [{style,file_fwd,file_rev,object_ref}]
                readsRef_fileInfo_list.append(readsRef_fileInfo)
            
            dprint(f'readsRef_fileInfo_list: {readsRef_fileInfo_list}')

            for readsRef_fileInfo in readsRef_fileInfo_list:
            reads_path = reads_pathAndInfo['files'][reads_ref]['files']['fwd_name']
            '''


            # GET ALL REFS IF REF IS TO SET
            reads_ref = params['reads_ref']
            dprint(f'reads_ref before fetch from sampleset: {reads_ref}') 
            reads_refsAndInfo = FileUtil.fetch_reads_refs_from_sampleset(reads_ref, self.workspace_url, self.srv_wiz_url) # upa -> [{'ref':upa,'name':name}]
            dprint(f'reads_refsAndInfo after fetch from sampleset: {reads_refsAndInfo}')


            # ISOLATE REFS
            reads_refs = [reads_refAndInfo['ref'] for reads_refAndInfo in reads_refsAndInfo]


            # REFS -> PATHS
            reads_pathsAndInfo = list(map(FileUtil.dl_getPath_from_upa, reads_refs, itertools.repeat(self.callback_url)))
            

            # SEPARATE PATHS BY TYPE
            readsPaths_byType_dict = dict()
            readsPaths_byType_dict['single'] = [reads_pathAndInfo['file_fwd'] for reads_pathAndInfo in reads_pathsAndInfo if reads_pathAndInfo['style'] == 'single']
            readsPaths_byType_dict['interleaved'] = [reads_pathAndInfo['file_fwd'] for reads_pathAndInfo in reads_pathsAndInfo if reads_pathAndInfo['style'] == 'interleaved']


            '''
            reads_pathAndInfo = ReadsUtils(self.callback_url).download_reads({ 
                                                                        "read_libraries": [reads_refs],
                                                                        "interleaved": "true"

                                                                        })
                                                                        
            dprint(f'reads_pathAndInfo:')
            dprint(reads_pathAndInfo)


            '''




            #
            cmd.append('--mapper')
            cmd.append(params['mapper'])


            cmd.append('--reference')  # FASTA file of contigs e.g. concatenated 
                                       #  genomes or assembly, or minimap2 index
                                       # (with --minimap2-reference-is-index),
                                       #  or BWA index stem (with -p bwa-mem).
                                       #  If multiple references FASTA files are
                                       #  provided and --sharded is specified,
                                       #  then reads will be mapped to references
                                       #  separately as sharded BAMs.
            cmd.extend(fasta_paths)

            
            # ADD READS PATHS TO CMD

            if readsPaths_byType_dict['interleaved']:
                cmd.append('--interleaved') # interleaved FASTA(Q) files for mapping
                cmd.extend(readsPaths_byType_dict['interleaved'])

            if readsPaths_byType_dict['single']:
                cmd.append('--single')
                cmd.extend(readsPaths_byType_dict['single'])




        else:
            raise Exception('Must supply either mapping or reads, neither was supplied')

        


        # OUTPUT TYPE ARGS

        out_args_genStats = '--methods relative_abundance mean trimmed_mean covered_fraction covered_bases variance length count reads_per_base rpkm'.split()  
        out_args_hist = '--methods coverage_histogram'.split()
        out_args_metabat = '--methods metabat'.split()
                

        if params['cover_per'] == 'contig':
            out_args_genStats.remove('relative_abundance')



        # RUN CMD

        dprint('CMDs:', cmd, out_args_genStats, out_args_hist)

        
        

        dprint('RUNNING/PRINT STATS CMD'); out_genStats = subprocess.run(cmd + out_args_genStats, stdout=subprocess.PIPE).stdout.decode('utf-8'); dprint(out_genStats)
        dprint('RUNNING/PRINT HIST CMD'); out_hist = subprocess.run(cmd + out_args_hist, stdout=subprocess.PIPE).stdout.decode('utf-8'); #dprint(out_hist.stdout.)
        dprint('RUNNING/PRINT METABAT CMD'); out_metabat = subprocess.run(cmd + out_args_metabat, stdout=subprocess.PIPE).stdout.decode('utf-8'); dprint(out_metabat)

         

        #####
        #####
        #####
        #####
        #####
        #####

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': 'This is the text in the report'},
                                                'workspace_name': params['workspace_name']})
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
