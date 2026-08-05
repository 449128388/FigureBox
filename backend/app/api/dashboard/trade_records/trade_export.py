"""
trade_export.py - 交易模块-账单导出子路由

功能说明：
- 提供交易账单导出 API 端点（按业务边界拆分自原 trade_records.py）
- 委托给 trade_records_service.bill_export_service，零业务内联
- 支持 xlsx / csv 流式下载

API端点：
- GET /export   导出交易账单（流式响应 StreamingResponse）

依赖：
- fastapi.APIRouter
- fastapi.responses.StreamingResponse
- app.services.dashboard_service.trade_records_service.BillExportService
- app.api.users.get_current_user

创建时间: 2026-08-04（从 trade_records.py 拆分）
作者: FigureBox Team
"""

import io
from typing import Optional
from fastapi import APIRouter, Depends, Request, Response, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.trade_records_service import BillExportService

router = APIRouter()


@router.get("/export")
async def export_trade_bill(
    request: Request,
    response: Response,
    range: str = Query("current", description="导出范围: current-当前月份, all-全部历史"),
    format: str = Query("xlsx", description="文件格式: xlsx-Excel, csv-CSV"),
    year: Optional[int] = Query(None, description="年份（当range=current时必填）"),
    month: Optional[int] = Query(None, description="月份（当range=current时必填）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出交易账单

    支持导出当前月份或全部历史交易记录
    支持Excel(.xlsx)或CSV格式
    """
    user_id = current_user.id

    # 生成文件内容
    file_content = BillExportService.export_bill(
        db=db,
        user_id=user_id,
        export_range=range,
        year=year,
        month=month,
        file_format=format
    )

    # 设置文件名
    if range == "current" and year and month:
        filename = f"交易账单_{year}年{month}月.{format}"
    else:
        filename = f"交易账单_全部历史.{format}"

    # 设置响应头
    media_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if format == "xlsx"
        else "text/csv; charset=utf-8"
    )

    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename.encode('utf-8').decode('latin-1')}"
        }
    )
