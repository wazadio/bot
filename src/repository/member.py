from src.db.mssql import Database
from src.models.member import Member, MemberORM

class MemberRepository:
    def __init__(self, db: Database):
        self.db: Database = db

    def get_member_by_id(self, member_id: int) -> Member:
        return self.db.session.query(Member).filter(Member.Id == member_id).first()
    
    def get_members(self, limit: int = 20) -> list[Member]:
        return self.db.session.query(Member).limit(limit).all()
    
    def get_non_members(self, limit: int = 20, offset: int = 0) -> list[Member]:
        non_members = self.db.session.query(MemberORM).filter(MemberORM.IsMembership == False, MemberORM.IsActived == True).order_by(MemberORM.Id).limit(limit).offset(offset).all()
        return [Member.model_validate(m) for m in non_members]
    
    def get_by_phone(self, phone: str) -> Member | None:
        member_orm = self.db.session.query(MemberORM).filter(MemberORM.Phone == phone, MemberORM.IsMembership == True, MemberORM.IsActived == True).order_by(MemberORM.Id.desc()).first()
        if member_orm:
            return Member.model_validate(member_orm)
        return None
    
    def get_member_by_membership_time(self, membership_time: str, limit: int, offset: int) -> list[Member]:
        if limit is not None and offset is not None:
            members = self.db.session.query(MemberORM).filter(MemberORM.MembershipTime <= membership_time, MemberORM.IsActived == True).order_by(MemberORM.Id.asc()).limit(limit).offset(offset).all()
        else:
            members = self.db.session.query(MemberORM).filter(MemberORM.MembershipTime <= membership_time, MemberORM.IsActived == True).all()
        return [Member.model_validate(m) for m in members]
    
    def update_member(self, member: Member) -> None:
        member_orm = self.db.session.query(MemberORM).filter(MemberORM.Id == member.Id).first()
        if member_orm:
            for key, value in member.model_dump().items():
                setattr(member_orm, key, value)
            self.db.session.commit()

    def get_member_by_telegram_id(self, telegram_id: int) -> Member | None:
        member_orm = self.db.session.query(MemberORM).filter(MemberORM.UserTelegramId == telegram_id, MemberORM.IsMembership == True, MemberORM.IsActived == True).first()
        if member_orm:
            return Member.model_validate(member_orm)
        return None