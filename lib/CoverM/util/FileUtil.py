import os
import logging
from pprint import pprint
import functools

from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.MetagenomeUtilsClient import MetagenomeUtils
from installed_clients.ReadsUtilsClient import ReadsUtils
from installed_clients.WorkspaceClient import Workspace
from installed_clients.SetAPIServiceClient import SetAPI

from .PrintUtil import *

####################################################################################################################
##### Code below from kb_gtdbk (with edits)
####################################################################################################################



def load_fastas(config, scratch: str, upa: str):
    '''
    Returns list of (fasta_path, upa)
    '''
    dfu = DataFileUtil(config['callback_url'])
    au = AssemblyUtil(config['callback_url'])
    mgu = MetagenomeUtils(config['callback_url'])
    ws = Workspace(config['workspace-url'])

    obj_data = dfu.get_objects({"object_refs": [upa]})['data'][0]
    obj_type = obj_data['info'][2]

    if 'KBaseSets.GenomeSet' in obj_type:
        upas = [gsi['ref'] for gsi in obj_data['data']['items']]
    elif 'KBaseSearch.GenomeSet' in obj_type:
        upas = [gse['ref'] for gse in obj_data['data']['elements'].values()]
    elif "KBaseGenomes.Genome" in obj_type:
        upas = [upa]
    elif "KBaseGenomes.ContigSet" in obj_type or "KBaseGenomeAnnotations.Assembly" in obj_type:
        # in this case we use the assembly file util to get the fasta file
        # file_output = os.path.join(scratch, "input_fasta.fa")
        faf = au.get_assembly_as_fasta({"ref": upa})
        return [(faf['path'], upa)]
    elif "KBaseSets.AssemblySet" in obj_type:
        fasta_paths = []
        for item_upa in obj_data['data']['items']:
            faf = au.get_assembly_as_fasta({"ref": item_upa['ref']})
            fasta_paths.append((faf['path'], item_upa['ref']))
        return fasta_paths
    elif 'KBaseMetagenomes.BinnedContigs' in obj_type:
        fasta_paths = []
        bin_file_dir = mgu.binned_contigs_to_file({'input_ref': upa, 'save_to_shock': 0})['bin_file_directory']
        for (dirpath, dirnames, filenames) in os.walk(bin_file_dir):
            for fasta_file in filenames:
                fasta_path = os.path.join(scratch, fasta_file)
                fasta_path = os.path.splitext(fasta_path)[0] + ".fa"
                copyfile(os.path.join(bin_file_dir, fasta_file), fasta_path)
                # Should I verify that the bins have contigs?
                # is it possible to have empty bins?
                fasta_paths.append((fasta_path, upa))
            break
        return fasta_paths
    else:
        raise Error('Input genome/metagenome reference has unhandled type')
        
    fasta_paths = []
    for genome_upa in upas:
        genome_data = ws.get_objects2( {'objects':[{"ref": genome_upa}]})['data'][0]['data']
        assembly_upa = genome_upa + ';' + str(genome_data.get('contigset_ref') or genome_data.get('assembly_ref'))
        faf = au.get_assembly_as_fasta({'ref': assembly_upa})
        fasta_paths.append((faf['path'], assembly_upa))

    return fasta_paths





####################################################################################################################
##### Code below from kb_hisat2 (with edits)
####################################################################################################################


