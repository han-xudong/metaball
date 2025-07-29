#!/usr/bin/env python

"""
Run Metaball

This script is to run the Metaball, capturing metaball's deformation and inferring the force and node 
displacement using the trained model.
"""

from metaball import Metaball

if __name__ == "__main__":
    # Create a metaball instance
    metaball = Metaball(name="metaball")
    # Run the metaball
    metaball.run()
