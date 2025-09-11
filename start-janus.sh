#!/bin/bash

# Janus Gateway 시작 스크립트

if [ "$1" = "prod" ]; then
    echo "🚀 서버용 Janus Gateway 시작..."
    docker-compose -f docker-compose.prod.yml up -d
else
    echo "🛠️  로컬 개발용 Janus Gateway 시작..."
    docker-compose up -d
fi

echo "✅ Janus Gateway가 시작되었습니다!"
echo "📊 상태 확인: docker ps"
echo "📋 로그 확인: docker logs janus"
