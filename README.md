# 🎥 YouTube Video Downloader
*A simple, fast YouTube downloader with a Flask API — download video (MP4) or extract audio (MP3).*  

![GitHub repo size](https://img.shields.io/github/repo-size/zerodbg/YouTube_vedio_downloader?style=for-the-badge&color=red)
![GitHub last commit](https://img.shields.io/github/last-commit/zerodbg/YouTube_vedio_downloader?style=for-the-badge&color=green)
![GitHub issues](https://img.shields.io/github/issues/zerodbg/YouTube_vedio_downloader?style=for-the-badge&color=yellow)
![License](https://img.shields.io/github/license/zerodbg/YouTube_vedio_downloader?style=for-the-badge&color=blue)

---

## 🚀 Overview
**YouTube Video Downloader** provides a tiny Flask API that downloads YouTube videos (MP4) or audio (MP3). Designed for easy integration with frontends or automation scripts. Perfect for demos, local automation, or building a GUI on top.

> ✅ Built with `Flask`, `flask_cors`, and `pytube`  
> ⚠️ Follow copyright rules — only download content you have rights to.

---

## ✨ Features
- Download YouTube videos as **MP4**
- Extract audio as **MP3** (requires FFmpeg for conversion)
- Simple REST `POST /download` endpoint
- Cross-Origin enabled (`flask_cors`) for frontend use
- Lightweight, easy to run locally or deploy

---

## 📦 Quickstart (recommended)
### 1. Clone
```bash
git clone https://github.com/zerodbg/YouTube_vedio_downloader.git
cd YouTube_vedio_downloader
