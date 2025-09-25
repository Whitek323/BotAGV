import numpy as np

from pydub import AudioSegment
from pydub.effects import high_pass_filter, low_pass_filter


class CuteVoice:
    def __init__(self,output_path, semitones=2, bit_depth=100, reverb_delay=20, reverb_decay=0.1):
        self.semitones = semitones
        self.bit_depth = bit_depth
        self.reverb_delay = reverb_delay
        self.reverb_decay = reverb_decay
        self.output_path = output_path

    def apply_pitch_shift(self, audio_segment):
        samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
        rate = 2 ** (self.semitones / 10.0)
        new_length = int(len(samples) / rate)
        resampled_samples = np.interp(
            np.linspace(0, len(samples), new_length),
            np.arange(len(samples)),
            samples
        )
        return AudioSegment(
            resampled_samples.astype(audio_segment.array_type).tobytes(),
            frame_rate=int(audio_segment.frame_rate * rate),
            sample_width=audio_segment.sample_width,
            channels=audio_segment.channels
        )

    def apply_ring_modulation(self, audio_segment, freq=0.5, magnitude=1):
        samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
        rate = audio_segment.frame_rate
        t = np.arange(len(samples)) / rate
        modulation = np.sin(2 * np.pi * freq * t)
        modulated_samples = samples * (1 - magnitude + magnitude * modulation)

        return AudioSegment(
            modulated_samples.astype(audio_segment.array_type).tobytes(),
            frame_rate=audio_segment.frame_rate,
            sample_width=audio_segment.sample_width,
            channels=audio_segment.channels
        )

    def apply_soft_distortion(self, audio_segment):
        samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
        max_val = np.iinfo(audio_segment.array_type).max
        step_size = max_val / (2 ** self.bit_depth)
        crushed_samples = np.round(samples / step_size) * step_size

        return AudioSegment(
            crushed_samples.astype(audio_segment.array_type).tobytes(),
            frame_rate=audio_segment.frame_rate,
            sample_width=audio_segment.sample_width,
            channels=audio_segment.channels
        )

    def apply_reverb(self, audio_segment):
        delayed = audio_segment - (1.0 - self.reverb_decay) * 20
        delayed = delayed.overlay(audio_segment, position=self.reverb_delay)
        return delayed

    def cute_robotize(self, input_path, output_path):
        sound = AudioSegment.from_file(input_path)

        # Processing
        higher_pitch = self.apply_pitch_shift(sound)
        filtered = high_pass_filter(higher_pitch, cutoff=700)
        filtered = low_pass_filter(filtered, cutoff=4000)
        softened = self.apply_soft_distortion(filtered)
        final = self.apply_reverb(softened)

        final.export(output_path, format="wav")
        
