#! usr/bin/python
#
# file:			sentistrength
# author:		Joram Wessels
# date:			14-03-2017
# Description:
#   Calls SentiStrength for the prior sentiments and reads them into a dict.
#
# Dependencies:
#   - SentiStrength 2.0 jar
#   - SentiStrength 2.0 corpora
#
# Public functions:
#
# prior_sentiment
#   Returns the updated contextual_features dict with the prior sentiments.

import os
import subprocess
import time

sentistrength_postfix = "0_out.txt"


def prior_sentiment(contextual_features, input_file, jar_file, data_location):
    """Enriche the contextual_features dict with prior sentiment scores.

    Args:
        contextual_features: The initial dict containing ALL context words
        input_file:			 The file containing a column of context words
        jar_file:			 The SentiStrength jar file
        data_location:		 The path to the folder with SentiStrength data

    Returns:
        The updated contextual_features dictionary with prior scores
            contextual_features{'context word': [count, prior score]}

    """
    command = ["java", "-jar", jar_file, "sentidata", data_location, "input",
               input_file]
    subp = subprocess.Popen(command, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1)
    file = open(input_file + sentistrength_postfix, 'r')
    file.readline()
    for line in file:
        tokens = [token.strip() for token in line.split('\t')]
        contextual_features[tokens[2]][1] = \
            (int(tokens[0]) + int(tokens[1]))/4.0
    file.close()
    os.remove(input_file)
    os.remove(input_file + sentistrength_postfix)
    return contextual_features
