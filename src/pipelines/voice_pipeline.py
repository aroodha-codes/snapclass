from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np 
import io
import librosa
import streamlit as st


@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()


def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        st.error('Voice recog error')
        return None
    

def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0
    
    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            similarity = np.dot(new_embedding, stored_embedding)
            if similarity> best_score:
                best_score = similarity
                best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score
    
    return None, best_score



def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    try:
        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000,
        )

        if (
            audio.size == 0
            or not np.all(np.isfinite(audio))
            or not np.any(audio)
        ):
            return None

        segments = librosa.effects.split(audio, top_db=30)
        encoder = None
        usable_segments = 0
        identified_results = {}

        for start, end in segments:
            if (end - start) < sr * 0.5:
                continue

            wav = preprocess_wav(audio[start:end])

            # Require at least half a second after preprocessing.
            if (
                wav.size < int(sr * 0.5)
                or not np.all(np.isfinite(wav))
                or not np.any(wav)
            ):
                continue

            if encoder is None:
                encoder = load_voice_encoder()

            embedding = encoder.embed_utterance(wav)
            usable_segments += 1

            sid, score = identify_speaker(
                embedding,
                candidates_dict,
                threshold,
            )

            if sid is not None:
                if (
                    sid not in identified_results
                    or score > identified_results[sid]
                ):
                    identified_results[sid] = score

        if usable_segments == 0:
            return None

        return identified_results

    except Exception:
        return None