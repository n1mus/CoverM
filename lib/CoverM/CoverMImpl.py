# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os

from Bio import SeqIO

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.AssemblyUtilClient import AssemblyUtil
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
    GIT_URL = ""
    GIT_COMMIT_HASH = "HEAD"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_CoverM(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_CoverM
        ############################################################################################
        ############################################################################################
        logging.info(f'Running run_CoverM with:\nctx: {ctx}\nparams: {params}')
        
        try:
            genome_or_mag_refs = params['genome_or_mag_refs']
            mapping_refs = params['mapping_refs']

        except ValueError:
            raise ValueError('Missing a param')

        assembly_util = AssemblyUtil(self.callback_url)
        fasta_file = assembly_util.get_assembly_as_fasta({'ref': genome_or_mag_refs})
        contig_str_list = SeqIO.parse(fasta_file['paths'])


        logging.info(f'Num contigs in fasta: {len(contig_str_list)}')

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['parameter_1']},
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
