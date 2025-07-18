from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from services.devices_logins import get_all_logs_data
from services.export_data import generate_xlsx

router = APIRouter(prefix="/export")

@router.get("/logs")
def export_data(startDate: str = Query(...), endDate: str = Query(...), local: Optional[str] = Query(None)):
    # Converter as strings ISO para datetime
    start = datetime.fromisoformat(startDate)
    end = datetime.fromisoformat(endDate + "T23:59:59")  # incluir o dia todo

    logs_data = get_all_logs_data(start, end, local)
    file = generate_xlsx(logs_data)
    
    return FileResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
