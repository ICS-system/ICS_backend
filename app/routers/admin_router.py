from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user, require_admin
from app.models.user_model import User

router = APIRouter(prefix="/management", tags=["Admin"], redirect_slashes=False)

# ========== 채널 관리 API ==========
@router.get("/channels", dependencies=[Depends(require_admin)])
async def get_channel_assignments(
    current_user: User = Depends(get_current_user)
):
    """채널번호 할당 현황 조회"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    # 채널번호 1-16 할당 현황 (프론트엔드 요구사항에 맞게)
    channels = []
    
    # 채널 1-15 (일반 사용자 채널)
    for channel_num in range(1, 16):
        user = await User.filter(channel_number=channel_num).first()
        channel_data = {
            "channel_number": channel_num,
            "assigned_user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "affiliation": user.affiliation,
                "channel_number": user.channel_number,
                "is_channel_assigned": user.is_channel_assigned  # 관리자가 명시적으로 할당한 상태
            } if user else None,
            "is_reporter_channel": False
        }
        channels.append(channel_data)
    
    # 채널 16 (신고자 채널)
    channels.append({
        "channel_number": 16,
        "assigned_user": None,
        "is_reporter_channel": True
    })
    
    return {"channels": channels}

@router.put("/channels/{channel_number}/assign", dependencies=[Depends(require_admin)])
async def assign_user_to_channel(
    channel_number: int,
    user_data: dict,
    current_user: User = Depends(get_current_user)
):
    """채널에 사용자 할당"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    # 채널번호 유효성 검사 (1-15만 허용)
    if not (1 <= channel_number <= 15):
        raise HTTPException(
            status_code=400, 
            detail="채널번호는 1-15 사이여야 합니다"
        )
    
    user_id = user_data.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=400, 
            detail="user_id가 필요합니다"
        )
    
    # 사용자 조회
    user = await User.get(id=user_id)
    
    # 기존 채널번호 사용자 확인
    existing_user = await User.filter(channel_number=channel_number).first()
    if existing_user and existing_user.id != user_id:
        raise HTTPException(
            status_code=400, 
            detail=f"채널번호 {channel_number}는 이미 {existing_user.username}에게 할당되었습니다"
        )
    
    # 사용자의 기존 채널번호 해제
    if user.channel_number:
        user.channel_number = None
        user.is_channel_assigned = False
    
    # 새 채널번호 할당
    user.channel_number = channel_number
    user.is_channel_assigned = True
    await user.save()
    
    return {"message": f"채널 {channel_number}에 {user.username}이 할당되었습니다"}

@router.put("/channels/{user_id}/assign", dependencies=[Depends(require_admin)])
async def assign_channel(
    user_id: int,
    channel_data: dict,
    current_user: User = Depends(get_current_user)
):
    """사용자에게 채널번호 할당/변경 (기존 API 유지)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    user = await User.get(id=user_id)
    new_channel = channel_data.get("channel_number")
    
    # 채널번호 유효성 검사 (1-15만 허용)
    if not (1 <= new_channel <= 15):
        raise HTTPException(
            status_code=400, 
            detail="채널번호는 1-15 사이여야 합니다"
        )
    
    # 기존 채널번호 사용자 확인
    existing_user = await User.filter(channel_number=new_channel).first()
    if existing_user and existing_user.id != user_id:
        raise HTTPException(
            status_code=400, 
            detail=f"채널번호 {new_channel}는 이미 {existing_user.username}에게 할당되었습니다"
        )
    
    # 채널번호 할당/변경
    user.channel_number = new_channel
    user.is_channel_assigned = True
    await user.save()
    
    return {"message": f"{user.username}에게 채널번호 {new_channel}가 할당되었습니다"}

@router.delete("/channels/{channel_number}/unassign", dependencies=[Depends(require_admin)])
async def unassign_user_from_channel(
    channel_number: int,
    current_user: User = Depends(get_current_user)
):
    """채널에서 사용자 해제"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    # 채널번호 유효성 검사 (1-15만 허용)
    if not (1 <= channel_number <= 15):
        raise HTTPException(
            status_code=400, 
            detail="채널번호는 1-15 사이여야 합니다"
        )
    
    # 해당 채널에 할당된 사용자 조회
    user = await User.filter(channel_number=channel_number).first()
    
    if not user:
        raise HTTPException(
            status_code=400, 
            detail=f"채널 {channel_number}에 할당된 사용자가 없습니다"
        )
    
    # 채널 해제
    user.channel_number = None
    user.is_channel_assigned = False
    await user.save()
    
    return {"message": f"채널 {channel_number}에서 {user.username}이 해제되었습니다"}

@router.delete("/channels/{user_id}/unassign", dependencies=[Depends(require_admin)])
async def unassign_channel(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """사용자의 채널번호 해제 (기존 API 유지)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    user = await User.get(id=user_id)
    user.channel_number = None
    user.is_channel_assigned = False
    await user.save()
    
    return {"message": f"{user.username}의 채널번호가 해제되었습니다"}

# ========== 사용자 관리 API ==========
@router.get("/users", dependencies=[Depends(require_admin)])
async def get_management_users(
    affiliation: str = None,
    current_user: User = Depends(get_current_user)
):
    """사용자 목록 조회"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    query = User.all()
    if affiliation:
        query = query.filter(affiliation=affiliation)
    
    users = await query.order_by('username')
    
    user_list = []
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "affiliation": user.affiliation,
            "channel_number": user.channel_number,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "is_channel_assigned": user.is_channel_assigned  # 관리자가 명시적으로 할당한 상태
        }
        user_list.append(user_data)
    
    return {"users": user_list}

@router.get("/users/unassigned", dependencies=[Depends(require_admin)])
async def get_unassigned_users(
    current_user: User = Depends(get_current_user)
):
    """채널 번호가 할당되지 않은 사용자 목록 조회 (채널 할당용)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    # 채널 번호가 할당되지 않은 사용자만 조회
    users = await User.filter(
        channel_number__isnull=True,
        role="streamer"  # 스트리머만 조회
    ).order_by('username')
    
    user_list = []
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "affiliation": user.affiliation,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        user_list.append(user_data)
    return {"users": user_list}
