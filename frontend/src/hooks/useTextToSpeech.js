import { useState, useEffect, useCallback } from "react";

export function useTextToSpeech() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [hasSupport, setHasSupport] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      setHasSupport(true);
    }
  }, []);

  const stop = useCallback(() => {
    if (hasSupport && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, [hasSupport]);

  const speak = useCallback((text, lang = "en") => {
    if (!hasSupport || !text) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95; // Slightly slower for crisp clarity
    utterance.pitch = 1.0;

    const targetLang = lang === "hi" ? "hi-IN" : "en-IN";
    utterance.lang = targetLang;

    // Try to find a matching voice if available
    const voices = window.speechSynthesis.getVoices();
    const matchedVoice = voices.find(v => v.lang === targetLang || v.lang.startsWith(lang));
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = (e) => {
      console.warn("Speech Synthesis Error:", e);
      setIsSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
  }, [hasSupport]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (hasSupport && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, [hasSupport]);

  return {
    speak,
    stop,
    isSpeaking,
    hasSupport
  };
}
