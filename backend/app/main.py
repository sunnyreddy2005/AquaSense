from __future__ import annotations

import io
import json
import os
import uuid
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.analytics_agent import AnalyticsAgent
from app.agents.anomaly_agent import AnomalyAgent
from app.agents.data_agent import DataAgent


DATA_DIR = Path(os.getenv("AQUASENSE_DATA_DIR", Path(__file__).resolve().parents[2] / ".data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "state.json"

app = FastAPI(title="AquaSense API", version="1.0.0")
app.add_middleware(
	CORSMiddleware,
	allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

data_agent = DataAgent()
analytics_agent = AnalyticsAgent()
anomaly_agent = AnomalyAgent()
datasets: dict[str, dict[str, Any]] = {}
settings: dict[str, Any] = {
	"theme": "light",
	"date_format": "yyyy-MM-dd",
	"default_date_range": 30,
	"forecast_horizon": 7,
	"anomaly_sensitivity": 3.0,
}


class ForecastRequest(BaseModel):
	horizon: int = Field(default=7, ge=1, le=90)
	frequency: str = Field(default="D", pattern="^(D|W|ME)$")


class QuestionRequest(BaseModel):
	question: str = Field(min_length=1, max_length=1000)


class SettingsRequest(BaseModel):
	theme: str | None = None
	date_format: str | None = None
	default_date_range: int | None = Field(default=None, ge=1, le=3650)
	forecast_horizon: int | None = Field(default=None, ge=1, le=90)
	anomaly_sensitivity: float | None = Field(default=None, ge=1, le=6)


def _save_state() -> None:
	STATE_FILE.write_text(json.dumps({"datasets": datasets, "settings": settings}, default=str), encoding="utf-8")


def _load_state() -> None:
	if not STATE_FILE.exists():
		return
	try:
		state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
		datasets.update(state.get("datasets", {}))
		settings.update(state.get("settings", {}))
	except (OSError, json.JSONDecodeError):
		return


def _dataset() -> tuple[str, dict[str, Any], pd.DataFrame]:
	if not datasets:
		raise HTTPException(status_code=404, detail="No dataset available. Upload a CSV first.")
	dataset_id = next(reversed(datasets))
	record = datasets[dataset_id]
	path = Path(record["processed_path"])
	if not path.exists():
		raise HTTPException(status_code=404, detail="The stored dataset is unavailable.")
	return dataset_id, record, pd.read_csv(path)


def _json_safe(value: Any) -> Any:
	if isinstance(value, list):
		return [_json_safe(item) for item in value]
	if isinstance(value, dict):
		return {key: _json_safe(item) for key, item in value.items()}
	if isinstance(value, (np.integer, np.floating)):
		return value.item()
	if isinstance(value, (pd.Timestamp, np.datetime64)):
		return str(value)
	if pd.isna(value):
		return None
	return value


def _profile_response(record: dict[str, Any]) -> dict[str, Any]:
	return {key: _json_safe(value) for key, value in record["profile"].items()}


def _require_columns(record: dict[str, Any]) -> tuple[str, str]:
	timestamp = record["profile"].get("timestamp_column")
	consumption = record["profile"].get("consumption_column")
	if not timestamp or not consumption:
		raise HTTPException(status_code=422, detail="The CSV must contain a date/time column and a water consumption column.")
	return timestamp, consumption


_load_state()


@app.get("/api/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)) -> dict[str, Any]:
	if not file.filename or Path(file.filename).suffix.lower() != ".csv":
		raise HTTPException(status_code=415, detail="Only CSV files are supported currently.")
	content = await file.read()
	if not content:
		raise HTTPException(status_code=400, detail="The uploaded file is empty.")
	if len(content) > 50 * 1024 * 1024:
		raise HTTPException(status_code=413, detail="The file must be smaller than 50 MB.")
	try:
		raw_df = pd.read_csv(io.BytesIO(content))
	except Exception as exc:
		raise HTTPException(status_code=422, detail=f"Could not parse CSV: {exc}") from exc
	if raw_df.empty:
		raise HTTPException(status_code=422, detail="The CSV contains no data rows.")

	dataset_id = str(uuid.uuid4())
	original_path = DATA_DIR / f"{dataset_id}-original.csv"
	processed_path = DATA_DIR / f"{dataset_id}-processed.csv"
	original_path.write_bytes(content)
	try:
		processed_df, profile, cleaning = data_agent.process_dataset(str(original_path))
	except RuntimeError as exc:
		original_path.unlink(missing_ok=True)
		raise HTTPException(status_code=422, detail=str(exc)) from exc
	if not profile.get("timestamp_column") or not profile.get("consumption_column"):
		original_path.unlink(missing_ok=True)
		raise HTTPException(status_code=422, detail="Required date/time and consumption columns were not detected.")

	processed_df.to_csv(processed_path, index=False)
	datasets[dataset_id] = {
		"id": dataset_id,
		"filename": file.filename,
		"processed_path": str(processed_path),
		"original_path": str(original_path),
		"created_at": pd.Timestamp.utcnow().isoformat(),
		"profile": profile,
		"cleaning": cleaning,
	}
	_save_state()
	record = datasets[dataset_id]
	return {"dataset": record | {"profile": _profile_response(record)}}


@app.get("/api/data")
def get_data(limit: int = 100, offset: int = 0) -> dict[str, Any]:
	_, record, df = _dataset()
	rows = df.iloc[offset : offset + min(limit, 1000)].replace({np.nan: None}).to_dict(orient="records")
	return {"dataset": record | {"profile": _profile_response(record)}, "rows": rows}


@app.get("/api/analytics")
def get_analytics() -> dict[str, Any]:
	_, record, df = _dataset()
	timestamp, consumption = _require_columns(record)
	overview = analytics_agent.generate_overview(df, timestamp, consumption)
	return {
		"profile": _profile_response(record),
		"overview": overview,
		"daily": analytics_agent.get_time_series(df, timestamp, consumption, "D"),
		"weekly": analytics_agent.get_time_series(df, timestamp, consumption, "W"),
		"monthly": analytics_agent.get_time_series(df, timestamp, consumption, "ME"),
		"hourly": analytics_agent.get_hourly_profile(df, timestamp, consumption),
	}


@app.get("/api/anomalies")
def get_anomalies() -> dict[str, Any]:
	_, record, df = _dataset()
	timestamp, consumption = _require_columns(record)
	return anomaly_agent.detect_anomalies(df, timestamp, consumption)


@app.post("/api/forecast")
def get_forecast(request: ForecastRequest) -> dict[str, Any]:
	_, record, df = _dataset()
	timestamp, consumption = _require_columns(record)
	series = df[[timestamp, consumption]].copy()
	series[timestamp] = pd.to_datetime(series[timestamp], errors="coerce")
	series[consumption] = pd.to_numeric(series[consumption], errors="coerce")
	series = series.dropna().set_index(timestamp)[consumption].resample(request.frequency).sum()
	if len(series) < 3:
		raise HTTPException(status_code=422, detail="Insufficient historical data to generate a reliable forecast.")
	window = min(7, len(series))
	recent = float(series.tail(window).mean())
	prior = float(series.iloc[-2 * window : -window].mean()) if len(series) >= window * 2 else recent
	slope = (recent - prior) / max(window, 1)
	predictions = []
	for step in range(1, request.horizon + 1):
		value = max(0.0, recent + slope * step)
		date = series.index[-1] + (pd.Timedelta(days=step) if request.frequency == "D" else pd.Timedelta(weeks=step))
		predictions.append({"timestamp": str(date), "forecast": round(value, 2), "lower": round(max(0, value * 0.85), 2), "upper": round(value * 1.15, 2)})
	historical = [{"timestamp": str(index), "consumption": round(float(value), 2)} for index, value in series.tail(90).items()]
	return {"historical": historical, "forecast": predictions, "trend": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"}


@app.post("/api/ai/analyze")
def analyze(request: QuestionRequest) -> dict[str, str]:
	_, record, df = _dataset()
	timestamp, consumption = _require_columns(record)
	values = pd.to_numeric(df[consumption], errors="coerce").dropna()
	question = request.question.lower()
	if "highest" in question or "peak" in question:
		row = df.loc[values.idxmax()]
		answer = f"The highest recorded consumption was {float(row[consumption]):,.2f} at {row[timestamp]} based on {len(values):,} valid observations."
	elif "lowest" in question or "minimum" in question:
		row = df.loc[values.idxmin()]
		answer = f"The lowest recorded consumption was {float(row[consumption]):,.2f} at {row[timestamp]} based on the uploaded dataset."
	elif "average" in question or "mean" in question:
		answer = f"The average consumption is {float(values.mean()):,.2f} across {len(values):,} valid observations."
	elif "recommend" in question or "reduce" in question:
		anomalies = anomaly_agent.detect_anomalies(df, timestamp, consumption)["total_anomalies_detected"]
		answer = f"The dataset contains {anomalies} detected unusual observations. Review those timestamps and compare their locations or categories before changing usage policies; the uploaded data does not establish a cause by itself."
	else:
		answer = f"The uploaded dataset contains {len(df):,} rows. Consumption totals {float(values.sum()):,.2f}, with an average of {float(values.mean()):,.2f}. Ask about peaks, averages, anomalies, or recommendations for a more specific evidence-based result."
	return {"answer": answer}


@app.get("/api/reports")
def report() -> dict[str, Any]:
	return {"analytics": get_analytics(), "anomalies": get_anomalies(), "generated_at": pd.Timestamp.utcnow().isoformat()}


@app.get("/api/reports.csv")
def report_csv() -> StreamingResponse:
	_, record, df = _dataset()
	timestamp, consumption = _require_columns(record)
	output = io.StringIO()
	df[[timestamp, consumption]].to_csv(output, index=False)
	return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=aquasense-report.csv"})


@app.get("/api/settings")
def get_settings() -> dict[str, Any]:
	return settings


@app.put("/api/settings")
def update_settings(request: SettingsRequest) -> dict[str, Any]:
	settings.update({key: value for key, value in request.model_dump().items() if value is not None})
	_save_state()
	return settings
