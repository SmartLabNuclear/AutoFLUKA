#!/usr/bin/env python3
"""
Ollama model advisor, shared across AutoSAM, RADIANT-LLM, and AutoFLUKA --
the three apps that share the same Ollama tool-calling architecture
(utils/ollama_local.py's check_ollama_tool_support()). A model confirmed
here via any one of them genuinely carries over to the others, since the
confirmation is about the model + Ollama's OpenAI-compat API, not about
which app happened to run the test.

Detects this machine's GPU/VRAM (or falls back to total RAM for CPU-only
setups), checks what Ollama models are already installed, and recommends
the biggest model confirmed to run on hardware at or below this machine's
level -- not just whatever happens to match its own VRAM bracket -- while
distinguishing models this project has actually confirmed work with
tool-calling from untested suggestions.

Deliberately dependency-free (standard library only): meant to be run
right after cloning the repo, before any `pip install`. Never installs
anything itself -- it only prints `ollama pull` commands for you to run.

Usage:
    python recommend_ollama_model.py
"""

from __future__ import annotations

import ctypes
import json
import platform
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

TIERS_FILE = Path(__file__).parent / "ollama_model_tiers.json"
OLLAMA_BASE_URL_DEFAULT = "http://localhost:11434"


def load_tiers() -> dict:
    with open(TIERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_nvidia_gpu() -> Optional[tuple[str, float]]:
    """Return (gpu_name, vram_gb) via nvidia-smi, or None if unavailable."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        line = result.stdout.strip().splitlines()[0]
        name, vram_mb = [p.strip() for p in line.split(",")]
        return name, round(float(vram_mb) / 1024, 1)
    except Exception:
        return None


def detect_total_ram_gb() -> Optional[float]:
    """Cross-platform total system RAM, stdlib only."""
    system = platform.system()
    try:
        if system == "Windows":
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))  # type: ignore[attr-defined]
            return round(stat.ullTotalPhys / (1024 ** 3), 1)

        if system == "Darwin":
            out = subprocess.run(
                ["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, timeout=5, check=True
            )
            return round(int(out.stdout.strip()) / (1024 ** 3), 1)

        # Linux and other POSIX
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return round(kb / (1024 ** 2), 1)
    except Exception:
        return None
    return None


def is_apple_silicon() -> bool:
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def check_ollama_reachable(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=5):
            return True
    except Exception:
        return False


def list_installed_ollama_models(base_url: str) -> Optional[list[str]]:
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return None


def gather_eligible_models(tiers: dict, rounded_gb: int, key: str) -> list[dict]:
    """
    Every model from any tier whose min_vram_gb <= rounded_gb.

    A model confirmed to work on LESS VRAM than this machine has is assumed
    to also work here -- same weights, same or less CPU/GPU offload needed --
    so it stays eligible for recommendation on stronger hardware instead of
    being silently capped at whatever this machine's own tier happens to list.
    Rounding (not the raw float) absorbs nvidia-smi reporting jitter between
    otherwise-identical GPU classes (e.g. a "12GB" card reporting 11.9 GB).
    """
    eligible: list[dict] = []
    for tier in tiers["vram_tiers"]:
        if tier["min_vram_gb"] <= rounded_gb:
            eligible.extend(tier.get(key, []))
    return eligible


def best_model(models: list[dict]) -> Optional[dict]:
    if not models:
        return None
    return max(models, key=lambda m: m.get("param_billions", 0))


def print_install_commands(m: dict) -> None:
    if m.get("pullable", True):
        print(f"    ollama pull {m['model']}")
        return
    recipe = m.get("build_recipe")
    if not recipe:
        print(f"    # {m['model']} is not directly pullable, and no build recipe is on file for it.")
        return
    print(f"    # {m['model']} is a custom local build (not a registry tag) -- build it from {m.get('base_model', 'its base model')}:")
    for cmd in recipe["commands"]:
        print(f"    {cmd}")


def print_gpu_recommendation(tiers: dict, vram_gb: float, installed: Optional[list[str]]) -> None:
    rounded_gb = round(vram_gb)
    installed_set = set(installed or [])

    eligible_confirmed = gather_eligible_models(tiers, rounded_gb, "confirmed_models")
    if not eligible_confirmed:
        print(f"No tier on file yet for {vram_gb} GB VRAM (below the lowest tier this project has tested).")
        print("This hardware hasn't been characterized by this project yet -- consider reporting")
        print("back what you find, so it can be added to ollama_model_tiers.json.")
        return

    best = best_model(eligible_confirmed)
    others = sorted(
        (m for m in eligible_confirmed if m["model"] != best["model"]),
        key=lambda m: -m.get("param_billions", 0),
    )
    installed_others = {m["model"] for m in others if m["model"] in installed_set}

    print(f"Your hardware: ~{rounded_gb} GB VRAM (detected {vram_gb} GB)")
    print(f"Best confirmed model your hardware can run: {best['model']} ({best.get('param_billions', '?')}B params)")
    if best.get("notes"):
        print(f"  {best['notes']}")
    for hw in best.get("confirmed_hardware", []):
        print(f"  confirmed on: {hw['hardware']}, {hw['date']}")
        if hw.get("notes"):
            print(f"    {hw['notes']}")
    print()

    if best["model"] in installed_set:
        print("  You already have this installed. No action needed.")
    else:
        if installed_others:
            print(f"  You currently have {', '.join(sorted(installed_others))} installed -- that still works, "
                  f"but {best['model']} is confirmed on hardware at or below yours and has more capacity.")
            print()
        print("  To install:")
        print_install_commands(best)

    if others:
        print()
        print("  Other confirmed options for your hardware (smaller/lighter):")
        for m in others:
            tag = " (installed)" if m["model"] in installed_set else ""
            print(f"    - {m['model']} ({m.get('param_billions', '?')}B){tag}")

    eligible_suggested = [
        m for m in gather_eligible_models(tiers, rounded_gb, "suggested_models")
        if m["model"] not in {c["model"] for c in eligible_confirmed}
    ]
    if eligible_suggested:
        print()
        print("  Untested but worth trying (not independently confirmed on hardware like yours):")
        for m in sorted(eligible_suggested, key=lambda m: -m.get("param_billions", 0)):
            print(f"    - {m['model']}")
            print(f"      {m['reason']}")
        print()
        print("  To try one of these instead:")
        for m in eligible_suggested:
            print_install_commands(m)


def print_cpu_fallback(tiers: dict, installed: Optional[list[str]]) -> None:
    fallback = tiers["cpu_only_fallback"]
    print("No usable GPU detected (or VRAM too low to be useful) -- falling back to CPU-only suggestions.")
    print("These will be slow. None of these are yet confirmed for tool-calling in this project:")
    for m in fallback["suggested_models"]:
        print(f"    - {m['model']}")
        print(f"      {m['reason']}")
    print()
    print("To try one:")
    for m in fallback["suggested_models"]:
        print(f"    ollama pull {m['model']}")


def main() -> int:
    print("=== Ollama Model Advisor (AutoSAM / RADIANT-LLM / AutoFLUKA) ===\n")

    tiers = load_tiers()
    if tiers.get("last_reviewed"):
        print(f"(Model catalog last reviewed: {tiers['last_reviewed']} -- newer Ollama releases may exist but aren't cataloged here yet.)\n")

    print("Detecting hardware...")
    gpu = detect_nvidia_gpu()
    ram_gb = detect_total_ram_gb()

    if gpu:
        name, vram_gb = gpu
        print(f"  GPU: {name} ({vram_gb} GB VRAM)")
        if ram_gb:
            print(f"  System RAM: {ram_gb} GB")
    elif is_apple_silicon():
        print(f"  Apple Silicon detected (unified memory): {ram_gb} GB total")
    elif ram_gb:
        print(f"  No NVIDIA GPU detected. System RAM: {ram_gb} GB")
    else:
        print("  Could not detect GPU or RAM on this system.")

    print("\nChecking Ollama...")
    import os

    base_url = os.environ.get("OLLAMA_BASE_URL", OLLAMA_BASE_URL_DEFAULT).rstrip("/")
    if not check_ollama_reachable(base_url):
        print(f"  Ollama not reachable at {base_url}.")
        print("  Install it first: https://ollama.com, then re-run this script.")
        return 1

    installed = list_installed_ollama_models(base_url)
    print(f"  Ollama is running at {base_url}")
    if installed:
        print("  Installed models:")
        for m in installed:
            print(f"    - {m}")
    else:
        print("  No models installed yet.")

    print()

    if gpu:
        _, vram_gb = gpu
        print_gpu_recommendation(tiers, vram_gb, installed)
    else:
        print_cpu_fallback(tiers, installed)

    return 0


if __name__ == "__main__":
    sys.exit(main())
