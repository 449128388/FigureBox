"""
板块分析服务模块

功能说明：
- 提供板块涨幅排行分析
- 支持按多个维度（材质/制造商/作品/原画作者）分组计算板块表现
- 支持获取热门板块及其代表手办
- 支持基于用户持仓的个性化板块排名

板块定义：
- 按指定维度（material/manufacturer/work/original_art）进行分组
- 计算板块内手办的加权平均涨跌幅
- 展示板块代表手办

创建时间: 2026-05-18
作者: FigureBox Team
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.figure import Figure
from app.models.hpi import HPIComponent


# 板块维度配置：code -> (数据库列名, 中文显示名, 默认兜底名)
DIMENSION_CONFIG: Dict[str, tuple] = {
    "work": (Figure.work, "作品", "其他"),
    "manufacturer": (Figure.manufacturer, "制造商", "未注明"),
    "material": (Figure.material, "材质", "未注明"),
    "original_art": (Figure.original_art, "原画作者", "未注明"),
}

# 支持「多值拆包」的维度（字段值以"、"分隔时需均分权重与体数）
SPLIT_DIMENSIONS = {"manufacturer", "material"}


class SectorService:
    """板块分析服务类"""

    @classmethod
    def get_supported_dimensions(cls) -> List[Dict[str, str]]:
        """返回支持的板块维度列表（含 code 与中文名）"""
        return [
            {"code": code, "name": name}
            for code, (_, name, _) in DIMENSION_CONFIG.items()
        ]

    @classmethod
    def get_sector_performance(cls, db: Session) -> List[Dict[str, Any]]:
        """
        获取板块涨幅排行

        按IP系列(work)分组，计算每个板块的平均涨跌幅

        Args:
            db: 数据库会话

        Returns:
            List[Dict]: 板块列表，包含名称、涨幅、代表手办
        """
        all_figures = db.query(Figure).filter(Figure.is_active == 1).all()

        if not all_figures:
            return []

        # 按作品分组
        work_groups = {}
        for fig in all_figures:
            work = fig.work or "其他"
            if work not in work_groups:
                work_groups[work] = []
            work_groups[work].append(fig)

        sectors = []
        for work, work_figures in work_groups.items():
            if len(work_figures) > 0:
                # 计算板块平均涨跌幅
                valid_figures = [f for f in work_figures if f.price and f.price > 0]
                if valid_figures:
                    avg_change = sum(
                        ((f.market_price or f.price or 0) - f.price) / f.price * 100
                        for f in valid_figures
                    ) / len(valid_figures)

                    # 取前3个手办作为代表
                    sector_figures = [f.name for f in work_figures[:3]]

                    sectors.append({
                        "name": work,
                        "change": round(avg_change, 1),
                        "stocks": "、".join(sector_figures) if sector_figures else "暂无"
                    })

        # 按涨幅排序，取前5个板块
        sectors.sort(key=lambda x: abs(x["change"]), reverse=True)
        return sectors[:5]

    @classmethod
    def get_user_sector_ranking(
        cls,
        db: Session,
        user_id: int,
        dimension: str = "work",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        获取用户持仓板块涨幅排行

        基于用户投资复盘（HPI 成分股）按指定维度聚合：
        - 板块收益率 = 板块内手办加权平均收益率
        - 权重 = 该手办历史交易金额 / 板块内手办历史总交易金额
        - 板块体数 = 板块内手办体数（quantity 之和）
        - 代表手办 = 板块内权重 TOP3 的手办名称

        Args:
            db: 数据库会话
            user_id: 用户ID
            dimension: 维度 code，可选值 work / manufacturer / material / original_art
            limit: 返回板块数量上限

        Returns:
            Dict:
                - sectors: List，按 |板块收益率| 降序，最多 limit 个
                    - dimension / dimension_name / name / change / stocks
                    - body_count: 体数（quantity 之和）
                    - figure_count: 唯一手办数（兼容旧字段）
                - total: 全量板块数（不受 limit 限制）
        """
        # 取用户最新的 HPI 成分股（关联 Figure 获取维度字段）
        latest_date_subq = (
            db.query(func.max(HPIComponent.record_date))
            .filter(HPIComponent.user_id == user_id)
            .scalar_subquery()
        )
        rows = (
            db.query(
                HPIComponent,
                Figure.name.label("figure_name"),
                Figure.work.label("work"),
                Figure.manufacturer.label("manufacturer"),
                Figure.material.label("material"),
                Figure.original_art.label("original_art"),
            )
            .outerjoin(Figure, HPIComponent.figure_id == Figure.id)
            .filter(
                HPIComponent.user_id == user_id,
                HPIComponent.record_date == latest_date_subq,
            )
            .all()
        )

        # 取维度配置，兜底为 work
        if dimension not in DIMENSION_CONFIG:
            dimension = "work"
        dim_fallback = DIMENSION_CONFIG[dimension][2]
        dim_label = DIMENSION_CONFIG[dimension][1]

        if not rows:
            return {"sectors": [], "total": 0}

        # 按指定维度分组
        groups: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            # SQLAlchemy 2.x 的 Row 对象支持下标访问，row[0] 即 HPIComponent 实例
            comp = row[0]
            figure_name = getattr(row, "figure_name", "") or ""
            # 通过 labeled 列名取维度字段值
            dim_value = getattr(row, dimension, None)
            raw_sector_name = (str(dim_value).strip() if dim_value else "") or dim_fallback

            # 处理多值（manufacturer / material 维度以"、"分隔），拆分后均分权重和体数
            if dimension in SPLIT_DIMENSIONS and "、" in raw_sector_name:
                sector_names = [s.strip() for s in raw_sector_name.split("、") if s.strip()]
            else:
                sector_names = [raw_sector_name]

            weight = float(getattr(comp, "weight", 0) or 0)
            return_pct = float(getattr(comp, "return_pct", 0) or 0)
            quantity = int(getattr(comp, "quantity", 0) or 0)

            # 多厂商时均分权重和体数
            split_weight = weight / len(sector_names) if len(sector_names) > 1 else weight
            split_quantity = quantity / len(sector_names) if len(sector_names) > 1 else quantity

            for sector_name in sector_names:
                bucket = groups.setdefault(sector_name, {
                    "weighted_return_sum": 0.0,
                    "weight_sum": 0.0,
                    "figures": {},
                    "body_count": 0,
                    "figure_count": 0,
                })
                bucket["weighted_return_sum"] += split_weight * return_pct
                bucket["weight_sum"] += split_weight
                bucket["body_count"] += split_quantity
                existing = bucket["figures"].get(comp.figure_id)
                if existing:
                    existing["weight"] += split_weight
                else:
                    bucket["figure_count"] += 1
                    bucket["figures"][comp.figure_id] = {
                        "name": figure_name or f"手办 #{comp.figure_id}",
                        "weight": split_weight,
                        "return_pct": return_pct,
                    }

        sectors: List[Dict[str, Any]] = []
        for name, data in groups.items():
            if data["weight_sum"] <= 0:
                continue
            sector_change = data["weighted_return_sum"] / data["weight_sum"]
            # 代表手办 = 板块内权重 TOP3
            top_figures = sorted(
                data["figures"].values(), key=lambda x: x["weight"], reverse=True
            )[:3]
            stocks = "、".join(f["name"] for f in top_figures) if top_figures else "暂无"
            sectors.append({
                "dimension": dimension,
                "dimension_name": dim_label,
                "name": name,
                "change": round(sector_change, 1),
                "stocks": stocks,
                # 体数 = 板块内全部 in-cabinet + sold 行的 quantity 之和
                # 浮点除法（如 3/2=1.4999999999999998）统一 round 1 位避免前端展示长尾小数
                "body_count": round(data["body_count"], 1),
                # 唯一手办数（兼容旧字段）
                "figure_count": data["figure_count"],
            })

        # 板块涨幅排行排序规则：
        # 1. 当涨幅>0 的板块数 > limit：仅展示涨幅>0，按涨幅从高到低排序
        # 2. 当 0 < 涨幅>0 的板块数 <= limit：先展示所有涨幅>0（按涨幅降序），再展示跌幅<0（按跌幅从小到大，即 -1 > -5 > -10）
        # 3. 当涨幅>0 的板块数 == 0：仅展示跌幅<0，按跌幅从小到大排序
        positive_sectors = [s for s in sectors if s["change"] > 0]
        negative_sectors = [s for s in sectors if s["change"] < 0]
        positive_sectors.sort(key=lambda x: x["change"], reverse=True)
        negative_sectors.sort(key=lambda x: x["change"], reverse=True)
        ordered_sectors = positive_sectors + negative_sectors

        total = len(sectors)  # 全量板块数（不受 limit 限制）
        return {
            "sectors": ordered_sectors[:limit],
            "total": total,
        }

    @classmethod
    def get_sector_figures(
        cls,
        db: Session,
        user_id: int,
        dimension: str,
        sector_name: str,
    ) -> Dict[str, Any]:
        """
        获取指定板块下用户持仓手办明细（用于二级展开展示）

        返回该板块下所有手办：
        - name / scale / manufacturer / meta 等基础信息
        - buy_price = first_buy_price（人民币）
        - current_price = current_price（人民币）
        - change_pct = return_pct
        - status = holding / sold
        - thumb = 第一张图（无图用兜底 emoji）
        汇总信息：
        - total_buy / total_current
        - change_pct（板块收益率）
        - holding_count / sold_count

        Args:
            db: 数据库会话
            user_id: 用户ID
            dimension: 维度 code
            sector_name: 板块名（与 get_user_sector_ranking 返回的 name 一致）

        Returns:
            Dict: 板块详情
        """
        # 维度兜底
        if dimension not in DIMENSION_CONFIG:
            dimension = "work"
        dim_fallback = DIMENSION_CONFIG[dimension][2]
        dim_label = DIMENSION_CONFIG[dimension][1]

        # 取用户最新 HPI 成分股 + Figure 详情
        latest_date_subq = (
            db.query(func.max(HPIComponent.record_date))
            .filter(HPIComponent.user_id == user_id)
            .scalar_subquery()
        )
        rows = (
            db.query(
                HPIComponent,
                Figure.id.label("fig_id"),
                Figure.name.label("figure_name"),
                Figure.scale.label("scale"),
                Figure.manufacturer.label("manufacturer"),
                Figure.images.label("images"),
                Figure.work.label("work"),
                Figure.manufacturer.label("manufacturer_col"),
                Figure.material.label("material"),
                Figure.original_art.label("original_art"),
            )
            .outerjoin(Figure, HPIComponent.figure_id == Figure.id)
            .filter(
                HPIComponent.user_id == user_id,
                HPIComponent.record_date == latest_date_subq,
            )
            .all()
        )

        # 过滤出指定板块
        matched = []
        for row in rows:
            comp = row[0]
            dim_value = getattr(row, dimension, None)
            raw_value = (str(dim_value).strip() if dim_value else "") or dim_fallback
            # SPLIT_DIMENSIONS 维度支持拆包匹配：value="进口PU、高级树脂、金属铭牌", sector_name="进口PU" → 匹配
            if dimension in SPLIT_DIMENSIONS and "、" in raw_value:
                names = [n.strip() for n in raw_value.split("、") if n.strip()]
                if sector_name in names:
                    matched.append((row, comp))
            elif raw_value == sector_name:
                matched.append((row, comp))

        figures: List[Dict[str, Any]] = []
        total_buy = 0.0
        total_current = 0.0
        total_weighted_return = 0.0
        total_weight = 0.0
        holding_count = 0
        sold_count = 0

        for row, comp in matched:
            figure_name = getattr(row, "figure_name", "") or f"手办 #{comp.figure_id}"
            scale = getattr(row, "scale", "") or ""
            manufacturer = getattr(row, "manufacturer", "") or ""
            images_raw = getattr(row, "images", None) or []
            first_image = ""
            if isinstance(images_raw, list) and images_raw:
                first_image = str(images_raw[0])
            elif isinstance(images_raw, str) and images_raw:
                # 兼容 JSON 字符串
                first_image = images_raw.split(",")[0].strip().strip('"').strip("'")

            buy_price = round(float(getattr(comp, "first_buy_price", 0) or 0), 2)
            current_price = round(float(getattr(comp, "current_price", 0) or 0), 2)
            sell_price_raw = getattr(comp, "sell_price", None)
            sell_price_val = round(float(sell_price_raw), 2) if sell_price_raw else None
            return_pct = round(float(getattr(comp, "return_pct", 0) or 0), 1)
            is_sold = bool(getattr(comp, "is_sold", 0))
            quantity = int(getattr(comp, "quantity", 1) or 1)
            weight = float(getattr(comp, "weight", 0) or 0)

            # meta 文本：1/7比例·ALTER
            meta_parts = []
            if scale:
                meta_parts.append(scale)
            if manufacturer:
                meta_parts.append(manufacturer)
            meta = " · ".join(meta_parts)

            figures.append({
                "figure_id": comp.figure_id,
                "name": figure_name,
                "meta": meta,
                "thumb": first_image,
                "buy_price": buy_price,
                "current_price": current_price,
                "change_pct": return_pct,
                "status": "sold" if is_sold else "holding",
                "quantity": quantity,
                "sell_price": sell_price_val,  # 已出价（在柜行为 null）
            })

            total_buy += buy_price * quantity
            total_current += current_price * quantity
            total_weighted_return += return_pct * weight
            total_weight += weight
            if is_sold:
                sold_count += quantity
            else:
                holding_count += quantity

        # 按 |涨跌幅| 降序展示
        figures.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

        # 板块收益率（板块内加权平均）
        sector_change = round(
            total_weighted_return / total_weight, 1
        ) if total_weight > 0 else 0.0

        return {
            "dimension": dimension,
            "dimension_name": dim_label,
            "name": sector_name,
            "change": sector_change,
            "figures": figures,
            "summary": {
                "total_buy": round(total_buy, 2),
                "total_current": round(total_current, 2),
                "change_pct": sector_change,
                "holding_count": holding_count,
                "sold_count": sold_count,
                "body_count": holding_count + sold_count,
                "figure_count": len(figures),
            },
        }
