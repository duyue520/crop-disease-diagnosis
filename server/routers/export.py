"""
批量导出路由: Excel / PDF
"""
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

from urllib.parse import quote

from ..database import get_db
from ..models.db_models import User
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/api/export", tags=["导出"])


def generate_excel(user: User, db: Session) -> io.BytesIO:
    """生成诊断记录 Excel 文件"""
    wb = Workbook()
    ws = wb.active
    ws.title = "叶片病害诊断记录"

    # 样式
    header_font = Font(name="Microsoft YaHei", size=12, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="228B22", end_color="228B22", fill_type="solid")
    cell_font = Font(name="Microsoft YaHei", size=10)
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"),
    )

    # 标题
    ws.merge_cells("A1:H1")
    ws["A1"] = f"叶片病害智能诊断记录 —— {user.username}"
    ws["A1"].font = Font(name="Microsoft YaHei", size=16, bold=True, color="228B22")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 35

    # 表头
    headers = ["序号", "诊断日期", "主要病害", "置信度(%)", "是否健康", "严重度", "严重度(%)", "排名第2", "排名第3"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws.row_dimensions[3].height = 25

    # 数据
    records = sorted(user.diagnoses, key=lambda r: r.created_at, reverse=True)
    for i, r in enumerate(records):
        row = i + 4
        vals = [
            i + 1,
            r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
            r.top1_disease,
            r.top1_confidence,
            "健康" if r.is_healthy else "病害",
            r.severity or "",
            r.severity_percent or "",
            f"{r.top2_disease} ({r.top2_confidence}%)" if r.top2_disease else "",
            f"{r.top3_disease} ({r.top3_confidence}%)" if r.top3_disease else "",
        ]
        for col, val in enumerate(vals, 1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.font = cell_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

            # 健康行绿色、病害行浅红
            if r.is_healthy:
                cell.fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
            else:
                cell.fill = PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid")

    # 列宽
    widths = [6, 20, 25, 12, 10, 8, 10, 25, 25]
    for col, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(row=3, column=col).column_letter].width = w

    # 统计行
    stat_row = len(records) + 5
    total = len(records)
    healthy = sum(1 for r in records if r.is_healthy)
    ws.merge_cells(start_row=stat_row, start_column=1, end_row=stat_row, end_column=9)
    stat_cell = ws.cell(row=stat_row, column=1,
                        value=f"共 {total} 次诊断 | 健康 {healthy} 次 | 病害 {total - healthy} 次")
    stat_cell.font = Font(name="Microsoft YaHei", size=12, bold=True, color="333333")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


@router.get("/excel")
def export_excel(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """导出诊断记录为 Excel 文件"""
    if len(user.diagnoses) == 0:
        raise HTTPException(404, "暂无诊断记录")
    buf = generate_excel(user, db)
    filename = f"diagnosis_{user.username}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )


@router.get("/pdf")
def export_pdf(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """导出诊断报告为 PDF"""
    raise HTTPException(501, "PDF 导出功能开发中，请使用 Excel 导出")
