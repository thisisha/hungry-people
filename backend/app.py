import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import DatabaseManager
from models.budget_models import db
from services.data_processor import DataProcessor
from services.recommendation_engine import RecommendationEngine
from services.feature_flags import FeatureFlags
from routes.budget_routes import budget_bp

app = Flask(__name__)
CORS(app)  # CORS 활성화

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hungry_people.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy 초기화
db.init_app(app)
migrate = Migrate(app, db)

# 데이터베이스 매니저 및 추천 엔진 초기화
db_manager = DatabaseManager()
recommendation_engine = RecommendationEngine()

# 예산 관리 블루프린트 등록
app.register_blueprint(budget_bp)

@app.route('/')
def index():
    """메인 페이지 서빙"""
    return send_from_directory('..', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """정적 파일 서빙"""
    return send_from_directory('..', filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'message': 'Hungry People API 서버가 정상적으로 작동 중입니다.'
    })

@app.route('/healthz', methods=['GET'])
def healthz():
    """Kubernetes 스타일 헬스체크"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """백년가게 목록 조회"""
    try:
        region = request.args.get('region')
        keyword = request.args.get('keyword')
        limit = int(request.args.get('limit', 50))
        
        if region:
            restaurants = db_manager.get_restaurants_by_region(region)
        elif keyword:
            restaurants = db_manager.get_restaurants_by_keyword(keyword)
        else:
            # 전체 조회 (제한)
            restaurants = db_manager.get_restaurants_by_keyword('')
        
        # 제한 적용
        restaurants = restaurants[:limit]
        
        return jsonify({
            'success': True,
            'data': restaurants,
            'count': len(restaurants)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    """특정 백년가게 상세 정보 조회"""
    try:
        restaurants = db_manager.get_restaurants_by_keyword('')
        restaurant = next((r for r in restaurants if r['id'] == restaurant_id), None)
        
        if not restaurant:
            return jsonify({
                'success': False,
                'error': '백년가게를 찾을 수 없습니다.'
            }), 404
        
        return jsonify({
            'success': True,
            'data': restaurant
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """행사일정 목록 조회"""
    try:
        region = request.args.get('region')
        location = request.args.get('location')
        limit = int(request.args.get('limit', 50))
        
        if region:
            events = db_manager.get_events_by_region(region)
        elif location:
            events = db_manager.get_events_by_location(location)
        else:
            # 전체 조회 (제한)
            events = db_manager.get_events_by_region('')
        
        # 제한 적용
        events = events[:limit]
        
        return jsonify({
            'success': True,
            'data': events,
            'count': len(events)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """추천 서비스 - 행사 장소 근처 백년가게 추천"""
    try:
        location = request.args.get('location')
        region = request.args.get('region')
        event_id = request.args.get('event_id')
        limit = int(request.args.get('limit', 10))
        
        if not location and not region and not event_id:
            return jsonify({
                'success': False,
                'error': 'location, region 또는 event_id 파라미터가 필요합니다.'
            }), 400
        
        # 추천 타입별 처리
        if event_id:
            restaurants = recommendation_engine.get_event_based_recommendations(int(event_id), limit)
            recommendation_type = 'event_based'
        elif location:
            restaurants = recommendation_engine.get_location_based_recommendations(location, limit)
            recommendation_type = 'location_based'
        else:
            restaurants = recommendation_engine.get_region_based_recommendations(region, limit)
            recommendation_type = 'region_based'
        
        return jsonify({
            'success': True,
            'data': restaurants,
            'count': len(restaurants),
            'recommendation_type': recommendation_type,
            'search_criteria': {
                'location': location,
                'region': region,
                'event_id': event_id
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """지역 목록 조회"""
    try:
        regions = db_manager.get_all_regions()
        
        return jsonify({
            'success': True,
            'data': regions,
            'count': len(regions)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search', methods=['GET'])
def search():
    """통합 검색"""
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')  # all, restaurants, events
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify({
                'success': False,
                'error': '검색어가 필요합니다.'
            }), 400
        
        results = {
            'restaurants': [],
            'events': []
        }
        
        if search_type in ['all', 'restaurants']:
            restaurants = db_manager.get_restaurants_by_keyword(query)[:limit//2]
            results['restaurants'] = restaurants
        
        if search_type in ['all', 'events']:
            events = db_manager.get_events_by_location(query)[:limit//2]
            results['events'] = events
        
        total_count = len(results['restaurants']) + len(results['events'])
        
        return jsonify({
            'success': True,
            'data': results,
            'total_count': total_count,
            'query': query
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/smart-recommendations', methods=['GET'])
def get_smart_recommendations():
    """스마트 추천 - 사용자 쿼리 분석하여 최적의 추천 제공"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({
                'success': False,
                'error': '검색어가 필요합니다.'
            }), 400
        
        # 스마트 추천 엔진 사용
        recommendations = recommendation_engine.get_smart_recommendations(query, limit)
        
        return jsonify({
            'success': True,
            'data': recommendations,
            'query': query
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """통계 정보 조회"""
    try:
        regions = db_manager.get_all_regions()
        
        stats = {
            'total_restaurants': len(db_manager.get_restaurants_by_keyword('')),
            'total_events': len(db_manager.get_events_by_region('')),
            'total_regions': len(regions),
            'regions': regions
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'API 엔드포인트를 찾을 수 없습니다.'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '서버 내부 오류가 발생했습니다.'
    }), 500

if __name__ == '__main__':
    print("Hungry People API 서버를 시작합니다...")
    print("API 엔드포인트:")
    print("  GET /api/health - 서버 상태 확인")
    print("  GET /api/restaurants - 백년가게 목록")
    print("  GET /api/restaurants/<id> - 백년가게 상세")
    print("  GET /api/events - 행사일정 목록")
    print("  GET /api/recommendations - 추천 서비스")
    print("  GET /api/smart-recommendations - 스마트 추천")
    print("  GET /api/regions - 지역 목록")
    print("  GET /api/search - 통합 검색")
    print("  GET /api/stats - 통계 정보")
    
    # Railway 환경 변수에서 포트를 가져옴
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('RAILWAY_ENVIRONMENT') != 'production'
    
    print(f"\n서버 시작: http://0.0.0.0:{port}")
    print(f"디버그 모드: {debug}")
    print(f"Railway 환경: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)