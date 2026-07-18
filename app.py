"""
PASCO 온도센서 실시간 웹앱 (Streamlit)
========================================
브라우저에서:
  - [센서 연결] 버튼으로 PASCO 무선 온도센서에 연결
  - [측정 시작 / 정지] 로 실시간 수집 제어
  - x축=경과 시간(초), y축=온도(°C) 그래프가 실시간 갱신
  - [CSV 다운로드] 버튼으로 데이터 저장

실행 준비:
  pip install streamlit pasco pandas
실행:
  streamlit run pasco_streamlit_app.py
  → 자동으로 브라우저(localhost:8501)가 열립니다.

중요:
  * 이 앱은 반드시 '블루투스가 되는 PC'에서 로컬로 실행해야 합니다.
    (클라우드 서버에 올리면 교실 센서에 연결할 수 없습니다.)
  * 센서 종류에 따라 측정값 이름이 'Temperature'가 아닐 수 있어
    연결 후 목록을 보고 사이드바에서 바꿀 수 있게 해두었습니다.
"""

import time
from datetime import datetime
from io import StringIO

import pandas as pd
import streamlit as st

# pasco 는 설치되어 있어야 합니다. 없으면 안내 메시지 출력.
try:
    from pasco.pasco_ble_device import PASCOBLEDevice
    PASCO_AVAILABLE = True
except Exception:
    PASCO_AVAILABLE = False


# ----------------------------------------------------------------------
# 페이지 설정
# ----------------------------------------------------------------------
st.set_page_config(page_title="PASCO 온도센서 실시간 측정", page_icon="🌡️")
st.title("🌡️ PASCO 온도센서 실시간 측정")

# ----------------------------------------------------------------------
# 세션 상태 초기화 (앱이 새로고침돼도 값이 유지되도록)
# ----------------------------------------------------------------------
def init_state():
    defaults = {
        "sensor": None,          # 연결된 센서 객체
        "connected": False,      # 연결 여부
        "device_name": "",       # 센서 이름
        "measurements": [],      # 이 센서가 제공하는 측정값 목록
        "collecting": False,     # 측정 중 여부
        "start_time": None,      # 측정 시작 시각
        "times": [],             # 경과 시간(초) 리스트
        "temps": [],             # 온도(°C) 리스트
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ----------------------------------------------------------------------
# 사이드바: 설정 + 연결 제어
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 설정")

    if not PASCO_AVAILABLE:
        st.error("`pasco` 패키지가 없습니다.\n\n터미널에서 실행:\n`pip install pasco`")

    # 측정값 이름: 연결 후 목록이 있으면 선택박스, 없으면 직접 입력
    if st.session_state.measurements:
        measurement_name = st.selectbox(
            "측정값 이름", st.session_state.measurements,
            index=0,
        )
    else:
        measurement_name = st.text_input("측정값 이름", value="Temperature")

    sample_interval = st.slider(
        "측정 간격 (초)", min_value=0.2, max_value=5.0, value=1.0, step=0.2
    )

    st.divider()

    # ---- 연결 / 해제 버튼 ----
    if not st.session_state.connected:
        if st.button("🔌 센서 연결", type="primary", use_container_width=True,
                     disabled=not PASCO_AVAILABLE):
            with st.spinner("주변 PASCO 센서를 검색 중..."):
                try:
                    sensor = PASCOBLEDevice()
                    found = sensor.scan()
                    if not found:
                        st.error("센서를 찾지 못했습니다. 전원과 블루투스를 확인하세요.")
                    else:
                        sensor.connect(found[0])
                        st.session_state.sensor = sensor
                        st.session_state.connected = True
                        st.session_state.device_name = sensor.get_device_name(found[0])
                        try:
                            st.session_state.measurements = sensor.get_measurement_list()
                        except Exception:
                            st.session_state.measurements = []
                        st.rerun()
                except Exception as e:
                    st.error(f"연결 오류: {e}")
    else:
        st.success(f"연결됨: {st.session_state.device_name}")
        if st.button("⛔ 연결 해제", use_container_width=True):
            try:
                st.session_state.sensor.disconnect()
            except Exception:
                pass
            st.session_state.sensor = None
            st.session_state.connected = False
            st.session_state.collecting = False
            st.rerun()


# ----------------------------------------------------------------------
# 측정 제어 버튼 (본문 상단)
# ----------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ 측정 시작", use_container_width=True,
                 disabled=not st.session_state.connected or st.session_state.collecting):
        st.session_state.collecting = True
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()
        st.rerun()

with col2:
    if st.button("⏸️ 정지", use_container_width=True,
                 disabled=not st.session_state.collecting):
        st.session_state.collecting = False
        st.rerun()

with col3:
    if st.button("🗑️ 초기화", use_container_width=True):
        st.session_state.times = []
        st.session_state.temps = []
        st.session_state.start_time = None
        st.session_state.collecting = False
        st.rerun()


# ----------------------------------------------------------------------
# 실시간 측정 + 그래프 (fragment 로 주기적 자동 갱신)
# ----------------------------------------------------------------------
@st.fragment(run_every=sample_interval if st.session_state.collecting else None)
def live_view():
    # 측정 중이면 센서에서 값을 하나 읽어 추가
    if st.session_state.collecting and st.session_state.sensor is not None:
        try:
            value = st.session_state.sensor.read_data(measurement_name)
            if value is not None:
                elapsed = round(time.time() - st.session_state.start_time, 2)
                st.session_state.times.append(elapsed)
                st.session_state.temps.append(float(value))
        except Exception as e:
            st.warning(f"측정 오류: {e}")

    # 현재까지 데이터로 표/그래프/다운로드 구성
    df = pd.DataFrame({
        "경과시간(초)": st.session_state.times,
        "온도(°C)": st.session_state.temps,
    })

    # 상단 지표
    if not df.empty:
        latest = df["온도(°C)"].iloc[-1]
        st.metric("현재 온도", f"{latest:.2f} °C", f"측정 {len(df)}개")

    # 실시간 그래프 (x축 시간, y축 온도)
    if not df.empty:
        st.line_chart(df, x="경과시간(초)", y="온도(°C)", height=360)
    else:
        st.info("아직 데이터가 없습니다. 센서 연결 후 [측정 시작]을 누르세요.")

    # CSV 다운로드
    if not df.empty:
        buf = StringIO()
        df.to_csv(buf, index=False, encoding="utf-8-sig")
        st.download_button(
            "⬇️ CSV 다운로드",
            data=buf.getvalue().encode("utf-8-sig"),
            file_name=f"temperature_{datetime.now():%Y%m%d_%H%M%S}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        with st.expander("데이터 표 보기"):
            st.dataframe(df, use_container_width=True, height=240)


live_view()
