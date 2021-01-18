# -*- coding: utf-8 -*-

from sst_unittest import *
from sst_unittest_support import *

import os
import shutil

################################################################################
# Code to support a single instance module initialize, must be called setUp method

module_init = 0
module_sema = threading.Semaphore()

def initializeTestModule_SingleInstance(class_inst):
    global module_init
    global module_sema

    module_sema.acquire()
    if module_init != 1:
        # Put your single instance Init Code Here
        class_inst._setupbalarTestFiles()
        module_init = 1

    module_sema.release()

################################################################################

### NOTE NOTE NOTE NOTE - This is boilerplate copy of Cramsim testsuite ranamed
### to balar, more balar work will be done soon.


class testcase_balar(SSTTestCase):

    def initializeClass(self, testName):
        super(type(self), self).initializeClass(testName)
        # Put test based setup code here. it is called before testing starts
        # NOTE: This method is called once for every test

    def setUp(self):
        super(type(self), self).setUp()
        initializeTestModule_SingleInstance(self)

    def tearDown(self):
        # Put test based teardown code here. it is called once after every test
        super(type(self), self).tearDown()

#####

    def test_balar_1_R(self):
        self.balar_test_template("1_R")

    def test_balar_1_RW(self):
        self.balar_test_template("1_RW")

#####

    def balar_test_template(self, testcase):

        # Get the path to the test files
        test_path = self.get_testsuite_dir()
        outdir = self.get_test_output_run_dir()
        tmpdir = self.get_test_output_tmp_dir()

        self.balarElementDir = os.path.abspath("{0}/../".format(test_path))
        self.balarElementTestsDir = "{0}/tests".format(self.balarElementDir)
        self.testbalarDir = "{0}/testbalar".format(tmpdir)
        self.testbalarTestsDir = "{0}/tests".format(self.testbalarDir)

        # Set the various file paths
        testDataFileName="test_balar_{0}".format(testcase)

        reffile = "{0}/refFiles/{1}.out".format(test_path, testDataFileName)
        outfile = "{0}/{1}.out".format(outdir, testDataFileName)
        errfile = "{0}/{1}.err".format(outdir, testDataFileName)
        mpioutfiles = "{0}/{1}.testfile".format(outdir, testDataFileName)

        testpyfilepath = "{0}/test_txntrace.py".format(self.testbalarTestsDir)
        tracefile      = "{0}/sst-balar-trace_verimem_{1}.trc".format(self.testbalarTestsDir, testcase)
        configfile     = "{0}/ddr4_verimem.cfg".format(self.testbalarDir)

        if os.path.isfile(testpyfilepath):
            sdlfile = testpyfilepath
            otherargs = '--model-options=\"--configfile={0} traceFile={1}\"'.format(configfile, tracefile)
        else:
            sdlfile = "{0}/test_txntrace4.py".format(self.testbalarTestsDir)
            otherargs = '--model-options=\"--configfile={0} --traceFile={1}\"'.format(configfile, tracefile)

        # Run SST
        self.run_sst(sdlfile, outfile, errfile, other_args=otherargs, mpi_out_files=mpioutfiles)

        # NOTE: THE PASS / FAIL EVALUATIONS ARE PORTED FROM THE SQE BAMBOO
        #       BASED testSuite_XXX.sh THESE SHOULD BE RE-EVALUATED BY THE
        #       DEVELOPER AGAINST THE LATEST VERSION OF SST TO SEE IF THE
        #       TESTS & RESULT FILES ARE STILL VALID

        # Perform the test
        # NOTE: This is how the bamboo tests does it, and its very crude.  The
        #       testing_compare_diff will always fail, so all it looks for is the
        #       "Simulation complete" message to decide pass/fail
        #       This should be improved upon to check for real data...
        cmp_result = testing_compare_diff(outfile, reffile)
        if not cmp_result:
            cmd = 'grep -q "Simulation is complete" {0} '.format(outfile)
            grep_result = os.system(cmd) == 0
            self.assertTrue(grep_result, "Output file {0} does not contain a simulation complete message".format(outfile, reffile))
        else:
            self.assertTrue(cmp_result, "Output file {0} does not match Reference File {1}".format(outfile, reffile))

#####

    def _setupbalarTestFiles(self):
        # NOTE: This routine is called a single time at module startup, so it
        #       may have some redunant
        log_debug("_setupbalarTestFiles() Running")
        test_path = self.get_testsuite_dir()
        outdir = self.get_test_output_run_dir()
        tmpdir = self.get_test_output_tmp_dir()

        self.balarElementDir = os.path.abspath("{0}/../".format(test_path))
        self.balarElementTestsDir = "{0}/tests".format(self.balarElementDir)
        self.testbalarDir = "{0}/testbalar".format(tmpdir)
        self.testbalarTestsDir = "{0}/tests".format(self.testbalarDir)

        # Create a clean version of the testbalar Directory
        if os.path.isdir(self.testbalarDir):
            shutil.rmtree(self.testbalarDir, True)
        os.makedirs(self.testbalarDir)
        os.makedirs(self.testbalarTestsDir)

        # Create a simlink of the ddr4_verimem.cfg file
        os_symlink_file(self.balarElementDir, self.testbalarDir, "ddr4_verimem.cfg")

        # Create a simlink of each file in the balar/Tests directory
        for f in os.listdir(self.balarElementTestsDir):
            os_symlink_file(self.balarElementTestsDir, self.testbalarTestsDir, f)

        # wget a test file tar.gz
        testfile = "sst-balar_trace_verimem_trace_files.tar.gz"
        fileurl = "https://github.com/sstsimulator/sst-downloads/releases/download/TestFiles/{0}".format(testfile)
        self.assertTrue(os_wget(fileurl, self.testbalarTestsDir), "Failed to download {0}".format(testfile))

        # Extract the test file
        filename = "{0}/{1}".format(self.testbalarTestsDir, testfile)
        os_extract_tar(filename, self.testbalarTestsDir)

