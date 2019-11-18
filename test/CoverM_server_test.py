# -*- coding: utf-8 -*-
import os
import time
import unittest
import itertools
from configparser import ConfigParser

from CoverM.CoverMImpl import CoverM
from CoverM.CoverMServer import MethodContext
from CoverM.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class CoverMTest(unittest.TestCase):

    S_oneidensis_assembly_upa = '79/16/1'

    rhodo_pairedEndLib_upa = '33163/2/1'
    rhodo_assembly_upa = '33163/6/2'

    SURF_pairedEndLib_upa = '33297/6/1'
    SURF_assembly_upa = '33297/10/3'
    SURF_MEGAHITMaxBin_BinnedCont_upa = '33297/15/1'
    SURF_MEGAHITMetaBAT_BinnedCont_upa = '33297/16/1'
    SURF_MEGAHITCONCOCT_BinnedCont_upa = '33297/14/9'

    lib2_singleEndLib_upa = '33297/9/1'
    lib2_assembly_upa = '33297/11/1'
    lib2_CONCOCT_BinnedCont_upa = '33297/13/3'


    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('CoverM'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'CoverM',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = CoverM(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa


    def test_pipeline(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        '''result = self.serviceImpl.run_CoverM(self.ctx, {
            'mode': 'local_test',
            'workspace_name': self.wsName,
            'genome_ref': self.rhodo_assembly_upa,
            'reads_ref': self.rhodo_pairedEndLib_upa,
            'mapper': 'minimap2-sr'
            })'''
        result = self.serviceImpl.run_CoverM(self.ctx, {
            'mode': 'ssh',
            'workspace_name': self.wsName,
            'genome_ref': self.SURF_MEGAHITMetaBAT_BinnedCont_upa,
            'reads_ref': self.SURF_pairedEndLib_upa,
            'mapper': 'minimap2-sr'
            })


    
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

