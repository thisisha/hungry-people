import csv
import os
from typing import List, Dict, Any

class CSVReader:
    """한글 CSV 파일을 읽기 위한 클래스"""
    
    def __init__(self):
        self.encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr']
    
    def read_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        CSV 파일을 읽어서 딕셔너리 리스트로 반환
        
        Args:
            file_path: CSV 파일 경로
            
        Returns:
            List[Dict[str, Any]]: CSV 데이터를 딕셔너리 리스트로 변환한 결과
        """
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding, newline='') as file:
                    reader = csv.DictReader(file)
                    data = list(reader)
                    print(f"Successfully read {file_path} with encoding: {encoding}")
                    print(f"Total rows: {len(data)}")
                    return data
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error reading {file_path} with encoding {encoding}: {e}")
                continue
        
        raise Exception(f"Failed to read {file_path} with any encoding")

class DataProcessor:
    """CSV 데이터를 처리하는 클래스"""
    
    def __init__(self):
        self.csv_reader = CSVReader()
    
    def load_restaurant_data(self, file_path: str) -> List[Dict[str, Any]]:
        """백년가게 데이터 로드"""
        data = self.csv_reader.read_csv(file_path)
        
        # 데이터 정제 및 변환
        processed_data = []
        for row in data:
            processed_row = {
                'id': int(row.get('연번', 0)),
                'name': row.get('업체명', '').strip(),
                'address': row.get('업체주소', '').strip(),
                'phone': row.get('연락처', '').strip(),
                'region': self._extract_region(row.get('업체주소', ''))
            }
            processed_data.append(processed_row)
        
        return processed_data
    
    def load_event_data(self, file_path: str) -> List[Dict[str, Any]]:
        """행사일정 데이터 로드"""
        data = self.csv_reader.read_csv(file_path)
        
        processed_data = []
        for row in data:
            processed_row = {
                'id': int(row.get('순번', 0)),
                'organization': row.get('기관명', '').strip(),
                'event_name': row.get('행사명', '').strip(),
                'host_organization': row.get('주관기관명', '').strip(),
                'region': row.get('행사지역', '').strip(),
                'location': row.get('행사장소', '').strip(),
                'tech_category': row.get('기술 분류', '').strip(),
                'hashtags': row.get('해시태그', '').strip(),
                'start_date': row.get('행사기간-시작일', '').strip(),
                'end_date': row.get('행사기간-종료일', '').strip()
            }
            processed_data.append(processed_row)
        
        return processed_data
    
    def load_schedule_data(self, file_path: str) -> List[Dict[str, Any]]:
        """유관기관 일정 데이터 로드"""
        data = self.csv_reader.read_csv(file_path)
        
        processed_data = []
        for row in data:
            processed_row = {
                'id': int(row.get('구분', 0)),
                'start_date': row.get('일정 시작일', '').strip(),
                'end_date': row.get('일정 종료일', '').strip(),
                'title': row.get('일정제목', '').strip(),
                'created_date': row.get('작성일', '').strip()
            }
            processed_data.append(processed_row)
        
        return processed_data
    
    def _extract_region(self, address: str) -> str:
        """주소에서 지역 정보 추출"""
        if not address:
            return ''
        
        # 주요 지역 키워드 추출
        regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', 
                  '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
        
        for region in regions:
            if region in address:
                return region
        
        return '기타'

if __name__ == "__main__":
    processor = DataProcessor()
    
    # 데이터 로드 테스트
    try:
        restaurant_data = processor.load_restaurant_data('data/소상공인시장진흥공단_전국 백년가게 지정리스트 현황 정보_20250724.csv')
        print(f"\n백년가게 데이터 로드 완료: {len(restaurant_data)}개")
        print("샘플 데이터:")
        for i, item in enumerate(restaurant_data[:3]):
            print(f"  {i+1}. {item}")
        
        event_data = processor.load_event_data('data/(재)연구개발특구진흥재단_행사일정_20250714.csv')
        print(f"\n행사일정 데이터 로드 완료: {len(event_data)}개")
        print("샘플 데이터:")
        for i, item in enumerate(event_data[:3]):
            print(f"  {i+1}. {item}")
        
        schedule_data = processor.load_schedule_data('data/(재)연구개발특구진흥재단_재단 유관기관 일정_20250821.csv')
        print(f"\n유관기관 일정 데이터 로드 완료: {len(schedule_data)}개")
        print("샘플 데이터:")
        for i, item in enumerate(schedule_data[:3]):
            print(f"  {i+1}. {item}")
            
    except Exception as e:
        print(f"데이터 로드 중 오류 발생: {e}")
