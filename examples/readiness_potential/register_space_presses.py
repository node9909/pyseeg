'''
The following example was tested with OpenBCI Ganglion board.
'''

from pyseeg.communication import record_data
from pyseeg.stimuli import WaitKeyPress

# 0. Define output path (default is in your home directory).
output_path = '/tmp/pyseeg_test_output.csv'

# 1. Create stimuli object.
sti = WaitKeyPress(fullscr=False, duration_sec=10)

# 2. Record data with triggers (20 seconds or delete key press).
record_data(sti, output_path=output_path)
#TODO: add aux channels to the output.

# 3. Optionally: plot the data.
from pyseeg.visualization import plot_data
plot_data(output_path)

'''
The acquisition manager will ask the stimuli controller about the `state`
each time it collects the data (255 times per second in the case of OpenBCI).
Then the complete information will be saved to a file (sample id, channels
recordings, auxilliary channels, state).
'''
