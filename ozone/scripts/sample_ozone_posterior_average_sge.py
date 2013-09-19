"""
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

Written (W) 2013 Heiko Strathmann
"""

from engines.BatchClusterParameters import BatchClusterParameters
from engines.SGEComputationEngine import SGEComputationEngine
from main.distribution.Gaussian import Gaussian
from main.mcmc.MCMCChain import MCMCChain
from main.mcmc.MCMCParams import MCMCParams
from main.mcmc.output.StatisticsOutput import StatisticsOutput
from main.mcmc.output.StoreChainOutput import StoreChainOutput
from main.mcmc.samplers.StandardMetropolis import StandardMetropolis
from numpy.lib.twodim_base import diag, eye
from numpy.ma.core import asarray
from os.path import expanduser
from ozone.distribution.OzonePosteriorAverageEngine import \
    OzonePosteriorAverageEngine
from pickle import dump
from tools.Log import Log
import logging
import os

def main():
    Log.set_loglevel(logging.DEBUG)
    
    prior = Gaussian(Sigma=eye(2) * 100)
    num_estimates = 5
    
    home = expanduser("~")
    folder = os.sep.join([home, "ozone_initial_test"])
    parameter_prefix="#$ -P jump"
    cluster_parameters = BatchClusterParameters(foldername=folder,
                                            memory=4,
                                            loglevel=logging.DEBUG,
                                            parameter_prefix=parameter_prefix)
        
    computation_engine = SGEComputationEngine(cluster_parameters, check_interval=10)
    posterior = OzonePosteriorAverageEngine(computation_engine=computation_engine,
                                        num_estimates=num_estimates,
                                        prior=prior)
    
    proposal_cov = diag([ 4.000000000000000e-05, 1.072091680000000e+02])
    mcmc_sampler = StandardMetropolis(posterior, scale=1.0, cov=proposal_cov)
    
    start = asarray([-11.35, -13.1])
    mcmc_params = MCMCParams(start=start, num_iterations=2000)
    chain = MCMCChain(mcmc_sampler, mcmc_params)
    
#    chain.append_mcmc_output(PlottingOutput(None, plot_from=1, lag=1))
    chain.append_mcmc_output(StatisticsOutput(print_from=1, lag=1))
    
    store_chain_output = StoreChainOutput(folder, lag=50)
    chain.append_mcmc_output(store_chain_output)
    
    loaded = store_chain_output.load_last_stored_chain()
    if loaded is None:
        logging.info("Running chain from scratch")
    else:
        logging.info("Running chain from iteration %d" % loaded.iteration)
        chain = loaded
        
    chain.run()
    
    f = open(folder + os.sep + "final_chain", "w")
    dump(chain, f)
    f.close()

if __name__ == "__main__":
    main()