import asyncio
import os
import re
import shutil
from pathlib import Path

import spacy
from fastapi import HTTPException, status

from database import DATA_DIR
from system_settings import get_edge_tts_rate_string

MEDIA_DIR = DATA_DIR / "media"
AUDIO_DIR = MEDIA_DIR / "audio" / "articles"
MEDIA_URL_PREFIX = "/media"
DEFAULT_VOICE = "en-US-JennyNeural"

_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.blank("en")
        _nlp.add_pipe(
            "sentencizer",
            config={"punct_chars": [".", "!", "?", "。", "！", "？"]},
        )
    return _nlp


def normalize_article_content(content: str) -> str:
    paragraphs = [re.sub(r"[ \t]+", " ", line).strip() for line in content.splitlines()]
    paragraphs = [paragraph for paragraph in paragraphs if paragraph]
    if not paragraphs:
        return ""

    normalized_paragraphs = []
    for paragraph in paragraphs:
        doc = get_nlp()(paragraph)
        normalized = " ".join(token.text for token in doc if not token.is_space)
        normalized = re.sub(r"\s+([,.;:!?%。，！？；：）\]\}])", r"\1", normalized)
        normalized = re.sub(r"([\(\[\{（])\s+", r"\1", normalized)
        normalized = re.sub(r"([,;:，；：])(?:\s*\1)+", r"\1", normalized)
        normalized = re.sub(r"([.!?。！？])(?:\s*[.!?。！？])+", r"\1", normalized)
        normalized_paragraphs.append(re.sub(r"[ \t]+", " ", normalized).strip())

    return "\n".join(normalized_paragraphs)


def split_sentences(content: str) -> list[str]:
    if not content:
        return []

    doc = get_nlp()(content)
    return [sentence.text.strip() for sentence in doc.sents if sentence.text.strip()]


def article_audio_url(article_id: str, filename: str) -> str:
    return f"{MEDIA_URL_PREFIX}/audio/articles/{article_id}/{filename}"


async def save_tts_audio(text: str, output_path: Path) -> None:
    import edge_tts

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(".tmp.mp3")
    voice = os.getenv("LINGUA_TTS_VOICE", DEFAULT_VOICE)
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=get_edge_tts_rate_string(),
    )
    await communicate.save(str(temp_path))
    temp_path.replace(output_path)


def generate_article_audio(article_id: str, content: str, sentences: list[str]) -> tuple[str, list[dict[str, str]]]:
    article_dir = AUDIO_DIR / article_id
    temp_dir = AUDIO_DIR / f"{article_id}.tmp"
    shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    if not content:
        shutil.rmtree(article_dir, ignore_errors=True)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return "", []

    try:
        asyncio.run(save_tts_audio(content, temp_dir / "article.mp3"))
        sentence_payloads = []
        for index, sentence in enumerate(sentences, start=1):
            filename = f"sentence_{index:03d}.mp3"
            asyncio.run(save_tts_audio(sentence, temp_dir / filename))
            sentence_payloads.append(
                {
                    "content": sentence,
                    "audio_url": article_audio_url(article_id, filename),
                }
            )
    except Exception as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"音频生成失败：{exc}",
        ) from exc

    shutil.rmtree(article_dir, ignore_errors=True)
    temp_dir.replace(article_dir)
    return article_audio_url(article_id, "article.mp3"), sentence_payloads


def build_article_assets(article_id: str, content: str) -> tuple[str, str, list[dict[str, str]]]:
    normalized_content = normalize_article_content(content)
    sentences = split_sentences(normalized_content)
    audio_url, sentence_payloads = generate_article_audio(article_id, normalized_content, sentences)
    return normalized_content, audio_url, sentence_payloads
