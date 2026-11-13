"""Service for federated moderation report propagation."""

from sqlalchemy.orm import Session
from app.models.moderation_report import ModerationReport


class ModerationReportService:
    def create(
        self, db: Session, reporter_node: str, target_node: str, reason: str, target_user_ref: str | None = None
    ) -> ModerationReport:
        obj = ModerationReport(
            reporter_node=reporter_node, target_node=target_node, reason=reason, target_user_ref=target_user_ref
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_for_node(self, db: Session, node_domain: str):
        return (
            db.query(ModerationReport)
            .filter(ModerationReport.target_node == node_domain)
            .order_by(ModerationReport.id.desc())
            .all()
        )
