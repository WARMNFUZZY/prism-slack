import os
import subprocess
import glob
import re

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


# Convert an image sequence to a video
class ConvertImageSequence:
    def __init__(self, core):
        self.core = core

    # Convert an image sequence to a video
    @err_catcher(name=__name__)
    def convertImageSequence(self, sequence):
        # Define the "slack" output folder
        folder_path = os.path.dirname(sequence)

        # Construct input and output paths
        if self.core.appPlugin.pluginName == "Houdini":
            input_sequence = sequence.replace(".$F4.", ".%04d.")
        else:
            input_sequence = sequence.replace(".####.", ".%04d.")

        basename = os.path.basename(input_sequence).split(".%04d.")[0]
        output_file = os.path.join(folder_path, basename + ".mp4")

        ffmpegPath = os.path.join(
            self.core.prismLibs, "Tools", "FFmpeg", "bin", "ffmpeg.exe"
        )
        ffmpegPath = ffmpegPath.replace("\\", "/")

        if not os.path.exists(ffmpegPath):
            self.core.popup(f"ffmpeg not found at {ffmpegPath}")
            return

        # Search for matching files to determine the start frame
        pattern = input_sequence.replace(".%04d.", ".*.")
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
            result = subprocess.run(
                [
                    ffmpegPath,
                    "-framerate",
                    "24",
                    "-start_number",
                    start_frame,
                    "-i",
                    input_sequence,
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    output_file,
                ],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            self.core.popup(f"Error running ffmpeg: {e.stderr.decode()}")
            return

        output_file = output_file.replace("\\", "/")
        return output_file

    @err_catcher(name=__name__)
    def checkConversion(self, output_file, state, type, ui):
        ext = os.path.splitext(output_file)[1].replace(".", "")

        rangeType = state.cb_rangeType.currentText()

        if rangeType == "Single Frame" or rangeType in ["Scene", "Shot"]:
            startFrame = state.l_rangeStart.text()
            endFrame = state.l_rangeEnd.text()

        if rangeType == "Custom":
            startFrame = state.sp_rangeStart.text()
            endFrame = state.sp_rangeEnd.text()

        if rangeType == "Expression":
            if ui == "DL":
                print("Expression ranges are not supported right now.")
            else:
                self.core.popup(
                    "Your render has been published but it was not published to Slack. The plugin does not currently support expression ranges."
                )
            return

        if ext in ["exr", "png", "jpg"]:
            if rangeType == "Single Frame":
                output = [output_file]
                converted = None

            if rangeType != "Single Frame" and startFrame == endFrame:
                output = output_file.replace(
                    "#" * self.core.framePadding, str(startFrame)
                )
                output = [output]
                converted = None

            if rangeType != "Single Frame" and startFrame < endFrame:
                if state.chb_mediaConversion.isChecked() is False:
                    convert = self.convertImageSequence(output_file)
                    output = [output_file]
                    converted = [convert]
                else:
                    option = state.cb_mediaConversion.currentText().lower()
                    ext = self.retrieveExtension(option)

                    base = os.path.basename(output_file).split(".")[0]
                    if type == "render":
                        version_directory = os.path.dirname(
                            os.path.dirname(output_file)
                        )
                        aov_directory = os.path.basename(os.path.dirname(output_file))
                        file = base.split(f"_{aov_directory}")[0]
                        converted_directory = (
                            f"{version_directory} ({ext})/{aov_directory}"
                        )
                        converted_files = f"{converted_directory}/{file} ({ext})_{aov_directory}.{ext}"
                    elif type == "pb":
                        version_directory = os.path.dirname(output_file)
                        aov_directory = os.path.basename(os.path.dirname(output_file))
                        file = f"{base} ({ext})"
                        converted_directory = f"{version_directory} ({ext})"
                        converted_files = f"{converted_directory}/{file}.{ext}"

                    output = [output_file]
                    converted = [converted_files]
                    if ext in ["png", "jpg"]:
                        framePad = "#" * self.core.framePadding
                        if type == "render":
                            sequence = f"{converted_directory}/{file} ({ext})_{aov_directory}.{framePad}.{ext}"
                        else:
                            sequence = f"{converted_directory}/{file}.{framePad}.{ext}"
                        convert = self.convertImageSequence(sequence)
                        output = [output_file]
                        converted = [convert]

        return output, converted

    # Get proper extension from media conversion type
    @err_catcher(name=__name__)
    def retrieveExtension(self, option):
        if "png" in option:
            ext = "png"
        elif "jpg" in option:
            ext = "jpg"
        elif "mp4" in option:
            ext = "mp4"
        elif "mov" in option:
            ext = "mov"
        else:
            ext = option

        return ext
