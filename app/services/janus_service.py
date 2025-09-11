class JanusService:
    def __init__(self):
        # 서버 환경에 맞게 URL 설정
        import os
        if os.getenv("ENV_FILE") and "prod" in os.getenv("ENV_FILE"):
            # 프로덕션 환경 - hanswell.app 서버에서 Janus 접근 (HTTPS 사용)
            self.admin_url = "https://hanswell.app:8088/janus/admin"
        else:
            # 로컬 개발 환경
            self.admin_url = "http://localhost:8088/janus/admin"
    
    async def create_videoroom(self, room_id: int, description: str) -> dict[int, str]:
        """Videoroom 생성 (Admin API 사용)"""
        import requests
        
        # Room 생성
        room_data = {
            "janus": "message_plugin",
            "plugin": "janus.plugin.videoroom",
            "request": "create",
            "room": room_id,
            "description": description,
            "publishers": 16,  # 최대 16명 (채널 1~16)
            "is_private": False
        }
        
        try:
            # Room 생성
            response = requests.post(self.admin_url, json=room_data)
            print(f"Room {room_id} 생성: {response.status_code}")
            print(f"Room 생성 응답: {response.text}")
            
            if response.status_code == 200:
                return {"room_id": room_id, "status": "created"}
            else:
                return {"room_id": room_id, "status": "error", "message": response.text}
                
        except Exception as e:
            print(f"Room 생성 오류: {e}")
            return {"room_id": room_id, "status": "error", "message": str(e)}

