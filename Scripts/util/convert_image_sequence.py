import os
import subprocess
import glob
import re

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class ConvertImageSequence():
    def __init__(self, core):
        self.core = core

    @err_catcher(name=__name__)
    def convertImageSequence(self, sequence):
        # Define the "slack" output folder
        folder_path = os.path.dirname(sequence)
        slack_folder = os.path.join(folder_path, "slack")
        
        if not os.path.exists(slack_folder):
            os.makedirs(slack_folder)

        # Construct input and output paths
        input_sequence = sequence.replace('.####.', '.%04d.')
        basename = os.path.basename(sequence).split('.####.')[0]
        output_file = os.path.join(slack_folder, basename + '.mp4')
        
        ffmpegPath = os.path.join(self.core.prismLibs, "Tools", "FFmpeg", "bin", "ffmpeg.exe")
        ffmpegPath = ffmpegPath.replace('\\', '/')

        if not os.path.exists(ffmpegPath):
            self.core.popup(f"ffmpeg not found at {ffmpegPath}")
            return

        # Search for matching files to determine the start frame
        pattern = sequence.replace('.####.', '.*.')
        files = sorted(glob.glob(pattern))
        if not files:
            self.core.popup(f"No files found matching pattern: {pattern}")
            return
        
        start_frame = re.search(r"\.(\d{4})\.", files[0])
        if start_frame:
            start_frame = start_frame.group(1)
        else:
            self.core.popup("Failed to determine the starting frame.")
            return

        # Run ffmpeg to create the video
        try:
            result = subprocess.run([
                ffmpegPath,
                "-framerate", "24",
                "-start_number", start_frame,
                "-i", input_sequence,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                output_file
            ], capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            self.core.popup(f"Error running ffmpeg: {e.stderr.decode()}")
            return

        output_file = output_file.replace("\\", "/")
        return output_file