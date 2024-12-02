import re
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')
import sys
print ('argument list', sys.argv)
srt_file_path = sys.argv[1]

def count_syllables_french(word):
    word = word.lower()
    count = 0
    vowels = 'aeiouyàâäéèêëîïôöùûü'
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith('e'):
        count -= 1
    if word.endswith('es'):
        count -= 1
    if word.endswith('ent'):
        count -= 1
    if count <= 0:
        count = 1
    return count

def estimate_time(start_time, end_time, current_syllables, total_syllables):
    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)
    total_duration = end_seconds - start_seconds
    proportion = current_syllables / total_syllables
    estimated_duration = total_duration * proportion
    estimated_end = start_seconds + estimated_duration
    return seconds_to_time(estimated_end)

def time_to_seconds(time_str):
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def seconds_to_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def extract_sentences_from_srt(file_path, language='french'):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    subtitle_blocks = re.split(r'\n\n', content.strip())

    sentences_with_timestamps = []
    current_sentence = ""
    current_start_time = ""
    current_end_time = ""

    for block in subtitle_blocks:
        lines = block.split('\n')
        if len(lines) < 3:
            continue

        start_time, end_time = lines[1].split(' --> ')
        start_time = start_time.strip()
        end_time = end_time.strip()

        subtitle_text = ' '.join(lines[2:])
        subtitle_text = re.sub(r'<[^>]+>', '', subtitle_text)

        # If this is the first block, set the current_start_time
        if not current_start_time:
            current_start_time = start_time

        # Check if adding the new subtitle text would create a new sentence
        temp_text = (current_sentence + ' ' + subtitle_text).strip()
        if len(sent_tokenize(temp_text, language=language)) == 1:
            current_sentence = temp_text
            current_end_time = end_time
        else:
            if current_sentence:
                sentences_with_timestamps.append((current_start_time, current_end_time, current_sentence.strip()))
            current_sentence = subtitle_text
            current_start_time = start_time
            current_end_time = end_time

    if current_sentence:
        sentences_with_timestamps.append((current_start_time, current_end_time, current_sentence.strip()))

    final_sentences = []
    for start_time, end_time, text in sentences_with_timestamps:
        sentences = sent_tokenize(text, language=language)

        total_syllables = sum(count_syllables_french(word) for word in text.split())
        current_syllables = 0
        for i, sentence in enumerate(sentences):
            sentence_syllables = sum(count_syllables_french(word) for word in sentence.split())
            current_syllables += sentence_syllables
            estimated_end=""
            if i == len(sentences) - 1:
                final_sentences.append((start_time, end_time, sentence))
            else:
                estimated_end = estimate_time(start_time, end_time, current_syllables, total_syllables)
                final_sentences.append((start_time, estimated_end, sentence))
            start_time = estimated_end

    return final_sentences


# Example usage
# srt_file_path = 'path/to/your/subtitle_file.srt'
extracted_sentences = extract_sentences_from_srt(srt_file_path, language='french')

for start_time, end_time, sentence in extracted_sentences:
    start_str = f"Starts at {start_time}" if start_time else ""
    end_str = f"Ends at {end_time}" if end_time else ""
    time_info = " ".join(filter(None, [start_str, end_str]))
    print(f"{time_info} {sentence}")