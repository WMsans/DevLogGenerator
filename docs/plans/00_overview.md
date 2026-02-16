# Local Dev Log Generator — Implementation Plan

**Goal:** Build a CLI tool that turns git history into narrated video dev logs using a local LLM, TTS, and video compositing pipeline.

**Architecture:** A three-phase state machine (Init → Expand → Render) orchestrated by a `typer` CLI. Each phase reads/writes Markdown files as its contract, keeping stages decoupled. Git interaction is handled by `GitPython`, LLM calls go through `ollama`'s REST API, audio through `coqui-tts`, and video assembly through `moviepy` + FFmpeg.

**Tech Stack:** Python 3.10+, typer, questionary, GitPython, ollama (HTTP), coqui-tts, moviepy, FFmpeg
