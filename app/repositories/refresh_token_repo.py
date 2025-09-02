from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.refresh_token import RefreshToken
from typing import Optional
from datetime import datetime

class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        """Create a new refresh token"""
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        result = await self.session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token == token,
                    RefreshToken.is_revoked == False,
                    RefreshToken.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_refresh_token_by_user(self, user_id: int) -> Optional[RefreshToken]:
        """Get active refresh token for user"""
        result = await self.session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked == False,
                    RefreshToken.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token"""
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        refresh_token = result.scalar_one_or_none()
        
        if refresh_token:
            refresh_token.is_revoked = True
            await self.session.commit()
            return True
        return False

    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revoke all refresh tokens for a user"""
        result = await self.session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked == False
                )
            )
        )
        tokens = result.scalars().all()
        
        count = 0
        for token in tokens:
            token.is_revoked = True
            count += 1
        
        await self.session.commit()
        return count

    async def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from database"""
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow())
        )
        expired_tokens = result.scalars().all()
        
        count = 0
        for token in expired_tokens:
            await self.session.delete(token)
            count += 1
        
        await self.session.commit()
        return count