def fetch_reads_refs_from_sampleset(ref: str, ws_url, srv_wiz_url):
    """
    From the given object ref, return a list of all reads objects that are a part of that
    object. E.g., if ref is a ReadsSet, return a list of all PairedEndLibrary or SingleEndLibrary
    refs that are a member of that ReadsSet. This is returned as a list of dictionaries as follows:
    {
        "ref": reads object reference,
        "condition": condition string associated with that reads object,
        "name": reads object name (needed for saving an AlignmentSet)
    }
    The only one required is "ref", all other keys may or may not be present, based on the reads
    object or object type in initial ref variable. E.g. a RNASeqSampleSet might have condition info
    for each reads object, but a single PairedEndLibrary may not have that info.
    If ref is already a Reads library, just returns a list with ref as a single element.
    """
    obj_type = get_object_type(ref, ws_url)
    refs = list()
    if "KBaseSets.ReadsSet" in obj_type or "KBaseRNASeq.RNASeqSampleSet" in obj_type:
        print("Looking up reads references in ReadsSet object")
        set_client = SetAPI(srv_wiz_url)
        reads_set = set_client.get_reads_set_v1({
                                            "ref": ref,
                                            "include_item_info": 0,
                                            "include_set_item_ref_paths": 1
        })
        print("Got results from ReadsSet object")
        pprint(reads_set)
        ref_list = [r["ref_path"] for r in reads_set["data"]["items"]]
        reads_names = get_object_names(ref_list, ws_url)
        for reads in reads_set["data"]["items"]:
            ref = reads["ref_path"]
            refs.append({
                "ref": ref,
                "condition": reads["label"],
                "name": reads_names[ref]
            })
    elif ("KBaseAssembly.SingleEndLibrary" in obj_type or
          "KBaseFile.SingleEndLibrary" in obj_type or
          "KBaseAssembly.PairedEndLibrary" in obj_type or
          "KBaseFile.PairedEndLibrary" in obj_type):
        refs.append({
            "ref": ref,
            "name": get_object_names([ref], ws_url)[ref]
        })
    else:
        raise ValueError("Unable to fetch reads reference from object {} "
                         "which is a {}".format(ref, obj_type))

    return refs


# fetch_reads_from_reference
def dl_getPath_from_upa(ref: str, callback_url) -> dict:
    """
    Fetch a FASTQ file (or 2 for paired-end) from a reads reference.
    Returns the following structure:
    {
        "style": "paired", "single", or "interleaved",
        "file_fwd": path_to_file,
        "file_rev": path_to_file, only if paired end,
        "object_ref": reads reference for downstream convenience.
    }
    """
    try:
        print("Fetching reads from object {}".format(ref))
        reads_client = ReadsUtils(callback_url)
        reads_dl = reads_client.download_reads({
            "read_libraries": [ref],
            "interleaved": "true"
        })
        pprint(reads_dl)
        reads_files = reads_dl['files'][ref]['files']
        ret_reads = {
            "object_ref": ref,
            "style": reads_files["type"],
            "file_fwd": reads_files["fwd"]
        }
        if reads_files.get("rev", None) is not None:
            ret_reads["file_rev"] = reads_files["rev"]
        return ret_reads
    except Exception as e:
        raise e



def check_ref_type(ref, allowed_types, ws_url):
    """
    Validates the object type of ref against the list of allowed types. If it passes, this
    returns True, otherwise False.
    Really, all this does is verify that at least one of the strings in allowed_types is
    a substring of the ref object type name.
    Ex1:
    ref = 11/22/33, which is a "KBaseGenomes.Genome-4.0"
    allowed_types = ["assembly", "KBaseFile.Assembly"]
    returns False
    Ex2:
    ref = 44/55/66, which is a "KBaseGenomes.Genome-4.0"
    allowed_types = ["assembly", "genome"]
    returns True
    """
    obj_type = get_object_type(ref, ws_url).lower()
    for t in allowed_types:
        if t.lower() in obj_type:
            return True
    return False


def get_object_type(ref, ws_url):
    """
    Fetches and returns the typed object name of ref from the given workspace url.
    If that object doesn't exist, or there's another Workspace error, this raises a
    RuntimeError exception.
    """
    ws = Workspace(ws_url)
    info = ws.get_object_info3({"objects": [{"ref": ref}]})
    obj_info = info.get("infos", [[]])[0]
    if len(obj_info) == 0:
        raise RuntimeError("An error occurred while fetching type info from the Workspace. "
                           "No information returned for reference {}".format(ref))
    return obj_info[2]


def get_object_names(ref_list, ws_url):
    """
    From a list of workspace references, returns a mapping from ref -> name of the object.
    """
    ws = Workspace(ws_url)
    obj_ids = list()
    for ref in ref_list:
        obj_ids.append({"ref": ref})
    info = ws.get_object_info3({"objects": obj_ids})
    name_map = dict()
    # might be in a data palette, so we can't just use the ref.
    # we already have the refs as passed previously, so use those for mapping, as they're in
    # the same order as what's returned.
    for i in range(len(info["infos"])):
        name_map[ref_list[i]] = info["infos"][i][1]
    return name_map
