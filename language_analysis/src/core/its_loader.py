import xml.etree.ElementTree as ET

def parse_file(its_file_path):
    try:
        print(f"Parsing ITS file: {its_file_path}")
        tree = ET.parse(its_file_path)
        root = tree.getroot()
        print("File parsed successfully!")
        return tree, root

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return False

    except FileNotFoundError:
        print(f"File not found: {its_file_path}")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def extract_recording_info(root, its_file_path):
    print("Running extract_recording_info...")
    
    recording_info = {}

    processing_unit = root.find('.//ProcessingUnit')
    if processing_unit is not None:
        recording_info = {
            'file_path': its_file_path,
            'software_version': processing_unit.get('version', 'Unknown'),
            'analysis_date': processing_unit.get('analysisDate', 'Unknown'),
            'analysis_version': processing_unit.get('analysisVersion', 'Unknown')
        }

    recording = root.find('.//Recording')
    if recording is not None:
        recording_info.update({
            'recording_num': recording.get('num', 'Unknown'),
            'start_time': recording.get('startTime', 'Unknown'),
            'end_time': recording.get('endTime', 'Unknown'),
            'start_clock_time': recording.get('startClockTime', 'Unknown'),
            'end_clock_time': recording.get('endClockTime', 'Unknown')
        })

        try:
            start = float(recording_info['start_time'])
            end = float(recording_info['end_time'])
            duration_seconds = (end - start) / 1000
            recording_info['duration_seconds'] = duration_seconds
            recording_info['duration_hours'] = duration_seconds / 3600
        except:
            pass

    child_info = root.find('.//ChildInfo')
    if child_info is not None:
        recording_info.update({
            'child_gender': child_info.get('gender', 'Unknown'),
            'child_age_months': child_info.get('ageInMonths', 'Unknown'),
            'child_age_weeks': child_info.get('ageInWeeks', 'Unknown'),
            'child_dob': child_info.get('dob', 'Unknown')
        })

    return recording_info