class JanusService:
    def __init__(self):
        # 서버 환경에 맞게 URL 설정
        import os
        if os.getenv("ENV_FILE") and "prod" in os.getenv("ENV_FILE"):
            # 프로덕션 환경 - hanswell.app Janus Admin API에 접근 (포트 7088, 경로 /admin)
            self.admin_url = "http://hanswell.app:7088/admin"
        else:
            # 로컬 개발 환경
            self.admin_url = "http://127.0.0.1:7088/admin"
        
        # Admin Secret (Janus 설정에 맞게 조정 필요)
        self.admin_secret = "janusoverlord"
    
    async def create_videoroom(self, room_id: int, description: str) -> dict[int, str]:
        """Videoroom 생성 (Admin API 사용)"""
        import requests
        
        # 먼저 방이 이미 존재하는지 확인
        try:
            list_response = requests.post(self.admin_url, json={
                "janus": "message_plugin",
                "plugin": "janus.plugin.videoroom",
                "request": {"request": "list"},
                "admin_secret": self.admin_secret
            })
            
            if list_response.status_code == 200 and str(room_id) in list_response.text:
                print(f"Room {room_id} 이미 존재함 - 생성 건너뛰기")
                return {"room_id": room_id, "status": "exists"}
                
        except Exception as e:
            print(f"Room 목록 확인 오류: {e}")
            # 목록 확인 실패해도 계속 진행
        
        # Room 생성 (permanent=true로 재시작 후에도 유지)
        import uuid
        transaction_id = str(uuid.uuid4())
        
        room_data = {
            "janus": "message_plugin",
            "plugin": "janus.plugin.videoroom",
            "request": {
                "request": "create",
                "room": room_id,
                "description": description,
                "publishers": 16,  # 최대 16명 (채널 1~16)
                "is_private": False,
                "permanent": True,  # 재시작 후에도 방 유지
            },
            "transaction": transaction_id,
            "admin_secret": self.admin_secret
        }
        
        try:
            # Room 생성
            print(f"[JanusAdmin] POST {self.admin_url} room_id={room_id}")
            response = requests.post(self.admin_url, json=room_data)
            print(f"Room {room_id} 생성: {response.status_code}")
            print(f"Room 생성 응답: {response.text}")
            
            if response.status_code == 200:
                # 응답 내용 확인
                if "error" in response.text.lower():
                    print(f"Janus 오류 발생하지만 방은 생성됨: {response.text}")
                    return {"room_id": room_id, "status": "created_with_error", "message": response.text}
                else:
                    return {"room_id": room_id, "status": "created"}
            elif "already exists" in response.text.lower():
                # 방이 이미 존재하는 경우
                print(f"Room {room_id} 이미 존재함")
                return {"room_id": room_id, "status": "exists"}
            else:
                return {"room_id": room_id, "status": "error", "message": response.text}
                
        except Exception as e:
            print(f"Room 생성 오류: {e}")
            return {"room_id": room_id, "status": "error", "message": str(e)}

