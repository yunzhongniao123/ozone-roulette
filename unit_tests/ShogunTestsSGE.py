
from numpy.random import randint
import os
from os.path import expanduser
import shutil
import unittest

from independent_jobs.aggregators.ScalarResultAggregator import ScalarResultAggregator
from independent_jobs.engines.BatchClusterParameters import BatchClusterParameters
from independent_jobs.engines.SGEComputationEngine import SGEComputationEngine
from independent_jobs.engines.SerialComputationEngine import SerialComputationEngine
from independent_jobs.jobs.DummyJob import DummyJob
from ozone.jobs.ShogunJobImportLogdet import ShogunJobImportLogdet


class ShogunImportComputation(object):
    def __init__(self, engine):
        self.engine = engine
    
    def go_to_bed(self, sleep_time):
        job = ShogunJobImportLogdet(ScalarResultAggregator(), sleep_time)
        agg = self.engine.submit_job(job)
        return agg

class ShogunTestsSGE(unittest.TestCase):
    def engine_tester(self, engine, sleep_times):
        dc = ShogunImportComputation(engine)
        
        aggregators = []
        num_submissions = len(sleep_times)
        for i in range(num_submissions):
            aggregators.append(dc.go_to_bed(sleep_times[i]))
            
        self.assertEqual(len(aggregators), num_submissions)
        
        engine.wait_for_all()
        
        results = []
        for i in range(num_submissions):
            aggregators[i].finalize()
            results.append(aggregators[i].get_final_result().result)
            
        for i in range(num_submissions):
            self.assertEqual(results[i], sleep_times[i])

    def test_shogun_on_serial_engine(self):
        home = expanduser("~")
        folder = os.sep.join([home, "unit_test_shogun_on_sge_dummy_result"])
        try:
            shutil.rmtree(folder)
        except OSError:
            pass
        engine = SerialComputationEngine()
        num_submissions = 3
        sleep_times = randint(0, 3, num_submissions)
        self.engine_tester(engine, sleep_times)

    def test_shogun_on_sge_engine(self):
        home = expanduser("~")
        folder = os.sep.join([home, "unit_test_shogun_on_sge_dummy_result"])
        try:
            shutil.rmtree(folder)
        except OSError:
            pass
        pbs_parameters = BatchClusterParameters(foldername=folder)
        engine = SGEComputationEngine(pbs_parameters, check_interval=1)
        num_submissions = 1
        sleep_times = randint(0, 3, num_submissions)
        self.engine_tester(engine, sleep_times)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
