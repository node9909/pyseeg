import sys
import csv
sys.path.append('..')
sys.path.append('../..')
import open_bci_v3 as bci
import datetime
import time

import multiprocessing as mp
from psychopy import visual

import modules.filterlib as flt
import modules.blink as blk
# import modules.plotlib as pltmod
import modules.spellerlib as spell

output_dir = '../../data/'

# code the time to name file or variable
csv_filename = output_dir + \
    datetime.datetime.now().strftime("%Y%m%d%H%M") + \
    '.csv'


def func_blink_det(blink_det):
    def plotData(sample):

        # get sample form the first channel (index '0')
        smp = sample.channel_data[0]

        # filter fist sample (place in list with the index '0')
        smp_flted = frt.filterIIR(smp, 0)

        # detect all blinks (signal amplifications above 60uV)
        brt.blink_detect(smp_flted, 60)

        # report it the new blink is spotted
        if brt.new_blink:
            print(brt.blinks_num)
            blink_det.put(brt.blinks_num)

        # # online plotting using matplotlib blit
        # prt.frame_plot(smp_flted)

        with open(csv_filename, 'at') as f:
            save = csv.writer(f)
            save.writerow([smp, smp_flted, brt.blinks_num])
            # save.writerow([sample.id] + sample.channel_data)

    if __name__ == '__main__':

        # filtering in real time object creation
        frt = flt.FltRealTime()

        # blink detection in real time object creation
        brt = blk.BlinkRealTime()

        # plotting in real time object creation
        # prt = pltmod.OnlinePlot(samples_per_frame=2)

        port = '/dev/ttyUSB1'
        baud = 115200
        board = bci.OpenBCIBoard(port=port, baud=baud)
        board.start_streaming(plotData)


blink_det = mp.Queue()

proc_blink_det = mp.Process(
    name='proc_',
    target=func_blink_det,
    args=(blink_det)
    )

proc_blink_det.start()


############################################
#                                          #
#             SPELLER SECTION              #
#                                          #
############################################

# store typed text in string variable
text_typed = 'Typed text:\n'

# object generating table with the letters
generator = spell.TablesGenerator()

# generate rows tables
rows = generator.rows_generate()
# generate cols tables
cols = generator.cols_generate()

# generate rows tables for PschoPy display
rows_stim = generator.rows_stim_generate()
# generate cols tables for PschoPy display
cols_stim = generator.cols_stim_generate()

# main loop. Only delete allows to escape it
# TODO: repair this. Typling delete doesn't break the loop
# TODO: latency time after previous decision
while True:
    # stim for typed text display
    text_typed_stim = visual.TextStim(
        generator.win_main, text=text_typed,
        font='Monospace', pos=(0, -300), height='40', wrapWidth=600
        )
    # get the time to furter reference as time of the last decision
    last_time = time.time()
    row = 0
    rows_stim[row].draw()
    text_typed_stim.draw()
    generator.win_main.flip()

    # get the time of the previous decision
    last_time = time.time()
    # blink presence flag
    blink_present = False
    # rows display loop. Awaits for the decision (typed space)
    while not blink_present:
        if time.time() - last_time > 2:
            if row > 3:
                row = -1
            row += 1

            rows_stim[row].draw()
            text_typed_stim.draw()
            generator.win_main.flip()

            # get the time of the previous decision
            last_time = time.time()
        if not blink_det.empty():
            blink_present = True
            # to remove an object from the que
            blink_det.get()

    # clear the flag
    blink_present = False

    # get the time of the previous decision
    last_time = time.time()
    col = 0
    cols_stim[row][col].draw()
    text_typed_stim.draw()
    generator.win_main.flip()

    last_time = time.time()
    # rows display loop. Awaits for the decision (typed space)
    while not blink_present:
        if time.time() - last_time > 2:
            if col > 3:
                col = -1
            col += 1

            cols_stim[row][col].draw()
            text_typed_stim.draw()
            generator.win_main.flip()

            last_time = time.time()
        if not blink_det.empty():
            blink_present = True
            # to remove an object from the que
            blink_det.get()

    # clear the flag
    blink_present = False

    # delete last char in the typed_text variable
    if row == 4 and col == 4:
        text_typed = text_typed[:-1]
        # console interface issue, feedback
        print('last char deleted')

    # insert space to the typed_text variable
    elif row == 4 and col == 3:
        text_typed += ' '
        # console interface issue, feedback
        print('[space]')

    # insert choosed letter to the typed_text variable
    else:
        text_typed += cols[row][col][row*2+1][col*4+2]
        # console interface issue, feedback
        print(cols[row][col][row*2+1][col*4+2])
        print(row)
        print(col)

# close the window after main loop ends
generator.win_main.close()