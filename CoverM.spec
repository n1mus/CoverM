/*
A KBase module: CoverM
*/

module CoverM {

    typedef structure {
        string workspace_name;
        string workspace_id;
        string genome_ref;
        string reads_ref;
	string mapper;
    } CoverMParams;

    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function returns results in a KBaseReport
    */
    funcdef run_CoverM(CoverMParams params) returns (ReportResults output) authentication required;

};
