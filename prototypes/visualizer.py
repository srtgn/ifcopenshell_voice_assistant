# #!/usr/bin/env python3
# """Plot the live microphone signal(s) with matplotlib.

# Matplotlib and NumPy have to be installed.

# """
# import argparse
# import queue
# import sys

# from matplotlib.animation import FuncAnimation
# import matplotlib.pyplot as plt
# import numpy as np
# import sounddevice as sd


# def int_or_str(text):
#     """Helper function for argument parsing."""
#     try:
#         return int(text)
#     except ValueError:
#         return text


# parser = argparse.ArgumentParser(add_help=False)
# parser.add_argument(
#     '-l', '--list-devices', action='store_true',
#     help='show list of audio devices and exit')
# args, remaining = parser.parse_known_args()
# if args.list_devices:
#     print(sd.query_devices())
#     parser.exit(0)
# parser = argparse.ArgumentParser(
#     description=__doc__,
#     formatter_class=argparse.RawDescriptionHelpFormatter,
#     parents=[parser])
# parser.add_argument(
#     'channels', type=int, default=[1], nargs='*', metavar='CHANNEL',
#     help='input channels to plot (default: the first)')
# parser.add_argument(
#     '-d', '--device', type=int_or_str,
#     help='input device (numeric ID or substring)')
# parser.add_argument(
#     '-w', '--window', type=float, default=200, metavar='DURATION',
#     help='visible time slot (default: %(default)s ms)')
# parser.add_argument(
#     '-i', '--interval', type=float, default=30,
#     help='minimum time between plot updates (default: %(default)s ms)')
# parser.add_argument(
#     '-b', '--blocksize', type=int, help='block size (in samples)')
# parser.add_argument(
#     '-r', '--samplerate', type=float, help='sampling rate of audio device')
# parser.add_argument(
#     '-n', '--downsample', type=int, default=10, metavar='N',
#     help='display every Nth sample (default: %(default)s)')
# args = parser.parse_args(remaining)
# if any(c < 1 for c in args.channels):
#     parser.error('argument CHANNEL: must be >= 1')
# mapping = [c - 1 for c in args.channels]  # Channel numbers start with 1
# q = queue.Queue()


# def audio_callback(indata, frames, time, status):
#     """This is called (from a separate thread) for each audio block."""
#     if status:
#         print(status, file=sys.stderr)
#     # Fancy indexing with mapping creates a (necessary!) copy:
#     q.put(indata[::args.downsample, mapping])


# def update_plot(frame):
#     """This is called by matplotlib for each plot update.

#     Typically, audio callbacks happen more frequently than plot updates,
#     therefore the queue tends to contain multiple blocks of audio data.

#     """
#     global plotdata
#     while True:
#         try:
#             data = q.get_nowait()
#         except queue.Empty:
#             break
#         shift = len(data)
#         plotdata = np.roll(plotdata, -shift, axis=0)
#         plotdata[-shift:, :] = data
#     for column, line in enumerate(lines):
#         line.set_ydata(plotdata[:, column])
#     return lines


# try:
#     if args.samplerate is None:
#         device_info = sd.query_devices(args.device, 'input')
#         args.samplerate = device_info['default_samplerate']

#     length = int(args.window * args.samplerate / (1000 * args.downsample))
#     plotdata = np.zeros((length, len(args.channels)))

#     fig, ax = plt.subplots()
#     lines = ax.plot(plotdata)
#     if len(args.channels) > 1:
#         ax.legend(['channel {}'.format(c) for c in args.channels],
#                   loc='lower left', ncol=len(args.channels))
#     ax.axis((0, len(plotdata), -1, 1))
#     ax.set_yticks([0])
#     ax.yaxis.grid(True)
#     ax.tick_params(bottom=False, top=False, labelbottom=False,
#                    right=False, left=False, labelleft=False)
#     fig.tight_layout(pad=0)

#     stream = sd.InputStream(
#         device=args.device, channels=max(args.channels),
#         samplerate=args.samplerate, callback=audio_callback)
#     ani = FuncAnimation(fig, update_plot, interval=args.interval, blit=True)
#     with stream:
#         plt.show()
# except Exception as e:
#     parser.exit(type(e).__name__ + ': ' + str(e))



#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""
import argparse
import math
import shutil

import numpy as np
import sounddevice as sd

usage_line = ' press <enter> to quit, +<enter> or -<enter> to change scaling '


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


try:
    columns, _ = shutil.get_terminal_size()
except AttributeError:
    columns = 80

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__ + '\n\nSupported keys:' + usage_line,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-b', '--block-duration', type=float, metavar='DURATION', default=50,
    help='block size (default %(default)s milliseconds)')
parser.add_argument(
    '-c', '--columns', type=int, default=columns,
    help='width of spectrogram')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-g', '--gain', type=float, default=10,
    help='initial gain factor (default %(default)s)')
parser.add_argument(
    '-r', '--range', type=float, nargs=2,
    metavar=('LOW', 'HIGH'), default=[100, 2000],
    help='frequency range (default %(default)s Hz)')
args = parser.parse_args(remaining)
low, high = args.range
if high <= low:
    parser.error('HIGH must be greater than LOW')

# Create a nice output gradient using ANSI escape sequences.
# Stolen from https://gist.github.com/maurisvh/df919538bcef391bc89f
colors = 30, 34, 35, 91, 93, 97
chars = ' :%#\t#%:'
gradient = []
for bg, fg in zip(colors, colors[1:]):
    for char in chars:
        if char == '\t':
            bg, fg = fg, bg
        else:
            gradient.append('\x1b[{};{}m{}'.format(fg, bg + 10, char))

try:
    samplerate = sd.query_devices(args.device, 'input')['default_samplerate']

    delta_f = (high - low) / (args.columns - 1)
    fftsize = math.ceil(samplerate / delta_f)
    low_bin = math.floor(low / delta_f)

    def callback(indata, frames, time, status):
        if status:
            text = ' ' + str(status) + ' '
            print('\x1b[34;40m', text.center(args.columns, '#'),
                  '\x1b[0m', sep='')
        if any(indata):
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
            magnitude *= args.gain / fftsize
            line = (gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                    for x in magnitude[low_bin:low_bin + args.columns])
            print(*line, sep='', end='\x1b[0m\n')
        else:
            print('no input')

    with sd.InputStream(device=args.device, channels=1, callback=callback,
                        blocksize=int(samplerate * args.block_duration / 1000),
                        samplerate=samplerate):
        while True:
            response = input()
            if response in ('', 'q', 'Q'):
                break
            for ch in response:
                if ch == '+':
                    args.gain *= 2
                elif ch == '-':
                    args.gain /= 2
                else:
                    print('\x1b[31;40m', usage_line.center(args.columns, '#'),
                          '\x1b[0m', sep='')
                    break
except KeyboardInterrupt:
    parser.exit('Interrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))