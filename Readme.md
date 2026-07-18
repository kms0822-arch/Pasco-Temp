# 🌡️ PASCO 온도센서 실시간 측정 웹앱

PASCO 무선 온도센서(BLE)에 연결해 **실시간으로 온도를 수집**하고,
**시간-온도 그래프**를 그리며, **CSV로 내려받을 수 있는** Streamlit 웹앱입니다.
중·고등학교 과학 실험 수업용으로 만들었습니다.

## ✨ 기능

- PASCO 무선 센서 자동 검색 및 연결
- 실시간 온도 측정 (측정 간격 0.2~5초 조절)
- x축 = 경과 시간(초), y축 = 온도(°C) 실시간 그래프
- 측정 데이터 CSV 다운로드 (엑셀 한글 호환)
- 측정 시작 / 정지 / 초기화 제어

## ⚠️ 꼭 읽어주세요 — 로컬 실행 전용

이 앱은 블루투스로 센서에 연결하기 때문에 **블루투스가 되는 PC에서 직접(로컬) 실행**해야 합니다.
**Streamlit Cloud 등 온라인 서버에 배포하면 센서에 연결되지 않습니다**(서버에는 블루투스가 없습니다).
GitHub은 코드 공유·백업 용도로만 사용하세요.

지원 환경: Windows / macOS / Chromebook 등 **블루투스 내장 PC** + Python 3.8 이상

## 🚀 설치 및 실행

```bash
# 1) 저장소 내려받기
git clone https://github.com/<사용자명>/pasco-temperature-app.git
cd pasco-temperature-app

# 2) 필요한 패키지 설치
pip install -r requirements.txt

# 3) 실행
streamlit run streamlit_app.py
```

실행하면 브라우저(`http://localhost:8501`)가 자동으로 열립니다.

## 📖 사용법

1. 센서 전원을 켠다 (LED 깜빡임 = 연결 대기)
2. 사이드바에서 **[🔌 센서 연결]** 클릭
3. 연결되면 측정값 이름이 목록으로 표시됨 → 온도 측정값 선택
4. **[▶️ 측정 시작]** → 실시간 그래프 갱신 시작
5. **[⬇️ CSV 다운로드]** 로 데이터 저장

> 💡 같은 와이파이 네트워크라면 학생 기기 브라우저에서
> `http://<선생님PC의 IP>:8501` 로 접속해 그래프를 함께 볼 수 있습니다.

## 🔧 문제 해결

- **센서를 못 찾을 때**: 센서 전원과 PC 블루투스가 켜져 있는지 확인
- **측정값 이름이 다를 때**: 연결 후 사이드바 목록에서 선택 (센서 종류마다 다름)
- **`pasco` 설치 오류**: `pip install pasco` 를 단독으로 다시 실행

## 📦 사용 기술

- [Streamlit](https://streamlit.io/) — 웹 UI
- [PASCO Python Library](https://github.com/PASCOscientific/pasco_python) — 센서 연결
- pandas — 데이터 처리 / CSV
