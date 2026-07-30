from google import genai
from google.genai import types
import asyncio
import json
import re
import time
from typing import Dict, Any

from app.config import settings
from app.models.schemas import StockIndicators, AgentAnalysis, FullAnalysisResponse, QuickAnalysisResponse
from app.prompts import technical_analyst, fundamental_analyst, risk_manager
from app.models.enums import AgentRole


class AIAnalyzer:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-1.5-flash"  # Aktif ve güncel model adı

    async def _call_agent(self, system_prompt: str, user_prompt: str, retries: int = 3) -> Dict[str, Any]:
        """Gemini API'ye prompt gönderir. 429 durumunda retry yapar."""
        text = ""
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.3,
                    ),
                )
                text = response.text.strip()

                # Markdown ```json ... ``` bloğunu temizle
                json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
                if json_match:
                    text = json_match.group(1).strip()

                # İlk { ... } bloğunu bul
                brace_match = re.search(r"\{[\s\S]*\}", text)
                if brace_match:
                    text = brace_match.group(0)

                return json.loads(text)

            except json.JSONDecodeError:
                return {
                    "signal": "TUT",
                    "confidence": 0.5,
                    "key_points": ["JSON ayrıştırma hatası."],
                    "analysis_text": f"Yanıt işlenemedi: {text[:200]}"
                }
            except Exception as e:
                err = str(e)
                # Rate limit (429) → bekle ve tekrar dene
                if "429" in err and attempt < retries - 1:
                    wait_sec = 10 * (attempt + 1)  # 10s, 20s, 30s
                    await asyncio.sleep(wait_sec)
                    continue
                return {
                    "signal": "TUT",
                    "confidence": 0.0,
                    "key_points": [f"API Hatası: {err[:150]}"],
                    "analysis_text": "Yapay zeka analizi sırasında bir hata oluştu."
                }
        return {"signal": "TUT", "confidence": 0.0, "key_points": ["Maksimum deneme sayısına ulaşıldı."], "analysis_text": ""}

    async def run_full_analysis(
        self,
        symbol: str,
        indicators: StockIndicators,
        stock_info: dict
    ) -> FullAnalysisResponse:
        """
        3 Ajanlı mimari:
          Adım 1 → Teknik Analist + Temel Analist paralel çalışır
          Adım 2 → Risk Yöneticisi ikisini birleştirip final karar verir
        """
        tech_prompt = technical_analyst.build_user_prompt(symbol, indicators)
        fund_prompt = fundamental_analyst.build_user_prompt(symbol, indicators, stock_info)

        # Ajan 1 → sıralı çalıştır (ücretsiz katmanda 429 hatası vermemek için)
        tech_result = await self._call_agent(technical_analyst.SYSTEM_PROMPT, tech_prompt)
        await asyncio.sleep(2)  # rate limit için kısa bekleme
        fund_result = await self._call_agent(fundamental_analyst.SYSTEM_PROMPT, fund_prompt)
        await asyncio.sleep(2)

        # Ajan 3: Risk Yöneticisi
        risk_prompt = risk_manager.build_user_prompt(symbol, tech_result, fund_result)
        risk_result = await self._call_agent(risk_manager.SYSTEM_PROMPT, risk_prompt)

        # Risk Yöneticisi'nden eksik alanları akıllıca tamamla
        risk_signal = risk_result.get("signal", "TUT")
        risk_confidence = float(risk_result.get("confidence", 0.5))
        risk_final_decision = risk_result.get("final_decision") or risk_signal
        risk_final_confidence = float(risk_result.get("final_confidence") or risk_confidence)
        risk_summary = (
            risk_result.get("summary")
            or risk_result.get("analysis_text")
            or f"{symbol} analizi tamamlandı. Final karar: {risk_final_decision}."
        )

        return FullAnalysisResponse(
            symbol=symbol,
            timestamp=indicators.timestamp,
            indicators=indicators,
            technical_analysis=AgentAnalysis(
                agent_name="Teknik Analist",
                agent_role=AgentRole.TEKNIK_ANALIST,
                analysis_text=tech_result.get("analysis_text", ""),
                signal=tech_result.get("signal", "TUT"),
                confidence=float(tech_result.get("confidence", 0.5)),
                key_points=tech_result.get("key_points", []),
            ),
            fundamental_analysis=AgentAnalysis(
                agent_name="Temel Analist",
                agent_role=AgentRole.TEMEL_ANALIST,
                analysis_text=fund_result.get("analysis_text", ""),
                signal=fund_result.get("signal", "TUT"),
                confidence=float(fund_result.get("confidence", 0.5)),
                key_points=fund_result.get("key_points", []),
            ),
            risk_assessment=AgentAnalysis(
                agent_name="Risk Yöneticisi",
                agent_role=AgentRole.RISK_YONETICISI,
                analysis_text=risk_result.get("analysis_text", ""),
                signal=risk_signal,
                confidence=risk_confidence,
                key_points=risk_result.get("key_points", []),
            ),
            final_decision=risk_final_decision,
            final_confidence=risk_final_confidence,
            summary=risk_summary,

        )

    async def run_quick_analysis(
        self,
        symbol: str,
        indicators: StockIndicators,
    ) -> QuickAnalysisResponse:
        """Algoritmik hızlı sinyal — API çağrısı yapmaz."""
        rsi      = indicators.rsi_14
        macd     = indicators.macd
        macd_sig = indicators.macd_signal
        price    = indicators.last_price
        sma200   = indicators.sma_200

        bullish_score = 0
        reasons: list[str] = []

        if rsi is not None:
            if rsi < 30:
                reasons.append(f"RSI aşırı satım bölgesinde ({rsi:.1f} < 30)")
                bullish_score += 1
            elif rsi > 70:
                reasons.append(f"RSI aşırı alım bölgesinde ({rsi:.1f} > 70)")
                bullish_score -= 1
            else:
                reasons.append(f"RSI nötr bölgede ({rsi:.1f})")

        macd_text = "MACD verisi yok"
        if macd is not None and macd_sig is not None:
            if macd > macd_sig:
                macd_text = f"MACD pozitif ({macd:.3f} > sinyal {macd_sig:.3f})"
                bullish_score += 1
            else:
                macd_text = f"MACD negatif ({macd:.3f} < sinyal {macd_sig:.3f})"
                bullish_score -= 1

        trend = "YATAY"
        if sma200 is not None:
            if price > sma200:
                trend = "YUKARI"
                reasons.append(f"Fiyat SMA200 üzerinde ({price:.2f} > {sma200:.2f})")
                bullish_score += 1
            else:
                trend = "ASAGI"
                reasons.append(f"Fiyat SMA200 altında ({price:.2f} < {sma200:.2f})")
                bullish_score -= 1

        signal = "AL" if bullish_score >= 2 else ("SAT" if bullish_score <= -2 else "TUT")

        summary = (
            f"{symbol} algoritmik analizi: {', '.join(reasons)}. "
            f"{macd_text}. Genel trend: {trend}."
        )

        return QuickAnalysisResponse(
            symbol=symbol,
            timestamp=indicators.timestamp,
            rsi_14=rsi,
            macd_signal_text=macd_text,
            trend=trend,
            quick_signal=signal,
            summary=summary,
        )