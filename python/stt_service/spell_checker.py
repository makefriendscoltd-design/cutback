"""
Korean Spell Checker

자막용 한국어 맞춤법/띄어쓰기 교정.

Naver 맞춤법 검사기(공개 웹 엔드포인트)에 직접 HTTP 호출.
- 인터넷 필요
- 호출 전에 검색 페이지에서 passportKey 를 한 번 가져와 캐시
- 자막 텍스트(보통 30자 미만)에만 적용 → 500자 제한 안전
- 실패 시 원본 그대로 반환 (절대 예외 전파 안 함)

py-hanspell 패키지는 modern pip 와 호환되지 않아 직접 구현.
"""

import json
import logging
import re
import time
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)


_NAVER_SPELLER_URL = "https://m.search.naver.com/p/csearch/ocontent/util/SpellerProxy"
_NAVER_SEARCH_URL = "https://search.naver.com/search.naver"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://search.naver.com/",
}

# JSONP wrapper 제거용
_JSONP_RE = re.compile(r"^[^(]*\((.*)\)\s*;?\s*$", re.DOTALL)
# Naver 결과의 <em class='red_text'>...</em> 같은 태그 제거
_TAG_RE = re.compile(r"<[^>]+>")
# 검색 페이지에서 passportKey 추출
_PASSPORT_RE = re.compile(r"passportKey['\"\s:=]+([A-Za-z0-9]+)")


class KoreanSpellChecker:
    """한국어 자막 맞춤법 교정기 (Naver Speller)"""

    def __init__(self, timeout: float = 5.0, throttle: float = 0.05) -> None:
        self.timeout = timeout
        self.throttle = throttle  # 호출 간 간격 (rate-limit 회피)
        self.available = False
        self._session = requests.Session()
        self._session.headers.update(_HEADERS)
        self._passport_key: Optional[str] = None

        try:
            self._refresh_passport_key()
            # 헬스 체크
            test = self._call("테스트입니다")
            if test is not None:
                self.available = True
                logger.info("KoreanSpellChecker initialized (Naver speller)")
            else:
                logger.warning("Naver speller responded without result - disabled")
        except Exception as exc:
            logger.warning(
                f"Naver speller unreachable - spell check disabled: {exc}"
            )

    def _refresh_passport_key(self) -> None:
        """검색 페이지에서 passportKey 를 가져와 캐시."""
        resp = self._session.get(
            _NAVER_SEARCH_URL,
            params={"query": "맞춤법검사기"},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        match = _PASSPORT_RE.search(resp.text)
        if not match:
            raise RuntimeError("passportKey not found in Naver search page")
        self._passport_key = match.group(1)
        logger.debug("passportKey refreshed")

    def _call(self, text: str, retry: bool = True) -> Optional[str]:
        """Naver speller 한 번 호출. 교정 텍스트 반환 또는 None."""
        if not text or not text.strip():
            return text
        params: dict[str, str] = {
            "_callback": "cb",
            "q": text,
            "color_blindness": "0",
        }
        passport = self._passport_key
        if passport:
            params["passportKey"] = passport

        resp = self._session.get(
            _NAVER_SPELLER_URL,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        body = resp.text

        # JSONP → JSON
        match = _JSONP_RE.match(body)
        payload = match.group(1) if match else body
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return None

        msg = data.get("message", {}) if isinstance(data, dict) else {}

        # 키 만료 시 한 번만 재시도
        if msg.get("error") and retry:
            logger.info("passportKey expired, refreshing")
            try:
                self._refresh_passport_key()
                return self._call(text, retry=False)
            except Exception as exc:
                logger.debug(f"passport refresh failed: {exc}")
                return None

        result = msg.get("result")
        if not isinstance(result, dict):
            return None

        # 우선순위: notag_html → html(태그 제거) → origin_html
        for key in ("notag_html", "html", "origin_html"):
            value = result.get(key)
            if isinstance(value, str) and value:
                cleaned = _TAG_RE.sub("", value).strip()
                if cleaned:
                    return cleaned
        return None

    def check_one(self, text: str) -> str:
        """단일 텍스트 교정. 실패 시 원본 반환."""
        if not self.available or not text or not text.strip():
            return text
        try:
            corrected = self._call(text)
            if corrected:
                return corrected
            return text
        except Exception as exc:
            logger.debug(f"spell check skipped: {exc}")
            return text

    def check_batch(self, texts: List[str]) -> List[str]:
        """여러 텍스트 일괄 교정. 개별 실패는 원본 유지."""
        if not self.available:
            return list(texts)

        results: List[str] = []
        changed = 0

        for text in texts:
            corrected = self.check_one(text)
            if corrected != text:
                changed += 1
            results.append(corrected)
            if self.throttle > 0:
                time.sleep(self.throttle)

        logger.info(
            f"spell check completed: {changed}/{len(texts)} changed"
        )
        return results
