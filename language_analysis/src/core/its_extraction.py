import pandas as pd

def extract_segments(root):
    segments = []

    for i, segment in enumerate(root.findall(".//Segment")):
        seg_data = {
            "segment_id": i,
            "start_time": segment.get("startTime", "0"),
            "end_time": segment.get("endTime", "0"),
            "speaker_type": segment.get("spkr", "Unknown"),
            "child_utt_count": segment.get("childUttCnt", "0"),
            "child_utt_len": segment.get("childUttLen", "0"),
            "fem_adult_word_cnt": segment.get("femAdultWordCnt", "0"),
            "male_adult_word_cnt": segment.get("maleAdultWordCnt", "0"),
            "fem_adult_utt_cnt": segment.get("femAdultUttCnt", "0"),
            "male_adult_utt_cnt": segment.get("maleAdultUttCnt", "0"),
            "overlap_cnt": segment.get("overlapCnt", "0"),
        }

        try:
            start = float(seg_data["start_time"])
            end = float(seg_data["end_time"])
            seg_data["duration_seconds"] = (end - start) / 1000
        except:
            seg_data["duration_seconds"] = 0

        segments.append(seg_data)

    print(f"Extracted {len(segments)} segments")
    return segments


def extract_conversations(root):
    conversations = []

    for i, conv in enumerate(root.findall(".//Conversation")):
        conv_data = {
            "conversation_id": i,
            "start_time": conv.get("startTime", "0"),
            "end_time": conv.get("endTime", "0"),
            "turn_count": conv.get("turnTaking", "0"),
        }

        try:
            start = float(conv_data["start_time"])
            end = float(conv_data["end_time"])
            conv_data["duration_seconds"] = (end - start) / 1000
        except:
            conv_data["duration_seconds"] = 0

        conversations.append(conv_data)

    print(f"Extracted {len(conversations)} conversations")
    return conversations