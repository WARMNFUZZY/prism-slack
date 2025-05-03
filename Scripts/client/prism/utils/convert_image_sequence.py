import os
import subprocess

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


def check_conversion(core, state_data, ext, output_path):
    if core.appPlugin.pluginName == "Houdini":
        if state_data['state_type'] == 'pb' and state_data['extension'] == ".mp4":
            directory = os.path.dirname(output_path)
            base = os.path.basename(output_path).split(".")[0]
            output = f"{directory}/{base}{state_data['extension']}"
            return [output]

    if ext not in ["png", "jpg", "exr"]:
        return [output_path]

    if state_data["range_type"] == "Expression":
        core.popup(
            "Your render has been published but the Slack plugin does not support expression ranges yet."
        )
        raise ValueError("Invalid range type.")

    if core.getPlugin("MediaExtension"):
        if state_data["convert_media"] is True:
            return _handle_media_conversion_checkbox(state_data, core, output_path)

    if state_data["range_type"] == "Single Frame":
        return _handle_single_frame(state_data, output_path)

    if state_data["range_type"] in ["Scene", "Shot", "Custom", "Node"]:
        return _handle_scene_shot_custom_node(state_data, core, output_path)
    
    if state_data["range_type"] == "Shot + 1":
        return _shot_plus_one(state_data, core, output_path)
    
    else:
        raise ValueError("Invalid range type.")
    

def _handle_media_conversion_checkbox(state_data, core, outputPath):
    option = state_data["converted_extension"].lower()
    option = _retrieve_extension(option)
    base = os.path.basename(outputPath).split(".")[0]
    top_directory = os.path.dirname(outputPath)
    output_list = []

    if state_data["state_type"] == "pb":
        if option in ["mp4", "mov"]:
            converted_file = f"{top_directory} ({option})/{base} ({option}).{option}"
            output_list.append(converted_file)
        
        elif option in ["png", "jpg"]:
            framePad = "#" * core.framePadding
            sequence = f"{top_directory} ({option})/{base} ({option}).{framePad}.{option}"
            convert = _convert_image_sequence(core, sequence, state_data)
            output_list.append(convert)

    elif state_data["state_type"] == "render":
        aov = os.path.dirname(outputPath).split("/")[-1]
        version_folder = os.path.dirname(os.path.dirname(outputPath)).split("/")[-1]
        top_directory = os.path.dirname(os.path.dirname(os.path.dirname(outputPath)))
        version_directory_ext = f"{version_folder} ({option})"
        base = base.replace(version_folder, version_directory_ext)

        if option in ["mp4", "mov"]:
            converted_file = f"{top_directory}/{version_directory_ext}/{aov}/{base}.{option}"
            output_list.append(converted_file)
        
        elif option in ["png", "jpg"]:
            framePad = "#" * core.framePadding
            sequence = f"{top_directory}/{version_directory_ext}/{aov}/{base}.{framePad}.{option}"
            convert = _convert_image_sequence(core, sequence, state_data)
            output_list.append(convert)

    return output_list


# Convert an image sequence to a video
@err_catcher(name=__name__)
def _convert_image_sequence(core, sequence, state_data):
    folder_path = os.path.dirname(sequence)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    input_sequence = _convert_sequence_path(core, sequence, state_data)
    
    # Determine the starting frame
    start_frame = state_data["start_frame"]

    # Construct input and output paths
    contstructed_file = _construct_output_file(input_sequence)

    # Run ffmpeg to create the video
    output_file = _convert_to_mp4(core, input_sequence, start_frame, contstructed_file)
    
    return output_file


# Convert the sequence path to a more universal format
def _convert_sequence_path(core, sequence, state_data):
    if state_data['app'] == "Houdini":
        if state_data['convert_media'] is True:
            input_sequence = sequence.replace("#" * core.framePadding, "%04d")
        else:
            input_sequence = sequence.replace(".$F4.", ".%04d.")
    
    elif state_data['app'] == "Cinema4D":
        if state_data['convert_media'] is True:
            input_sequence = sequence.replace("#" * core.framePadding, "%04d")
        else:
            input_sequence = sequence.replace("..", ".%04d.")

    else:
        input_sequence = sequence.replace("#" * core.framePadding, "%04d")

    return input_sequence


# Construct the output file path for ffmpeg
def _construct_output_file(input_sequence):
    basename = os.path.basename(input_sequence).split(".%04d.")[0]
    directory = os.path.dirname(input_sequence)
    output_file = os.path.join(directory, basename + ".mp4")

    return output_file


# Convert the image sequence to an mp4 video
def _convert_to_mp4(core, input_sequence, start_frame, output_file):
    ffmpegPath = os.path.join(core.prismLibs, "Tools", "FFmpeg", "bin", "ffmpeg.exe")
    ffmpegPath = ffmpegPath.replace("\\", "/")
    
    if not os.path.exists(ffmpegPath):
        raise SystemError(f"ffmpeg not found at {ffmpegPath}")
        return

    try:
        result = subprocess.run(
            [
                ffmpegPath,
                "-y",
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
        print(f"Error running ffmpeg: {e.stderr.decode()}")
        return

    output_file = output_file.replace("\\", "/")

    return output_file


def _handle_single_frame(state_data, output_path):
    output_ext = os.path.splitext(output_path)[1]
    output_basename = os.path.splitext(output_path)[0]
    
    if os.path.exists(f"{output_basename}{output_ext}"):
        output = f"{output_basename}{output_ext}"
    else:
        output = f"{output_basename}.{state_data['start_frame']}{output_ext}"

    return [output]


def _handle_scene_shot_custom_node(state_data, core, output_path):
    if int(state_data["start_frame"]) == int(state_data["end_frame"]):
        if core.appPlugin.pluginName == "Houdini":
            file = output_path.replace("$F4", state_data['start_frame'])
        
        elif core.appPlugin.pluginName == "Cinema4D":
            file = output_path.replace("..", f".{state_data['start_frame']}.")
        
        else:
            file = output_path.replace("#" * core.framePadding, state_data["start_frame"])
        
        outputList = [file]

    elif int(state_data["start_frame"]) < int(state_data["end_frame"]):
        convert = _convert_image_sequence(core, output_path, state_data)
        outputList = [convert]

    else:
        raise ValueError("Invalid range.")

    return outputList


def _handle_custom(state_data, core, output_path):
    if int(state_data["start_frame"]) == int(state_data["end_frame"]):
        file = output_path.replace("#" * core.framePadding, state_data["start_frame"])
        outputList = [file]

    elif int(state_data["start_frame"]) < int(state_data["end_frame"]):
        convert = _convert_image_sequence(core, output_path, state_data)
        outputList = [convert]

    else:
        raise ValueError("Invalid range.")

    return outputList


def _handle_node(state_data, core, output_path):
    if int(state_data["start_frame"]) == int(state_data["end_frame"]):
        file = output_path.replace("$F4" * core.framePadding, state_data["start_frame"])
        outputList = [file]
    
    elif int(state_data["start_frame"]) < int(state_data["end_frame"]):
        convert = _convert_image_sequence(core, output_path, state_data)
        outputList = [convert]
    
    else:
        raise ValueError("Invalid range.")
    
    return outputList


def _shot_plus_one(state_data, core, output_path):

    convert = _convert_image_sequence(core, output_path, state_data)
    outputList = [convert]

    return outputList


# Get proper extension from media conversion type
def _retrieve_extension(option):
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